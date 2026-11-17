#!/usr/bin/env python3
"""Validate a configuration example from the routing guide in containerlab.

The example is read from the vendor tab of the guide page itself, so the lab
always tests the published text. Each run has two phases:

1. control: the DUT runs only the base config; every announced prefix must
   reach the collector.
2. test: the snippet is applied in a config session; prefixes listed under
   `accept` must reach the collector, prefixes under `reject` must not.

expect.yml lists one or more cases. Each case runs in a fresh lab and may
select code blocks of the tab (`blocks`) and add vendor specific `context`
config that the snippet relies on but does not contain. `tab` overrides the
vendor's default tab name; a case may define a literal `snippet` for
counter-checks, which the report marks as not taken from the guide.
`attributes` compares route attributes (communities, large_communities,
origin, as_path at the collector; local_pref on the DUT, None if the DUT has
no such route; route_count at the collector with prefix ipv4 or ipv6;
session_state of the collector's session to the DUT address in prefix) with
the expected value in the control and/or test phase.

Usage:
    ./run.py route_filtering/inbound/prefix_length --vendor arista [--keep]
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import yaml

LABS = Path(__file__).resolve().parent
REPO = LABS.parent
TOPO = LABS / "common" / "topo.clab.yml"

VENDORS = {
    # Arista boots with the base config as startup-config.
    "arista": {
        "tab": "Arista EOS",
        "kind": "arista_ceos",
        "image": os.environ.get("RG_ARISTA_IMAGE", "ceos64:4.36.3M"),
        "startup": LABS / "common" / "base" / "arista.cfg",
    },
    # VyOS boots with the containerlab default config; the base config is
    # applied as set commands after deployment.
    "vyos": {
        "tab": "VyOS",
        "kind": "vyosnetworks_vyos",
        "image": os.environ.get("RG_VYOS_IMAGE", "vyos:2026.11.15-0018-rolling"),
        "base": LABS / "common" / "base" / "vyos.cfg",
    },
    # FRR runs as a plain linux node; addresses are set by the topology, the
    # BGP base config is applied with vtysh after deployment.
    "frr": {
        "tab": "Cisco IOS / FRRouting",
        "kind": "linux",
        "image": os.environ.get("RG_FRR_IMAGE", "quay.io/frrouting/frr:10.7.1"),
        "base": LABS / "common" / "base" / "frr.cfg",
        "node": {
            "binds": ["frr/daemons:/etc/frr/daemons"],
            "exec": [
                "sysctl -w net.ipv6.conf.all.disable_ipv6=0",
                "touch /etc/frr/vtysh.conf",
                "ip addr add 198.51.100.0/31 dev eth1",
                "ip addr add 2001:db8::2/64 dev eth1",
                "ip addr add 198.51.100.2/31 dev eth2",
                "ip addr add 2001:db8:1::2/64 dev eth2",
            ],
        },
    },
}

VYOS_SCRIPT = "source /opt/vyatta/etc/functions/script-template\n{body}\n"
VYOS_ERRORS = re.compile(r"invalid|failed|error|not valid", re.IGNORECASE)

BOOT_TIMEOUT = 600
CONVERGE_TIMEOUT = 90


def sh(cmd, env=None, check=True):
    res = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if check and res.returncode != 0:
        sys.exit(f"command failed: {' '.join(cmd)}\n{res.stdout}{res.stderr}")
    return res


def extract_blocks(page, tab):
    """Return the code blocks of the given content tab, dedented."""
    lines = page.read_text().splitlines()
    try:
        start = lines.index(f'=== "{tab}"')
    except ValueError:
        sys.exit(f'tab "{tab}" not found in {page}')
    blocks, current = [], None
    for line in lines[start + 1:]:
        if line and not line.startswith("    "):
            break
        text = line[4:]
        if text.strip().startswith("```"):
            if current is None:
                current = []
            else:
                blocks.append("\n".join(current))
                current = None
        elif current is not None:
            current.append(text)
    if not blocks:
        sys.exit(f'tab "{tab}" in {page} contains no code block')
    return blocks


class Lab:
    def __init__(self, page_dir, vendor):
        self.vendor_name = vendor
        self.sessions = 0
        self.vendor = VENDORS[vendor]
        slug = page_dir.name.replace("_", "-")
        self.name = f"rg-{slug}-{vendor}"
        self.env = dict(
            os.environ,
            RG_LAB_NAME=self.name,
            RG_DUT_KIND=self.vendor["kind"],
            RG_DUT_IMAGE=self.vendor["image"],
            RG_DUT_CONFIG=str(self.vendor.get("startup", "none")),
            RG_INJECT_CONFIG=str(page_dir / "inject.conf"),
        )
        # Per-run copy of the topology next to the original, so relative binds
        # keep working; without a startup-config the key is dropped, because
        # containerlab rejects an empty path.
        self.topo = TOPO.with_name(f".{self.name}.clab.yml")
        topo = yaml.safe_load(TOPO.read_text())
        dut = topo["topology"]["nodes"]["dut"]
        if "startup" not in self.vendor:
            del dut["startup-config"]
        dut.update(self.vendor.get("node", {}))
        # Optional page specific collector config, e.g. when the collector
        # has to announce routes itself
        if (page_dir / "collector.conf").exists():
            topo["topology"]["nodes"]["collector"]["binds"][1] = f"{page_dir / 'collector.conf'}:/etc/frr/frr.conf"
        # Optional RPKI cache: RTRTR serves the page's rtr.json (ROAs and
        # ASPAs) on dut:eth3. StayRTR v0.6.4 only speaks RTR v0/v1 and
        # therefore cannot deliver ASPAs.
        rtr_json = page_dir / "rtr.json"
        if rtr_json.exists():
            topo["topology"]["nodes"]["rtr"] = {
                "kind": "linux",
                "image": os.environ.get("RG_RTR_IMAGE", "nlnetlabs/rtrtr:v0.3.3"),
                "user": "0",
                "binds": [f"{rtr_json}:/rtr.json:ro", f"{LABS / 'common' / 'rtrtr.conf'}:/etc/rtrtr.conf:ro"],
                "cmd": "--config /etc/rtrtr.conf",
                "exec": ["ip addr add 198.51.100.5/31 dev eth1"],
            }
            topo["topology"]["links"].append({"endpoints": ["dut:eth3", "rtr:eth1"]})
        self.topo.write_text(yaml.safe_dump(topo, sort_keys=False))

    def container(self, node):
        return f"clab-{self.name}-{node}"

    def deploy(self):
        sh(["containerlab", "deploy", "-t", str(self.topo), "--reconfigure"], env=self.env)

    def destroy(self):
        sh(["containerlab", "destroy", "-t", str(self.topo), "--cleanup"], env=self.env, check=False)

    def vtysh(self, node, command):
        out = sh(["docker", "exec", self.container(node), "vtysh", "-c", command]).stdout
        return json.loads(out)

    def eos(self, commands):
        return sh(["docker", "exec", self.container("dut"), "Cli", "-p", "15", "-c", commands], check=False)

    def vbash(self, body):
        """Run a VyOS script as admin in group vyattacfg (see VyOS docs: command scripting)."""
        dut = self.container("dut")
        script = VYOS_SCRIPT.format(body=body)
        subprocess.run(["docker", "exec", "-i", dut, "sh", "-c", "cat > /tmp/rg.sh"], input=script, text=True, check=True)
        return sh(["docker", "exec", "-u", "admin", dut, "sg", "vyattacfg", "-c", "/bin/vbash /tmp/rg.sh"], check=False)

    def apply(self, snippet):
        """Apply config lines in one commit, return the CLI error lines."""
        if self.vendor_name == "arista":
            # EOS refuses to reuse a committed session name
            self.sessions += 1
            res = self.eos("\n".join([f"configure session rg{self.sessions}", snippet, "commit"]))
            return [l for l in (res.stdout + res.stderr).splitlines() if l.startswith("%")]
        if self.vendor_name == "frr":
            dut = self.container("dut")
            subprocess.run(["docker", "exec", "-i", dut, "sh", "-c", "cat > /tmp/rg.conf"],
                           input=snippet + "\n", text=True, check=True)
            res = sh(["docker", "exec", dut, "vtysh", "-f", "/tmp/rg.conf"], check=False)
            errors = [l for l in (res.stdout + res.stderr).splitlines() if "%" in l]
            if res.returncode != 0 and not errors:
                errors = [f"vtysh exit code {res.returncode}"]
            return errors
        res = self.vbash("\n".join(["configure", snippet, "commit", "exit"]))
        return [l for l in (res.stdout + res.stderr).splitlines() if VYOS_ERRORS.search(l)]

    def running_lines(self):
        if self.vendor_name == "arista":
            return {l.strip() for l in self.eos("show running-config").stdout.splitlines()}
        if self.vendor_name == "frr":
            # FRR adds sequence numbers to prefix-list entries
            out = sh(["docker", "exec", self.container("dut"), "vtysh", "-c", "show running-config"]).stdout
            return {re.sub(r" seq \d+", "", l.strip()) for l in out.splitlines()}
        out = self.vbash("show configuration commands").stdout
        return {l.strip().replace("'", "") for l in out.splitlines()}

    def version(self):
        if self.vendor_name == "arista":
            return self.eos("show version").stdout.strip()
        if self.vendor_name == "frr":
            return sh(["docker", "exec", self.container("dut"), "vtysh", "-c", "show version"]).stdout.strip()
        return self.vbash("show version").stdout.strip()

    def established(self, node):
        summary = self.vtysh(node, "show bgp summary json")
        peers = [p for af in summary.values() for p in af.get("peers", {}).values()]
        return bool(peers) and all(p.get("state") == "Established" for p in peers)

    def collector_path(self, prefix):
        """Best path for a prefix at the collector (FRR JSON), or None."""
        af = "ipv6" if ":" in prefix else "ipv4"
        paths = self.vtysh("collector", f"show bgp {af} unicast {prefix} json").get("paths", [])
        return next((p for p in paths if p.get("bestpath", {}).get("overall")), None)

    def dut_local_pref(self, prefix):
        """Local preference of the active path on the DUT, or None."""
        af = "ipv6" if ":" in prefix else "ip"
        if self.vendor_name == "arista":
            data = json.loads(self.eos(f"show {af} bgp {prefix} | json").stdout)
            entry = data["vrfs"]["default"]["bgpRouteEntries"].get(prefix, {})
            paths = [p for p in entry.get("bgpRoutePaths", []) if p.get("routeType", {}).get("active")]
            return paths[0].get("localPreference") if paths else None
        af = "ipv6" if ":" in prefix else "ipv4"
        out = sh(["docker", "exec", self.container("dut"), "vtysh", "-c", f"show bgp {af} unicast {prefix} json"]).stdout
        paths = json.loads(out).get("paths", [])
        best = next((p for p in paths if p.get("bestpath", {}).get("overall")), None)
        return best.get("locPrf") if best else None

    def attribute(self, prefix, field):
        """Current value of a route attribute; lists are sorted for comparison."""
        if field == "session_state":
            # prefix is the DUT's address as seen by the collector
            summary = self.vtysh("collector", "show bgp summary json")
            states = [af["peers"][prefix]["state"] for af in summary.values() if prefix in af.get("peers", {})]
            return states[0] if states else None
        if field == "route_count":
            # prefix is the address family here: ipv4 or ipv6
            return len(self.vtysh("collector", f"show bgp {prefix} unicast json").get("routes", {}))
        if field == "local_pref":
            return self.dut_local_pref(prefix)
        path = self.collector_path(prefix)
        if path is None:
            return None
        if field == "communities":
            return sorted(path.get("community", {}).get("string", "").split())
        if field == "large_communities":
            return sorted(path.get("largeCommunity", {}).get("string", "").split())
        if field == "origin":
            return path.get("origin")
        if field == "as_path":
            return path.get("aspath", {}).get("string")
        sys.exit(f"unknown attribute field {field}")

    def collector_routes(self):
        routes = set()
        for af in ("ipv4", "ipv6"):
            routes |= set(self.vtysh("collector", f"show bgp {af} unicast json").get("routes", {}))
        return routes


def wait_for(check, timeout, what):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if check():
                return True
        except (json.JSONDecodeError, SystemExit):
            pass
        time.sleep(5)
    print(f"timeout waiting for {what}")
    return False


def attributes_ok(lab, case, phase):
    """Check the case's attribute expectations for one phase ("control" or "test")."""
    for a in case.get("attributes", []):
        if phase in a:
            want = sorted(a[phase]) if isinstance(a[phase], list) else a[phase]
            if lab.attribute(a["prefix"], a["field"]) != want:
                return False
    return True


def attribute_report(lab, case, phase):
    lines = []
    for a in case.get("attributes", []):
        if phase in a:
            want = sorted(a[phase]) if isinstance(a[phase], list) else a[phase]
            got = lab.attribute(a["prefix"], a["field"])
            mark = "ok" if got == want else "MISMATCH"
            lines.append(f"- {a['field']} of {a['prefix']}: expected {want}, got {got} ({mark})")
    return lines


def run_case(lab, case, snippet, context, report):
    """Deploy a fresh lab, run control and test phase, return True on success."""
    accept, reject = set(case.get("accept", [])), set(case.get("reject", []))
    results = {}
    lab.deploy()
    if "base" in lab.vendor:
        base = lab.vendor["base"].read_text()
        errors = lab.apply("\n".join(l for l in base.splitlines() if l and not l.startswith("#")))
        if errors:
            sys.exit(f"base config failed: {errors}")
    if context:
        errors = lab.apply(context)
        if errors:
            sys.exit(f"context config failed: {errors}")

    if not wait_for(lambda: lab.established("inject") and lab.established("collector"), BOOT_TIMEOUT, "BGP sessions"):
        sys.exit("BGP sessions did not come up")

    # Phase 1: control run without the snippet
    results["control"] = wait_for(lambda: accept | reject <= lab.collector_routes() and attributes_ok(lab, case, "control"),
                                  CONVERGE_TIMEOUT, "control routes")
    seen = lab.collector_routes()
    report += ["", "### Context (applied with the base config, not part of the snippet)", "```", context or "(none)", "```",
               "", "### Control run (base config only)", "",
               f"- expected at collector: all {len(accept | reject)} announced prefixes",
               f"- missing: {sorted((accept | reject) - seen) or 'none'}",
               *attribute_report(lab, case, "control"),
               f"- result: {'PASS' if results['control'] else 'FAIL'}"]

    # Phase 2: apply the snippet exactly as published
    errors = lab.apply(snippet)
    running_lines = lab.running_lines()
    # comments and mode commands (EOS RCF: compile, commit, exit) do not show up in the config
    missing_lines = [l for l in snippet.splitlines()
                     if l.strip() and not l.strip().startswith(("!", "#"))
                     and l.strip() not in ("exit", "compile", "commit") and l.strip() not in running_lines]
    results["apply"] = not errors and not missing_lines
    report += ["", "### Snippet", "```", snippet, "```", "",
               f"- CLI errors: {errors or 'none'}",
               f"- snippet lines missing in running-config: {missing_lines or 'none'}",
               f"- result: {'PASS' if results['apply'] else 'FAIL'}"]

    # Route refresh in both directions so new inbound and outbound policies are evaluated
    sh(["docker", "exec", lab.container("inject"), "vtysh", "-c", "clear bgp * soft out"])
    sh(["docker", "exec", lab.container("collector"), "vtysh", "-c", "clear bgp * soft in"])
    sh(["docker", "exec", lab.container("collector"), "vtysh", "-c", "clear bgp * soft out"])
    results["test"] = wait_for(lambda: accept <= lab.collector_routes() and not reject & lab.collector_routes()
                               and attributes_ok(lab, case, "test"), CONVERGE_TIMEOUT, "test routes")
    seen = lab.collector_routes()
    report += ["", "### Test run (with snippet)", "",
               f"- accepted as expected: {sorted(accept & seen)}",
               f"- missing although expected: {sorted(accept - seen) or 'none'}",
               f"- rejected as expected: {sorted(reject - seen)}",
               f"- present although rejected: {sorted(reject & seen) or 'none'}",
               *attribute_report(lab, case, "test"),
               f"- result: {'PASS' if results['test'] else 'FAIL'}"]
    return all(results.get(k) for k in ("control", "apply", "test"))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("page", help="lab directory relative to labs/, e.g. route_filtering/inbound/prefix_length")
    parser.add_argument("--vendor", choices=VENDORS, required=True)
    parser.add_argument("--keep", action="store_true", help="do not destroy the lab after the last case")
    args = parser.parse_args()

    page_dir = LABS / args.page
    expect = yaml.safe_load((page_dir / "expect.yml").read_text())
    lab = Lab(page_dir, args.vendor)
    tab = expect.get("tab", lab.vendor["tab"])
    # Only read the guide when a case uses its code blocks
    if all("snippet" in c for c in expect["cases"]):
        blocks = []
    else:
        blocks = extract_blocks(REPO / expect["page"], tab)
    image_id = sh(["docker", "image", "inspect", lab.vendor["image"], "--format", "{{.Id}}"]).stdout.strip()
    report = [f"# {expect['page']} / {tab}", "",
              f"- date: {datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')}",
              f"- lab: {lab.name}",
              f"- image: {lab.vendor['image']} ({image_id})"]

    passed = True
    for i, case in enumerate(expect["cases"]):
        if "snippet" in case:
            snippet = case["snippet"].strip()
            source = "snippet NOT from the guide, defined in expect.yml"
        else:
            selected = case.get("blocks", range(len(blocks)))
            snippet = "\n".join(blocks[n] for n in selected)
            source = f"code blocks {list(selected)} of the guide tab"
        context = case.get("context", {}).get(args.vendor, "").strip()
        report += ["", f"## Case: {case['name']} ({source})"]
        try:
            ok = run_case(lab, case, snippet, context, report)
            if i == 0:
                report += ["", "### DUT version", "```", lab.version(), "```"]
        finally:
            if not (args.keep and i == len(expect["cases"]) - 1):
                lab.destroy()
        report += ["", f"**Case result: {'PASS' if ok else 'FAIL'}**"]
        passed = passed and ok

    report += ["", f"**Overall: {'PASS' if passed else 'FAIL'}**", ""]
    out = LABS / "reports" / args.page / f"{args.vendor}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report))
    print("\n".join(report))
    print(f"report: {out}")
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()

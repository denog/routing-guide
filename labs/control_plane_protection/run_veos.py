#!/usr/bin/env python3
"""Validate session protection examples (TCP-AO, keyrings) on two vEOS VMs.

TCP-AO needs a TCP stack with TCP-AO support, so these examples run on vEOS
VMs instead of cEOS containers. Deploy the VMs once (they take ~10 minutes to
boot) and keep them running:

    containerlab deploy -t topo-veos.clab.yml

Each case resets both VMs to their startup-config, checks that the BGP
session comes up without authentication (control), applies the DUT snippet
and the peer config, and checks the session state and the TCP-AO details.

Usage:
    ./run_veos.py tcp-authentication-option
"""

import argparse
import base64
import datetime
import json
import re
import ssl
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from run import REPO, extract_blocks  # noqa: E402

LAB = "rg-veos"
NEIGHBOR = {"dut": "198.51.100.1", "peer": "198.51.100.0"}
TIMEOUT = 300


def eapi(node, cmds, fmt="text"):
    """Run commands via eAPI; returns the result list or raises with the CLI errors."""
    ip = subprocess.run(["docker", "inspect", "-f", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}",
                         f"clab-{LAB}-{node}"], capture_output=True, text=True, check=True).stdout.strip()
    body = {"jsonrpc": "2.0", "method": "runCmds", "id": 1,
            "params": {"version": 1, "cmds": ["enable"] + cmds, "format": fmt}}
    req = urllib.request.Request(f"https://{ip}/command-api", data=json.dumps(body).encode(), headers={
        "Authorization": "Basic " + base64.b64encode(b"admin:admin").decode(),
        "Content-Type": "application/json"})
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # eAPI is briefly unavailable after "configure replace", so retry on connection errors
    deadline = time.time() + 600
    while True:
        try:
            res = json.load(urllib.request.urlopen(req, context=ctx, timeout=600))
            break
        except (urllib.error.URLError, ConnectionError):
            if time.time() > deadline:
                raise
            time.sleep(15)
    if "error" in res:
        errors = [e for d in res["error"].get("data", []) for e in d.get("errors", [])]
        raise RuntimeError(errors or [res["error"]["message"]])
    return res["result"][1:]


def text(node, cmd):
    return eapi(node, [cmd])[0]["output"]


def neighbor(node):
    peers = eapi(node, [f"show ip bgp neighbors {NEIGHBOR[node]}"], "json")[0]["vrfs"]["default"]["peerList"]
    return peers[0] if peers else {}


def apply(node, config, session):
    """Apply config lines in one config session; returns the CLI errors."""
    lines = [l for l in config.splitlines() if l.strip() and not l.strip().startswith("!")]
    try:
        eapi(node, [f"configure session {session}"] + lines + ["commit"])
        return []
    except RuntimeError as err:
        eapi(node, [f"configure session {session}", "abort"])
        return err.args[0]


def parallel(func, *args_per_node):
    """Run func for dut and peer at the same time (commits on vEOS are slow)."""
    results = {}
    threads = [threading.Thread(target=lambda n=n, a=a: results.__setitem__(n, func(n, *a)))
               for n, a in zip(("dut", "peer"), args_per_node)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results


def wait_for(check, timeout=TIMEOUT):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if check():
            return True
        time.sleep(10)
    return False


def expand_secret(line):
    """Regex for how EOS shows a secret line in the running-config: the key is
    stored encrypted and a single lifetime ('infinite' or 'START END') is
    written out as identical receive and transmit lifetimes."""
    m = re.match(r"secret (\S+) (?:0 )?\S+ (.*)$", line)
    rest = m.group(2)
    if "receive-lifetime" not in rest:
        rest = f"receive-lifetime {rest} transmit-lifetime {rest}"
    return re.compile(rf"secret {re.escape(m.group(1))} 7 \S+ {re.escape(rest)}$")


def missing_lines(node, snippet):
    running = [l.strip() for l in text(node, "show running-config").splitlines()]
    missing = []
    for line in (l.strip() for l in snippet.splitlines()):
        if not line or line.startswith("!") or line == "exit":
            continue
        if line.startswith("secret "):
            if not any(expand_secret(line).match(r) for r in running):
                missing.append(line)
        elif line not in running:
            missing.append(line)
    return missing


def render(template, now):
    """Replace {t+SECONDS} with a UTC timestamp relative to the DUT clock."""
    return re.sub(r"\{t\+(\d+)\}",
                  lambda m: (now + datetime.timedelta(seconds=int(m.group(1)))).strftime("%Y-%m-%d %H:%M:%S"),
                  template)


def run_case(case, blocks, report, number):
    ok = True
    # Reset both VMs to the base config and check the session without authentication
    for node in ("dut", "peer"):
        eapi(node, ["configure replace startup-config"])
    control = wait_for(lambda: neighbor("dut").get("state") == "Established")
    report += ["", "### Control run (base config, no authentication)", "",
               f"- session state: {neighbor('dut').get('state')}",
               f"- result: {'PASS' if control else 'FAIL'}"]
    ok &= control

    clock = eapi("dut", ["show clock"], "json")[0]
    now = datetime.datetime.fromtimestamp(clock["utcTime"], datetime.timezone.utc)
    if "snippet" in case["dut"]:
        dut_config = render(case["dut"]["snippet"], now).strip()
        source = "snippet NOT from the guide, defined in expect.yml"
    else:
        dut_config = "\n".join(blocks[n] for n in case["dut"].get("blocks", range(len(blocks))))
        source = "guide tab"
    peer_config = render(case["peer"], now).strip()

    errors = parallel(apply, (dut_config, f"rg{number}"), (peer_config, f"rg{number}"))
    missing = missing_lines("dut", dut_config)
    applied = not errors["dut"] and not errors["peer"] and not missing
    report += ["", f"### DUT config ({source})", "```", dut_config, "```",
               "", "### Peer config (expect.yml)", "```", peer_config, "```", "",
               f"- CLI errors: dut {errors['dut'] or 'none'}, peer {errors['peer'] or 'none'}",
               f"- DUT config lines missing in running-config: {missing or 'none'}",
               f"- result: {'PASS' if applied else 'FAIL'}"]
    ok &= applied

    expect = case["expect"]
    if expect.get("established", True):
        up = wait_for(lambda: neighbor("dut").get("state") == "Established")
    else:
        # the session must stay down for the whole wait time
        up = wait_for(lambda: neighbor("dut").get("state") == "Established", expect.get("wait", 120))
    state_ok = up == expect.get("established", True)
    report += ["", "### Test run", "",
               f"- session state: {neighbor('dut').get('state')} (expected "
               f"{'Established' if expect.get('established', True) else 'not Established'})",
               f"- result: {'PASS' if state_ok else 'FAIL'}"]
    ok &= state_ok

    if "rotation" in expect:
        # Wait until the given offset (relative to the DUT clock at apply time)
        # and make sure the session was not re-established in between
        before = neighbor("dut").get("establishedTransitions")
        end = now + datetime.timedelta(seconds=expect["rotation"]["wait_until"])
        while datetime.datetime.now(datetime.timezone.utc) < end:
            time.sleep(10)
        time.sleep(30)
        after = neighbor("dut")
        stable = after.get("state") == "Established" and after.get("establishedTransitions") == before
        report += [f"- established transitions before/after key rotation: {before}/{after.get('establishedTransitions')}",
                   f"- session stayed up during rotation: {'PASS' if stable else 'FAIL'}"]
        ok &= stable

    detail = text("dut", f"show ip bgp neighbors {NEIGHBOR['dut']}")
    for pattern in expect.get("neighbor", []):
        found = re.search(pattern, detail, re.MULTILINE) is not None
        report.append(f"- neighbor detail matches /{pattern}/: {'PASS' if found else 'FAIL'}")
        ok &= found
    if "profile" in expect:
        profile = text("dut", f"show management security session shared-secret profile {expect['profile']['name']}")
        for pattern in expect["profile"]["match"]:
            found = re.search(pattern, profile, re.MULTILINE) is not None
            report.append(f"- profile matches /{pattern}/: {'PASS' if found else 'FAIL'}")
            ok &= found
        report += ["", "```", profile.strip(), "```"]
    return ok


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("page", help="lab directory in control_plane_protection/, e.g. tcp-authentication-option")
    args = parser.parse_args()

    expect = yaml.safe_load((HERE / args.page / "expect.yml").read_text())
    blocks = extract_blocks(REPO / expect["page"], expect.get("tab", "Arista EOS"))
    version = text("dut", "show version")
    report = [f"# {expect['page']} / {expect.get('tab', 'Arista EOS')}", "",
              f"- date: {datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')}",
              f"- lab: {LAB} (vEOS VMs)", "", "```", version.strip(), "```"]
    passed = True
    for i, case in enumerate(expect["cases"], 1):
        report += ["", f"## Case: {case['name']}"]
        ok = run_case(case, blocks, report, i)
        report += ["", f"**Case result: {'PASS' if ok else 'FAIL'}**"]
        passed &= ok
    report += ["", f"**Overall: {'PASS' if passed else 'FAIL'}**", ""]
    out = HERE.parent / "reports" / "control_plane_protection" / f"{args.page}-arista.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report))
    print("\n".join(report))
    print(f"report: {out}")
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()

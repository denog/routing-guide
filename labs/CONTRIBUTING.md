# Contributing to the labs

This guide explains how to add a test for a guide page, how to describe the
expected results, and how to add a vendor. Read the [README](README.md) first
for the overall idea.

- [Adding a test for a guide page](#adding-a-test-for-a-guide-page)
- [Rules for examples](#rules-for-examples)
- [Address and AS plan](#address-and-as-plan)
- [Files of a lab directory](#files-of-a-lab-directory)
- [expect.yml reference](#expectyml-reference)
- [TCP-AO tests on vEOS](#tcp-ao-tests-on-veos)
- [Adding a vendor](#adding-a-vendor)
- [How the runner works](#how-the-runner-works)
- [Style](#style)

## Adding a test for a guide page

The example below adds a test for the Arista example of
`docs/guides/route_filtering/inbound/prefix_length.md`.

**1. Write the example on the guide page.** Add a content tab with the vendor
name used by the runner (`Arista EOS`, `VyOS` or `Cisco IOS / FRRouting`) and
put the configuration in a code block. Use the addresses and AS numbers of
the [address plan](#address-and-as-plan), so the example can be loaded as it
is:

````markdown
=== "Arista EOS"
    ```
    ip prefix-list PREFIX_LENGTH_v4
       seq 10 permit 0.0.0.0/0 ge 25 le 32
    ...
    router bgp 64500
       address-family ipv4
          neighbor 198.51.100.1 route-map example-in in
    ```

    See the EOS manual: [ACLs and Route Maps](https://www.arista.com/en/um-eos/eos-acls-and-route-maps).
````

End the tab with a link to the vendor documentation (see
[Rules for examples](#rules-for-examples)).

**2. Create the lab directory.** It has the same path as the page below
`docs/guides/`:

```shell
mkdir -p labs/route_filtering/inbound/prefix_length
```

**3. Decide which routes inject announces.** Pick routes that the example
must accept and routes it must reject. Cover the edge cases: the shortest and
longest allowed prefix, one beyond each limit, IPv4 and IPv6. Write them to
`inject.conf` (an FRR config, see [inject.conf](#injectconf)).

**4. Write `expect.yml`.** List the routes the collector must or must not
see after the example was applied, and any route attributes to check:

```yaml
page: docs/guides/route_filtering/inbound/prefix_length.md
cases:
  - name: reject too short and too long prefixes
    context:
      arista: route-map example-in permit 1000
    accept: [0.0.0.0/0, 10.0.0.0/8, 203.0.113.0/24, "3fff::/20"]
    reject: [10.0.0.0/7, 203.0.113.128/25, "3fff:0:1:1::/64"]
```

**5. Run the test** and read the report:

```shell
cd labs
./run.py route_filtering/inbound/prefix_length --vendor arista
```

**6. Check that the test can fail.** A test that cannot fail proves
nothing. Change the example on purpose (e.g. `ge 25` to `ge 26`) and run the
test again; it must fail. Revert the change afterwards.

**7. Update the page.** Remove the `<Vendor> missing` tag from the front
matter of the page and add the report to your pull request.

## Rules for examples

The runner loads the example exactly as it is written on the page. That
leads to a few rules for writing examples:

- **Loadable as written.** No placeholders like `<YOUR ASN>` or `...` in a
  tested code block. Use values from the address plan and say in the text
  which values the reader has to replace, e.g. "Replace 64500 with your ASN".
- **One code block per step.** If a tab has variants (e.g. "accept only the
  default route" and "reject the default route"), put each variant in its own
  code block. A case selects the blocks it needs with `blocks`.
- **Say what is missing.** If the example is a fragment (e.g. a route-map with
  only `deny` entries), say so in the text ("The route-map needs further
  `permit` entries, otherwise all other routes are denied as well") and add
  the missing part as `context` in `expect.yml`.
- **Configuration only.** Every line must appear in the running configuration
  after it is applied. Comment lines (`!`, `#`) and the mode commands `exit`,
  `compile` and `commit` are ignored by this check; other operational
  commands (e.g. `show ...`) are not allowed in a tested block.
- **Describe observed behavior only.** If the text says what the router does
  (e.g. "the session is shut down"), the test has to check exactly that.
- **Link the vendor documentation.** End every vendor tab with a link to the
  vendor's documentation of the commands used, after the last code block and
  outside the code fences:

  ```markdown
      See the EOS manual: [Maintenance Mode](https://www.arista.com/en/um-eos/eos-maintenance-mode).
  ```

  Prefer official, publicly readable manual or command reference pages, and
  check that the page really covers the feature. Link several pages if the
  example spans several topics. If the only matching page needs a login, add
  "(<Vendor> account required)". If there is no matching page, leave the link
  out and mention it in the pull request.

The runner compares lines after removing leading and trailing whitespace.
Vendor specific differences are handled:

| Vendor | Applied with | Error detection | Comparison with running config |
|---|---|---|---|
| Arista | `configure session`, `commit` | lines starting with `%` | as shown by `show running-config` |
| VyOS | `vbash` script with `configure`/`commit` | lines containing `invalid`, `failed`, `error`, `not valid` | `show configuration commands`, quotes removed |
| FRR | `vtysh -f` | lines containing `%`, non-zero exit code | `show running-config`, `seq N` removed |

## Address and AS plan

All values are documentation resources from
[docs/contribution/example-networks.md](../docs/contribution/example-networks.md).

| Node | AS | Interface | IPv4 | IPv6 |
|---|---|---|---|---|
| dut | 64500 | eth1 (Ethernet1) to inject | 198.51.100.0/31 | 2001:db8::2/64 |
| dut | | eth2 (Ethernet2) to collector | 198.51.100.2/31 | 2001:db8:1::2/64 |
| dut | | eth3 (Ethernet3) to rtr, only with `rtr.json` | 198.51.100.4/31 (in `context`) | |
| inject | 64496 | eth1 | 198.51.100.1/31 | 2001:db8::1/64 |
| collector | 64511 | eth1 | 198.51.100.3/31 | 2001:db8:1::3/64 |
| rtr | | eth1, RTR on TCP 3323 | 198.51.100.5/31 | |

So in examples:

- the DUT is `router bgp 64500`
- the neighbor routes come from is `198.51.100.1` / `2001:db8::1` (inject)
- the neighbor routes go to is `198.51.100.3` / `2001:db8:1::3` (collector)

Use these prefixes for test routes, they do not overlap with the link
networks: `203.0.113.0/24`, `192.0.2.0/24`, `198.51.100.128/25`, `3fff::/20`
and its subnets, `2001:db8:100::/48`. `10.0.0.0/8` is useful for prefix
length tests. Further AS numbers for AS paths: 64497 to 64510.

## Files of a lab directory

| File | Required | Purpose |
|---|---|---|
| `expect.yml` | yes | guide page, cases, expected results |
| `inject.conf` | yes | FRR config of inject: the test routes |
| `collector.conf` | no | replaces the default collector config, if the collector has to announce routes itself (e.g. `peer_locking`) |
| `rtr.json` | no | ROAs and ASPAs; adds the RPKI cache `rtr` to the topology |

### inject.conf

A complete FRR configuration. Start from an existing one, e.g.
`route_filtering/inbound/tier1_asn/inject.conf`. Important settings:

```
router bgp 64496
 no bgp ebgp-requires-policy
 no bgp default ipv4-unicast
 no bgp network import-check
 neighbor 198.51.100.0 remote-as 64500
 neighbor 2001:db8::2 remote-as 64500
 address-family ipv4 unicast
  neighbor 198.51.100.0 activate
  network 203.0.113.0/24 route-map SET-ATTRIBUTES
```

| Setting | Why |
|---|---|
| `no bgp ebgp-requires-policy` | FRR does not send or accept eBGP routes without a policy otherwise (RFC 8212) |
| `no bgp default ipv4-unicast` | address families are activated explicitly per neighbor |
| `no bgp network import-check` | `network` statements are announced without a matching route in the routing table |

Attributes are set with route-maps on the `network` statement:

| Needed | FRR route-map line |
|---|---|
| communities | `set community 64500:100 64496:1` |
| large communities | `set large-community 64500:0:100 64496:0:1` |
| graceful shutdown | `set community graceful-shutdown` |
| AS path `64496 1299 64497` | `set as-path prepend 1299 64497` (inject adds 64496 itself) |
| origin | `set origin incomplete` |

Write prefixes in canonical form (`2001:7f8:0:0:1::/80`, not
`2001:7f8::1:0:0:0/80`), because they are compared with the FRR output as
text. `python3 -c 'import ipaddress; print(ipaddress.ip_network("..."))'`
prints the canonical form.

### rtr.json

The JSON format read by [RTRTR](https://rtrtr.docs.nlnetlabs.nl/), the same
as the rpki-client output:

```json
{
  "roas": [
    {"prefix": "203.0.113.0/24", "maxLength": 24, "asn": 64496}
  ],
  "aspas": [
    {"customer_asid": 64497, "providers": [64496]}
  ]
}
```

The DUT reaches the cache at `198.51.100.5` port 3323 via its third
interface. The interface itself must be configured as `context`, e.g. for
Arista:

```yaml
context:
  arista: |
    interface Ethernet3
       no switchport
       ip address 198.51.100.4/31
```

## expect.yml reference

```yaml
page: docs/guides/route_filtering/inbound/own_bgp_communities.md  # required
tab: Arista EOS          # optional, default: the vendor's tab name

cases:                   # required, one or more; each runs in a fresh lab
  - name: delete own communities and accept the routes   # required
    blocks: [0, 2, 3]    # optional, code blocks of the tab (0 = first), default: all
    snippet: |           # optional, instead of blocks: literal config, NOT from the guide
      ...
    context:             # optional, config per vendor applied before the control run
      arista: route-map peer-in permit 1000
      vyos: set policy route-map peer-in rule 1000 action permit
    accept: [203.0.113.0/24, "3fff::/20"]   # must reach the collector after the example
    reject: [192.0.2.0/24]                  # must not reach the collector after the example
    attributes:          # optional, see below
      - {prefix: 203.0.113.0/24, field: communities, control: ["64496:1", "64500:100"], test: ["64496:1"]}
```

All prefixes in `accept` and `reject` must reach the collector in the control
run. Quote IPv6 prefixes (`"3fff::/20"`, `"::/0"`); unquoted colons can be
misread by YAML.

### attributes

Each entry checks one value in the control run (`control`), in the test run
(`test`), or both. An entry without `control` or `test` for a phase is not
checked in that phase.

| `field` | `prefix` | Value | Where |
|---|---|---|---|
| `communities` | route | list of standard communities, well-known ones by name (`graceful-shutdown`) | collector |
| `large_communities` | route | list of large communities | collector |
| `origin` | route | `IGP`, `EGP` or `incomplete` | collector |
| `as_path` | route | AS path as string, e.g. `"64500 64496 17400"` | collector |
| `local_pref` | route | number, or `null` if the DUT has no such route | DUT |
| `route_count` | `ipv4` or `ipv6` | number of routes | collector |
| `session_state` | address of the DUT as seen by the collector | e.g. `Established`, `Idle` | collector |

Lists are compared without regard to order. `local_pref: null` is the way
to check that the DUT rejected a route it received (it is then also not at
the collector, but the collector cannot tell why).

### Literal snippets

A case with `snippet` does not test the guide. Use it for counter-checks
(e.g. "the corrected version of a broken example works") or investigations.
The report marks such cases as "snippet NOT from the guide".

## TCP-AO tests on vEOS

`control_plane_protection/run_veos.py` uses its own `expect.yml` format,
because the test is about the BGP session, not about routes:

```yaml
page: docs/guides/control_plane_protection/keyring.md
cases:
  - name: key rotation while the session is up
    dut: {blocks: [0]}          # or {snippet: "..."}
    peer: |                     # config for the peer VM (AS64496, neighbor 198.51.100.0)
      ...
    expect:
      established: true         # false: the session must stay down for `wait` seconds
      wait: 180
      neighbor: ["^TCP-AO Authentication:", "Current key ID: 2"]   # regexes on `show ip bgp neighbors`
      profile:                  # regexes on `show management security session shared-secret profile`
        name: bgp-keyring
        match: ["Current transmit secret: ID: 2"]
      rotation: {wait_until: 480}   # wait until DUT clock at apply time + 480 s, the session must not flap
```

In `snippet` and `peer`, `{t+N}` is replaced by the DUT clock at apply time
plus N seconds (format `yyyy-mm-dd hh:mm:ss`, UTC). This allows key lifetimes
that expire during the test.

The DUT is `198.51.100.0` (AS64500), the peer `198.51.100.1` (AS64496).
Secrets are stored encrypted in the running configuration, so the runner
compares `secret` lines without the key.

## Adding a vendor

A vendor is an entry in `VENDORS` in `run.py` plus a few vendor specific
methods. Steps:

1. **Find the containerlab kind** in the
   [containerlab documentation](https://containerlab.dev/manual/kinds/)
   and prepare the image.
2. **Write the base configuration** `common/base/<vendor>.cfg`: interface
   addresses and the four BGP sessions from the
   [address plan](#address-and-as-plan), without any policy. Two ways:
   - as startup configuration (key `startup`), if the kind accepts the
     vendor's native config format (Arista)
   - as commands applied after deployment (key `base`), using the same way
     as the examples are applied (VyOS, FRR)
3. **Add the entry to `VENDORS`:**

   ```python
   "myvendor": {
       "tab": "My Vendor OS",            # tab title on the guide pages
       "kind": "myvendor_kind",          # containerlab kind
       "image": os.environ.get("RG_MYVENDOR_IMAGE", "myvendor:1.2.3"),
       "base": LABS / "common" / "base" / "myvendor.cfg",
       # "node": {...}                   # optional extra topology settings (binds, exec, env)
   },
   ```

4. **Implement the vendor in the `Lab` methods:**
   - `apply(snippet)`: apply config lines in one commit and return the error
     lines. Check that errors are really detected: apply an invalid command on
     purpose and make sure `apply` returns it.
   - `running_lines()`: running configuration as a set of normalized lines,
     in the same format as the examples are written
   - `version()`: software version for the report
   - `dut_local_pref(prefix)`: only if the vendor has no FRR `vtysh`
5. **Make sure the control run of an existing test passes**, e.g.
   `prefix_length`. Without the example, the DUT must pass on all routes
   (watch out for defaults like eBGP policies required by RFC 8212).
6. **Document the image** in the README.

## How the runner works

`run.py`, in order:

1. Reads `expect.yml` and extracts the code blocks of the vendor tab
   (`extract_blocks`): the lines after `=== "<tab>"` that are indented by
   four spaces, fenced code blocks only.
2. Writes a per-run copy of `common/topo.clab.yml` next to the original
   (`common/.rg-<page>-<vendor>.clab.yml`) with the vendor's DUT node and, if
   present, the page's `collector.conf` and the `rtr` node.
3. For every case: deploys the lab, applies base config and context, waits
   until all BGP sessions of inject and collector are established, runs the
   control phase, applies the example, triggers a route refresh (inject
   `soft out`, collector `soft in` and `soft out`), runs the test phase,
   destroys the lab.
4. Writes the report.

Checks are retried every five seconds for up to 90 seconds, so BGP has time
to converge; the result is taken from the last attempt.

## Style

- Files follow the repository's [.editorconfig](../.editorconfig); the
  existing CI checks them with
  [editorconfig-checker](https://github.com/editorconfig-checker/editorconfig-checker).
- Lab directories, file names and comments in English.
- Comment `expect.yml` with what each route is meant to test; a reader should
  understand the case without reading `inject.conf`.
- Commit `labs/`, but not `reports/`, `logs/`, `clab-*/` and `.rg-*.clab.yml`
  (see `.gitignore`).

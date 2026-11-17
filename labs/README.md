# Labs

This directory contains [containerlab](https://containerlab.dev/) labs that
check the configuration examples of the routing guide. A test takes the
example **from the guide page itself**, loads it on a router and checks that
it does what the page says. If a test passes, the published text has been run
on the tested software version.

To add a test for a page or a new vendor, read [CONTRIBUTING.md](CONTRIBUTING.md).
AI agents additionally follow [AGENTS.md](AGENTS.md).

- [How a test works](#how-a-test-works)
- [Requirements](#requirements)
- [Preparing the images](#preparing-the-images)
- [Running a test](#running-a-test)
- [Reading the report](#reading-the-report)
- [TCP-AO and keyring tests](#tcp-ao-and-keyring-tests)
- [Directory layout](#directory-layout)
- [Troubleshooting](#troubleshooting)
- [Known limits](#known-limits)

## How a test works

Every test uses the same small topology. The router that runs the example,
the device under test (DUT), sits between two [FRRouting](https://frrouting.org/)
neighbors:

```
inject (FRR, AS64496) --eBGP--> dut (AS64500) --eBGP--> collector (FRR, AS64511)
                                  |
                                  rtr (RTRTR, RPKI cache, only for RPKI/ASPA pages)
```

- **inject** announces test routes to the DUT: routes the example must
  accept and routes it must reject, with communities, AS paths or origins
  as needed.
- **collector** receives what the DUT passes on. Most checks look at the
  collector, so they do not depend on the CLI output of the DUT vendor.
- **rtr** is an RPKI cache that serves ROAs and ASPAs from a JSON file.

The expected results for a page are written down in an `expect.yml` file.
Each **case** in it runs in a fresh lab in three steps:

1. **Control run.** The DUT runs only a base configuration (interfaces and
   BGP sessions). Every announced route must reach the collector, and route
   attributes must have their "before" values. This makes sure that the
   result of step 3 is caused by the example and not by a default behavior
   of the router.
2. **Apply the example.** The code block is taken from the vendor tab of the
   guide page (e.g. `=== "Arista EOS"`) and applied in one configuration
   session. There must be no CLI errors, and every line of the example must
   show up in the running configuration afterwards.
3. **Test run.** After a BGP route refresh, the routes listed as `accept`
   must reach the collector, the routes listed as `reject` must not, and
   route attributes (communities, origin, AS path, local preference, ...)
   must have their "after" values.

Configuration that the example relies on, but does not contain, is called
**context** (typically a final `permit` entry of a route-map). It is applied
together with the base configuration, written in `expect.yml` and shown in
the report, so it is always visible what was added to the published text.

## Requirements

- A Linux host, amd64. macOS is not supported directly; containerlab only
  runs there inside a Linux VM.
- [Docker](https://docs.docker.com/engine/install/) and
  [containerlab](https://containerlab.dev/install/)
- Python 3 with [PyYAML](https://pypi.org/project/PyYAML/) (`pip3 install pyyaml`)
- KVM (`/dev/kvm`), only for the vEOS VMs used by the TCP-AO tests
- For VyOS: a host kernel >= 6.3 (see [Known limits](#known-limits))

The tests were developed with containerlab 0.82.0 and Docker 29.9 on
Ubuntu 22.04.

## Preparing the images

Vendor images are not part of this repository. FRR and RTRTR are public and
pulled automatically; Arista and VyOS images have to be prepared once.

| Image (default name) | Used for | How to get it |
|---|---|---|
| `ceos64:4.36.3M` | Arista DUT | Download cEOS-lab (64 bit) from [arista.com](https://www.arista.com/en/support/software-download) (free account required) and import it: `docker import cEOS64-lab-4.36.3M.tar.xz ceos64:4.36.3M` |
| `vrnetlab/arista_veos:4.36.3M` | TCP-AO/keyring tests | Download vEOS-lab from arista.com and build the image with [vrnetlab](https://github.com/srl-labs/vrnetlab) |
| `vyos:2026.11.15-0018-rolling` | VyOS DUT | `images/vyos/build.sh 2026.11.15-0018-rolling` builds it from a [VyOS nightly ISO](https://github.com/vyos/vyos-nightly-build/releases) |
| `quay.io/frrouting/frr:10.7.1` | inject, collector, FRR DUT | pulled automatically |
| `nlnetlabs/rtrtr:v0.3.3` | RPKI cache | pulled automatically |

Other image names or versions can be set with environment variables:
`RG_ARISTA_IMAGE`, `RG_VYOS_IMAGE`, `RG_FRR_IMAGE`, `RG_RTR_IMAGE`,
`RG_VEOS_IMAGE`. Example:

```shell
RG_ARISTA_IMAGE=ceos64:4.37.0F ./run.py route_filtering/inbound/rpki --vendor arista
```

## Running a test

Tests are started from the `labs/` directory with the path of the lab
directory and the vendor:

```shell
cd labs
./run.py route_filtering/inbound/prefix_length --vendor arista
```

Vendors: `arista`, `vyos`, `frr`.

The lab is created, all cases are run, and the lab is destroyed again.
`--keep` keeps the lab of the last case running, so you can log in and look
around:

```shell
./run.py route_filtering/inbound/rpki --vendor arista --keep
docker exec -it clab-rg-rpki-arista-dut Cli        # Arista
docker exec -it clab-rg-rpki-arista-collector vtysh
containerlab destroy -t common/.rg-rpki-arista.clab.yml --cleanup
```

The exit code is 0 if all cases passed. A test takes about two to four
minutes per case, mostly for booting the DUT.

Lab names start with `rg-`, and all labs use their own management network
`rg-mgmt` (172.31.250.0/24), so they do not interfere with other labs on the
same host. Run one test at a time; parallel deployments can overload a busy
Docker daemon.

To run all tests for a vendor:

```shell
for e in $(find route_filtering -name expect.yml); do
  ./run.py "$(dirname "$e")" --vendor arista || echo "FAILED: $e"
done
```

## Reading the report

Every run writes a Markdown report to
`reports/<lab path>/<vendor>.md` (not committed). It contains:

- date, lab name, image name and image ID
- the `show version` output of the DUT
- for every case: the context, the example as loaded, CLI errors, lines
  missing in the running configuration, and every single check of the
  control and the test run with expected and actual value
- `PASS`/`FAIL` per step, per case and overall

The report is the evidence for a pull request: attach it or paste the
relevant part when you add or change an example.

A failed control run means the test setup is wrong (the lab does not
behave as expected even without the example). A failed test run with a
passed control run means the example does not do what the page says.

## TCP-AO and keyring tests

TCP-AO needs TCP-AO support in the TCP stack. The cEOS container uses the
TCP stack of the host kernel, so these examples are tested on two vEOS VMs
instead (`control_plane_protection/`). The VMs boot in about ten minutes,
so they are deployed once and reused:

```shell
cd labs/control_plane_protection
containerlab deploy -t topo-veos.clab.yml
./run_veos.py tcp-authentication-option
./run_veos.py keyring
containerlab destroy -t topo-veos.clab.yml --cleanup
```

Each case resets both VMs to their startup configuration, checks that the
session comes up without authentication, applies the example on the DUT and
the matching configuration on the peer, and checks the session state and the
TCP-AO details. Negative cases (wrong key) check that the session stays down.

## Directory layout

```
labs/
  README.md                 this file
  CONTRIBUTING.md           how to add tests and vendors
  run.py                    test runner (Arista, VyOS, FRR as DUT)
  common/
    topo.clab.yml           topology shared by all tests
    base/                   base config of the DUT per vendor
    frr/                    FRR daemons file and default collector config
    rtrtr.conf              RPKI cache config
  route_filtering/...       one directory per guide page, same path as in docs/guides/
    <page>/expect.yml       expected results
    <page>/inject.conf      routes announced by inject
  control_plane_protection/ TCP-AO/keyring tests on vEOS VMs
  images/vyos/              build script for the VyOS image
  checks/                   investigations that are not tests of a guide example
```

`checks/` holds labs that were used to find out how a platform behaves or to
verify a problem in an existing example, e.g. `checks/frr_match_and` shows
that several `match` statements in one FRR route-map entry are combined with
AND.

## Troubleshooting

**`tab "..." not found`**: the guide page has no tab with that exact title.
The runner looks for `=== "Arista EOS"`, `=== "VyOS"` or
`=== "Cisco IOS / FRRouting"`; other titles need `tab:` in `expect.yml`.

**`BGP sessions did not come up`**: the DUT did not boot within ten
minutes or the base config is broken. Rerun with `--keep` and check the DUT
with `docker logs` and its CLI.

**Control run fails**: the lab does not behave as expected without the
example. Check `inject.conf` (are all routes announced?) and the
expectations of the control phase in `expect.yml`.

**`snippet lines missing in running-config`**: the router accepted the
command but shows it differently, or the line is not configuration (e.g. a
mode command). See [CONTRIBUTING.md](CONTRIBUTING.md#rules-for-examples).

**`context deadline exceeded` or `Conflict. The container name ... is
already in use`**: the Docker daemon was too slow. Destroy the lab
(`containerlab destroy -t common/.rg-<name>.clab.yml --cleanup`) and run the
test again.

**vEOS does not start: `failed to set MSR 0x345`**: QEMU cannot use the
host CPU's performance monitoring. `topo-veos.clab.yml` already disables it
with `QEMU_CPU: host,level=9,pmu=off`.

**vEOS boots, but SSH/eAPI time out**: the VM has too little memory. The
topology gives each VM 4 GB and 4 vCPUs.

## Known limits

- A test proves the behavior of the tested software version only. The
  report records the exact image.
- cEOS is a container version of EOS. It shows the control plane behavior
  (BGP, policies); hardware specific behavior is not covered.
- VyOS rolling releases from 2026 use the nftables command `destroy` when
  configuring interfaces, which needs Linux >= 6.3. On older host kernels the
  base configuration fails with `Commit failed`.
- The Arista EULA does not allow distributing the images, so the tests do not
  run in the GitHub CI.

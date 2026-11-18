# Instructions for AI agents

These instructions are for AI coding agents working on the labs. Humans
should start with the [README](README.md); it and
[CONTRIBUTING.md](CONTRIBUTING.md) explain how the labs work, the
`expect.yml` format and how to add tests or vendors. Read both before you
change anything.

## Goal

Every configuration example in the guide is backed by a lab test that loads
the published text on a real router image and checks its effect. A passing
test is the only accepted evidence that an example is correct.

## Ground rules

1. **Never write configuration from memory.** Take the syntax from the
   vendor's documentation or from the device itself (CLI help `?`, built-in
   docs such as EOS `help attribute` for RCF). Name the source in the pull
   request.
2. **An example goes into the guide only with a passing test.** Remove the
   `<Vendor> missing` tag from a page only when all cases of its test pass.
   If a test cannot pass, leave the tag and explain why.
3. **Check that the test can fail.** Before you trust a pass, change the
   example on purpose (e.g. a prefix length) and make sure the test fails.
4. **Describe only measured behavior.** If the guide text says what the router
   does ("the session is shut down"), the test must check exactly that. Do not
   add claims you did not observe.
5. **Do not bend the test to the example.** Configuration the example relies
   on goes into `context` in `expect.yml`, visible in the report. If the
   example is wrong, fix the example and say what was wrong.
6. **Do not change other vendors' examples without a test.** If you suspect a
   bug in an existing example, prove it with a lab (see `checks/`) and report
   it to the user instead of silently editing it.
7. **Report failures as they are.** Quote the relevant report lines. A failed
   control run means the setup is wrong, not the example.
8. **Use the documentation resources** from
   `docs/contribution/example-networks.md` and the address plan in
   CONTRIBUTING.md. Never use real customer, company or host data in examples,
   labs or commits.
9. **Link the vendor documentation in every vendor tab you add or change.**
   - Put the link at the end of the tab, after the last code block, indented
     like the rest of the tab and outside any code fence (the runner must not
     see it), e.g.

     ```markdown
         See the EOS manual: [Maintenance Mode](https://www.arista.com/en/um-eos/eos-maintenance-mode).
     ```

   - Prefer official, publicly readable pages of the vendor (manual chapter or
     command reference) that cover the commands used in the example. Link
     several pages if the example spans several topics, and say which topic a
     link is for when it is not obvious, e.g. "(community lists)".
   - Open every public page before you link it and check that it really
     covers the feature. Do not link public pages you only know by title or
     from search results.
   - If the only matching page needs a login, link it and add
     "(<Vendor> account required)", e.g. "(Arista account required)". Such a
     page may be linked without reading it, if its title clearly names the
     feature of the example.
   - If you cannot find a matching page, add no link and say so in the pull
     request. Never link a page that is merely related.

## Environment

- Every contributor uses their own lab environment (Linux, Docker,
  containerlab, KVM for vEOS). Do not write host names, addresses, user names
  or credentials of a lab environment into this repository.
- If the host is shared with other labs, only touch your own: lab names start
  with `rg-`, the management network is `rg-mgmt`. Never destroy labs or
  networks you did not create.
- Run tests one at a time. Parallel deployments can make a busy Docker daemon
  time out.
- Tests take minutes (vEOS: about ten minutes to boot). Run long jobs in
  `tmux` or `screen` with output written to a log file, and poll the log, so
  a dropped connection does not kill the run.
- Vendor images are not in the repository and must not be committed or
  uploaded anywhere (license).

## Commands

```shell
cd labs
./run.py <lab path> --vendor arista            # one page, e.g. route_filtering/inbound/rpki
./run.py <lab path> --vendor arista --keep     # keep the last lab for debugging
containerlab destroy -t common/.rg-<page>-<vendor>.clab.yml --cleanup

cd control_plane_protection                    # TCP-AO / keyring on vEOS
containerlab deploy -t topo-veos.clab.yml
./run_veos.py tcp-authentication-option

# before committing
ec                                             # editorconfig-checker, as in the CI
python3 -c 'import yaml,glob; [yaml.safe_load(open(f)) for f in glob.glob("labs/**/*.yml", recursive=True)]'
```

## Known pitfalls

Learned while building the labs; check these before you debug for hours.

**Lab and tools**

- containerlab does not accept an empty `startup-config` path; the runner
  removes the key for vendors without a startup config.
- `docker exec ... Cli -c` (cEOS) ignores `?`. To read CLI help, run the CLI
  in a pseudo terminal (e.g. Python `pty`).
- After `configure replace` on vEOS, eAPI is unavailable for a short time;
  `run_veos.py` retries.
- vEOS under vrnetlab: `failed to set MSR 0x345` is fixed by
  `QEMU_CPU=host,level=9,pmu=off`; with 2 GB RAM the VM does not respond after
  boot (the topology uses 4 GB and 4 vCPUs). Commits on vEOS can take minutes.
- `context deadline exceeded` or a container name conflict: destroy the lab
  and run again.
- `containerlab destroy --cleanup` removes the shared management network
  `rg-mgmt`. Never destroy an `rg-` lab while another test is deploying, or
  the deployment fails with `network rg-mgmt not found`.
- FRR prints prefixes in canonical form; write them the same way in
  `expect.yml` and `inject.conf`.
- StayRTR v0.6.4 speaks RTR v0/v1 only and cannot deliver ASPAs; the labs use
  RTRTR.
- VyOS rolling needs a host kernel >= 6.3 (nftables `destroy`).
- The repository's `.editorconfig` requires indentation in multiples of two in
  YAML files, also inside block scalars with router configuration.

**Router behavior (verified in the labs)**

- FRR requires a policy on eBGP sessions by default (RFC 8212,
  `ebgp-requires-policy`); the FRR nodes turn it off.
- FRR combines several `match` statements in one route-map entry with AND.
  `match ip address ...` and `match ipv6 address ...` in the same entry match
  nothing (`checks/frr_match_and`).
- EOS applies a community regexp in `match community` to the whole community
  list of a route: use `_64500:`, not `^64500:`.
- EOS honors the graceful shutdown community without configuration (local
  preference 0).
- EOS `maximum-advertised-routes` shuts the session down when the limit is
  exceeded.
- EOS ASPA needs the BGP role (`local-role`) of the session, RTR version 2,
  `aspa` on the RPKI cache, and an RCF function to drop
  `ASPA_INVALID`; without a role all routes of the neighbor are rejected.
- EOS TCP-AO does not support separate receive and transmit lifetimes (Arista
  TOI "BGP TCP Authentication Option (TCP-AO)"); with different ones the
  profile has no valid secrets and the session stays down. Use the single
  lifetime form `secret ID 0 KEY START END`.

## When you hand over

Summarize for the next person or agent: which pages you tested, the result
per page (with the report), what you changed in the guide, and what is open.
Keep environment specific details out of the repository.

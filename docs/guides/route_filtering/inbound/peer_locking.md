---
tags:
  - BIRD missing
  - Cisco missing
  - Cisco IOS XR missing
  - FRR missing
  - Huawei VRP missing
  - Junos missing
  - Mikrotik missing
  - Nokia SR OS missing
  - OpenBGPD missing
  - VyOS missing
  - RtBrick RBFS missing
---

# Peer Locking

Peer locking protects against route leaks with knowledge about your direct peers: if you have a direct session with a large network, you do not expect to learn routes through this network from any other neighbor.

The concept was introduced by NTT. Job Snijders described it on the [NANOG mailing list](https://seclists.org/nanog/2016/Jun/280) in June 2016: "AT&T and NTT agreed (through email) that there should be no intermediate networks between 2914 & 7018, therefore NTT blocks announcements that match as-path-regexp '\_7018\_' on any and all eBGP sessions, except the direct sessions with 7018."

So for every locked peer ASN, reject routes containing this ASN on all eBGP sessions except the direct sessions with that peer. Agree on this with the peer first, otherwise you might drop legitimate routes.

A simpler variant, rejecting routes containing Tier 1 ASNs from customers and IXP peers, is described on the [Tier 1 ASNs](tier1_asn.md) page.

## Configuration

=== "Arista EOS"
    AS64496 is the locked peer. Apply the route-map to all eBGP sessions except the direct sessions with AS64496. The route-map needs further `permit` entries, otherwise all other routes are denied as well.
    ```
    ip as-path access-list peerlock-64496 permit _64496_ any
    !
    route-map peer-in deny 5
       match as-path peerlock-64496
    !
    router bgp 64500
       address-family ipv4
          neighbor 198.51.100.3 route-map peer-in in
       address-family ipv6
          neighbor 2001:db8:1::3 route-map peer-in in
    ```

    See the EOS manual: [Border Gateway Protocol (BGP)](https://www.arista.com/en/um-eos/eos-border-gateway-protocol-bgp) (AS path access lists) and [ACLs and Route Maps](https://www.arista.com/en/um-eos/eos-acls-and-route-maps).

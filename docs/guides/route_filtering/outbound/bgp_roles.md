---
tags:
  - Arista missing
  - BIRD missing
  - Cisco missing
  - Cisco IOS XR missing
  - Huawei VRP missing
  - Junos missing
  - MikroTik missing
  - Nokia SR OS missing
  - OpenBGPD missing
  - VyOS missing
  - RtBrick RBFS missing
---

# BGP Roles
BGP roles are defined in [RFC9234](https://www.rfc-editor.org/rfc/rfc9234) and provide an easy way to route leaks prevention, detection and mitigation.

The concept of BGP roles is sometimes also known under the name of the optional BGP Path Attribute "Only to Customer" (OTC).

Possible values for local role are:

- Provider:
    MAY propagate any available route to a Customer.
- Customer:
    MAY propagate any route learned from a Customer, or that is locally originated, to a Provider. All other routes MUST NOT be propagated.
- Route Server (RS):
    MAY propagate any available route to a Route Server Client (RS-Client).
- Route Server Client (RS-Client):
    MAY propagate any route learned from a Customer, or that is locally originated, to an RS. All other routes MUST NOT be propagated.
- Peer:
    MAY propagate any route learned from a Customer, or that is locally originated, to a Peer. All other routes MUST NOT be propagated.


=== "FRRouting"
    In FRRouting valid values are: provider, rs-server, rs-client, customer, peer.
    If strict-mode is set, your neighbor must send you Capability with the value of his role (by setting local-role on his side). Otherwise, a Role Mismatch Notification will be sent.
    ```
    router bgp 64496
      neighbor 198.51.100.1 local-role customer strict
    ```

## Resources
- <https://media.ccc.de/v/denog18-30-the-leak-proof-routing-table-mastering-bgp-roles-roas-and-aspa>

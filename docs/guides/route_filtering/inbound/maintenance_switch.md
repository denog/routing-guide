---
tags:
  - BIRD missing
  - Cisco missing
  - Cisco IOS XR missing
  - FRR missing
  - Huawei VRP missing
  - Mikrotik missing
  - Nokia SR OS missing
  - OpenBGPD missing
  - VyOS missing
  - RtBrick RBFS missing
---

# Maintenance switch
## Purpose
The maintenance switch provides you with an easy way to drain every BGP session on your router by rejecting all routes in- and outbound.
This can apply to the entire router or groups of sessions, like e. g. every peering at an IXP. This way you can ensure traffic reroutes gracefully before shutting off an interface or the router during a maintenance.

## Configuration

=== "Juniper JunOS"
    ```
    # Normal configuration
    set policy-options policy-statement MAINTENANCE-MODE term ACTIVATE-MAINTENANCE then reject
    deactivate policy-options policy-statement MAINTENANCE-MODE term ACTIVATE-MAINTENANCE
    set policy-options policy-statement MAINTENANCE-MODE then next policy

    set protocols bgp group MY_NEIGHBOR_GROUP 198.51.100.1 import MAINTENANCE-MODE
    set protocols bgp group MY_NEIGHBOR_GROUP 198.51.100.1 import <regular filtering policies go after the switch>
    set protocols bgp group MY_NEIGHBOR_GROUP 198.51.100.1 export MAINTENANCE-MODE
    set protocols bgp group MY_NEIGHBOR_GROUP 198.51.100.1 export <Regular filtering policies go after the switch>

    # Add this to activate the switch
    activate policy-options policy-statement MAINTENANCE-MODE term ACTIVATE-MAINTENANCE
    ```

=== "Arista EOS"
    EOS has a built-in maintenance mode. While the unit is in maintenance, the BGP profile replaces the policy of all neighbors in the group with a route-map that denies all routes in- and outbound.
    ```
    route-map maintenance-deny-all deny 10
    !
    group bgp maintenance-peers
       neighbor 198.51.100.1
       neighbor 2001:db8::1
       maintenance profile bgp drain-all
    !
    maintenance
       profile bgp drain-all
          initiator route-map maintenance-deny-all inout
       unit maintenance-peers
          group bgp maintenance-peers
    ```

    Add this to activate the switch, remove it with `no quiesce` to deactivate it:
    ```
    maintenance
       unit maintenance-peers
          quiesce
    ```

    See the EOS manual: [Maintenance Mode](https://www.arista.com/en/um-eos/eos-maintenance-mode).

---
tags:
  - Arista missing
  - BIRD missing
  - Cisco missing
  - Huawei VRP missing
  - Junos missing
  - Nokia SR OS missing
  - OpenBGPD missing
  - RtBrick RBFS missing
---

# Origin Type

## Motivation

In BGPs Best Path Selection Algorithm at step 3 the *origin type* of a prefix is evaluated. The following origin types exist (in descending order of preference):

- **IGP** - the prefix was generated statically with a BGP *network* statement
- **EGP** - the prefix was received via *EGP* (the predecessor protocol of BGP which no longer exists)
- **Incomplete** - the prefix was redistributed from another routing protcol (including static route) into BGP.

This rule has been overlooked for a long time, as the originator of a prefix sets this attribute and, according to [RFC4271](https://www.rfc-editor.org/rfc/rfc4271), it *should not* be changed by any AS forwarding the announcement.

However, [it has been discovered](https://ripe91.ripe.net/programme/meeting-plan/sessions/30/GJ8PFJ/)
that certain transit providers manipulate this attribute in order to attract more traffic. Keep in mind that this is evaluated after *Local Preference* and *AS path length* but before *MED*, so if a customer AS sets the same local preference to all its transit providers,  a transit provider which modifies *Origin Type* from *Incomplete* to *IGP* attracts more traffic (if the AS paths have the same length).

## Countermeasure

It is currently not possible to skip the evaluation of *Origin Type* in best path selection. So the only way to counter this behaviour of certain transit providers is to reset *Origin Type* for all received prefixes to the same value. **This should only be done if you are a stub-AS and do not have any AS-customers**.

## Configuration

=== "Cisco IOS XR"
    ```
    route-policy import-all
      set origin igp
    end-policy
    ```
=== "FRRouting"
    ```
    route-map import-all permit 100
      set origin IGP
    ```
=== "Mikrotik"
    ```
    /routing filter rule
    add chain=import-all rule="set bgp-origin igp"
    ```

=== "VyOS"
    VyOS has two modes (operational and configuration mode). Enter configuration mode with
    `configure` to make changes. Use `commit` to apply them and `save` to keep them after reboot.
    ```
    set policy route-map import-all rule 100 action permit
    set policy route-map import-all rule 100 set origin igp
    ```

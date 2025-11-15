---
tags:
  - Huawei VRP missing
  - OpenBGPD missing
  - VyOS missing
---

# TTL Security

Instead of using a password, relying on the *TTL* value of incoming TCP packets is easier to handle and to implement.

[RFC5082](https://www.rfc-editor.org/rfc/rfc5082) describes, how setting the TTL value of packets when sending to 255, and checking that value when receiving, makes it an impossible-to-spoof security measure.

As the TTL is decreased by every hop, when you receive a packet with TTL 255, it *must* have been sent by a directly adjacent node.

This feature must be set on both ends to work - if you set it on one end only, one side sends IP packets with a TTL of 1, and the other with a TTL of 255, and a session cannot be established.

Configuration examples:

=== "Arista EOS"
    ```
    router bgp 64500
       neighbor 198.51.100.1 ttl maximum-hops 1
    ```

=== "Cisco IOS classic / IOS XE / FRRouting"
    On Cisco IOS or FRRouting you configure how many hops your neighbor is away:
    ```
    router bgp 64500
    ...
    neighbor 198.51.100.1 ttl-security hops 1
    ```

=== "Cisco IOS XR"
    On Cisco IOS XR you just configure ttl-security without an hop parameter:
    ```
    router bgp 64500
    ...
    neighbor 198.51.100.1 ttl-security
    ```

=== "Mikrotik"
    On Mikrotik, you do not configure how many maximum hops a peer can be away, but the TTL value, which is 255 for directly adjacent peers (this is also the default value):
    ```
    add in-filter=upstream-in name=AS64496 out-filter=upstream-out \
        remote-address=198.51.100.1 remote-as=64496 ttl=255
    ```

=== "Juniper"
    On JunOS you configure how many hops your neighbors in a group are away:
    ```
    set protocols bgp group <GROUPNAME> ttl 255
    ```
    On JunOS you configure how many hops a specific neighbor in a group is away:
    ```
    set protocols bgp group <GROUPNAME> neighbor 198.51.100.1 ttl 255
    ```

=== "RtBrick RBFS"
    TTL security is activated with the ttl-security command on a single-hop BGP session, which sets the IPv4 TTL value in packets to 255. For multihop BGP sessions, TTL security is also enabled with ttl-security, but you must additionally configure the ttl-limit to match the expected IPv4 TTL value.
    ```
    set instance <INSTANCE> protocol bgp peer-group <GROUPNAME> ttl-security enable
    ```
=== "Bird2"
    ```
    protocol bgp name4 {
      ttl security 1;
    }
    ```
=== "Nokia SR OS classic CLI"
    ```
    /configure router "Base" bgp
        group "as64500"
            [...]
            authentication-key "mysecretpassword"
            [...]
        exit
    ```

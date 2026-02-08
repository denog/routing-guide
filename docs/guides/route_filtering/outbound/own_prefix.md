---
tags:
  - BIRD missing
  - Huawei VRP missing
  - Mikrotik missing
  - Nokia SR OS missing
  - OpenBGPD missing
  - RtBrick RBFS missing
---

# Announce your own prefixes

## Purpose

As a network participating in the global Internet you want to tell other networks about your own prefixes and announce them to the public Internet.

!!! note
    Your peers and upstreams might also apply incoming BGP filters to your BGP sessions and filter your prefixes. Please make sure to create appropriate [RPKI objects](https://www.ripe.net/manage-ips-and-asns/resource-management/rpki/), route/route6 objects and AS sets, for example in the RIPE datebase. It is best practice to also create an AS set although you currently only have one ASN, because if your BGP peers build filters based on your AS set you don't need to inform them if you ever announce prefixes with an additional origin ASN.

## Configuration

=== "Juniper JunOS"

    Config snippet for JunOS
    ```
    ```

=== "Cisco IOS"

    Please note that Cisco IOS is permissive by default. If you do not apply any filters, all prefixes will be shared between your BGP peers.

    Config snippet for Cisco IOS
    ```
    ```

=== "Cisco IOS XR"

    Config snippet for Cisco IOS XR
    ```
    ```

=== "Arista EOS"

    Config snippet for Arista EOS
    ```
    ```

=== "FRRouting"

    Config snippet for FRRouting
    ```
    ip prefix-list outgoing seq 10 permit 192.0.2.0/24
    ip prefix-list outgoing seq 100 deny 0.0.0.0/0 le 32

    ipv6 prefix-list outgoing-6 seq 10 permit 2001:db8::/32
    ipv6 prefix-list outgoing-6 seq 100 deny ::/0 le 128

    router bgp 64496
      no bgp default ipv4-unicast
      bgp log-neighbor-changes
      bgp router-id 192.0.2.10

      neighbor 198.51.100.1 remote-as 65550
      neighbor 3fff::1582 remote-as 65550

      address-family ipv4 unicast
        network 192.0.2.0/24
        neighbor 198.51.100.1 activate
        neighbor 198.51.100.1 prefix-list outgoing out
      exit-address-family

      address-family ipv6 unicast
        network 2001:db8::/32
        neighbor 3fff::1582 activate
        neighbor 3fff::1582 prefix-list outgoing-6 out
      exit-address-family
    exit
    ```

=== "VyOS 1.4"
    VyOS has two modes (operational and configuration mode). Enter configuration mode with
    `configure` to make changes. Use `commit` to apply them and `save` to keep them after reboot.

    ```
    set policy prefix-list outgoing rule 10 action permit
    set policy prefix-list outgoing rule 10 prefix 192.0.2.0/24
    set policy prefix-list outgoing rule 100 action deny
    set policy prefix-list outgoing rule 100 le 32
    set policy prefix-list outgoing rule 100 prefix 0.0.0.0/0

    set policy prefix-list6 outgoing-6 rule 10 action permit
    set policy prefix-list6 outgoing-6 rule 10 prefix 2001:db8::/32
    set policy prefix-list6 outgoing-6 rule 100 action deny
    set policy prefix-list6 outgoing-6 rule 100 le 128
    set policy prefix-list6 outgoing-6 rule 100 prefix ::/0

    set protocols bgp system-as 64496

    set protocols bgp parameters router-id 192.0.2.10

    set protocols bgp parameters log-neighbor-changes
    set protocols bgp parameters ebgp-requires-policy
    set protocols bgp parameters network-import-check

    set protocols bgp address-family ipv4-unicast network 192.0.2.0/24
    set protocols bgp address-family ipv6-unicast network 2001:db8::/32

    edit protocols bgp neighbor 198.51.100.1
    set remote-as 65550
    set address-family ipv4-unicast prefix-list export outgoing
    exit

    edit protocols bgp neighbor 3fff::1582
    set remote-as 65550
    set address-family ipv6-unicast prefix-list export outgoing-6
    exit
    ```

    !!! note
        For dynamic routing, VyOS uses FRR. However, VyOS applies some potentially
        problematic defaults, such as:

        - `no bgp ebgp-requires-policy`, see [Require policy to start a BGP session](../inbound/require_policy.md) for details.
        - `no bgp network import-check`

        To view the final FRR configuration, run:
        ```sh
        vtysh -c 'show running-config'
        ```
        This should match the configuration in the FRR tab on this website.

=== "VyOS 1.5"
    Please refer to the VyOS 1.4 configuration guide first.

    VyOS 1.5 introduces another potentially problematic default.

    Starting with version 1.5, FRR is configured not to enforce the remote AS
    as the first AS in the AS_PATH. This setting is typically only necessary when
    connected to an IXP RS[^1].

    To resolve this, you need to enable enforce-first-as for every neighbor.

    For the configuration shown in the VyOS 1.4 tab, apply the following commands:
    ```
    set protocols bgp neighbor 198.51.100.1 enforce-first-as
    set protocols bgp neighbor 3fff::1582 enforce-first-as
    ```

[^1]: Internet eXchange Points Route Servers

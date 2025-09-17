# Announce your own prefixes

## Purpose

As a network participating in the global Internet you want to tell other networks about your own prefixes and announce them to the public Internet.

!!! note
    You peers and upstreams might also apply incoming BGP filters to your BGP sessions and filter your prefixes. Please make sure to create appropriate [RPKI objects](https://www.ripe.net/manage-ips-and-asns/resource-management/rpki/), route/route6 objects and AS sets, for example in the RIPE datebase. It is best practice to also create an AS set although you currebtly only have one ASN, because if your BGP peers build filters based on your AS set you don't need to inform them if you ever announce prefixes with an additional origin ASN.

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

---


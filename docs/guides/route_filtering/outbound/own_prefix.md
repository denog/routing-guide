# Announce your own prefixes

## Purpose

As a network participating in the global Internet you want to tell other networks about your own prefixes and announce them to the public Internet.

You peers and upstreams might also apply incoming BGP filters to your BGP sessions and filter your prefixes. Please make sure to create appropriate [RPKI objects](https://www.ripe.net/manage-ips-and-asns/resource-management/rpki/), route/route6 objects and AS sets, for example in the RIPE datebase. It is best practice to also create an AS set although you only have one ASN, because if your BGP peers build filters based on your AS set you don't need to inform them if you ever announce prefixes with an additional origin ASN.

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

---


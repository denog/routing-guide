# Announce customer prefixes

## Purpose

If you do have BGP customers and need to provide IP transit to them you have to announce therr prefixes to your peers, upstreams and customers in addition to your own prefixes.

Please make sure to filter the prefixes of your BGP customers directly on the BGP sessions to your customer as strict as possible. Allow your BGP customers to announce their own prefixes only. If your BGP customers also have other BGP customers you will have to accept their prefixes also. Tag the prefixes of your customers with your network specific informational BGP community and announce prefixes tagged with this BGP community to your external BGP peers.

!!! note
    Explain/link how to build filters based on ASN or AS-Set.

## Configuration

=== "Juniper JunOS"

    Config snippet for JunOS
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


# Announce customer prefixes

## Purpose

If you do have BGP customers and need to provide IP transit to them you have to announce therr prefixes to your peers, upstreams and customers in addition to your own prefixes.

Please make sure to filter the prefixes of your BGP customers directly on the BGP sessions to your customer as strict as possible. Allow your BGP customers to announce their own prefixes only. If your BGP customers also have other BGP customers you will have to accept their prefixes also. Tag the prefixes of your customers with your network specific informational BGP community and announce prefixes tagged with this BGP community to your external BGP peers.

!!! note
    Explain/link how to build filters based on ASN or AS-Set.

## Configuration

=== "Juniper JunOS"

    Static approach with a prefix list:
    ```
    set policy-options prefix-list CUSTOMER-PREFIXES-V4 <PLEASE INSERT CUSTOMER PREFIX HERE>
    set policy-options prefix-list CUSTOMER-PREFIXES-V6 <PLEASE INSERT CUSTOMER PREFIX HERE>
    
    set policy-options policy-statement MY_OUTPUT_FILTER term CUSTOMER-PREFIXES-V4 from prefix-list CUSTOMER-PREFIXES-V4
    set policy-options policy-statement MY_OUTPUT_FILTER term CUSTOMER-PREFIXES-V4 then accept
    set policy-options policy-statement MY_OUTPUT_FILTER term CUSTOMER-PREFIXES-V6 from family inet6
    set policy-options policy-statement MY_OUTPUT_FILTER term CUSTOMER-PREFIXES-V6 from prefix-list CUSTOMER-PREFIXES-V6
    set policy-options policy-statement MY_OUTPUT_FILTER term CUSTOMER-PREFIXES-V6 then accept
    ```

    Dynamic approach with BGP communities:

    Create Policy, Prefix List and Community for BGP Import:
    This adds a policy for the customer BGP session, to control which prefixes to import and tag them with the specific community
    ```
    set policy-options prefix-list CUSTOMER-BLAH-V4 <PLEASE INSERT CUSTOMER PREFIX HERE>
    set policy-options prefix-list CUSTOMER-BLAH-V6 <PLEASE INSERT CUSTOMER PREFIX HERE>
    
    set policy-options community CUSTOMER members 65534:100
    
    set policy-options policy-statement CUSTOMER-BLAH-IN term TAG-PREFIXES then community add CUSTOMER
    set policy-options policy-statement CUSTOMER-BLAH-IN term TAG-PREFIXES then next term
    set policy-options policy-statement CUSTOMER-BLAH-IN term CUSTOMER-ROUTES-V4 from prefix-list CUSTOMER-BLAH-V4
    set policy-options policy-statement CUSTOMER-BLAH-IN term CUSTOMER-ROUTES-V4 then accept
    set policy-options policy-statement CUSTOMER-BLAH-IN term CUSTOMER-ROUTES-V6 from family inet6
    set policy-options policy-statement CUSTOMER-BLAH-IN term CUSTOMER-ROUTES-V6 from prefix-list CUSTOMER-BLAH-V6
    set policy-options policy-statement CUSTOMER-BLAH-IN term CUSTOMER-ROUTES-V6 then accept
    ```

    On the BGP session to the customer we're adding this policy:
    ```
    set protocols bgp group CUSTOMER-V4 neighbor 198.51.100.38 import CUSTOMER-BLAH-IN
    set protocols bgp group CUSTOMER-V4 neighbor 198.51.100.38 import REJECT
    ```

    Could also be used for static routes by applying a previously created group:
    ```
    set groups TAG-CUSTOMER-ROUTES routing-options rib inet6.0 static route <*> community 65534:100
    set groups TAG-CUSTOMER-ROUTES routing-options static route <*> community 65534:100
    
    set routing-options aggregate route 203.0.113.0/24 apply-groups TAG-CUSTOMER-ROUTES
    ```

    And then applied to the upstream BGP session:

    ```
    set policy-options policy-statement MY_OUTPUT_FILTER term CUSTOMER-PREFIXES-V4 from community CUSTOMER
    set policy-options policy-statement MY_OUTPUT_FILTER term CUSTOMER-PREFIXES-V4 from route-filter 0.0.0.0/0 prefix-length-range /8-/24
    set policy-options policy-statement MY_OUTPUT_FILTER term CUSTOMER-PREFIXES-V4 then accept
    set policy-options policy-statement MY_OUTPUT_FILTER term CUSTOMER-PREFIXES-V6 from family inet6
    set policy-options policy-statement MY_OUTPUT_FILTER term CUSTOMER-PREFIXES-V6 from community CUSTOMER
    set policy-options policy-statement MY_OUTPUT_FILTER term CUSTOMER-PREFIXES-V6 from route-filter ::/0 prefix-length-range /12-/48
    set policy-options policy-statement MY_OUTPUT_FILTER term CUSTOMER-PREFIXES-V6 then accept
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


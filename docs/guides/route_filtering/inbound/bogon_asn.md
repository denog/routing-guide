# Bogon AS

## Purpose
Bogon AS are autonomous systems which are used for test or demo applications. These AS may not be used on the public Internet.

## Description

## Configuration

=== "Cisco IOS XR"
    ```
    as-path-set bogon-asns
       # RFC7607
       ios-regex '_0_',
       # 2 to 4 byte ASN migrations
       passes-through '23456',
       # RFC5398
       passes-through '[64496..64511]',
       passes-through '[65536..65551]',
       # RFC6996
       passes-through '[64512..65534]',
       passes-through '[4200000000..4294967294]',
       # RFC7300
       passes-through '65535',
       passes-through '4294967295',
       # IANA reserved
       passes-through '[65552..131071]'
    end-set

    route-policy import_from_ebgp
        if as-path in bogon-asns then
            drop
        else
            pass
        endif
    end-policy
    ```

=== "Bird2"
    ```
    define BOGON_ASNS = [
      0,                      # RFC 7607
      23456,                  # RFC 4893 AS_TRANS
      64496..64511,           # RFC 5398 and documentation/example ASNs
      64512..65534,           # RFC 6996 Private ASNs
      65535,                  # RFC 7300 Last 16 bit ASN
      65536..65551,           # RFC 5398 and documentation/example ASNs
      65552..131071,          # RFC IANA reserved ASNs
      4200000000..4294967294, # RFC 6996 Private ASNs
      4294967295              # RFC 7300 Last 32 bit ASN
    ];
    function reject_bogon_asns()
    int set bogon_asns;
    {
      bogon_asns = BOGON_ASNS;
      if ( bgp_path ~ bogon_asns ) then {
        # optional logging:
        # print "Reject: bogon AS_PATH: ", net, " ", bgp_path;
        reject;
      }
    }
    filter import_all {
      reject_bogon_asns();
      ...
      accept;
    }
    ```

=== "Nokia SR OS classic CLI"
    ```
    /configure router "Base" policy-options
    begin
           as-path-group "bogon-asns"
                entry 10 expression ".* 23456 .*"
                entry 15 expression ".* [64496-64511] .*"
                entry 20 expression ".* [65536-65551] .*"
                entry 25 expression ".* [64512-65534] .*"
                entry 30 expression ".* [4200000000-4294967294] .*"
                entry 35 expression ".* 65535 .*"
                entry 40 expression ".* 4294967295 .*"
                entry 45 expression ".* [65552-131071] .*"
            exit
            policy-statement "inbound"
                description "inbound peering policy"
                [...]
                entry 10
                    from
                        as-path-group "bogon-asns"
                    exit
                    action drop
                    exit
                exit
                [...]
            exit
    commit
    ```

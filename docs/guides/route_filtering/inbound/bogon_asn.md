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

=== "FRRouting"
    FRRouting uses regular expressions only for AS-path access-lists. The following list was compiled using a numeric range to regex converter:
    ```
    bgp as-path access-list bogon-asns permit _0_
    bgp as-path access-list bogon-asns permit _23456_
    bgp as-path access-list bogon-asns permit _(6449[6-9]|64[5-9][0-9]{2}|6[5-9][0-9]{3})_
    bgp as-path access-list bogon-asns permit _(7000[0-9]|700[1-9][0-9]|70[1-9][0-9]{2}|7[1-9][0-9]{3}|[89][0-9]{4}|1[0-2][0-9]{4}|130[0-9]{3}|1310[0-6][0-9]|13107[01])_
    bgp as-path access-list bogon-asns permit _(420000000[0-9]|42000000[1-9][0-9]|4200000[1-9][0-9]{2}|420000[1-9][0-9]{3}|42000[1-9][0-9]{4}|4200[1-9][0-9]{5}|420[1-9][0-9]{6}|42[1-8][0-9]{7}|429[0-3][0-9]{6}|4294[0-8][0-9]{5}|42949[0-5][0-9]{4}|429496[0-6][0-9]{3}|4294967[01][0-9]{2}|42949672[0-8][0-9]|429496729[0-5])_

    route-map import-all deny 100
      match as-path bogon-asns
    ```

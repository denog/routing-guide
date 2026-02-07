---
tags:
  - Huawei VRP missing
  - OpenBGPD missing
  - RtBrick RBFS missing
---

# Bogon Prefixes

"Bogon" prefixes are non-routeable or reserved prefixes which should never be seen in the global routing table.

## IPv4

When IPv4 was created, the inventors reserved certain part of the address space for specific purposes. These were the times of class-A,B,C networks (if anybody still mentions them - the concept was abolished in 1993 in some RFCs starting with
[RFC1517](https://www.rfc-editor.org/rfc/rfc1517)).

The following IPv4 space is still considered to be not routable and should never be announced via BGP:

- **Private IPv4 space** as defined in [RFC1918](https://www.rfc-editor.org/rfc/rfc1918). Networks *10.0.0.0/8*, *172.16.0.0/12* and *192.168.0.0/16* are reserved for private use and should never be announced.
- **IPv4 networks reserved for documentation purposes** defined in [RFC5737](https://www.rfc-editor.org/rfc/rfc5737). These three networks are reserved and should not be routed (but you might see them in this document as example networks).
- **Reserved for multicast:** The address block *224.0.0.0/4* was reserved for multicast and cannot be used for anything else. Do not accept announcements out of it via BGP.
- **So-called *Class-E*:** The network block *240.0.0.0/4* was always reserved "for future use" which never came. Today this range is considered to be not usable and therefore should not be accepted via BGP.
- **More can be found** at this [IANA website](https://www.iana.org/assignments/iana-ipv4-special-registry/iana-ipv4-special-registry.xhtml). Everything with "Globally Reachable False" should be filtered out.

## IPv6

In IPv6, there is a [similar list at IANA](http://www.iana.org/assignments/ipv6-address-space). However, for IPv6 it is easier to positive-filter for *2000::/3*, as this is the only block where **currently** unicast address assignments were made from. Currently. You might check frequently if other blocks have been added. It is strongly recommended that you automate this task.

## Configuration Examples

=== "Cisco IOS / FRRouting"
    For IPv4, you can simply add all unwanted prefixes to the list we defined in the previous section:
    ```
    ip prefix-list ipv4-unwanted permit 10.0.0.0/8 le 32
    ip prefix-list ipv4-unwanted permit 172.16.0.0/12 le 32
    ip prefix-list ipv4-unwanted permit 192.168.0.0/16 le 32
    ...
    ```

=== "Cisco IOS XR"
    For IPv4, you can simply add all unwanted prefixes to the list:
    ```
    prefix-set bogon-ipv4
      # RFC1122 'this' Network
      0.0.0.0/8 le 32,
      # RFC1918 Private
      10.0.0.0/8 le 32,
      # RFC6598 Carrier grade nat space
      100.64.0.0/10 le 32,
      # RFC1122 Loopback
      127.0.0.0/8 le 32,
      # RFC3927 Link Local
      169.254.0.0/16 le 32,
      # RFC1918 Private
      172.16.0.0/12 le 32,
      # RFC6890 Protocol Assignments
      192.0.0.0/24 le 32,
      # RFC5737 Documentation TEST-NET-1
      192.0.2.0/24 le 32,
      # RFC7526 6to4 anycast relay
      192.88.99.0/24 le 32,
      # RFC1918 Private
      192.168.0.0/16 le 32,
      # RFC2544 Benchmarking
      198.18.0.0/15 le 32,
      # RFC5737 Documentation TEST-NET-2
      198.51.100.0/24 le 32,
      # RFC5737 Documentation TEST-NET-3
      203.0.113.0/24 le 32,
      # RFC5771 Multicast
      224.0.0.0/4 le 32,
      # RFC1112 Reserved
      240.0.0.0/4 le 32
    end-set

    prefix-set bogon-ipv6
      # IETF reserved
      ::/8 le 128,
      # RFC6666 Discard-Only Address Block
      100::/64 le 128,
      # RFC4380,RFC8190 TEREDO
      2001::/32 le 128,
      # RFC5180 Benchmarking
      2001:2::/48 le 128,
      # RFC7450 Documentation
      2001:db8::/32 le 128,
      # RFC3056 6to4
      2002::/16 le 128,
      # RFC9637 Documentation Space
      3fff::/20 le 128,
      # RFC4193,RFC8190 Unique-Local
      fc00::/7 le 128,
      # RFC4291 Link-Local Unicast
      fe80::/10 le 128
    end-set

    route-policy reject-bogons-ipv4-networks
      if destination in bogon-ipv4 then
        drop
      endif
    end-policy
    route-policy reject-bogons-ipv6-networks
      if destination in bogon-ipv6 then
        drop
      endif
    end-policy
    ...
    ```

=== "Mikrotik"
    You can add this to your existing filter or you can create a sub-filter for better readability:
    ```
    /routing filter
    add action=reject chain=ipv4-unwanted prefix=10.0.0.0/8 prefix-length=8-32
    add action=reject chain=ipv4-unwanted prefix=172.16.0.0/12 prefix-length=12-32
    add action=reject chain=ipv4-unwanted prefix=192.168.0.0/16 prefix-length=16-32
    ...
    ```

=== "BIRD 2/3"
    ```
    define BOGON_PREFIXES4 = [
      0.0.0.0/8+,         # RFC1122 'this' Network
      10.0.0.0/8+,        # RFC1918 Private
      100.64.0.0/10+,     # RFC6598 Carrier grade nat space
      127.0.0.0/8+,       # RFC1122 Loopback
      169.254.0.0/16+,    # RFC3927 Link Local
      172.16.0.0/12+,     # RFC1918 Private
      192.0.2.0/24+,      # RFC5737 Documentation TEST-NET-1
      192.168.0.0/16+,    # RFC1918 Private
      198.18.0.0/15+,     # RFC2544 Benchmarking
      198.51.100.0/24+,   # RFC5737 Documentation TEST-NET-2
      203.0.113.0/24+,    # RFC5737 Documentation TEST-NET-3
      224.0.0.0/4+,       # RFC5771 Multicast
      240.0.0.0/4+        # RFC1112 Reserved
    ];
    define BOGON_PREFIXES6 = [
      ::/8+,            # RFC4291 Loopback and more
      0100::/64+,       # RFC6666 Discard-Only Address Block
      2001:2::/48+,     # RFC5180 Benchmarking
      2001:10::/28+     # RFC4843 ORCHID
      2001:db8::/32+,   # RFC7450 Documentation
      3ffe::/16+,       # RFC3701 old 6bone
      3fff::/20+,       # RFC9637 Documentation
      5f00::/16+,       # RFC9602 SRv6 SIDs
      fc00::/7+,        # RFC4193,RFC8190 Unique-Local
      fe80::/10+        # RFC4291 Link-Local Unicast
      fec0::/10+        # RFC3879 old Site-Local Unicast
      ff00::/8+         # RFC4291 Multicast
    ];
    function reject_bogon_prefixes4()
    prefix set bogon_prefixes4;
    {
      bogon_prefixes4 = BOGON_PREFIXES4;
      if (net ~ bogon_prefixes4) then {
        # optional logging:
        # print "Reject: Bogon prefix: ", net, " ", bgp_path;
        reject;
      }
    }
    function reject_bogon_prefixes6()
    prefix set bogon_prefixes6;
    {
      bogon_prefixes6 = BOGON_PREFIXES6;
      if (net ~ bogon_prefixes6) then {
        # optional logging:
        # print "Reject: Bogon prefix: ", net, " ", bgp_path;
        reject;
      }
    }
    filter import_ipv4 {
      reject_bogon_prefixes4();
      ...
      accept;
    }
    filter import_ipv6 {
      reject_bogon_prefixes6();
      ...
      accept;
    }
    ```

=== "Juniper JunOS"
    For IPv4 as an own policy:
    ```
    set policy-options policy-statement IPV4-BOGONS term IANA-LOCAL-IDENTIFICATION from route-filter 0.0.0.0/8 orlonger
    set policy-options policy-statement IPV4-BOGONS term IANA-LOCAL-IDENTIFICATION then accept
    set policy-options policy-statement IPV4-BOGONS term RFC1918 from route-filter 10.0.0.0/8 orlonger
    set policy-options policy-statement IPV4-BOGONS term RFC1918 from route-filter 172.16.0.0/12 orlonger
    set policy-options policy-statement IPV4-BOGONS term RFC1918 from route-filter 192.168.0.0/16 orlonger
    set policy-options policy-statement IPV4-BOGONS term RFC1918 then accept
    set policy-options policy-statement IPV4-BOGONS term IANA-SHARED-ADDRESS from route-filter 100.64.0.0/10 orlonger
    set policy-options policy-statement IPV4-BOGONS term IANA-SHARED-ADDRESS then accept
    set policy-options policy-statement IPV4-BOGONS term IANA-LOOPBACK from route-filter 127.0.0.0/8 orlonger
    set policy-options policy-statement IPV4-BOGONS term IANA-LOOPBACK then accept
    set policy-options policy-statement IPV4-BOGONS term IANA-LINK-LOCAL-ADDRESSING from route-filter 169.254.0.0/16 orlonger
    set policy-options policy-statement IPV4-BOGONS term IANA-LINK-LOCAL-ADDRESSING then accept
    set policy-options policy-statement IPV4-BOGONS term IANA-IPV4-SPECIAL-PURPOSE from route-filter 192.0.0.0/24 orlonger
    set policy-options policy-statement IPV4-BOGONS term IANA-IPV4-SPECIAL-PURPOSE then accept
    set policy-options policy-statement IPV4-BOGONS term IANA-TEST-NET-1 from route-filter 192.0.2.0/24 orlonger
    set policy-options policy-statement IPV4-BOGONS term IANA-TEST-NET-1 then accept
    set policy-options policy-statement IPV4-BOGONS term IANA-BENCHMARK-TESTING from route-filter 198.18.0.0/15 orlonger
    set policy-options policy-statement IPV4-BOGONS term IANA-BENCHMARK-TESTING then accept
    set policy-options policy-statement IPV4-BOGONS term IANA-TEST-NET-2 from route-filter 198.51.100.0/24 orlonger
    set policy-options policy-statement IPV4-BOGONS term IANA-TEST-NET-2 then accept
    set policy-options policy-statement IPV4-BOGONS term IANA-TEST-NET-3 from route-filter 203.0.113.0/24 orlonger
    set policy-options policy-statement IPV4-BOGONS term IANA-TEST-NET-3 then accept
    set policy-options policy-statement IPV4-BOGONS term IANA-MULTICAST from route-filter 224.0.0.0/4 orlonger
    set policy-options policy-statement IPV4-BOGONS term IANA-MULTICAST then accept
    set policy-options policy-statement IPV4-BOGONS term IANA-CLASS-E from route-filter 240.0.0.0/4 orlonger
    set policy-options policy-statement IPV4-BOGONS term IANA-CLASS-E then accept
    set policy-options policy-statement IPV4-BOGONS term REJECT from route-filter 0.0.0.0/0 orlonger
    set policy-options policy-statement IPV4-BOGONS term REJECT then reject
    ```

    For IPv6 as an own policy:
    ```
    set policy-options policy-statement IPV6-BOGONS term V4MAPPED-ETC from route-filter 0000::/8 orlonger
    set policy-options policy-statement IPV6-BOGONS term V4MAPPED-ETC then accept
    set policy-options policy-statement IPV6-BOGONS term MULTICAST from route-filter fe00::/9 orlonger
    set policy-options policy-statement IPV6-BOGONS term MULTICAST from route-filter ff00::/8 orlonger
    set policy-options policy-statement IPV6-BOGONS term MULTICAST then accept
    set policy-options policy-statement IPV6-BOGONS term DOCUMENTATION-PREFIX from route-filter 2001:db8::/32 orlonger
    set policy-options policy-statement IPV6-BOGONS term DOCUMENTATION-PREFIX from route-filter 3fff::/20 orlonger
    set policy-options policy-statement IPV6-BOGONS term DOCUMENTATION-PREFIX then accept
    set policy-options policy-statement IPV6-BOGONS term 6BONE from route-filter 3ffe::/16 orlonger
    set policy-options policy-statement IPV6-BOGONS term 6BONE then accept
    set policy-options policy-statement IPV6-BOGONS term TEREDO-ACCEPT from route-filter 2001::/32 exact
    set policy-options policy-statement IPV6-BOGONS term TEREDO-ACCEPT then next policy
    set policy-options policy-statement IPV6-BOGONS term TEREDO-REJECT from route-filter 2001::/32 longer
    set policy-options policy-statement IPV6-BOGONS term TEREDO-REJECT then accept
    set policy-options policy-statement IPV6-BOGONS term 6TO4-ACCEPT from route-filter 2002::/16 exact
    set policy-options policy-statement IPV6-BOGONS term 6TO4-ACCEPT then next policy
    set policy-options policy-statement IPV6-BOGONS term 6TO4-REJECT from route-filter 2002::/16 longer
    set policy-options policy-statement IPV6-BOGONS term 6TO4-REJECT then accept
    set policy-options policy-statement IPV6-BOGONS term REJECT from route-filter 0::/0 orlonger
    set policy-options policy-statement IPV6-BOGONS term REJECT then reject
    ```

    Usage within another policy (nested policies):
    ```
    set policy-options policy-statement MY_INPUT_POLICY term BOGONS-V4 from family inet
    set policy-options policy-statement MY_INPUT_POLICY term BOGONS-V4 from policy IPV4-BOGONS
    set policy-options policy-statement MY_INPUT_POLICY term BOGONS-V4 then trace
    set policy-options policy-statement MY_INPUT_POLICY term BOGONS-V4 then reject
    set policy-options policy-statement MY_INPUT_POLICY term BOGONS-V6 from family inet6
    set policy-options policy-statement MY_INPUT_POLICY term BOGONS-V6 from policy IPV6-BOGONS
    set policy-options policy-statement MY_INPUT_POLICY term BOGONS-V6 then trace
    set policy-options policy-statement MY_INPUT_POLICY term BOGONS-V6 then reject
    ```

=== "Nokia SR OS classic CLI"
    ```
    /configure router "Base" policy-options
    begin
            prefix-list "v4-bogons"
                prefix 0.0.0.0/8 longer
                prefix 10.0.0.0/8 longer
                prefix 100.64.0.0/10 longer
                prefix 127.0.0.0/8 longer
                prefix 169.254.0.0/16 longer
                prefix 172.16.0.0/12 longer
                prefix 192.0.0.0/24 longer
                prefix 192.0.2.0/24 longer
                prefix 192.168.0.0/16 longer
                prefix 198.18.0.0/15 longer
                prefix 198.51.100.0/24 longer
                prefix 203.0.113.0/24 longer
                prefix 224.0.0.0/4 longer
                prefix 240.0.0.0/4 longer
            exit
            prefix-list "v6-bogons"
                prefix ::/8 longer
                prefix 100::/64 longer
                prefix 2001:2::/48 longer
                prefix 2001:10::/28 longer
                prefix 2001:db8::/32 longer
                prefix 3ffe::/16 longer
                prefix 3fff::/20 longer
                prefix 5f00::/16 longer
                prefix fc00::/7 longer
                prefix fe80::/10 longer
                prefix fec0::/10 longer
                prefix ff00::/8 longer
            exit
            policy-statement "inbound"
                description "inbound peering policy"
                [...]
                entry 30
                    from
                        prefix-list "v4-bogons"
                    exit
                    action drop
                    exit
                exit
                entry 40
                    from
                        prefix-list "v6-bogons"
                    exit
                    action drop
                    exit
                exit
                [...]
            exit
    commit
    ```

=== "Arista EOS legacy"
    ```
    ip prefix-list BOGONS_v4
       seq 1 permit 0.0.0.0/8 le 32
       seq 2 permit 10.0.0.0/8 le 32
       seq 3 permit 100.64.0.0/10 le 32
       seq 4 permit 127.0.0.0/8 le 32
       seq 5 permit 169.254.0.0/16 le 32
       seq 6 permit 172.16.0.0/12 le 32
       seq 7 permit 192.0.2.0/24 le 32
       seq 8 permit 192.88.99.0/24 le 32
       seq 9 permit 192.168.0.0/16 le 32
       seq 10 permit 198.18.0.0/15 le 32
       seq 11 permit 198.51.100.0/24 le 32
       seq 12 permit 203.0.113.0/24 le 32
       seq 13 permit 224.0.0.0/4 le 32
       seq 14 permit 240.0.0.0/4 le 32
    !
    ipv6 prefix-list BOGONS_v6
       seq 1 permit 100::/64
       seq 2 permit 2001:2::/48
       seq 3 permit 2001:10::/28
       seq 4 permit 2001:db8::/32
       seq 5 permit 2002::/16
       seq 6 permit 3ffe::/16
       seq 7 permit fc00::/7
       seq 8 permit fe80::/10
       seq 9 permit fec0::/10
       seq 10 permit ff00::/8
       set 11 permit 3fff::/20
       set 12 permit 5f00::/16
    !
    route-map example-in deny 14
       match ip address prefix-list BOGONS_v4
    route-map example-in deny 16
       match ipv6 address prefix-list BOGONS_v6
    !
    router bgp 64500
       address-family ipv6
          neighbor 2001:db8::1 route-map example-in in
       address-family ipv4
          neighbor 198.51.100.1 route-map example-in in
    ```

=== "Arista EOS RCF"
    ```
    ip prefix-list BOGONS_v4
       seq 1 permit 0.0.0.0/8 le 32
       seq 2 permit 10.0.0.0/8 le 32
       seq 3 permit 100.64.0.0/10 le 32
       seq 4 permit 127.0.0.0/8 le 32
       seq 5 permit 169.254.0.0/16 le 32
       seq 6 permit 172.16.0.0/12 le 32
       seq 7 permit 192.0.2.0/24 le 32
       seq 8 permit 192.88.99.0/24 le 32
       seq 9 permit 192.168.0.0/16 le 32
       seq 10 permit 198.18.0.0/15 le 32
       seq 11 permit 198.51.100.0/24 le 32
       seq 12 permit 203.0.113.0/24 le 32
       seq 13 permit 224.0.0.0/4 le 32
       seq 14 permit 240.0.0.0/4 le 32
    !
    ipv6 prefix-list BOGONS_v6
       seq 1 permit 100::/64
       seq 2 permit 2001:2::/48
       seq 3 permit 2001:10::/28
       seq 4 permit 2001:db8::/32
       seq 5 permit 2002::/16
       seq 6 permit 3ffe::/16
       seq 7 permit fc00::/7
       seq 8 permit fe80::/10
       seq 9 permit fec0::/10
       seq 10 permit ff00::/8
       set 11 permit 3fff::/20
       set 12 permit 5f00::/16
    !
    router general
    control-functions
       code unit example
    function bogon_v4() {
        return prefix match prefix_list_v4 BOGONS_v4;
    }
    function bogon_v6() {
        return prefix match prefix_list_v4 BOGONS_v4;
    }
    function example_in() {
        if bogon_v4() {
            exit false;
        } else if bogon_v6() {
            exit false;
        }
    }
    EOF
          compile
          commit
          exit
       exit
    !
    router bgp 64500
       address-family ipv6
          neighbor 2001:db8::1 rcf in example_in()
       address-family ipv4
          neighbor 198.51.100.1 rcf in example_in()
    ```

=== "VyOS"
    VyOS has two modes (operational and configuration mode). Enter configuration mode with
    `configure` to make changes. Use `commit` to apply them and `save` to keep them after reboot.
    ```
    set policy prefix-list special-purpose rule 10 action permit
    set policy prefix-list special-purpose rule 10 prefix 0.0.0.0/8
    set policy prefix-list special-purpose rule 10 le 32
    set policy prefix-list special-purpose rule 11 action permit
    set policy prefix-list special-purpose rule 11 prefix 10.0.0.0/8
    set policy prefix-list special-purpose rule 11 le 32
    set policy prefix-list special-purpose rule 12 action permit
    set policy prefix-list special-purpose rule 12 prefix 100.64.0.0/10
    set policy prefix-list special-purpose rule 12 le 32
    set policy prefix-list special-purpose rule 13 action permit
    set policy prefix-list special-purpose rule 13 prefix 127.0.0.0/8
    set policy prefix-list special-purpose rule 13 le 32
    set policy prefix-list special-purpose rule 14 action permit
    set policy prefix-list special-purpose rule 14 prefix 169.254.0.0/16
    set policy prefix-list special-purpose rule 14 le 32
    set policy prefix-list special-purpose rule 15 action permit
    set policy prefix-list special-purpose rule 15 prefix 172.16.0.0/12
    set policy prefix-list special-purpose rule 15 le 32
    set policy prefix-list special-purpose rule 16 action permit
    set policy prefix-list special-purpose rule 16 prefix 192.0.0.0/24
    set policy prefix-list special-purpose rule 16 le 32
    set policy prefix-list special-purpose rule 17 action permit
    set policy prefix-list special-purpose rule 17 prefix 192.0.2.0/24
    set policy prefix-list special-purpose rule 17 le 32
    set policy prefix-list special-purpose rule 18 action permit
    set policy prefix-list special-purpose rule 18 prefix 192.88.99.2/32
    set policy prefix-list special-purpose rule 19 action permit
    set policy prefix-list special-purpose rule 19 prefix 192.168.0.0/16
    set policy prefix-list special-purpose rule 19 le 32
    set policy prefix-list special-purpose rule 20 action permit
    set policy prefix-list special-purpose rule 20 prefix 198.18.0.0/15
    set policy prefix-list special-purpose rule 20 le 32
    set policy prefix-list special-purpose rule 21 action permit
    set policy prefix-list special-purpose rule 21 prefix 198.51.100.0/24
    set policy prefix-list special-purpose rule 21 le 32
    set policy prefix-list special-purpose rule 22 action permit
    set policy prefix-list special-purpose rule 22 prefix 203.0.113.0/24
    set policy prefix-list special-purpose rule 22 le 32

    set policy prefix-list6 special-purpose-6 rule 10 action permit
    set policy prefix-list6 special-purpose-6 rule 10 prefix ::/64
    set policy prefix-list6 special-purpose-6 rule 10 le 128
    set policy prefix-list6 special-purpose-6 rule 11 action permit
    set policy prefix-list6 special-purpose-6 rule 11 prefix 64:ff9b:1::/48
    set policy prefix-list6 special-purpose-6 rule 11 le 128
    set policy prefix-list6 special-purpose-6 rule 12 action permit
    set policy prefix-list6 special-purpose-6 rule 12 prefix 100:0:0:1::/64
    set policy prefix-list6 special-purpose-6 rule 12 le 128
    set policy prefix-list6 special-purpose-6 rule 13 action permit
    set policy prefix-list6 special-purpose-6 rule 13 prefix 100::/64
    set policy prefix-list6 special-purpose-6 rule 13 le 128
    set policy prefix-list6 special-purpose-6 rule 14 action permit
    set policy prefix-list6 special-purpose-6 rule 14 prefix 2001::/23
    set policy prefix-list6 special-purpose-6 rule 14 le 128
    set policy prefix-list6 special-purpose-6 rule 15 action permit
    set policy prefix-list6 special-purpose-6 rule 15 prefix 2001:2::/48
    set policy prefix-list6 special-purpose-6 rule 15 le 128
    set policy prefix-list6 special-purpose-6 rule 16 action permit
    set policy prefix-list6 special-purpose-6 rule 16 prefix 2001:db8::/32
    set policy prefix-list6 special-purpose-6 rule 16 le 128
    set policy prefix-list6 special-purpose-6 rule 17 action permit
    set policy prefix-list6 special-purpose-6 rule 17 prefix 2002::/16
    set policy prefix-list6 special-purpose-6 rule 17 le 128
    set policy prefix-list6 special-purpose-6 rule 18 action permit
    set policy prefix-list6 special-purpose-6 rule 18 prefix 3fff::/20
    set policy prefix-list6 special-purpose-6 rule 18 le 128
    set policy prefix-list6 special-purpose-6 rule 19 action permit
    set policy prefix-list6 special-purpose-6 rule 19 prefix 5f00::/16
    set policy prefix-list6 special-purpose-6 rule 19 le 128
    set policy prefix-list6 special-purpose-6 rule 20 action permit
    set policy prefix-list6 special-purpose-6 rule 20 prefix fc00::/7
    set policy prefix-list6 special-purpose-6 rule 20 le 128
    set policy prefix-list6 special-purpose-6 rule 21 action permit
    set policy prefix-list6 special-purpose-6 rule 21 prefix fe80::/10
    set policy prefix-list6 special-purpose-6 rule 21 le 128
    ```

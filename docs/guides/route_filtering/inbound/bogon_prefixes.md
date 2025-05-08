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

=== "Cisco IOS"
    For IPv4, you can simply add all unwanted prefixes to the list we defined in the previous section:
    ```
    ip prefix-list ipv4-unwanted permit 192.168.0.0/16 le 32
    ip prefix-list ipv4-unwanted permit 172.16.0.0/12 le 32
    ip prefix-list ipv4-unwanted permit 10.0.0.0/8 le 32
    ...
    ```

=== "Cisco IOS XR"
    For IPv4, you can simply add all unwanted prefixes to the list:
    ```
    prefix-set bogon-ipv4
      # RFC 1122 'this' Network
      0.0.0.0/8 le 32,
      # RFC 1918 Private
      10.0.0.0/8 le 32,
      # RFC 6598 Carrier grade nat space
      100.64.0.0/10 le 32,
      # RFC 1122 Loopback
      127.0.0.0/8 le 32,
      # RFC 3927 Link Local
      169.254.0.0/16 le 32,
      # RFC 1918 Private
      172.16.0.0/12 le 32,
      # RFC 6890 Protocol Assignments
      192.0.0.0/24 le 32,
      # RFC 5737 Documentation TEST-NET-1
      192.0.2.0/24 le 32,
      # RFC 7526 6to4 anycast relay
      192.88.99.0/24 le 32,
      # RFC 1918 Private
      192.168.0.0/16 le 32,
      # RFC 2544 Benchmarking
      198.18.0.0/15 le 32,
      # RFC 5737 Documentation TEST-NET-2
      198.51.100.0/24 le 32,
      # RFC 5737 Documentation TEST-NET-3
      203.0.113.0/24 le 32,
      # RFC 5771 Multicast
      224.0.0.0/4 le 32,
      # RFC 1112 Reserved
      240.0.0.0/4 le 32
    end-set
    
    prefix-set bogon-ipv6
      #IETF reserved
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
    add action=reject chain=ipv4-unwanted prefix=192.168.0.0/16 prefix-length=16-32
    add action=reject chain=ipv4-unwanted prefix=172.16.0.0/12 prefix-length=12-32
    add action=reject chain=ipv4-unwanted prefix=10.0.0.0/8 prefix-length=8-32
    ...
    ```

=== "Bird2"
    ```
    define BOGON_PREFIXES4 = [
      0.0.0.0/8+,         # RFC 1122 'this' Network
      10.0.0.0/8+,        # RFC 1918 Private
      100.64.0.0/10+,     # RFC 6598 Carrier grade nat space
      127.0.0.0/8+,       # RFC 1122 Loopback
      169.254.0.0/16+,    # RFC 3927 Link Local
      172.16.0.0/12+,     # RFC 1918 Private
      192.0.2.0/24+,      # RFC 5737 Documentation TEST-NET-1
      192.168.0.0/16+,    # RFC 1918 Private
      198.18.0.0/15+,     # RFC 2544 Benchmarking
      198.51.100.0/24+,   # RFC 5737 Documentation TEST-NET-2
      203.0.113.0/24+,    # RFC 5737 Documentation TEST-NET-3
      224.0.0.0/4+,       # RFC 5771 Multicast
      240.0.0.0/4+        # RFC 1112 Reserved
    ];
    define BOGON_PREFIXES6 = [
        ::/8+,           # RFC4291 Loopback and more
        0100::/64+,      # RFC6666 Discard-Only Address Block
        2001:2::/48+,    # RFC5180 Benchmarking
        2001:10::/28+    # RFC4843 ORCHID
        2001:db8::/32+,  # RFC7450 Documentation
        3ffe::/16+,      # RFC3701 old 6bone
        3fff::/20+,      # RFC9637 Documentation
        5f00::/16+,      # RFC9602 SRv6 SIDs
        fc00::/7+,       # RFC4193,RFC8190 Unique-Local
        fe80::/10+       # RFC4291 Link-Local Unicast
        fec0::/10+       # RFC3879 old Site-Local Unicast
        ff00::/8+        # RFC4291 Multicast
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

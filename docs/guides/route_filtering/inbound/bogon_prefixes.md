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

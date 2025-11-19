---
tags:
  - Text missing
---

# Well-known BGP Communities

So-called well-known communities are defined in RFCs and must be processed by all BGP
speaking entities. The [IANA](https://iana.org) keeps a [list](https://www.iana.org/assignments/bgp-well-known-communities/bgp-well-known-communities.xhtml) of well-known communities.

The following well-known communities are quite useful.

## NO-EXPORT

BGP prefixes tagged with NO-EXPORT must not be advertised via eBGP to other Autonomous
Systems. Defined in [RFC1997](https://www.rfc-editor.org/rfc/rfc1997.html),
this well-known community is useful for:

- Announcing more specific prefixes to your eBGP neighbors and making sure they are
not announced further. To do this, set NO-EXPORT on your outgoing route-map (or
similar).
- Keeping your own specific routes inside your own AS. For this, set NO-EXPORT when
injecting your prefixes into BGP and leave it off the network blocks which should be
announced externally.

## NO-ADVERTISE

This well-known community is even stricter then NO-EXPORT. *NO-ADVERTISE* forbids a router
from announcing a prefix to any BGP neighbor; this also includes iBGP.

## NO-PEER

Defined in [RFC3765](https://www.rfc-editor.org/rfc/rfc3765.html) this community marks prefixes
which should not be advertised via bilateral peering sessions.

## BLACKHOLE

Defined 2016 in [RFC7999](<https://www.rfc-editor.org/rfc/rfc7999.html>),
this well-known community asks the receiving operator to blackhole
or block all traffic destined to the prefix with this community attached.

For this to work properly, the receiver should accept longer than usual prefixes (up to /32 in
IPv4 and up to /128 in IPv6). Also, the receiver should not propagate these prefixes further,
so either the sender also attaches a NO-EXPORT or the receiver should.
The purpose, of course, is to fight DoS or DDoS attacks.

## ACCEPT-OWN

Defined in [RFC7611](https://www.rfc-editor.org/rfc/rfc7611.html).

## GRACEFUL-SHUTDOWN

Defined in [RFC8326](https://www.rfc-editor.org/rfc/rfc8326.html).

## LLGR-STALE and NO-LLGR

Both defined in [RFC9494](https://www.rfc-editor.org/rfc/rfc9494.html).

# Blackhole Routing

## Purpose

Destination based Remotely Triggered Blackhole Routing is standardised in [RFC3882](https://www.rfc-editor.org/rfc/rfc3882.html). It is a technique which allows a BGP community to be attached to a prefix, and then all traffic to that destination prefix will be dropped.

One use case for RTBH is that a destination prefix is under attack (usually a DDoS attack) and an RTBH route is created to mitigate the attack.

For example, the traffic load towards the destination prefix is causing network connectivity problems for other users on the network, not just the prefix under attack. This can happen when a large amount of traffic is sent to a prefix, and the traffic is coming from many different sources, and entering the network at multiple different points. At each point where traffic enters the network, the increased traffic volume from the attack is not exceptionally high. However, at the point in the network where the customer is connected, all this excess traffic is aggregated in one place, to forward on to the customer. The router where the customer (victim) is connected might be receiving so much traffic for that customer, it's links become congested, which affects all other customers connected to that same router.

If the customer (victim) is receiving more traffic than they can handle, creating an RTBH route to drop all traffic towards that customer has no additional impact on the customer, they are effectively already offline. However, the RTBH route can prevent other customers or services from being caught in the "blast radius" of the attack directed at the customer. That is can also cause the attack to end earlier. When attackers flood a target with traffic in order to overwhelm the target, some small amount of return traffic from the victim may be received by the attacker. This lets the attack know that the victim is "still alive", and so the attack continues. With an RTBH route in place, the destination prefix is completely unreachable, and thus the attack has been "successful" (in that the target is now unreachable), and the attackers stop their attack.

Another use case for RTBH is for protecting prefixes which should be present in the routing table (i.e., in order to prevent another network from announcing those prefixes and hijacking traffic towards them), but should not be reachable (e.g., internal infrastructure prefixes).

RTBH routes are implemented by originating a route into BGP (a route received from another i/e-BGP peer, redistributing a static route, etc.) and adding a community to that route as it is advertised to BGP peers. Receiving BGP peers match on the community and force the next-hop of the received prefix to be a special IP address that is "null routed" (meaning, an IP address which points to a special interface, which drops all packets sent to that interface).

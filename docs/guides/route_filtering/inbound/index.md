# Motivation

A *raw* BGP full feed (the so-called "global routing table") contains a lot of junk you do not want in your routers. In the best case, it contains prefixes to non-routable networks; in the worst case, it can break your internal routing.

There are a number of measures to filter a full BGP feed which will be explained in the following sections.

In general, we have three sources of information to fill your BGP table:

- the raw input you receive from your peers
- one or more *block lists* where you define what you not want from that specific peer or from all peers
- an *allow list* or whitelist, where you define what you allow from that peer


Job Snijders defined that at
[RIPE77](https://ripe77.ripe.net/presentations/59-RIPE77_Snijders_Routing_Policy_Architecture.pdf) as intersecting sets.

![three circles](protect_your_bgp_session_001.png)

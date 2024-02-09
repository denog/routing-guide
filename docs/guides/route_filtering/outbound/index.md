# Motivation

When announcing prefixes to the public Internet you have to make sure to filter your announcements to your peers and transits. There are several best practices that are described separately in this chapter.

The global BGP table is getting bigger and bigger every day. This needs more and more RAM on BGP routers in the DFZ. Please make sure to aggregate your prefixes as much as possible. It is sometimes useful to announce some more specific prefixes for traffic engineering purposes, but please limit the scope of more specifics if possible and do not announce more specifics that are not required.

Please make sure to limit your announcements and do not be a transit provider between your peers and upstreams.

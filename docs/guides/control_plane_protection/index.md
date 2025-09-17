# Motivation

There are several reasons why control plane protection is needed for hosts running network protocols:

* Resource Protection: it is trivial to overwhelm a host with enough disingenuous request that it cannot process genuine requests (a Denial of Service attack). The amount of data received and process by the control plane, and from whom, can be restricted to protect the limited computing resources.
* Protection of Forwarding Information: only devices and users which are authorised to read and edit forwarding information should be able to do this. Access to forwarding protocols can be restricted to authorised persons/devices/applications to prevent forwarding information from leaking or being manipulated.
* Protocol Security: many software implementations of networking protocols contain both known and unknown security vulnerabilities. Limiting access to the networking protocols can reduce the likelihood of a successful attack against the forwarding protocol.

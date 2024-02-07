# Protect your BGP session

## Motivation

The idea of these measures is to protect your TCP-based BGP sessions against attacks. Keep in mind, these TCP sessions are long-living (speaking of weeks and months), so an attacker can take its time to try to destroy a BGP session by sending crafted packets.

## MD5 session password

The easiest countermeasure against TCP based attacks on BGP sessions is to use  MD5 protection as described in 
[RFC2385](https://www.rfc-editor.org/rfc/rfc2385.html).
When implementing this, keep in mind to also implement some key (password) handling procedures (just imagine your router has to be replaced and you have to re-create all eBGP configurations).

Example for setting an MD5 password:

=== "Cisco IOS"
    ```
    router bgp 64500
    ...
    neighbor 198.51.100.1 password mysecretpassword
    ```

=== "Mikrotik"
    ```
    add name=AS64496 remote-as=64496 \
        remote-address=198.51.100.1 tcp-md5-key=mysecretpassword
    ```

## TCP Authentication Option

MD5, which is widely used, is considered to be insecure and deprecated. To replace it, 
[RFC5925](https://www.rfc-editor.org/rfc/rfc5925.html)
defines a mechanism called *TCP Authentication Option*, please read the RFC for details. In short, it uses stronger codes to protect your session.

Unfortunately this is not widely implemented.

## TTL Security

Instead of using a password, relying on the *TTL* value of incoming TCP packets is easier to handle and to implement. 

[RFC5082](https://www.rfc-editor.org/rfc/rfc5082) describes, how setting the TTL value of packets when sending to 255, and checking that value when receiving, makes it an impossible-to-spoof security measure.

As the TTL is decreased by every hop, when you receive a packet with TTL 255, it *must* have been sent by a directly adjacent node.

This feature must be set on both ends to work - if you set it on one end only, one side sends IP packets with a TTL of 1, and the other with a TTL of 255, and a session cannot be established.

Configuration examples:

=== "Cisco IOS"
    On Cisco IOS you configure how many hops your neighbor is away:
    ```
    router bgp 64500
    ...
    neighbor 198.51.100.1 ttl-security hops 1
    ```
=== "Mikrotik"
    On Mikrotik, you do not configure how many maximum hops a peer can be away, but the TTL value, which is 255 for directly adjacent peers (this is also the default value):
    ```
    add in-filter=upstream-in name=AS64496 out-filter=upstream-out \
        remote-address=198.51.100.1 remote-as=64496 ttl=255
    ```

# Protect your BGP session

## Motivation

The idea of these measures is to protect your TCP-based BGP sessions against attacks. Keep in mind, these TCP sessions are long-living (speaking of weeks and months), so an attacker can take its time to try to destroy a BGP session by sending crafted packets.

## Authentication

### MD5 session password

The easiest countermeasure against TCP based attacks on BGP sessions is to use  MD5 protection as described in
[RFC2385](https://www.rfc-editor.org/rfc/rfc2385.html).
When implementing this, keep in mind to also implement some key (password) handling procedures (just imagine your router has to be replaced and you have to re-create all eBGP configurations).

Example for setting an MD5 password:

=== "Cisco IOS / FRRouting"
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

=== "Juniper"
    ```
    set protocols bgp group <GROUPNAME> neighbor 198.51.100.1 authentication-key "mysecretpassword"
    ```

=== "RtBrick RBFS"
    ```
    set instance <INSTANCE> tcp authentication <AUTHENTICATION-ID> type MD5
    set instance <INSTANCE> tcp authentication <AUTHENTICATION-ID> key1-id 1
    set instance <INSTANCE> tcp authentication <AUTHENTICATION-ID> key1-plain-text mysecretpassword
    set instance <INSTANCE> protocol bgp peer ipv4 <PEER> <SOURCE> authentication-id <AUTHENTICATION-ID>
    ```

### Keyring

Another method is to use keyrings or key-chains. A common problem is that replacing a password in a protected session leads to a restart of the whole session.
Using keyrings or key-chains addresses this problem in a way that a key (or password) is valid until a new password with a defined start-time is specified.
This new key will be negiotiated upfront and becomes active at the start-time.

=== "Juniper"
   ```
   set security authentication-key-chains key-chain <KEY-CHAIN-NAME> description "key chain for BGP"
   set security authentication-key-chains key-chain <KEY-CHAIN-NAME> key 1 secret mysecretpassword
   set security authentication-key-chains key-chain <KEY-CHAIN-NAME> key 1 start-time "2025-01-01.09:00:00 +0200"

   set protocols bgp group <GROUPNAME> authentication-algorithm hmac-sha-1-96
   set protocols bgp group <GROUPNAME> authentication-key-chain <KEY-CHAIN-NAME>
   ```

### TCP Authentication Option

MD5, which is widely used, is considered to be insecure and deprecated. To replace it,
[RFC5925](https://www.rfc-editor.org/rfc/rfc5925.html)
defines a mechanism called *TCP Authentication Option*, please read the RFC for details. In short, it uses stronger codes to protect your session.

Unfortunately this is not widely implemented.

=== "Juniper"
    ```
    set security authentication-key-chains key-chain <KEY-CHAIN-NAME> description "key chain for BGP"
    set security authentication-key-chains key-chain <KEY-CHAIN-NAME> key 1 secret mysecretpassword
    set security authentication-key-chains key-chain <KEY-CHAIN-NAME> key 1 start-time "2025-01-01.09:00:00 +0200"
    set security authentication-key-chains key-chain <KEY-CHAIN-NAME> key 1 algorithm ao
    set security authentication-key-chains key-chain <KEY-CHAIN-NAME> key 1 ao-attribute send-id 1
    set security authentication-key-chains key-chain <KEY-CHAIN-NAME> key 1 ao-attribute recv-id 1
    set security authentication-key-chains key-chain <KEY-CHAIN-NAME> key 1 ao-attribute tcp-ao-option enabled
    set security authentication-key-chains key-chain <KEY-CHAIN-NAME> key 1 ao-attribute cryptographic-algorithm aes-128-cmac-96
    set protocols bgp group <GROUPNAME> authentication-algorithm ao
    set protocols bgp group <GROUPNAME> authentication-key-chain <KEY-CHAIN-NAME>
    ```
=== "RtBrick RBFS"
    ```
    set instance <INSTANCE> tcp authentication <AUTHENTICATION-ID> type AES-128-CMAC-96
    set instance <INSTANCE> tcp authentication <AUTHENTICATION-ID> key1-id 1
    set instance <INSTANCE> tcp authentication <AUTHENTICATION-ID> key1-plain-text mysecretpassword
    set instance <INSTANCE> protocol bgp peer ipv4 <PEER> <SOURCE> authentication-id <AUTHENTICATION-ID>
    ```

## TTL Security

Instead of using a password, relying on the *TTL* value of incoming TCP packets is easier to handle and to implement.
 
[RFC5082](https://www.rfc-editor.org/rfc/rfc5082) describes, how setting the TTL value of packets when sending to 255, and checking that value when receiving, makes it an impossible-to-spoof security measure.

As the TTL is decreased by every hop, when you receive a packet with TTL 255, it *must* have been sent by a directly adjacent node.

This feature must be set on both ends to work - if you set it on one end only, one side sends IP packets with a TTL of 1, and the other with a TTL of 255, and a session cannot be established.

Configuration examples:

=== "Cisco IOS classic / IOS XE / FRRouting"
    On Cisco IOS or FRRouting you configure how many hops your neighbor is away:
    ```
    router bgp 64500
    ...
    neighbor 198.51.100.1 ttl-security hops 1
    ```
=== "Cisco IOS XR"
    On Cisco IOS XR you just configure ttl-security without an hop parameter:
    ```
    router bgp 64500
    ...
    neighbor 198.51.100.1 ttl-security
    ```
=== "Mikrotik"
    On Mikrotik, you do not configure how many maximum hops a peer can be away, but the TTL value, which is 255 for directly adjacent peers (this is also the default value):
    ```
    add in-filter=upstream-in name=AS64496 out-filter=upstream-out \
        remote-address=198.51.100.1 remote-as=64496 ttl=255
    ```
=== "Juniper"
    On Junos you configure how many hops your neighbors in a group are away:
    ```
    set protocols bgp group <GROUPNAME> ttl 255
    ```
    On Junos you configure how many hops a specific neighbor in a group is away:
    ```
    set protocols bgp group <GROUPNAME> neighbor 198.51.100.1 ttl 255
    ```
=== "RtBrick RBFS"
    TTL security is activated with the ttl-security command on a single-hop BGP session, which sets the IPv4 TTL value in packets to 255. For multihop BGP sessions, TTL security is also enabled with ttl-security, but you must additionally configure the ttl-limit to match the expected IPv4 TTL value.
    ```
    set instance <INSTANCE> protocol bgp peer-group <GROUPNAME> ttl-security enable
    ```

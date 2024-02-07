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

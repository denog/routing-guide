---
tags:
  - Cisco missing
  - Huawei VRP missing
  - OpenBGPD missing
  - VyOS missing
---

# MD5 session password

The easiest countermeasure against TCP based attacks on BGP sessions is to use MD5 protection as described in
[RFC2385](https://www.rfc-editor.org/rfc/rfc2385.html).
When implementing this, keep in mind to also implement some key (password) handling procedures (just imagine your router has to be replaced and you have to re-create all eBGP configurations).

Example for setting an MD5 password:

=== "Arista EOS"
    ```
    router bgp 64500
       neighbor 198.51.100.1 password mysecretpassword
    ```

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

=== "Bird"
    ```
    protocol bgp name4 {
      authentication md5;
      password "mysecretpassword";
    }

=== "Nokia SR OS classic CLI"
    ```
    /configure router "Base" bgp
        group "as64500"
            [...]
            authentication-key "mysecretpassword"
            [...]
        exit
    ```

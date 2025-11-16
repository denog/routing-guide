---
tags:
  - Arista missing
  - Cisco missing
  - Cisco IOS XR missing
  - FRR missing
  - Huawei VRP missing
  - Mikrotik missing
  - Nokia SR OS missing
  - OpenBGPD missing
  - VyOS missing
---

# TCP Authentication Option

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

=== "BIRD 2/3"
    Supported since Bird 2.17 and 3.1.0 on Linux. On BSD TCP-AO is currently not supported.

    See original post in [mailing list](https://bird.network.cz/pipermail/bird-users/2025-April/018156.html)
    or the [documentation](https://bird.nic.cz/doc/bird-3.1.4.html) for more details.

    ```
    protocol bgp {
      authentication ao;
      keys {
        key {
          id 0;
          secret "hello321";
          algorithm hmac sha256;
          preferred;
        };
        key {
          send id 2;
          recv id 1;
          secret "bye123";
          algorithm cmac aes128;
        };
      };
    }
    ```
    Note that TCP-AO authentication is not supported on dynamic BGP sessions.

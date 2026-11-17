---
tags:
  - BIRD missing
  - Cisco missing
  - Cisco IOS XR missing
  - FRR missing
  - Huawei VRP missing
  - Mikrotik missing
  - Nokia SR OS missing
  - OpenBGPD missing
  - VyOS missing
  - RtBrick RBFS missing
---

# Keyring

Another method is to use keyrings or key-chains. A common problem is that replacing a password in a protected session leads to a restart of the whole session.
Using keyrings or key-chains addresses this problem in a way that a key (or password) is valid until a new password with a defined start-time is specified.
This new key will be negotiated upfront and becomes active at the start-time.

=== "Juniper"
   ```
   set security authentication-key-chains key-chain <KEY-CHAIN-NAME> description "key chain for BGP"
   set security authentication-key-chains key-chain <KEY-CHAIN-NAME> key 1 secret mysecretpassword
   set security authentication-key-chains key-chain <KEY-CHAIN-NAME> key 1 start-time "2025-01-01.09:00:00 +0200"

   set protocols bgp group <GROUPNAME> authentication-algorithm hmac-sha-1-96
   set protocols bgp group <GROUPNAME> authentication-key-chain <KEY-CHAIN-NAME>
   ```

=== "Arista EOS"
    On EOS, keys with lifetimes are configured in a shared secret profile, which is used for TCP-AO (see [TCP Authentication Option](tcp-authentication-option.md)). Each key has one lifetime (start and end time in UTC, or `infinite`); TCP-AO does not support separate receive and transmit lifetimes. EOS sends with the key whose lifetime began most recently and accepts all keys that are currently valid. In this example key 2 takes over on 2026-01-01; the lifetimes of both keys overlap by one day, so both routers accept both keys while they change over.
    ```
    management security
       session shared-secret profile bgp-keyring
          secret 1 0 oldsecretpassword 2025-01-01 00:00:00 2026-01-02 00:00:00
          secret 2 0 newsecretpassword 2026-01-01 00:00:00 infinite
    !
    router bgp 64500
       neighbor 198.51.100.1 password shared-secret profile bgp-keyring algorithm aes-128-cmac-96
    ```

    See the Arista TOI [BGP TCP Authentication Option (TCP-AO)](https://www.arista.com/en/support/toi/eos-4-28-2f/16087-bgp-tcp-authentication-option-tcp-ao) (Arista account required, key rotation) and the EOS manual: [Session Management Commands](https://www.arista.com/en/um-eos/eos-session-management-commands) (shared secret profiles).

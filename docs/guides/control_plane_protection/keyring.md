---
tags:
  - Arista missing
  - BIRD missing
  - Cisco missing
  - Cisco IOS XR missing
  - FRR missing
  - Huawei VRP missing
  - Mikrotik missing
  - Nokia SR OS missing
  - OpenBGPD missing
  - VyOS missing
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

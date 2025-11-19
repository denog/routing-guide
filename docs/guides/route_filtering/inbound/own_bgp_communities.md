---
tags:
  - Arista missing
  - BIRD missing
  - Cisco missing
  - FRR missing
  - Huawei VRP missing
  - Mikrotik missing
  - Nokia SR OS missing
  - OpenBGPD missing
  - VyOS missing
---

# Own communities

## Purpose
A BGP community is bit of “extra information” that you can add to one of more prefixes which is advertised to BGP neighbors. This extra information can be used for things like traffic engineering or dynamic routing policies.
There are different types of communities (Standard, Extended, and Large). Not every manufacturer supports all types.

It is important to filter your own communities from the incoming external BGP Peer.

## Description
Your own communities should be stored in lists or sets and then used in policy for external BGP peers.

## Format
Depends on whether you operate a 16 oder 32-Bit ASN the format differs:

### Standard Communities:
32-Bit split in two 16-Bit values. If you already operate a 32-Bit ASN you can't use these.
    ```
    <YOUR_ASN>:[0-65535]
    ```

### Extended Communities:
64-Bit split into 3 parts:
    ```
    <purpose/type>:<YOUR_ASN>:<value>
    ```
Depends on the size of your ASN (16/32 Bit). Not very commonly used, better use the large community approach.

### Large Communities:
96-Bit split into 3 parts:
    ```
    <YOUR_ASN>:<value1>:<value2>
    ```

## Standard Communities
See https://routing.denog.de/guides/route_filtering/outbound/well_known_communities_traffic_engineering/

## Configuration Examples

=== "Cisco IOS XR"
    Using an *my-own* communitys-set you can add more communities to it that you want. Since these are your own complete communities, you can work with wildcards.
    ```
    community-set my-own-communities
      <YOUR OWN AS NUMBER>:*
    end-set
    !
    large-community-set my-own-large-communities
      <YOUR OWN AS NUMBER>:*:*
    end-set
    ```

    If you want to drop the prefix.
    ```
    route-policy drop-my-own-communities
      if community matches-any my-own-communities or community matches-any my-own-large-communities then
        drop
      else
        pass
      endif
    end-policy
    ```

    If you want to delete the communities and accept the prefix.
    ```
    route-policy clean-my-own-communities
      if community matches-any my-own-communities or community matches-any my-own-large-communities then
        delete community in my-own-communities
        delete large-community in my-own-large-communities
      endif
    end-policy
    ```
=== "Juniper JunOS"
Standard community
    ```
    set policy-options community CUSTOMER members 65534:100
    ```

Large community
    ```
    set policy-options community CUSTOMER members large:4200000001:0:1002
    set policy-options community TEST members large:64500:0:100
    set policy-options community UPSTREAM members large:65534:0:200
    ```

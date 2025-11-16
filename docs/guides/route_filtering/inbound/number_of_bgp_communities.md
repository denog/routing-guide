---
tags:
  - BIRD missing
  - Huawei VRP missing
  - Mikrotik missing
  - Nokia SR OS missing
  - OpenBGPD missing
  - VyOS missing
---

# Number of BGP communities

## Purpose

BGP Communities can give a lot of information about a prefix, for example where your BGP peer learned the prefix. As BGP Communities also consume router memory it is suggested to delete the BGP communities if too many of them are attached to a prefix.

## Configuration

=== "Cisco IOS"
    In Cisco IOS it is not possible to only delete BGP Communities from a prefix when there are more than a specific number attached. You can filter prefixes with eg. >=100 BGP Communities, but then your router won't have a route to the filtered prefix if you do not have a default route.
    ```
    router bgp 64500
      bgp maxcommunity-limit 99
      bgp maxextcommunity-limit 99
    ```

    If you do not want to loose any routes because of too many attached BGP Communities you could also remove all BGP Communities from the prefixes coming from your peer.
    ```
    ip community-list expanded ALL-COMMUNITIES permit .*
    !
    route-map BGP_FILTER_IN permit 100
     set comm-list ALL-COMMUNITIES delete
     set extcomm-list ALL-COMMUNITIES delete
    !
    router bgp 64500
     neighbor 198.51.100.1 route-map BGP_FILTER_IN in
    ```

=== "Cisco IOS XR"
    In Cisco IOS XR it is not possible to only delete BGP Communities from a prefix when there are more than a specific number attached. You can filter prefixes with eg. >=100 BGP Communities, but then your router won't have a route to the filtered prefix if you do not have a default route.
    ```
    router bgp 64500
      bgp maxcommunity-limit 99
      bgp maxextcommunity-limit 99
    ```

    If you do not want to loose any routes because of too many attached BGP Communities you could also remove all BGP Communities from the prefixes coming from your peer.
    ```
    ip community-list expanded ALL-COMMUNITIES permit .*
    !
    route-map BGP_FILTER_IN permit 100
     set comm-list ALL-COMMUNITIES delete
     set extcomm-list ALL-COMMUNITIES delete
    !
    router bgp 64500
     neighbor 198.51.100.1 route-map BGP_FILTER_IN in
    ```

=== "Juniper JunOS"
    In this example all BGP Communities are removed from a prefix when >= 100 BGP Communities are attached.
    ```
    policy-options {
        community ALL-COMMUNITIES members [ *:* origin:*:* large:*:*:* ];
        policy-statement BGP_FILTER_IN {
          term delete-too-many-communities {
            from community-count 100 orhigher;
            then {
                community delete ALL-COMMUNITIES;
            }
        }
    }
    ```

=== "Arista EOS"
    In this example all BGP Communities are removed from a prefix when >= 100 BGP Communities are attached.
    ```
    route-map BGP_FILTER_IN permit 100
        match community instances >= 100
        set community none
    !
    ```

=== "BIRD 2/3"
    ```
    function strip_too_many_communities()
    {
      if ( ( bgp_community.len + bgp_ext_community.len + bgp_large_community.len ) >= 100 ) then {
        # optional logging
        # print "Error: too many communities: ", bgp_community.len, " ", bgp_ext_community.len, " ",bgp_large_community.len;
        bgp_community.empty;
        bgp_ext_community.empty;
        bgp_large_community.empty;
      }
    }
    protocol bgp neighbor_name {
        ipv4 {
            import filter {
                strip_too_many_communities();
                # other filters
                accept;
            };
        }
        ipv6 {
            import filter {
                strip_too_many_communities();
                # other filters
                accept;
            };
        }
    }
    ```

=== "FRRouting"
    In FRRouting you can match in route-maps for prefixes with "less or equal" number of communities.
    So for filtering out prefixes with "more than" number of communities needs a route-map trick.
    From the documentation it is unclear if this applies only to old communities or also to large or extended communities.
    ```
    route-map too-many-communities permit 100
        ! true if 99 or less communities attached
        match community-limit 99
        on-match goto 200
    ! communities are deleted if 100 or more
    route-map too-many-communities permit 150
        set community none
    ! we continue at 200 if 99 or less communities
    route-map too-many-communities permit 200
    ...
    ```

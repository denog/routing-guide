---
tags:
  - Arista missing
  - Cisco missing
  - Cisco IOS XR missing
  - FRR missing
  - Huawei VRP missing
  - Junos missing
  - Nokia SR OS missing
  - OpenBGPD missing
  - VyOS missing
  - RtBrick RBFS missing
---

# Tier 1 ASNs

As a Tier 2/3 Network, you may want to filter out routes that have traversed Tier 1 ASNs at IXPs or from customers, as you probably don't want to provide transit for Tier 1 Networks or accept transit for Tier 1 Networks from your customers.

!!! danger "Caution"

    You should only apply this filter on your customers and IXP peers, not on your upstream transit providers.

Be aware that you need to manually check the prefix list as you could peer with for instance Microsoft of other parties on the list. So you need to do a quick sanity check on the AS numbers to fit your need.

=== "BIRD 2/3"
    ```
    define TRANSIT_ASNS = [
      174,                  # Cogent
      701,                  # UUNET
      1299,                 # Telia
      2914,                 # NTT Ltd.
      3257,                 # GTT Backbone
      3320,                 # Deutsche Telekom AG (DTAG)
      3356,                 # Level3
      3491,                 # PCCW
      4134,                 # Chinanet
      5511,                 # Orange opentransit
      6453,                 # Tata Communications
      6461,                 # Zayo Bandwidth
      6762,                 # Seabone / Telecom Italia
      6830,                 # Liberty Global
      7018                  # AT&T
    ];

    function reject_transit_paths()
    {
      if (bgp_path ~ TRANSIT_ASNS) then {
        # optional logging
        # print "Reject: Transit ASNs found on IXP Peering: ", net, " ", bgp_path;
        reject;
      }
    }

    protocol bgp example_ix_rs {
      ipv4 {
        import filter {
          reject_transit_paths();
          # other filters
          accept;
        };
      }
      ipv6 {
        import filter {
          reject_transit_paths();
          # other filters
          accept;
        };
      }
    }
    ```

=== "MikroTik"
    Source: [NLNOG](https://bgpfilterguide.nlnog.net/guides/no_transit_leaks/#routeros-v7)
    ```
    /routing/filter/num-list
    add list=TRANSIT_ASNS range=174 comment="Cogent" 
    add list=TRANSIT_ASNS range=701 comment="UUNET" 
    add list=TRANSIT_ASNS range=1299 comment="Telia" 
    add list=TRANSIT_ASNS range=2914 comment="NTT Ltd." 
    add list=TRANSIT_ASNS range=3257 comment="GTT Backbone" 
    add list=TRANSIT_ASNS range=3320 comment="Deutsche Telekom AG (DTAG)" 
    add list=TRANSIT_ASNS range=3356 comment="Level3" 
    add list=TRANSIT_ASNS range=3491 comment="PCCW" 
    add list=TRANSIT_ASNS range=4134 comment="Chinanet" 
    add list=TRANSIT_ASNS range=5511 comment="Orange opentransit" 
    add list=TRANSIT_ASNS range=6453 comment="Tata Communications" 
    add list=TRANSIT_ASNS range=6461 comment="Zayo Bandwidth" 
    add list=TRANSIT_ASNS range=6762 comment="Seabone / Telecom Italia" 
    add list=TRANSIT_ASNS range=6830 comment="Liberty Global"
    add list=TRANSIT_ASNS range=7018 comment="AT&T"  
    
    /routing/filter/rule
    add chain=reject_transit rule="if (bgp-as-path [[:TRANSIT_ASNS:]]){ reject }"

    add chain=CUSTOMER-IN rule="jump reject_transit"
    add chain=PEERING-OUT rule="jump reject_transit"
    ```

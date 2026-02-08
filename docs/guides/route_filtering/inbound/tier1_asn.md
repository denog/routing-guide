---
tags:
  - Arista missing
  - Cisco missing
  - Cisco IOS XR missing
  - FRR missing
  - Huawei VRP missing
  - Junos missing
  - Mikrotik missing
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
    int set transit_asns;
    {
      transit_asns = TRANSIT_ASNS;
      if (bgp_path ~ transit_asns) then {
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

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
# Set own informational communities
Informational communities propagate information about the prefixes and enable you (and others) to get insights or filter on the basis of this information. Common attributes include origin type, country/region and IXP.

=== "BIRD 2/3"
Add a community to routes imported from one session
    ```
    protocol bgp customer {
      ipv4 {
        import filter {
          bgp_community.add((<your ASN>,220));
        }
      }
      ipv6 {
        import filter {
          bgp_community.add((<your ASN>,220));
        }
      }
    }
    ```

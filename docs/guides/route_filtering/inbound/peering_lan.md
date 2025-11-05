---
tags:
  - Arista missing
  - Huawei VRP missing
  - Junos missing
  - Mikrotik missing
  - OpenBGPD missing
  - VyOS missing
---

# Peering LANs

When you are connected to an Internet Exchange Point, you have an interface configured
with an IP address and netmask of that IXP[^1]. If, now, someone else announces the same
network (or worse: a more specific sub-network) via BGP and you accept this announcement,
your router might prefer this announcement over the one of its own interface (especially if
the announcement is more specific).

So it is strongly recommended that you block BGP announcements of all IXP LANs you are
connected to.

If you are connected to many IXPs, you might want to automate this.
[PeeringDB](https://peeringdb.com) has a list of all IXP Lans. You need some software to extract this
and convert it to your router configuration.

## Configuration Examples

=== "Cisco IOS / FRRouting"
    ```
    # DE-CIX Frankfurt
    ip prefix-list ipv4-ixplans permit 80.81.192.0/21 le 32
    ...
    # DE-CIX Frankfurt
    ipv6 prefix-list ipv6-ixplans permit 2001:7f8::/64 le 128
    ...
    route-map prefixes-in deny 10
      match ip address prefix-list ipv4-ixplans
      match ipv6 address prefix-list ipv6-ixplans
    ```

=== "Cisco IOS XR"
    Define lists with peering networks:
    ```
    prefix-set peering-lan-ipv4-networks
      # DE-CIX Frankfurt
      80.81.192.0/21 le 32,
      ...
    end-set
    !
    prefix-set peering-lan-ipv6-networks
      # DE-CIX Frankfurt
      2001:7f8::/64 le 128,
      ...
    end-set
    ```

    Define policy to drop the prefix:
    ```
    route-policy drop-peering-lan-ipv4-networks
      if destination in peering-lan-ipv4-networks then
        drop
      else
        pass
      endif
    end-policy
    !
    route-policy drop-peering-lan-ipv6-networks
      if destination in peering-lan-ipv6-networks then
        drop
      else
        pass
      endif
    end-policy
    ```
=== "Bird2"
    ```
    define IXP_PREFIXES4 = [
      185.1.155.0/24 # LocIX DUS
    ];
    define IXP_PREFIXES6 = [
      2a0c:b641:701::/64 # LocIX DUS
    ];
    function reject_ixp_prefixes4()
    prefix set ixp_prefixes4;
    {
      ixp_prefixes4 = IXP_PREFIXES4;
      if (net ~ ixp_prefixes4) then {
        # optional logging
        # print "Reject: IXP Prefix detected: ", net, " ", bgp_path;
        reject;
      }
    }
    function reject_ixp_prefixes6()
    prefix set ixp_prefixes6;
    {
      ixp_prefixes6 = IXP_PREFIXES6;
      if (net ~ ixp_prefixes6) then {
        # optional logging
        # print "Reject: IXP Prefix detected: ", net, " ", bgp_path;
        reject;
      }
    }
    protocol bgp neighbor_name {
      ipv4 {
        import filter {
          reject_ixp_prefixes4();
          # other filters
          accept;
        };
      }
      ipv6 {
        import filter {
          reject_ixp_prefixes6();
          # other filters
          accept;
        };
      }
    }
    ```

=== "Nokia SR OS classic CLI"
    ```
    /configure router "Base" policy-options
    begin
            prefix-list "v4-ixplans"
                prefix 80.81.192.0/21 longer
            exit
            prefix-list "v6-ixplans"
                prefix 2001:7f8::/64 longer
            exit
            policy-statement "inbound"
                description "inbound peering policy"
                [...]
                entry 31
                    from
                        prefix-list "v4-ixplans"
                    exit
                    action drop
                    exit
                exit
                entry 41
                    from
                        prefix-list "v6-ixplans"
                    exit
                    action drop
                    exit
                exit
                [...]
            exit
    commit
    ```

[^1]: Internet eXchange Point

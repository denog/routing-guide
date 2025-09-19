---
tags:
  - Arista missing
  - Cisco IOS XR missing
  - Huawei VRP missing
  - Mikrotik missing
  - Nokia SR OS missing
  - OpenBGPD missing
  - VyOS missing
---


# Default Route

## Purpose

Per definition a *default route* means "route all packets this way unless there is a specific route for the destination IP address". A default route is expressed in IPv4 as 0.0.0.0/0 and as ::/0 in IPv6.

It is completely legitimate if a transit provider announces default routes to their customers. In case the customers router has limited memory for the routing table, it can simply *only* accept the default route, blocking all other more specific routes.

On the other hand, if you want the full routing table, you should not accept any default route from your transit providers. You must never accept a default route from any non-transit-provider neighbor.

## Configuration

=== "Cisco IOS / FRRouting"
    ```
    ip prefix-list default-route-v4 permit 0.0.0.0/0
    ipv6 prefix-list default-route-v6 permit ::/0
    ```

    Route-Map statement for allowing *only* default routes in:
    ```
    route-map prefixes-in permit 10
      match ip address prefix-list default-route-v4
      match ipv6 address prefix-list default-route-v6
    ```

    Route-Map statement for *not* allowing default routes in, but allowing all other prefixes:
    ```
    route-map prefixes-in deny 10
      match ip address prefix-list default-route-v4
      match ipv6 address prefix-list default-route-v6
    route-map prefixes-in allow 20
    ```

=== "Cisco IOS XR"
    Build prefix lists with default route entries
    ```
    prefix-set default-ipv4
      0.0.0.0/0
    end-set

    prefix-set default-ipv6
      ::/0
    end-set
    ```

    Build filters with the default route lists to *drop* default route
    ```
    route-policy reject-default-ipv4
      if destination in default-ipv4 then
        drop
      else
        pass
      endif
    end-policy

    route-policy reject-default-ipv6
      if destination in default-ipv6 then
        drop
      else
        pass
      endif
    end-policy
    ```

    Build filters with the default route lists to *allow* default route
    ```
    route-policy accept-default-ipv4
      if destination in default-ipv4 then
        pass
      else
        drop
      endif
    end-policy

    route-policy accept-default-ipv6
      if destination in default-ipv6 then
        pass
      else
        drop
      endif
    end-policy
    ```
    
=== "Bird2"
    ```
    function reject_default_route4()
    {
      if net = 0.0.0.0/0 then {
        # optional logging:
        # print "Reject: Defaultroute: ", net, " ", bgp_path;
        reject;
      }
    }
    function reject_default_route6()
    {
      if net = ::/0 then {
        # optional logging:
        # print "Reject: Defaultroute: ", net, " ", bgp_path;
        reject;
      }
    }
    filter import_ipv4 {
      reject_default_route4();
      ...
      accept;
    }
    filter import_ipv6 {
      reject_default_route6();
      ...
      accept;
    }
    ```

=== "Juniper JunOS"
     ```
     set policy-options policy-statement MY_INPUT_FILTER term DEFAULT-ROUTE from family inet
     set policy-options policy-statement MY_INPUT_FILTER term DEFAULT-ROUTE from route-filter 0.0.0.0/0 exact
     set policy-options policy-statement MY_INPUT_FILTER term DEFAULT-ROUTE then trace
     set policy-options policy-statement MY_INPUT_FILTER term DEFAULT-ROUTE then reject
     
     set policy-options policy-statement MY_INPUT_FILTER term DEFAULT-ROUTE-V6 from family inet6
     set policy-options policy-statement MY_INPUT_FILTER term DEFAULT-ROUTE-V6 from route-filter ::/0 exact
     set policy-options policy-statement MY_INPUT_FILTER term DEFAULT-ROUTE-V6 then trace
     set policy-options policy-statement MY_INPUT_FILTER term DEFAULT-ROUTE-V6 then reject
     ```

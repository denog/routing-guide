# Default Route

## Purpose

Per definition a *default route* means "route all packets this way unless there is a specific route for the destination IP address". A default route is expressed in IPv4 as 0.0.0.0/0 and as ::/0 in IPv6.

It is completely legitimate if a transit provider announces default routes to their customers. In case the customers router has limited memory for the routing table, it can simply *only* accept the default route, blocking all other more specific routes.

On the other hand, if you want the full routing table, you should not accept any default route from your transit providers. You must never accept a default route from any non-transit-provider neighbor.

## Configuration

=== "Cisco IOS"
    ```
    ip prefix-list default-route permit 0.0.0.0/0
    ipv6 prefix-list default-route permit ::/0
    ```

    Route-Map statement for allowing *only* default routes in:
    ```
    route-map prefixes-in permit 10
      match ip address prefix-list default-route
      match ipv6 address prefix-list default-route
    ```

    Route-Map statement for *not* allowing default routes in:
    ```
    route-map prefixes-in deny 10
      match ip address prefix-list default-route
      match ipv6 address prefix-list default-route
    ````

# Peering LANs

When you are connected to an Internet Exchange Point, you have an interface configured
with an IP address and netmask of that IXP. If, now, someone else announces the same
network (or worse: a more specific sub-network) via BGP and you accept this announcement,
your router might prefer this announcement over the one of its own interface (especially if
the announcement is more specific).

So it is strongly recommended that you block BGP announcements of all IXP LANs you are
connected to.

If you are connected to many IXPs, you might want to automate this.
[PeeringDB](https://peeringdb.com) has a list of all IXP Lans, you need some software to extract this
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

# Maximum Prefix (Outbound)

This is a quite new feature of some BGP implementations. Here we do not protect our own network, we protect the our neighbors from us accidentally flooding too many IP prefixes towards them.

Of course this also protects our own network, because if our neighbor accepted these prefixes and would send us all the traffic for them, we would drown in packets.

Configuration examples:

=== "FRRouting"
    This limits the number of prefixes sent to 1000, please note that the session is *not* shut down after the number is exceeded. Which prefixed are sent you cannot influence, this limits the usefulness of this feature.
    ```
    router bgp 64500
        address-family ipv4 unicast
            neighbor 198.51.100.1 maximum-prefix-out 1000
    ```

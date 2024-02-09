# Prefix length filtering

Normally (there are exceptions), prefixes are announced in certain minimum and maximum lengths in the global Internet routing table. Currently, they are:

- **IPv4, minimum size** is /24. No smaller networks should be announced. Possible exceptions: \Gls{blackholing}, or an announcement in combination with a NO-EXPORT community set from a customer to his upstream.
- **IPv6, minimum size** is /48. Same exceptions as within IPv4.
- **IPv4, maximum size** is a /8. Larger networks are not announced. Depending on your set-up, you might want to accept the default-route 0.0.0.0/0 from your upstream providers.
- **IPv6, maximum size** is currently a /16 (please take this with a grain of salt, this number might already have changed). The remark about accepting a default-route ::0 is the same.

Configuration examples:

=== "Cisco IOS"
    Using an *unwanted* prefix-list you can add  more prefixes to it that you not want. This shortens your configuration but might also decrease readability.
    ```
    ip prefix-list ipv4-unwanted permit 0.0.0.0/0 ge 25 le 32
    ip prefix-list ipv4-unwanted permit 0.0.0.0/0 ge 1 le 7
    !
    route-map upstream-in-v4 deny 50
        match ip address prefix-list ipv4-unwanted
    !
    ipv6 prefix-list ipv6-unwanted permit ::/0 ge 49 le 128
    ipv6 prefix-list ipv6-unwanted permit ::/0 ge 0 le 16
    !
    route-map upstream-in-v6 deny 45
        match ipv6 address prefix-list ipv6-unwanted
    !
    router bgp 64500
        neighbor 198.51.100.1 route-map upstream-in-v4 in
        !
        neighbor 2001:db8::1 route-map upstream-in-v6 in
        !

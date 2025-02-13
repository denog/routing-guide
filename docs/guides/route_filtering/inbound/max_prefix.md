# Maximum Prefix

This parameter is configured for each eBGP session and is the simplest and easiest security measure you can use. Unfortunately, many stop here. Please do not.

Maximum prefix defines a limit for the number of prefixes you accept from an eBGP peer. If the peer sends more, the eBGP session is shut down. Usually, routers keep the session down for some time, then it is automatically re-enabled. If the peer still sends more prefixes than allowed, it is shut down again.

For selecting this limit, the following rules of thumb can be used:

- For sessions to *peers*, the limit should be less than the total number of prefixes in the Internet. Set it at least to ten times the normal number of prefixes your peer announces. This protects you against your peer announcing the full routing table to you, but still allows normal growth. Check and adjust from time to time (or even better: Automate this).
- For sessions to your *upstream* provider, you must, of course, set the limit higher than the total number of prefixes in the Internet. It must be high enough to accommodate normal growth, so either set it *very* high or check and adjust it regularly. Otherwise, there can be surprising session shutdowns. This protects you against gross misconfigurations at your upstream provider (like sending you a lot of de-aggregated prefixes).

If you want to automate this, at [PeeringDB](https://peeringdb.com) networks can publish suggested values for maximum prefix.

Also, keep in mind that maximum prefix for IPv4 and IPv6 are two different values.

Configuration examples:

=== "Cisco IOS"
    This shuts down the session when 1000 prefixes are received and issues a warning at 95% (950 prefixes):
    ```
    router bgp 64500
    ...
    neighbor 198.51.100.1 maximum-prefix 1000 95
    ```

=== "Cisco IOS XR"
    This shuts down the session when 1000 prefixes are received, issues a warning at 95% (950 prefixes) and restarts the session after 60 minutes:
    ```
    router bgp 64500
        neighbor 198.51.100.1
        address-family ipv4 unicast
            maximum-prefix 1000 95 restart 60
    ```
=== "FRRouting"
    This shuts down the session when 1000 prefixes are received, issues a warning at 95% (950 prefixes) and restarts the session after 60 minutes:
    ```
    router bgp 64500
        address-family ipv4 unicast
            neighbor 198.51.100.1 maximum-prefix 1000 95 restart 60
    ```

=== "Mikrotik"
    This shuts down your session when 1000 prefixes are received and restarts it after one hour:
    ```
    add name=AS64496 remote-as=64496 \
        remote-address=198.51.100.1 max-prefix-limig=1000 max-prefix-restart-time=1h
    ```

=== "Bird2"
    ```
    protocol bgp neighbor_name {
      ipv4 {
         import limit 1000 restart;
      }
      ipv6 {
         import limit 500 restart;
      }
    }
    ```

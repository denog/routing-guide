---
tags:
  - Huawei VRP missing
  - OpenBGPD missing
  - RtBrick RBFS missing
---

# Maximum Prefix

This parameter is configured for each eBGP session and is the simplest security measure one can use. Unfortunately, many stop here. Please do not.

Maximum prefixes defines a limit for the number of prefixes you accept from an eBGP peer. If the peer sends more prefixes, the eBGP session can be shutdown or it can remain active but stop accepting new prefixes beyond the configured limit. If configured to shutdown the session when the configured limit is exceeded, most routers keep the session down for a period of time and then automatically re-establish the session after a delay timer has expired (in case the issue was only transient and the peer has reduced the number of prefixes they're advertising). If the peer still sends more prefixes than your configured limit, the session is automatically shutdown again. If the timer to reactivate the BGP session is too low, this results in the session continuously flapping, which is not good for network stability. Therefore some networks prefer to configure their devices not to automatically re-establish the session, but to require manual intervention.

For selecting this limit, the following rules of thumb can be used:

- For sessions to *peers*, the limit should be less than the total number of prefixes in the Internet. This protects you against your peer announcing the full routing table to you. The recommended values to uses are the peer's prefix limits published in their PeeringDB page. You may want to add a buffer to the published limits to allow for future growth from your peer, or check and adjust from time to time (or even better, automate this).
- For sessions to your *upstream* providers, you must of course set the limit higher than the total number of prefixes in the Internet. It must be high enough to accommodate normal growth, so either set it *very* high or check and adjust it regularly. Otherwise, there can be surprising session shutdowns. This protects you against gross misconfigurations from your upstream provider (like sending you a lot of de-aggregated prefixes).

If you want to automate this, networks can publish suggested values for maximum prefix limits at [PeeringDB](https://peeringdb.com).

Also, keep in mind that maximum prefix limits for IPv4 and IPv6 are two different values.

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
    For RouterOS v6 this shuts down your session when 1000 prefixes are received and restarts it after one hour:
    ```
    add name=AS64496 remote-as=64496 \
        remote-address=198.51.100.1 max-prefix-limit=1000 max-prefix-restart-time=1h
    ```

    On RouterOS v7 something like this should do:
    ```
    /routing/bgp/connection
    add instance=bgp-instance-1 name=HE local.role=ebgp \
        afi=ip input.limit-process-routes-ipv4=1000 remote.address=185.1.167.69 .as=6939
    add instance=bgp-instance-1 name=HE local.role=ebgp \
        afi=ipv6 input.limit-process-routes-ipv6=1000 remote.address=2001:7f8:f2:e1::6939:1 .as=6939
    ```
    The documentation however is a bit vague:
    
    > Try to limit the amount of received IPv4 routes to the specified number.
    > This number does not represent the exact number of routes going to be installed in the routing table by the peer.
    > BGP session "clear" command must be used to reset the flag if the limit is reached.

=== "BIRD 2/3"
    ```
    protocol bgp neighbor_name {
      ipv4 {
        import limit 1000 action restart;
      }
      ipv6 {
        import limit 500 action restart;
      }
    }
    ```

=== "Nokia SR OS classic CLI"
    ```
    /configure router "Base" bgp
            group "as64500"
                [...]
                prefix-limit ipv4 1000
                prefix-limit ipv6 500
                [...]
            exit
    ```

=== "Juniper JunOS"
    ```
    set protocols bgp group MY_NEIGHBOR_GROUP 198.51.100.1 family inet unicast accepted-prefix-limit maximum 10 drop-excess
    set protocols bgp group MY_NEIGHBOR_GROUP 2001:db8::1 family inet6 unicast accepted-prefix-limit maximum 5 drop-excess
    ```

=== "VyOS (>= 1.4)"

    VyOS has two modes (operational and configuration mode). Enter configuration mode with
    `configure` to make changes. Use `commit` to apply them and `save` to keep them after reboot.

    ```
    set protocols bgp neighbor 198.51.100.1 address-family ipv4-unicast maximum-prefix 1000
    ```

    It's not possible to configure a threshold value or adjust the action after limit is exceeded.

=== "Arista EOS legacy"
    This shuts down the session when 1000 prefixes are received and issues a warning at 95% (950 prefixes):
    ```
    router bgp 64500
    ...
    neighbor 198.51.100.1 maximum-routes 1000 warning-limit 95 percent
    ```

    This does not shutdown the session but stops accepting new prefixes beyond 1000 and issues a warning at 95% (950 prefixes):
    ```
    router bgp 64500
    ...
    neighbor 198.51.100.1 maximum-routes 1000 warning-limit 95 percent warning-only
    ```

=== "Arista EOS RCF"
    This shuts down the session when 1000 prefixes are received and issues a warning at 95% (950 prefixes):
    ```
    router bgp 64500
    ...
    neighbor 198.51.100.1 maximum-routes 1000 warning-limit 95 percent
    ```

    This does not shutdown the session but stops accepting new prefixes beyond 1000 and issues a warning at 95% (950 prefixes):
    ```
    router bgp 64500
    ...
    neighbor 198.51.100.1 maximum-routes 1000 warning-limit 95 percent warning-only
    ```

# Prefix length filtering

Normally (there are exceptions), prefixes are announced in certain minimum and maximum lengths in the global Internet routing table. Currently, they are:

- **IPv4, minimum size** is /24. No smaller networks should be announced. Possible exceptions: blackholing, or an announcement in combination with a *NO-EXPORT* community set, from a customer to his upstream.
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
    ```

=== "Cisco IOS XR"
    Use an *permitted* list and you can still customize the range. Please note that these areas are common on the public internet.
    ```
    # Define permitted IP prefixes
    prefix-set permitted-prefix-length-v4
        # Bigger than /8 or smaller than /24
        0.0.0.0/0 ge 8 le 24
    end-set
    prefix-set permitted-prefix-length-v6
        # Bigger than /16 or smaller than /48
        ::/0 ge 16 le 48
    end-set
    
    # If you want to implement it in separate filters, then like this policy:
    route-policy filter-incorrect-prefixes-v4
        if destionation in permitted-prefix-length-v4 then
            pass
        else
            drop
        endif
    end-policy
    route-policy filter-incorrect-prefixes-v6
        if destionation in permitted-prefix-length-v6 then
            pass
        else
            drop
        endif
    end-policy
    
    # If you want to implement it in one filter, then like this policy:
    route-policy filter-incorrect-prefixes
        if destionation in permitted-prefix-length-v4 or permitted-prefix-length-v6 then
            pass
        else
            drop
        endif
    end-policy
    ```

=== "Mikrotik"
    Mikrotik works with filter-lists, for easier readability you can use sub-filters (note this example only shows the filter lists itself):
    ```
    /routing filter
    add action=jump chain=upstream-in-v4 jump-target=ipv4-size
    ...
    add action=reject chain=ipv4-size prefix-length=0-7
    add action=reject chain=ipv4-size prefix-length=25-32
    ```

=== "Bird2"
    ```
    function reject_small_prefixes()
    {
      if (net.len > 24) then {
        # allow blackhole
        if (net.len != 32) then {
          # optional logging:
          # print "Reject: Too small prefix: ", net, " ", bgp_path;
          reject;
        }
      }
    }
    function reject_small_prefixes6()
    {
      if (net.len > 64) then {
        # allow blackhole
        if (net.len != 128) then {
          # optional logging:
          # print "Reject: Too small prefix: ", net, " ", bgp_path;
          reject;
        }
      }
    }
    filter import_ipv4() {
      reject_small_prefixes();
      ...
      accept;
    }
    filter import_ipv6() {
      reject_small_prefixes6();
      ...
      accept;
    }
    ```

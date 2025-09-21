# AS PATH Length

## Purpose

The AS PATH in the DFZ[^1] can become very long. At some point this can become an issue (with some Vendors/OSes). It should be considered to limit the maximum length of the AS PATH.

## Description

## Configuration

=== "Cisco IOS"
    ```
    router bgp 64500
     bgp maxas-limit 50
    ```

=== "Cisco IOS XR"
    ```
    route-policy AS-PATH-WAY-TOO-LONG
     if as-path length ge 50 then
      drop
     endif
    end-policy
    router bgp 64500
     neighor 198.51.100.1
      address-family ipv4 unicast
       route-policy AS-PATH-WAY-TOO-LONG in
     neighor 2001:db8::1
      address-family ipv6 unicast
       route-policy AS-PATH-WAY-TOO-LONG in
      exit
     exit
    exit
    ```

=== "Juniper JunOS"
    ```
    [edit policy-options]
        as-path AS-PATH-MAX-LENGTH ".{50,}";

    [edit policy-options policy-statement 4-BASE-IN]
        term AS-PATH-WAY-TOO-LONG {
          from {
            as-path AS-PATH-MAX-LENGTH;
          }
          then reject;
        }
    ```

=== "Bird2"
    ```
    function reject_long_aspaths()
    {
      if ( bgp_path.len > 50 ) then {
        # optional logging:
        # print "Reject: Too long AS path: ", net, " ", bgp_path;
        reject;
      }
    }
    filter import_all {
      reject_long_aspaths();
      ...
      accept;
    }
    ```

=== "FRRouting"
    FRRouting does not allow to limit the number of ASes in the path.

=== "Nokia SR OS classic CLI"
    ```
    /configure router "Base" policy-options
    begin
            policy-statement "inbound"
                description "inbound peering policy"
                [...]
                entry 25
                    from
                        as-path-length 100 or-higher
                    exit
                    action drop
                    exit
                exit
                [...]
            exit
    commit
    ```

=== "Arista EOS legacy"
    ```
    route-map example-in deny 10
       match as-path length >= 51
    !
    router bgp 64500
       address-family ipv6
          neighbor 2001:db8::1 route-map example-in in
       address-family ipv4
          neighbor 198.51.100.1 route-map example-in in
    ```

=== "Arista EOS RCF"
    ```
    router general
    control-functions
       code unit example
    function as_path_to_long() {
      return not as_path.length <= 50;
    }
    function example_in() {
      if as_path_to_long() {
        exit false;
      }
    }
    EOF
          compile
          commit
          exit
       exit
    !
    router bgp 64500
       address-family ipv6
          neighbor 2001:db8::1 rcf in example_in()
       address-family ipv4
          neighbor 198.51.100.1 rcf in example_in()
    ```

[^1]: Default Free Zone

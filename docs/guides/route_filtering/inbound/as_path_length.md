# AS PATH Length 

## Purpose
The AS PATH in the DFZ can become very long. At some point this can become an issue (with some Vendors/OSes). It should be considered to limit the maximum length of the AS PATH. 

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

=== "Juniper Junos"  
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
      if ( bgp_path.len > 100 ) then {
        # optional logging:
        # print "Reject: Too long AS path: ", net, " ", bgp_path;
        reject;
      }
    }
    filter import_all() {
      reject_long_aspaths();
      ...
      accept;
    }
    ```

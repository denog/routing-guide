# Own prefix

## Purpose
It is necessary to check incoming BGP prefixes to see if they match your own. This is because your own prefix should not come from outside.

There are exceptions when an AS is split. This rarely happens, and in those cases, the prefixes can come from outside.

## Description
Your own networks should be stored in lists and then used in policy for external BGP peers. 

## Configuration
=== "Cisco IOS XR"
    Add your own prefixes to the list:
    ```
    prefix-set my-own-network-ipv4
      <Please enter your own prefix with netmask here> le 32,
      <Please enter your own prefix with netmask here> le 32
    end-set
    
    prefix-set my-own-network-ipv6
      <Please enter your own prefix with netmask here> le 128,
      <Please enter your own prefix with netmask here> le 128
    end-set
    ```

    Use the prefix-list in a policy:
    ```
    route-policy reject-my-own-ipv4-networks
      if destination in my-own-network-ipv4 then
        drop
      else
        pass
      endif
    end-policy

    route-policy reject-my-own-ipv6-networks
      if destination in my-own-network-ipv6 then
        drop
      else
        pass
      endif
    end-policy
    ```
    The policy should be part of a central policy for the external BGP peer.

=== "Juniper JunOS"
    Create prefix list containtaing your own prefixes:
    ```
    set policy-options prefix-list MY-PREFIXES-V4 <PLEASE INSERT YOUR PREFIX HERE>
    
    set policy-options prefix-list MY-PREFIXES-V6 <PLEASE INSERT YOUR PREFIX HERE>
    ```

    Add it to your Import Policy:

    ```
    set policy-options policy-statement MY_INPUT_FILTER term FILTER-OWN-PREFIXES-V4 from family inet
    set policy-options policy-statement MY_INPUT_FILTER term FILTER-OWN-PREFIXES-V4 from prefix-list-filter MY-PREFIXES-V4 orlonger
    set policy-options policy-statement MY_INPUT_FILTER term FILTER-OWN-PREFIXES-V4 then trace
    set policy-options policy-statement MY_INPUT_FILTER term FILTER-OWN-PREFIXES-V4 then reject
    
    set policy-options policy-statement MY_INPUT_FILTER term FILTER-OWN-PREFIXES-V6 from family inet6
    set policy-options policy-statement MY_INPUT_FILTER term FILTER-OWN-PREFIXES-V6 from prefix-list-filter MY-PREFIXES-V6 orlonger
    set policy-options policy-statement MY_INPUT_FILTER term FILTER-OWN-PREFIXES-V6 then trace
    set policy-options policy-statement MY_INPUT_FILTER term FILTER-OWN-PREFIXES-V6 then reject
    ```
    

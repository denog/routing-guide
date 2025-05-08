# Own prefix

## Purpose
It is necessary to check incoming BGP prefixes to see if they match your own. This is because your own prefix should not come from outside.

There are exceptions when an AS is split. This rarely happens, and in those cases, the prefixes can come from outside.

## Description
Your own networks should be stored in lists and then used in policy for external BGP peers. 

## Configuration
=== "Cisco IOS XR"
    Your own prefixes to the list:
    ```
    prefix-set my-own-network-ipv4
      <Please enter your own prefix with netmask here> le 32,
      <Please enter your own prefix with netmask here> le 32
    end-set
    
    prefix-set my-own-network-ipv6
      <Please enter your own prefix with netmask here> le le 128,
      <Please enter your own prefix with netmask here> le le 128
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

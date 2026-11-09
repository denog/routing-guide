---
tags:
  - Arista missing
  - Cisco missing
  - Huawei VRP missing
  - Nokia SR OS missing
  - OpenBGPD missing
  - RtBrick RBFS missing
---

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

=== "FRRouting"
    ```
    ip prefix-list own seq 10 permit <PLEASE INSERT YOUR PREFIX HERE> le 24
    ip prefix-list own seq 100 deny 0.0.0.0/0 le 32

    ipv6 prefix-list own-6 seq 10 permit <PLEASE INSERT YOUR PREFIX HERE> le 48
    ipv6 prefix-list own-6 seq 100 deny ::/0 le 128

    route-map import deny 10
      match ip address prefix-list own
      match ipv6 address prefix-list own-6
    exit
    ```

=== "VyOS"
    VyOS has two modes (operational and configuration mode). Enter configuration mode with
    `configure` to make changes. Use `commit` to apply them and `save` to keep them after reboot.

    ```
    set policy prefix-list own rule 5 action permit
    set policy prefix-list own rule 5 prefix <PLEASE INSERT YOUR PREFIX HERE>
    set policy prefix-list own rule 5 le 24

    set policy prefix-list6 own-6 rule 5 action permit
    set policy prefix-list6 own-6 rule 5 prefix <PLEASE INSERT YOUR PREFIX HERE>
    set policy prefix-list6 own-6 rule 5 le 48

    set policy route-map import rule 10 action deny
    set policy route-map import rule 10 match ip address prefix-list own
    set policy route-map import rule 10 match ipv6 address prefix-list own-6
    ```

=== "MikroTik"
    ```
    /routing/filter/rule
    add chain=reject_own_prefixes rule="if ( afi ipv4 && dst in <PLEASE INSERT YOUR PREFIX HERE> ) { reject }"
    add chain=reject_own_prefixes rule="if ( afi ipv6 && dst in <PLEASE INSERT YOUR PREFIX HERE> ) { reject }"
    add chain=reject_own_prefixes rule=return comment="JUMP back to parent rule"

    add chain=DENOG-IN rule="jump reject_own_prefixes"
    ```

=== "Bird2"
    ```
    define OWN_PREFIXES_V4 = [
      <PLEASE INSERT YOUR PREFIX HERE>
    ];
    define OWN_PREFIXES_V6 = [
      <PLEASE INSERT YOUR PREFIX HERE>
    ];

    function reject_own_prefixes_v4()
    prefix set own_prefixes_v4;
    {
      own_prefixes_v4 = OWN_PREFIXES_V4;
      if (net ~ own_prefixes_v4) then reject;
    }
    function reject_own_prefixes_v6()
    prefix set own_prefixes_v6;
    {
      own_prefixes_v6 = OWN_PREFIXES_V6;
      if (net ~ own_prefixes_v6) then reject;
    }

    protocol bgp neighbor_name {
      ipv4 {
        import filter {
          reject_own_prefixes_v4();
          # other filters
          accept;
        };
      }
      ipv6 {
        import filter {
          reject_own_prefixes_v6();
          # other filters
          accept;
        };
      }
    }
    ```

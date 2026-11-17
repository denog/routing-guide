---
tags:
  - Cisco missing
  - Cisco IOS XR missing
  - Huawei VRP missing
  - Junos missing
  - Mikrotik missing
  - Nokia SR OS missing
  - OpenBGPD missing
  - RtBrick RBFS missing
---

# Graceful Shutdown
BGP-Graceful-Shutdown is a mechanism defined in [RFC6198](https://www.rfc-editor.org/rfc/rfc6198) to inform your BGP neighbor that you want to close the session. The peer will then stop sending you new routes and you can safely close the session. The purpose of this community is to reduce the amount of traffic lost when BGP peering sessions are about to be shut down deliberately, e.g. for planned maintenance.


=== "BIRD 2/3"
    ```
    function honor_graceful_shutdown()
    {
      if (65535, 0) ~ bgp_community then {
        bgp_local_pref = 0;
      }
    }

    protocol bgp neighbor_name {
      ipv4 {
        import filter {
          honor_graceful_shutdown();
          # other filters
          accept;
        };
      }
      ipv6 {
        import filter {
          honor_graceful_shutdown();
          # other filters
          accept;
        };
      }
    }
    ```

=== "FRR"
    ```
    router bgp 64500
      bgp graceful-shutdown
    ```

=== "VyOS"
    VyOS has two modes (operational and configuration mode). Enter configuration mode with
    `configure` to make changes. Use `commit` to apply them and `save` to keep them after reboot.
    ```
    set protocols bgp parameters graceful-shutdown
    ```

=== "Arista EOS"
    EOS honors the graceful shutdown community without any configuration: received routes carrying it get local preference 0. This cannot be disabled. Check the local preference of such a route with:
    ```
    show ip bgp 203.0.113.0/24
    ```

    See the EOS manual: [ACLs and Route Maps](https://www.arista.com/en/um-eos/eos-acls-and-route-maps) (`set community`, graceful shutdown).

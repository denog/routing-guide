# Graceful Shutdown
BGP-Graceful-Shutdown is a mechanism defined in [RFC6198](https://www.rfc-editor.org/rfc/RFC6198) to inform your BGP neighbor that you want to close the session. The peer will then stop sending you new routes and you can safely close the session. The purpose of this community is to reduce the amount of traffic lost when BGP peering sessions are about to be shut down deliberately, e.g. for planned maintenance.


=== "Bird2"
    ```
    function honor_graceful_shutdown() {
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

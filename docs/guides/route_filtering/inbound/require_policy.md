---
tags:
  - Arista missing
  - BIRD missing
  - Cisco missing
  - Huawei VRP missing
  - Junos missing
  - Mikrotik missing
  - OpenBGPD missing
---

# Require policy to start a BGP session

Some routers accept configuration commands as you type them in line by line. At others you *commit* your configuration once you have completed it.

Now, if you setup a BGP session to a neighbor and the router accepts it line by line, the session will be established once "enough" configuration is entered, independent if you have completed the configuration or not.

So imagine you enter the neighbors AS number and IP address and then you go for a coffee. This might be enough to establish a session. Without any filtering, you now will receive everything from that neighbor and also announce every valid prefix in your own BGP tables. Most of the times, this is not what you want.

[RFC8212](https://www.rfc-editor.org/rfc/rfc8212.html)
requires that you *must* configure an import and an export policy (= some filtering) on any external BGP session, otherwise the session will not be initiated or accepted.

The compliance of BGP implementations to RFC8212 is tracked
[here](https://github.com/bgp/RFC8212).

Configuration examples:

=== "Cisco IOS XR"
    No configuration necessary, RFC8212 is supported by default.

=== "FRRouting"
    This is enabled by default for traditional configuration.
    ```
    router bgp 64500
      bgp ebgp-requires-policy
    ```

=== "Nokia SR OS classic CLI"
    ```
    /configure router "Base" bgp
            ebgp-default-reject-policy import export
    ```

=== "VyOS (>= 1.4)"
    VyOS has two modes (operational and configuration mode). Enter configuration mode with
    `configure` to make changes. Use `commit` to apply them and `save` to keep them after reboot.

    ```
    set protocols bgp parameters ebgp-requires-policy
    ```


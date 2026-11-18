---
tags:
  - Cisco missing
  - Cisco IOS XR missing
  - Huawei VRP missing
  - Junos missing
  - Nokia SR OS missing
  - OpenBGPD missing
  - VyOS missing
  - RtBrick RBFS missing
---

# RPKI

With RPKI it is possible to validate the origin AS of a BGP announcement. This is done by checking the announcement against ROAs (Route Origin Authorizations) published in the RPKI system. It is a best practice to filter out invalid routes.

<!-- https://ripe79.ripe.net/presentations/40-RIPE79-Cloudflares-RPKI-validator.pdf (slide 34) -->
!!! note "Public RPKI RTR cache servers"
    Public RPKI RTR cache servers can be useful as a temporary solution
    until you host your own.

    - SSH: `rtr.rpki.cloudflare.com:8283` (user: `rpki` / pass: `rpki`)
    - Plaintext: `rtr.rpki.cloudflare.com:8282`

    More information can be found here:
    <https://blog.cloudflare.com/rpki-and-the-rtr-protocol/>

## Configuration Examples

=== "BIRD 2/3"
    ```bird
    roa4 table rpki4;
    roa6 table rpki6;

    protocol rpki routinator1 {
      roa4 { table rpki4; };
      roa6 { table rpki6; };
      remote "rpki1.example.com" port 3323; # replace with your RPKI validator
    }

    protocol rpki routinator2 {
      roa4 { table rpki4; };
      roa6 { table rpki6; };
      remote "rpki2.example.com" port 3323; # replace with your RPKI validator
      retry keep 90;
      refresh keep 900;
      expire keep 172800;
    }

    function reject_rpki_invalid4()
    {
      if roa_check(rpki4, net, bgp_path.last_nonaggregated) = ROA_INVALID then {
        # optional logging
        # print "Reject: RPKI invalid: ", net, " ", bgp_path;
        reject;
      }
    }

    function reject_rpki_invalid6()
    {
      if roa_check(rpki6, net, bgp_path.last_nonaggregated) = ROA_INVALID then {
        # optional logging
        # print "Reject: RPKI invalid: ", net, " ", bgp_path;
        reject;
      }
    }

    protocol bgp neighbor_name {
      ipv4 {
        import filter {
          reject_rpki_invalid4();
          ...
          accept;
        };
      };
      ipv6 {
        import filter {
          reject_rpki_invalid6();
          ...
          accept;
        };
      };
    }
    ```

=== "FRRouting"
    bpgd must be started with `-M rpki`, otherwise you get "Unknown command: rpki" errors. See
    [docs.frrouting.org/en/latest/bgp.html#enabling-rpki](https://docs.frrouting.org/en/latest/bgp.html#enabling-rpki)
    for more details.

    ```
    rpki
      rpki cache ssh rtr.rpki.example.com source 198.51.100.223 8283 rpki ./.ssh/id_rsa preference 1
      rpki cache tcp rtr.rpki.example.com 8282 preference 2
    exit

    router bgp 64496
      ! wait for RPKI cache server availablity to establish peering (requires frr >= 10.5)
      !neighbor 198.51.100.1 rpki strict

      address-family ipv4
        neighbor 198.51.100.1 route-map rpki in
      exit-address-family

      address-family ipv6
        neighbor 198.51.100.1 route-map rpki in
      exit-address-family
    exit
    
    ! drop invalid prefixes
    route-map rpki deny 10
      match rpki invalid

    route-map rpki permit 20
      match rpki notfound
      set local-preference 100

    route-map rpki permit 30
      match rpki valid
      set local-preference 200
    ```

=== "MikroTik"
    ```
    /routing rpki
    add address=10.23.23.23 comment="rpki1.example.com" group=VALIDATORS port=3323 refresh-interval=20
    add address=2001:db8::42 comment="rpki2.example.com" group=VALIDATORS port=3323 refresh-interval=20

    /routing/filter/rule
    add chain=check_rpki rule="rpki-verify VALIDATORS"
    add chain=check_rpki rule="if (rpki invalid) { reject } else { return }"

    add chain=DENOG-IN rule="jump check_rpki"
    ```

=== "Arista EOS"
    ```
    router bgp 64500
       rpki cache rpki-cache
          host 198.51.100.5 port 3323
       rpki origin-validation
          ebgp local
    !
    ! drop invalid prefixes
    route-map rpki deny 10
       match origin-as validity invalid
    route-map rpki permit 20
       match origin-as validity not-found
       set local-preference 100
    route-map rpki permit 30
       match origin-as validity valid
       set local-preference 200
    !
    router bgp 64500
       address-family ipv4
          neighbor 198.51.100.1 route-map rpki in
       address-family ipv6
          neighbor 2001:db8::1 route-map rpki in
    ```

    See the Arista TOI [BGP Validation with Resource Public Key Infrastructure (RPKI)](https://www.arista.com/en/support/toi/eos-4-24-0f/14470-bgp-prefix-origin-validation-with-resource-public-key-infrastructure-rpki) (Arista account required).

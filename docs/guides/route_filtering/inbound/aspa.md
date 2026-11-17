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
  - FRRouting missing
  - MikroTik missing
---

# ASPA
!!! note "ASPA draft status"
    The ASPA standard is still an Internet-Draft and not yet an official RFC.

An ASPA is a cryptographically signed object that allows holders of an Autonomous System Number (ASN) to authorize other ASNs as their provider networks. To use ASPA-filtering you will need a RPKI-Validator like [Routinator](https://github.com/NLnetLabs/routinator) with ASPA publishing enabled.

## Configuration Examples

=== "BIRD 2/3"
For BIRD2/3 the functions `aspa_check_downstream`, `aspa_check_upstream( table )` and `aspa_check(table, path, is_upstream)` exsist.
    ```bird
    aspa table aspatable;

    # rpki server with aspa enabled is requiered
    protocol rpki routinator1 {
      roa4 { table rpki4; };
      roa6 { table rpki6; };
      aspa { table aspatable; };
      remote "rpki1.example.com" port 3323; # replace with your RPKI validator
    }

    protocol rpki routinator2 {
      roa4 { table rpki4; };
      roa6 { table rpki6; };
      aspa { table aspatable; };
      remote "rpki2.example.com" port 3323; # replace with your RPKI validator
    }

    # use up ramp mode (Customer to Provider)
    function reject_aspa_invalid_upstream()
    {
      if aspa_check(aspatable, bgp_path, false) = ASPA_INVALID then {
          print "Reject: ASPA invalid: ", " ", bgp_path;
          reject;
      }
    }

    # use down ramp mode (Provider to Customer)
    function reject_aspa_invalid_downstream()
    {
      if aspa_check(aspatable, bgp_path, true) = ASPA_INVALID then {
          print "Reject: ASPA invalid: ", " ", bgp_path;
          reject;
      }
    }

    protocol bgp upstream {
      ipv4 {
        import filter {
          reject_aspa_invalid_upstream();
          ...
          accept;
        };
      };
      ipv6 {
        import filter {
          reject_aspa_invalid_upstream();
          ...
          accept;
        };
      };
    }

    protocol bgp downstream {
      ipv4 {
        import filter {
          reject_aspa_invalid_downstream();
          ...
          accept;
        };
      };
      ipv6 {
        import filter {
          reject_aspa_invalid_downstream();
          ...
          accept;
        };
      };
    }
    ```

=== "Arista EOS"
    The RPKI cache must deliver ASPAs (`aspa`) via RTR version 2. ASPA verification needs the BGP role of the session (`local-role` is your own role towards the neighbor, here `provider` towards a customer); without a role EOS rejects all routes from that neighbor. Invalid routes are dropped with a routing control function (RCF):
    ```
    router general
       control-functions
          code unit aspa
    function aspa_in() {
       if rpki.as_path_validity is ASPA_INVALID {
          return false;
       }
       return true;
    }
    EOF
          compile
          commit
          exit
       exit
    !
    router bgp 64500
       rpki cache rpki-cache
          host 198.51.100.5 port 3323
          aspa
       rpki as-path-validation
          ebgp local
       neighbor 198.51.100.1 local-role provider
       neighbor 2001:db8::1 local-role provider
       address-family ipv4
          neighbor 198.51.100.1 rcf in aspa_in()
       address-family ipv6
          neighbor 2001:db8::1 rcf in aspa_in()
    ```

    See the Arista TOI [BGP Validation with Resource Public Key Infrastructure (RPKI)](https://www.arista.com/en/support/toi/eos-4-24-0f/14470-bgp-prefix-origin-validation-with-resource-public-key-infrastructure-rpki) (Arista account required) and the EOS manual: [Routing Control Functions](https://www.arista.com/en/um-eos/eos-routing-control-functions).

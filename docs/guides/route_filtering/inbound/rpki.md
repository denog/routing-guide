# RPKI

## Configuration Examples
=== "Bird2"
    ```
    roa4 table rpki4;
    roa6 table rpki6;
    
    protocol rpki routinator {
        roa4 { table rpki4; };
        roa6 { table rpki6; };
        remote "rpki2.example.com" port 3323; # replace with your RPKI validator
    }
    function reject_rpki_invalid4() 
    {
    if roa_check(rpki4, net, bgp_path.last_nonaggregated) = ROA_INVALID then {
        print "Reject: RPKI invalid: ", net, " ", bgp_path;
        reject;
    }
    }

    function reject_rpki_invalid6() 
    {
    if roa_check(rpki6, net, bgp_path.last_nonaggregated) = ROA_INVALID then {
        print "Reject: RPKI invalid: ", net, " ", bgp_path;
        reject;
    }
    }
    protocol bgp neighbor_name {
        ipv4 {
            import filter {
                reject_ixp_prefixes4();
                # other filters
                accept;
            };
        }
        ipv6 {
            import filter {
                reject_ixp_prefixes6();
                # other filters
                accept;
            };
        }
    }
    ```

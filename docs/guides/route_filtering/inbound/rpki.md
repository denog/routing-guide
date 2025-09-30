# RPKI

With RPKI it is possible to validate the origin AS of a BGP announcement. This is done by checking the announcement against ROAs (Route Origin Authorizations) published in the RPKI system. It is a best practice to filter out invalid routes.

## Configuration Examples

=== "Bird2"
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

    function reject_rpki_invalid4() {
        if roa_check(rpki4, net, bgp_path.last_nonaggregated) = ROA_INVALID then {
            print "Reject: RPKI invalid: ", net, " ", bgp_path;
            reject;
        }
    }
    
    function reject_rpki_invalid6() {
        if roa_check(rpki6, net, bgp_path.last_nonaggregated) = ROA_INVALID then {
            print "Reject: RPKI invalid: ", net, " ", bgp_path;
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

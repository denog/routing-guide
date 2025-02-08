# Bogon AS

## Purpose
Bogon AS are autonomous systems which are used for test or demo applications. These AS may not be used on the public Internet.

=== "Cisco IOS XR"
    ```
    as-path-set bogon-asn
       ios-regex '_0_',
       passes-through '23456',
       passes-through '[64496..64511]',
       passes-through '[65536..65551]',
       passes-through '[64512..65534]',
       passes-through '[4200000000..4294967294]',
       passes-through '65535',
       passes-through '4294967295',
       passes-through '[65552..131071]'
    end-set
    
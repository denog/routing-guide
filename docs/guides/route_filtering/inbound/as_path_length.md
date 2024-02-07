# AS PATH Length 

## Purpose
The AS PATH in the DFZ can become very long. At some point this can become an issue (with some Vendors/OSes). It should be considered to limit the maximum length of the AS PATH. 

## Description

## Configuration

=== "Cisco IOS"
    ```
    please add
    ``` 

=== "Juniper Junos"  

    [edit policy-options]
        as-path AS-PATH-MAX-LENGTH ".{50,}";
        
    [edit policy-options policy-statement 4-BASE-IN]
        term AS-PATH-WAY-TOO-LONG {
    	  from {
            as-path AS-PATH-MAX-LENGTH;
        }
    then reject;
    }

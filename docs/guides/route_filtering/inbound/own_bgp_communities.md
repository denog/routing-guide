# Own prefix

## Purpose
A BGP community is bit of “extra information” that you can add to one of more prefixes which is advertised to BGP neighbors. This extra information can be used for things like traffic engineering or dynamic routing policies.
There are different types of communities (Standard, Extended, and Large). Not every manufacturer supports all types.

It is important to filter your own communities from the incoming external BGP Peer.

## Description
Your own communities should be stored in lists or sets and then used in policy for external BGP peers.

=== "Cisco IOS XR"
    Using an *my-own* communitys-set you can add  more communities to it that you want. Since these are your own complete communities, you can work with wildcards.
    ```
    community-set my-own-communitys
      <YOUR OWN AS NUMBER>:*
    end-set
    !
    large-community-set my-own-large-communitys
      <YOUR OWN AS NUMBER>:*:*
    end-set
    ```
    
    If you want to drop the prefix.
    ```
    route-policy drop-my-own-communitys
      if community matches-any my-own-communitys or community matches-any my-own-large-communitys then
        drop
      else
        pass
      endif
    end-policy
    ```

    If you want to delete the community and accept the prefix.
    ```
    route-policy clean-my-own-communitys
      if community matches-any my-own-communitys or community matches-any my-own-large-communitys then
        delete community in my-own-communitys
        delete large-community in my-own-large-communitys
      endif
    end-policy
    ```

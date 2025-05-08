# Own BGP communities

## Purpose
As long as you operate your own ASN you are allowed to create and use whatever BGP community it needs to mark incoming prefixes or prefixes learned internally.
One of the purposes is to "tag" routes with specific information like origion, the router it was learned on etc. The other purpose is filtering, to e.g. allow only specific prefixes with a specific community to be announced to your upstreams.

## Format

Depends on whether you operate a 16 oder 32-Bit ASN the format differs:

### Standard Communities:
32-Bit split in two 16-Bit values. If you already operate a 32-Bit ASN you can't use these.
   ```
   <YOUR_ASN>:[0-65535]
   ```

### Extended Communities:
64-Bit split into 3 parts:
   ```
   <purpose/type>:<YOUR_ASN>:<value>
   ```
Depends on the size of your ASN (16/32 Bit). Not very commonly used, better use the large community approach.

### Large Communities:
96-Bit split into 3 parts:
   ```
   <YOUR_ASN>:<value1>:<value2>
   ```

## Standard Communities
 See https://routing.denog.de/guides/route_filtering/outbound/well_known_communities_traffic_engineering/


## Configuration Examples

=== "Juniper"

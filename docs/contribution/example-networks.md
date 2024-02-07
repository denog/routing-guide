# Example networks for documentation

## Background

When writing documents you often need networks or IP addresses for examples. This page lists the networks which are explicitly mentioned in Internet Standards for this purpose.

### IPv4 Example Networks

#### Source: RFC5737

The following networks are fully routable /24 networks (256 addresses), but set aside for documentation purposes:

- 192.0.2.0/24
- 198.51.100.0/24
- 203.0.113.0/24

#### Source: RFC1918

The following networks are so-called private networks, they cannot be routed in the global BGP table but can be freely used in private networks:

- 10.0.0.0/8 (10.0.0.0 - 10.255.255.255)
- 172.16.0.0/12 (172.16.0.0 - 172.31.255.255)
- 192.168.0.0/16 (192.168.0.0. - 192.168.255.255)

### IPv6 Example Network

#### Source: RFC3849

The following network block is fully routable, but set aside for documentation purposes:

- 2001:db8::/32

### Autonomous System Numbers

#### Source: RFC5398

The following AS numbers are set aside for documentation purposes:

- 16-Bit numbers: 64496 - 64511
- 32-Bit numbers: 65536 - 65551

#### Source: RFC6996

The following AS numbers are reserved for private use:

- 16-Bit numbers: 64512 - 65534
- 32-Bit numbers: 4200000000 - 4294967294

### Domain Names

#### Source: RFC2606

The following domain names can be used for documentation:

- ".example" (Top-Level Domain)
- "example.com"
- "example.net"
- "example.org"

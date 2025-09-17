# Motivation

There are several reasons why forwarding plane protection is needed for hosts processing network traffic:

* Transmitting unwanted data: networked hosts may transmit unwanted data, sometimes by default e.g., sending LLDP frames or VRRP messages at an IXP. This can leak sensitive information, and/or alter the routing behaviour of other devices undesirably. Which data are transmitted by the local host can be limited to prevent security and forwarding issues.
* Receiving unwanted data: networked hosts may receive unwanted data e.g., receiving unsolicited IPv6 Router Advertisements. This can cause unexpected and undesired changes in forwarding behaviour. If data received by the local host should be processed and acted upon, can be limited to prevent security and forwarding issues.
* Forwarding unwanted data: networked hosts which have received unwanted data e.g., data with an unreachable source IP address, may forward that unwanted data onwards to additional hosts, further propagating the unwanted data. The forwarding of unwanted data can be restricted to prevent it's further propagation.

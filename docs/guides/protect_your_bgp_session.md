# Protect your BGP session

## Motivation

The idea of these measures is to protect your TCP-based BGP sessions against attacks. Keep in mind, these TCP sessions are long-living (speaking of weeks and months), so an attacker can take its time to try to destroy a BGP session sending crafted packets.

## MD5 session password

The easiest countermeasure against TCP based attacks on BGP sessions is to use  MD5 protection as described in RFC2385. When implementing this, keep in mind to also implement some key (password) handling procedures (just imagine your router has to be replaced and you have to re-create all eBGP configurations).

Example for setting an MD5 password on Cisco:
\begin{verbatim}
  router bgp 64500
  ...
  neighbor 10.96.1.1 password mysecretpassword
\end{verbatim}

Example for Mikrotik:
\begin{verbatim}
  add name=AS64496 remote-as=64496 \
    remote-address=10.96.1.1 tcp-md5-key=mysecretpassword
\end{verbatim}

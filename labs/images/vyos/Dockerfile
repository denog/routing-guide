# From https://containerlab.dev/manual/kinds/vyosnetworks_vyos/
FROM scratch

ADD rootfs.tar /

RUN for service in\
    getty.target \
    auditd.service \
    ;do systemctl mask $service; done && \
    systemctl disable kea-dhcp-ddns-server.service

HEALTHCHECK --start-period=10s CMD systemctl is-system-running

CMD ["/sbin/init"]

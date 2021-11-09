Steps to install xmppd on DUT
================================
#### By deb
- On Linux server
```
  1. apt-get install python-stdeb
  2. git clone https://github.com/SquidRo/xmppd
  3. cd xmppd; ./build_deb.sh
  4. copy output python-xmppd_0.1-1_all.deb to DUT
```
- On DUT
```
  1. pip install sleekxmpp (sleekxmpp-1.3.3 is required)
  2. dpkg -i python-xmppd_0.1-1_all.deb
  3. systemctl start xmppd.service
```


#!/usr/bin/expect

spawn /home/suyash/forticlientsslvpn/64bit/forticlientsslvpn_cli --server 14.98.58.218:10443 --vpnuser suyash.soni@whatfix.com
expect "Password for VPN"
send "WFXNW#@71suyash\r"
expect "Would you like to connect to this server? (Y/N)"
send "Y\r"
expect "STATUS::Tunnel running"
send "\r"
interact

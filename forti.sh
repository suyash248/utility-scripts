#!/usr/bin/expect

spawn /home/suyash/forticlientsslvpn/64bit/forticlientsslvpn_cli --server <ip>:<port> --vpnuser suyash.soni@gmail.com
expect "Password for VPN"
send "pass1234\r"
expect "Would you like to connect to this server? (Y/N)"
send "Y\r"
expect "STATUS::Tunnel running"
send "\r"
interact

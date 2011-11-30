#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os.path
import urllib2
import cgitb
cgitb.enable()

pm = urllib2.HTTPPasswordMgrWithDefaultRealm()
pm.add_password(None, '192.168.0.1', 'feiboserver', 'feibo')
hdlr = urllib2.HTTPBasicAuthHandler(pm)
o = urllib2.build_opener(hdlr)

namemap = {}
clients = o.open('http://192.168.0.1/lan_dhcp_clients.asp').read()
clients = clients[clients.index('var dhcpList=new Array')+22:clients.index("');")+2]
clients = eval(clients)
for row in clients:
	ar = row.split(';')
	namemap[ar[1]] = ar[0]

result = []

stat = o.open('http://192.168.0.1/statistic.asp').read()
stat = stat[stat.index('var reqStr'):stat.index('var reqtmp')]
stat = stat[stat.index('"')+1:stat.rindex('"')]
rowfmt = '<tr style="%s">' + '<td>%s</td>' * 10 + '</tr>'
for row in stat.split(','):
	ar = row.split(';')
	if ar[1] == '00:00:00:00:00:00':
		continue
	ar.insert(0, namemap.get(ar[0], ''))
	ar.insert(0, 'background-color:#F00000;'
			if int(ar[-2]) > 80000 or int(ar[-1]) >= 80 else '')
	result.append(rowfmt % tuple(ar))

print 'Content-Type: text/html'
print

print '''<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8;">
</head>
<body>
    <table border="1" cellspacing="0" cellpadding="0" style="table-layout:fixed" width="100%%">
        <thead style="background-color:#CCCCCC; color:#000000;">
        <tr align="center">
          <TH width="120">主机名</TH>
          <TH width="100">IP地址</TH>
          <TH width="120">MAC地址</TH>
          <TH width="55">↑包数</TH>
          <TH width="65">↑字节数</TH>
          <TH width="55">↓包数</TH>
          <TH width="65">↓字节数</TH>
          <TH width="50">↑速率</TH>
          <TH width="50">↓速率</TH>
          <TH width="45">连接数</TH>
        </tr>
        </thead>
        <tbody style="color:#000000" id="StatisticList" align="center">
%s
        </tbody>
    </table>
</body>
</html>''' % ('\n'.join(result),)

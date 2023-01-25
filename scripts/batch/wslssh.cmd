@echo off
wsl service ssh start
for /f "usebackq tokens=*" %%c in (`wsl ifconfig eth0 ^^^| awk '$1^=^=^"inet^"{print $2}'`) do set addr=%%c
echo WSL IP Address: %addr%
netsh interface portproxy delete v4tov4 listenport=22 listenaddr=0.0.0.0
netsh interface portproxy add v4tov4 listenport=22 listenaddr=0.0.0.0 connectport=22 connectaddress=%addr%
netsh interface portproxy show all
:end

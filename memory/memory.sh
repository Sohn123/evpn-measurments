pid=$(pgrep bgpd)
while true; do
echo $(sudo vtysh -c "show bgp l2vpn evpn statistics" | grep 'Total Prefixes' | grep -Eo '[0-9]*' && echo $(cat "/proc/${pid}/status" | grep "VmRSS" | grep -Eo '[0-9]*') && echo $(top -bn1 | grep -E "^[ ]*${pid}" | tr -s ' ' | cut -d " " -f10) && date +%s%N) | tee -a out.txt
done


while true; do
	pid=$(pgrep bgpd)
	time=$(date +%s%N)
	vtysh -c 'show bgp neighbors json'|jq "with_entries(.value |= {addressFamilyInfo,messageStats}) | map_values(.messageStats |= {depthInq,depthOutq,updatesSent,updatesRecv,totalSent,totalRecv}) |map_values(.addressFamilyInfo.l2VpnEvpn |= {packetQueueLength,acceptedPrefixCounter,sentPrefixCounter})+{"time":${time},"memory":$(cat "/proc/${pid}/status" | grep 'VmRSS' | grep -Eo '[0-9]*'),"cpu":$(top -bn1 | grep -E "^[ ]*${pid}" | cut -d "%" -f2 | grep -Eo "[^ ]*$")}" | tee -a /tmp/out.txt
done


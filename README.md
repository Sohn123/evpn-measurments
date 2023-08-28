# EVPN Measurement Scripts

This repository contains the scripts I used for the measurements in my bachelor's thesis. If want to use this code and you have a question drop me a message. 

## Memory

This is a shell script to monitor the number of BGP EVPN routes via vtysh in relation to the memory usage of the bgpd daemon.

## Propagation Time
Contains two python scripts that measure the propagation time. The scripts have to be run on different hosts that have to be connected via VXLAN and additionally on Layer 3 besides the VXLAN. The testdevice needs two connections to different VTEPs in the same VXLAN. For a more detailed explanation, take a look at my bachelor's thesis.

## Setup Time
Contains a python script to measure the setup time of a VXLAN. The setup time is the time between creating the VXLAN and a specific entry installed in the FDB.

## Monitoring
Scripts to monitor different statistics of the bgpd daemon. I used those to get inside for my measurement results.
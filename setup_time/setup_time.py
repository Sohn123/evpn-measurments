import subprocess
import socket
import struct
from time import sleep
import datetime

# Constants for netlink
RTM_NEWNEIGH = 28
NDA_LLADDR = 2
AF_BRIDGE = 7

def parse_ndmsg(data):
    return(struct.unpack('=BBHiHBB', data[:12]))


def log_ndmsg(ifindex, rtattr_list):
    for rtattr_type, rtattr_value in rtattr_list:
        if rtattr_type == NDA_LLADDR:
            mac_address = ":".join(f"{x:02x}" for x in rtattr_value)
            if mac_address == "3e:d5:13:2b:16:23":
                return True, datetime.datetime.now()
    return False, None

def parse_rtattr(rtattr_data):
    rtattr_list = []
    while len(rtattr_data) >= 4:
        rtattr_len, rtattr_type = struct.unpack("=HH", rtattr_data[:4])
        if rtattr_len <= 0:
            break
        rtattr_value = rtattr_data[4:rtattr_len]
        rtattr_list.append((rtattr_type, rtattr_value))
        rtattr_data = rtattr_data[rtattr_len+(rtattr_len%4):]
    return rtattr_list

def parse_rtneigh(msg_data):
    msg_len, msg_type, msg_flags, msg_seq, msg_pid = struct.unpack("=LHHLL", msg_data[:16])
    if msg_type == RTM_NEWNEIGH:
        family, _, _, index, state, flags, type = parse_ndmsg(msg_data[16:])
        #if family != AF_BRIDGE:
        #    return False, None
        rtattr_list = parse_rtattr(msg_data[28:])
        return log_ndmsg(index, rtattr_list)
    return False, None

def main():
    with open("log.txt", "a") as log:
        for i in range(1000):
            print(f"Start measurement: {i}")
            subprocess.run("ip link del br400".split(" "))
            subprocess.run("ip link del vxlan400".split(" "))
            # Wait till bgp revoked the routes
            s = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW)
            sleep(1)

            subprocess.run("ip link add vxlan400 type vxlan id 400 dstport 4789 local 10.242.2.27 nolearning".split(" "))
            #subprocess.run("ip link add vxlan400 type vxlan id 400 dstport 4789 local 10.242.2.27".split(" "))
            subprocess.run(f"ip link add br400 type bridge".split(" "))
            subprocess.run("ip link set br400 up".split(" "))
            subprocess.run("ip link set vxlan400 master br400".split(" "))
            s.bind((0, 4))
            subprocess.run("ip link set vxlan400 up".split(" "))
            start = datetime.datetime.now()
            end = None
            valid = True
            z = 0
            while True:
                print(z)
                z += 1
                data, _ = s.recvfrom(8192)
                found, end = parse_rtneigh(data)
                if found:
                    break
                if datetime.datetime.now() - start > datetime.timedelta(seconds=20):
                    valid = False
                    break
            if not valid:
                print("Failed")
                continue
            took = end - start
            print(took)
            log.write(f"{str((took.seconds * 1000)+  (took.microseconds / 1000))}\n")
            log.flush()
            s.close()

if __name__ == "__main__":
    main()

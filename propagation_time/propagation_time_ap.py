import subprocess
import socket
import struct
from time import sleep
import datetime
from multiprocessing.connection import Client
import argparse

# Constants for netlink
RTM_NEWNEIGH = 28
NDA_LLADDR = 2
NDA_DST = 1
AF_BRIDGE = 7

def parse_ndmsg(data):
    return(struct.unpack('=BBHiHBB', data[:12]))

def parse_newlink(data):
    return struct.unpack("=BBHiII", data[:16])

def log_ndmsg(ifindex, rtattr_list):
    ip = None
    found = False
    for rtattr_type, rtattr_value in rtattr_list:
        if rtattr_type == NDA_LLADDR:
            mac_address = ":".join(f"{x:02x}" for x in rtattr_value)
            if mac_address == "3e:d5:13:2b:16:23":
                found = True
        elif rtattr_type == NDA_DST:
            ip = '.'.join(f'{c}' for c in rtattr_value)
    if found:
        return ip
    print("Wrong mac")

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
        #    print("Is not bridge")
        #    return None
        rtattr_list = parse_rtattr(msg_data[28:])
        return log_ndmsg(index, rtattr_list)

def main(args):
    conn = Client((args.ip, args.port))
    with open("log.txt", "a") as log:
        result = subprocess.run(['bridge', 'fdb', 'show',  'br', 'br400', 'brport', 'vxlan400', 'self', 'dynamic'], stdout=subprocess.PIPE)
        vtep = [line for line in result.stdout.decode('utf-8').split('\n') if line.startswith("3e:d5:13:2b:16:23 dst")][0].split(" ")[2]
        for i in range(1000):
            print(f"Current vtep: {vtep}")
            print(f"Start measurement: {i}")
            old_vtep = vtep
            s = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW)
            s.bind((0, 4))
            conn.send("hello")
            start = datetime.datetime.now()
            invalid = False
            i = 0
            while vtep == old_vtep or vtep is None:
                i += 1
                print(i)
                data, _ = s.recvfrom(8192)
                vtep = parse_rtneigh(data)
                if datetime.datetime.now() - start > datetime.timedelta(seconds=90):
                    if vtep != old_vtep and vtep is not None:
                        print("Found out of time")
                    else:
                        print("Not finishing")
                    invalid = True
                    break
            end = datetime.datetime.now()
            s.close()
            if invalid:
                print("Invalid measurement")
                continue
            took = end - start
            print(took)
            log.write(f"{str((took.seconds * 1000)+  (took.microseconds / 1000))}\n")
            log.flush()
            sleep(1)
    conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', '-i', dest='ip', help='iperf host ip', default='10.242.2.2')
    parser.add_argument('--port', '-p', dest='port', help='iperf host ip', default=6000)
    args = parser.parse_args()
    main(args)

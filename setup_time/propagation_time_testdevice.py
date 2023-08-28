from multiprocessing.connection import Listener
import argparse
import os
from time import sleep
import subprocess

ports = ["enp7s0f1", "enp7s0f0"]
bridgeName = "testBridge"

def main(args):
    result = subprocess.run(["bridge","link", "show", "master", "testBridge"], stdout=subprocess.PIPE)
    if result.stdout.decode('utf-8').strip().split(" ")[1].startswith("enp7s0f0"):
        i = 1
    else:
        i = 0
    address = (args.ip, args.port)
    listener = Listener(address)
    conn = listener.accept()
    print("Accepted connection")
    while True:
        msg = conn.recv()
        # do something with msg
        if msg == 'close':
            print("Received close")
            conn.close()
            break
        delBridge = ports[i % len(ports)]
        addBridge = ports[(i+ 1) % len(ports)]
        os.popen(f"ip link set {delBridge} nomaster && ip link set {addBridge} master {bridgeName}")
        print(i)
        print(f"delBridge: {delBridge}")
        print(f"addBridge: {addBridge}")
        i += 1
    listener.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', '-i', dest='ip', help='iperf host ip', default='10.242.2.2')
    parser.add_argument('--port', '-p', dest='port', help='iperf host ip', default=6000)
    args = parser.parse_args()
    main(args)

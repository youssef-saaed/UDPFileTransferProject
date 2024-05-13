import sys
import random
import hashlib
import hmac

from socket import (socket, AF_INET, SOCK_DGRAM)
from Helpers import *


class FileTransfer:
    def __init__(self, hostname, port, window_size, timeout, secret_key):
        self.hostname = hostname
        self.port = port
        self.file_id = 0
        self.window_size = window_size
        # Convert the secret key to bytes
        self.secret_key = secret_key.encode('utf-8')
        self.socket = socket(AF_INET, SOCK_DGRAM)

    def send_with_mac(self, data):
        mac = hmac.new(self.secret_key, data, hashlib.sha256).digest()
        return data + mac

    def SendFile(self, filepath):
        packets = FileToSenderPackets(filepath, self.file_id, self.secret_key)
        window_start = 0
        window_end = min(window_start + self.window_size, len(packets) - 1)
        while window_start < len(packets) - 1:
            acks = set()

            for i in range(window_start, window_end):
                if random.random() <= 0.15:
                    continue
                # Add MAC to the packet
                packet = self.send_with_mac(packets[i])
                self.socket.sendto(packet, (self.hostname, self.port))

            # Rest of your code


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "Usage: python FileTransfer.py [file name] [window size] [timeout] [secret key]")
        sys.exit()
    file = sys.argv[1]
    window_size = int(sys.argv[2])
    timeout = float(sys.argv[3])
    secret_key = sys.argv[4]  # Take the secret key as provided
    file_transfer_obj = FileTransfer(
        "localhost", 1255, window_size, timeout, secret_key)
    file_transfer_obj.SendFile(file)

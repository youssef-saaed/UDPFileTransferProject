from socket import (socket, 
                    AF_INET, 
                    SOCK_DGRAM)
from Helpers import *
import random
import sys

class FileTransfer:
    def __init__(self, hostname, port, window_size, timeout):
        self.hostname = hostname
        self.port = port
        self.file_id = 0
        if window_size < 1:
            raise ValueError("Invalid window size!")
        self.window_size = window_size
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.timeout = timeout
        self.socket.settimeout(self.timeout)
        
    def SendFile(self, filepath):
        packets = FileToSenderPackets(filepath, self.file_id)
        window_start = 0
        window_end = min(window_start + self.window_size, len(packets) - 1)
        while window_start < len(packets) - 1:       
            acks = set()
            
            for i in range(window_start, window_end):
                if random.random() <= 0.15:
                    continue
                self.socket.sendto(packets[i], (self.hostname, self.port))
                
            timeout = 0
            while timeout < self.timeout * (window_end - window_start) and len(acks) < window_end - window_start:
                try:
                    ack, _ = self.socket.recvfrom(16)
                    seqeunce, file_id = LongBytesToNum(ack[:8]), LongBytesToNum(ack[8:])
                    if file_id == self.file_id:
                        acks.add(seqeunce)
                except:
                    pass
                timeout += self.timeout
            
            if len(acks) == window_end - window_start:
                window_start = window_end
            else:
                for i in range(window_start, window_end):
                    if not i in acks:
                        window_start = i
                        break
            window_end = min(window_start + self.window_size, len(packets) - 1)
            
        ack = None
        while not ack:
            try:
                self.socket.sendto(packets[-1], (self.hostname, self.port))
                ack, _ = self.socket.recvfrom(16)
                seqeunce, file_id = LongBytesToNum(ack[:8]), LongBytesToNum(ack[8:])
            except:
                pass
            
        self.file_id += 1
        
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python FileTransfer.py [file name] [window size] [timeout]")
        sys.exit()
    file = sys.argv[1]
    window_size = int(sys.argv[2])
    timeout = float(sys.argv[3])
    file_transfer_obj = FileTransfer("localhost", 1255, window_size, timeout)
    file_transfer_obj.SendFile(file)
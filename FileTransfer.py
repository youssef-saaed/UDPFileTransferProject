from socket import (socket, 
                    AF_INET, 
                    SOCK_DGRAM)

from Helpers import *

class FileTransfer:
    def __init__(self, hostname, port, window_size = 3):
        self.hostname = hostname
        self.port = port
        self.file_id = 0
        if window_size < 1:
            raise ValueError("Invalid window size!")
        self.window_size = window_size
        self.socket = socket(AF_INET, SOCK_DGRAM)
        
    def SendFile(self, filepath):
        packets = FileToSenderPackets(filepath, self.file_id)
        window_start = 0
        window_end = min(window_start + self.window_size, len(packets))
        while window_start < len(packets):           
            acks = set()
            
            for i in range(window_start, window_end):
                self.socket.sendto(packets[i], (self.hostname, self.port))
                
            timeout = 0
            while timeout < 0.01 * (window_end - window_start) and len(acks) < window_end - window_start:
                try:
                    self.socket.settimeout(0.01)
                    ack, _ = self.socket.recvfrom(16)
                    seqeunce, file_id = LongBytesToNum(ack[:8]), LongBytesToNum(ack[8:])
                    if file_id == self.file_id:
                        acks.add(seqeunce)
                except:
                    pass
                timeout += 0.01
            
            if len(acks) == window_end - window_start:
                window_start = window_end
            else:
                for i in range(window_start, window_end):
                    if not i in acks:
                        window_start = i
                        break
            window_end = min(window_start + self.window_size, len(packets))
        
if __name__ == "__main__":
    FileTransfer("localhost", 1255)
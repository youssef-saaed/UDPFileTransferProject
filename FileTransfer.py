from socket import (socket, 
                    AF_INET, 
                    SOCK_DGRAM)

def NumToLongBytes(num):
    num_bytes = [0] * 8
    for i in range(7, -1, -1):
        num_bytes[i] = num % 256
        num //= 256
    return num_bytes   

def MakeSenderPacket(buffer, sequence):
    buffer = list(buffer)
    buffer.insert(0, 0)
    sequence_bytes = NumToLongBytes(sequence)
    return sequence_bytes + buffer

def FileToSenderPackets(filepath):
    packets = []
    sequence = 0
    with open(filepath, "rb") as file_handler:
        buffer = file_handler.read(247)
        while buffer:
            packet = MakeSenderPacket(buffer, sequence)
            packets.append(packet)
            sequence += 1
            buffer = file_handler.read(247)
    packets[len(packets) - 1][8] = 1
    return [bytes(packet) for packet in packets]

class FileTransfer:
    def __init__(self, hostname, port, window_size = 3):
        self.hostname = hostname
        self.port = port
        if window_size < 1:
            raise ValueError("Invalid window size!")
        self.window_size = window_size
        self.socket = socket(AF_INET, SOCK_DGRAM)
        
    def SendFile(self, filepath):
        packets = FileToSenderPackets(filepath)
        print(packets)
        
FileTransfer("", 0).SendFile("./files/large file.jpeg")
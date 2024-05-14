from socket import (socket, 
                    AF_INET, 
                    SOCK_DGRAM)
from Helpers import *
import sys

class FileReceiver:
    def __init__(self, port):
        self.port = port
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind(("localhost", port))

    def send_acknowledgement(self, sequence, file_id, address):
        ack_packet = MakeReceiverPacket(sequence, file_id)
        self.sock.sendto(ack_packet, address)

    def order_packets(self, packets):
        ordered_packets = sorted(packets, key=lambda x: x["Sequence"])
        return ordered_packets

    def write_to_file(self, ordered_packets, save_path):
        with open(save_path, "wb") as file:
            for packet in ordered_packets:
                file.write(packet["Data"])

    def receive_file(self, save_path):
        packets = []
        recieved_seq = set()
        while True:
            packet, address = self.sock.recvfrom(256)
            unpacked_packet = Unpack(packet)
            self.send_acknowledgement(unpacked_packet["Sequence"], unpacked_packet["FileID"], address)
            if not unpacked_packet["Sequence"] in recieved_seq:
                packets.append(unpacked_packet)
                recieved_seq.add(unpacked_packet["Sequence"])
            
            if unpacked_packet["Trailer"] == 1:
                break
        ordered_packets = self.order_packets(packets)
        self.write_to_file(ordered_packets, save_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python Reciever.py [file destination]")
        sys.exit()
    secret_key = "pass1234"
    file = sys.argv[1]
    receiver = FileReceiver(1255)
    receiver.receive_file(file)
    print("Done!")
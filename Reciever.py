from socket import (socket, AF_INET, SOCK_DGRAM)
from Helpers import *
import sys
import hashlib
import hmac


class FileReceiver:
    def __init__(self, port, secret_key):
        self.port = port
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind(("localhost", port))
        self.secret_key = secret_key  # Secret key for HMAC

    def send_acknowledgment(self, sequence, file_id, address):
        ack_packet = MakeReceiverPacket(sequence, file_id)
        self.sock.sendto(ack_packet, address)

    def order_packets(self, packets):
        ordered_packets = sorted(packets, key=lambda x: x["Sequence"])
        return ordered_packets

    def write_to_file(self, ordered_packets, save_path):
        with open(save_path, "wb") as file:
            for packet in ordered_packets:
                file.write(packet["Data"])

    def verify_mac(self, data, mac):
        calculated_mac = hmac.new(
            self.secret_key, data, hashlib.sha256).digest()
        return hmac.compare_digest(calculated_mac, mac)

    def receive_file(self, save_path):
        packets = []
        received_seq = set()
        while True:
            packet, address = self.sock.recvfrom(4096)  # Increase buffer size
            unpacked_packet = Unpack(packet)

            # Verify MAC before proceeding
            if not self.verify_mac(unpacked_packet["Data"], unpacked_packet["MAC"]):
                # Handle invalid packet
                continue

            self.send_acknowledgment(
                unpacked_packet["Sequence"], unpacked_packet["FileID"], address)
            if unpacked_packet["Sequence"] not in received_seq:
                packets.append(unpacked_packet)
                received_seq.add(unpacked_packet["Sequence"])

            if unpacked_packet["Trailer"] == 1:
                break
        ordered_packets = self.order_packets(packets)
        self.write_to_file(ordered_packets, save_path)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python Reciever.py [file destination] [secret key]")
        sys.exit()
    file = sys.argv[1]
    secret_key = sys.argv[2].encode('utf-8')  # Convert the secret key to bytes
    receiver = FileReceiver(1255, secret_key)
    receiver.receive_file(file)
    print("Done!")

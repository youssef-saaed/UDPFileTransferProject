from socket import (socket,
                    AF_INET,
                    SOCK_DGRAM)
from Helpers import *
import random
import sys
import time
import matplotlib.pyplot as plt
from datetime import datetime


class FileTransfer:
    def __init__(self, hostname, port, window_size, timeout, secret_key):
        self.hostname = hostname
        self.port = port
        self.file_id = 0
        if window_size < 1:
            raise ValueError("Invalid window size!")
        self.window_size = window_size
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.timeout = timeout
        self.socket.settimeout(self.timeout)
        self.packet_log = []
        self.secret_key = secret_key[:8].encode()

    def SendFile(self, filepath):
        start_T = time.time()
        packets = FileToSenderPackets(filepath, self.file_id)
        window_start = 0
        window_end = min(window_start + self.window_size, len(packets) - 1)
        numOfBytes = 0
        retransmits = 0
        while window_start < len(packets) - 1:
            acks = set()
            for i in range(window_start, window_end):
                if random.random() <= 0.15:
                    continue
                self.socket.sendto(packets[i], (self.hostname, self.port))
                numOfBytes += len(packets[i])
                sended_T = datetime.now()
                self.packet_log.append((sended_T, i, 'sent'))

            timeout = 0
            while timeout < self.timeout * (window_end - window_start) and len(acks) < window_end - window_start:
                try:
                    ack, _ = self.socket.recvfrom(16)
                    sequence, file_id = LongBytesToNum(
                        ack[:8]), LongBytesToNum(ack[8:])
                    if file_id == self.file_id:
                        acks.add(sequence)
                        ack_time = datetime.now()
                        self.packet_log.append((ack_time, sequence, 'ack'))
                except:
                    pass
                timeout += self.timeout

            if len(acks) == window_end - window_start:
                window_start = window_end
            else:
                for i in range(window_start, window_end):
                    if not i in acks:
                        window_start = i
                        retransmits += 1
                        self.packet_log.append(
                            (datetime.now(), i, 'retransmit'))
                        break
            window_end = min(window_start + self.window_size, len(packets) - 1)

        ack = None
        while not ack:
            try:
                self.socket.sendto(packets[-1], (self.hostname, self.port))
                numOfBytes += len(packets[-1])
                ack, _ = self.socket.recvfrom(16)
                seqeunce, file_id = LongBytesToNum(
                    ack[:8]), LongBytesToNum(ack[8:])
            except:
                pass

        self.file_id += 1
        end_T = time.time()
        overall_time = end_T - start_T
        print(f"File received: {filepath}",
              f"Start time: {start_T}",
              f"End time: {end_T}",
              f"Elapsed time: {overall_time} seconds",
              f"Number of packets: {len(packets)}",
              f"Number of bytes: {numOfBytes}",
              f"Throughput: {numOfBytes/overall_time} bytes/sec",
              f"Retransmits: {retransmits}",
              f"Timeout: {self.timeout} seconds",
              f"Window size: {self.window_size}",
              f"Packet Loss: {len(packets) - len(acks)}",
              f"Packet Loss Rate: {(len(packets) - len(acks))/len(packets)}",
              f"packet/sec: {len(packets)/overall_time}",
              "Dn", sep="\n")
        self.plot_packet_log()

    def plot_packet_log(self):
        times_sent = [log[0] for log in self.packet_log if log[2] == 'sent']
        times_ack = [log[0] for log in self.packet_log if log[2] == 'ack']
        times_retransmit = [log[0]
                            for log in self.packet_log if log[2] == 'retransmit']
        seq_sent = [log[1] for log in self.packet_log if log[2] == 'sent']
        seq_ack = [log[1] for log in self.packet_log if log[2] == 'ack']
        seq_retransmit = [log[1]
                          for log in self.packet_log if log[2] == 'retransmit']

        plt.figure(figsize=(10, 6))
        plt.plot(times_sent, seq_sent, 'bo-', label='Sent Packets')
        plt.plot(times_ack, seq_ack, 'go-', label='Acknowledged Packets')
        plt.plot(times_retransmit, seq_retransmit,
                 'ro-', label='Retransmitted Packets')
        plt.xlabel('Time')
        plt.ylabel('Packet Sequence Number')
        plt.title('Packet Sequence Number vs Time')
        plt.grid(True)
        plt.legend()
        plt.show()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: python FileTransfer.py [file name] [window size] [timeout]")
        sys.exit()
    secret_key = "pass1234"
    file = sys.argv[1]
    window_size = int(sys.argv[2])
    timeout = float(sys.argv[3])
    file_transfer_obj = FileTransfer(
        "localhost", 1255, window_size, timeout, secret_key)
    file_transfer_obj.SendFile(file)

# Network Project: File Transfer Protocol

This project implements a file transfer protocol built on UDP with Reliable Data Transfer (RDT) 3.0 and Go-Back-N pipelining. For security, HMAC algorithm is used.

## Project Structure

The project consists of three Python files:

1. `FileTransfer.py`: This script is responsible for sending files.
2. `Receiver.py`: This script is responsible for receiving files.
3. `Helpers.py`: This script contains helper functions used by the sender and receiver scripts.

## FileTransfer.py

This script contains the `FileTransfer` class which is responsible for sending files. The class has the following methods:

- `__init__(self, hostname, port, window_size, timeout, secret_key)`: Initializes the `FileTransfer` object with the given hostname, port, window size, timeout, and secret key.
- `SendFile(self, filepath)`: Sends the file located at `filepath`. It uses a sliding window protocol with a window size specified during the object's initialization. If a packet is not acknowledged within the specified timeout, it is retransmitted.
- `plot_packet_log(self)`: Plots the sequence numbers of sent, acknowledged, and retransmitted packets over time.

## Receiver.py

This script contains the `FileReceiver` class which is responsible for receiving files. The class has the following methods:

- `__init__(self, port, secret_key)`: Initializes the `FileReceiver` object with the given port and secret key.
- `send_acknowledgement(self, sequence, file_id, address)`: Sends an acknowledgement for the packet with the given sequence number and file ID to the specified address.
- `receive_file(self, save_path)`: Receives a file and saves it at `save_path`. It sends acknowledgements for each received packet.
- `plot_packet_log(self)`: Plots the sequence numbers of received packets over time.

## Helpers.py

This script contains helper functions for packet creation, packet unpacking, and conversion between numbers and byte arrays.

## Usage

To send a file, run the `FileTransfer.py` script with the file name, window size, and timeout as command-line arguments. For example:

```bash
python FileTransfer.py [file name] [window size] [timeout]
```

To receive a file, run the `Receiver.py` script with the file destination as a command-line argument. For example:

```bash
python Receiver.py [file destination]
```

## Security

The HMAC algorithm is used for security. The secret key is hardcoded in the `FileTransfer.py` and `Receiver.py` scripts. It is used to create a hash-based message authentication code for each packet. This ensures the integrity and authenticity of the packets. The secret key is truncated to 8 bytes before it is used. 

## Note

This project uses a simple form of error control. If a packet is not acknowledged within the specified timeout, it is assumed to be lost and is retransmitted. This may not work well if the network has high latency. In such a case, the timeout may need to be increased. 

Also, the project uses a simple form of flow control. The sender maintains a window of packets that it can send without waiting for acknowledgements. If an acknowledgement is not received for the first packet in the window within the timeout, all packets in the window are retransmitted. This is known as Go-Back-N ARQ. 

The project also includes a plotting feature that plots the sequence numbers of sent, acknowledged, and retransmitted packets over time. This can be useful for visualizing the performance of the protocol. 

Please note that this project is for educational purposes and may not be suitable for use in a production environment.
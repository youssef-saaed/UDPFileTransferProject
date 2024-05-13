import hashlib
import hmac
import rsa


def NumToLongBytes(num):
    num_bytes = [0] * 8
    for i in range(7, -1, -1):
        num_bytes[i] = num % 256
        num //= 256
    return bytes(num_bytes)


def LongBytesToNum(bytes_arr):
    num = 0
    for i in range(8):
        num = num * 256 + bytes_arr[i]
    return num


def MakeSenderPacket(buffer, sequence, file_id, secret_key):
    buffer = list(buffer)
    buffer.insert(0, 0)
    sequence_bytes = NumToLongBytes(sequence)
    file_id_bytes = NumToLongBytes(file_id)
    # Calculate MAC and append it to the packet
    mac = hmac.new(secret_key, bytes(buffer), hashlib.sha256).digest()
    return sequence_bytes + file_id_bytes + bytes(buffer) + mac


def FileToSenderPackets(filepath, file_id, secret_key):
    packets = []
    sequence = 0
    with open(filepath, "rb") as file_handler:
        buffer = file_handler.read(239)
        while buffer:
            packet = MakeSenderPacket(buffer, sequence, file_id, secret_key)
            packets.append(packet)
            sequence += 1
            buffer = file_handler.read(239)
    # Mark the last packet as the trailer packet
    packets[-1] = packets[-1][:16] + b'\x01' + packets[-1][17:]
    return packets


def Unpack(packet):
    sequence = LongBytesToNum(packet[:8])
    file_id = LongBytesToNum(packet[8:16])
    trailer = int(packet[16])
    data = packet[17:-32]  # Extracting data excluding MAC
    mac = packet[-32:]  # Extract MAC
    return {"Sequence": sequence, "FileID": file_id, "Trailer": trailer, "Data": data, "MAC": mac}


def MakeReceiverPacket(sequence, file_id):
    sequence_bytes = NumToLongBytes(sequence)
    file_id_bytes = NumToLongBytes(file_id)
    return bytes(sequence_bytes + file_id_bytes)


def Unpack_ack(packet):
    sequence = LongBytesToNum(packet[:8])
    file_id = LongBytesToNum(packet[8:16])
    return {"Sequence": sequence, "FileID": file_id}

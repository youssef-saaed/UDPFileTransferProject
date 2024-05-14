import hashlib

def gen_key(key, size):
    f_repeats = size // len(key)
    remainder = size - f_repeats * len(key)
    return key[-remainder - 1 : -1] + key * f_repeats

def NumToLongBytes(num):
    num_bytes = [0] * 8
    for i in range(7, -1, -1):
        num_bytes[i] = num % 256
        num //= 256
    return num_bytes


def LongBytesToNum(bytes_arr):
    num = 0
    for i in range(8):
        num += num * 256 + bytes_arr[i]
    return num


def MakeSenderPacket(buffer, sequence, file_id):
    buffer = list(buffer)
    buffer.insert(0, 0)
    sequence_bytes = NumToLongBytes(sequence)
    file_id_bytes = NumToLongBytes(file_id)
    return sequence_bytes + file_id_bytes + buffer


def FileToSenderPackets(filepath, file_id, secret_key):
    packets = []
    sequence = 0
    with open(filepath, "rb") as file_handler:
        buffer = file_handler.read(463)
        while buffer:
            packet = MakeSenderPacket(buffer, sequence, file_id)
            packets.append(packet)
            sequence += 1
            buffer = file_handler.read(463)
    packets[-1][16] = 1
    packets = [bytes(packet) for packet in packets]
    hmac_key = hashlib.sha256(secret_key).digest()
    key = gen_key(hmac_key, len(packets[0]) + 32)
    for i in range(len(packets)):
        packets[i] += hmac_key
        packets[i] = bytes([a ^ b for a, b in zip(packets[i], key)])
    return packets


def Unpack(packet, secret_key):
    hmac_key = hashlib.sha256(secret_key).digest()
    key = gen_key(hmac_key, len(packet))
    packet = bytes([a ^ b for a, b in zip(packet, key)])
    sequence = LongBytesToNum(packet[:8])
    file_id = LongBytesToNum(packet[8:16])
    trailer = int(packet[16])
    data = packet[17:-32]
    return {"Sequence": sequence, "FileID": file_id, "Trailer": trailer, "Data": data, "HashedKey": packet[-32:]}


def MakeReceiverPacket(sequence, file_id):
    sequence_bytes = NumToLongBytes(sequence)
    file_id_bytes = NumToLongBytes(file_id)
    return bytes(sequence_bytes + file_id_bytes)


def Unpack_ack(packet):
    sequence = LongBytesToNum(packet[:8])
    file_id = LongBytesToNum(packet[8:16])
    return {"Sequence": sequence, "FileID": file_id}

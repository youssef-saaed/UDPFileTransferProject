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

def FileToSenderPackets(filepath, file_id):
    packets = []
    sequence = 0
    with open(filepath, "rb") as file_handler:
        buffer = file_handler.read(239)
        while buffer:
            packet = MakeSenderPacket(buffer, sequence, file_id)
            packets.append(packet)
            sequence += 1
            buffer = file_handler.read(239)
    packets[len(packets) - 1][16] = 1
    return [bytes(packet) for packet in packets]

def Unpack(packet):
    sequence = LongBytesToNum(packet[:8])
    file_id = LongBytesToNum(packet[8:16])
    trailer = int(packet[16])
    data = packet[17:]
    return {"Sequence": sequence, "FileID": file_id, "Trailer": trailer, "Data": data}
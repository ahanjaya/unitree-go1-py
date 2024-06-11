import struct

from src.utils.modes import ModelName, RobotType


def float_to_hex(f):
    return (struct.unpack(">I", struct.pack(">f", f))[0]).to_bytes(4, "little")


def hex_to_float(hex):
    # Convert bytes to integer with little-endian order
    int_data = int.from_bytes(hex, "little")

    # Pack integer to bytes with big-endian order and unpack as float
    return struct.unpack(">f", struct.pack(">I", int_data))[0]


def gen_crc(i) -> bytes:
    crc = 0xFFFFFFFF
    for j in struct.unpack("<%dI" % (len(i) / 4), i):
        for b in range(32):
            x = (crc >> 31) & 1
            crc <<= 1
            crc &= 0xFFFFFFFF
            if x ^ (1 & (j >> (31 - b))):
                crc ^= 0x04C11DB7
    crc = struct.pack("<I", crc)

    return crc


def encrypt_crc(crc_val) -> bytearray:
    crc_val = int.from_bytes(crc_val, byteorder="little")
    xor_val = 0xEDCAB9DE
    val = crc_val ^ xor_val
    data = struct.pack("<I", val)

    return bytearray(data[i] for i in [1, 2, 3, 0])


def byte_print(bytes) -> str:
    return "".join("{:02x}".format(x) for x in bytes)


def decode_sn(data):
    type_data, model_data = data[:2]
    type_name = RobotType(type_data)
    model_name = ModelName(model_data)

    product_name = f"{type_name}-{model_name}"
    id = f"{data[2]}-{data[3]}-{data[4]}[{data[5]}]"

    return product_name, id


def decode_version(data):
    hardware_version = f"{data[0]}.{data[1]}.{data[2]}"
    software_version = f"{data[3]}.{data[4]}.{data[5]}"

    return hardware_version, software_version


def sum_total_voltage(cell_voltages) -> int:
    return sum(cell_voltages) / 1000

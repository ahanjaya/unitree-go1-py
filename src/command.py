from typing import Tuple

from src.utils.common import byte_print, encrypt_crc, float_to_hex, gen_crc
from src.utils.modes import GaitType, MotorModeHigh, SpeedLevel


class BMSCmd:
    """The command to retrieve bms state."""

    def __init__(
        self, off: int = 0, reserve: Tuple[int, int, int] = [0, 0, 0]
    ) -> None:
        self.off = off
        self.reserve = reserve

    def get_bytes(self):
        return (
            (self.off).to_bytes(1, byteorder="little")
            + self.reserve[0].to_bytes(1, byteorder="little")
            + self.reserve[1].to_bytes(1, byteorder="little")
            + self.reserve[2].to_bytes(1, byteorder="little")
        )

    def from_bytes(self, data: bytes):
        self.off = data[0]
        self.reserve = [data[1], data[2], data[3]]
        return self


class LEDCmd:
    """Foot led brightness (0~255)"""

    def __init__(self, r: int, g: int, b: int) -> None:
        self.r = r
        self.g = g
        self.b = b

    def get_bytes(self) -> bytes:
        return (
            (self.r).to_bytes(1, byteorder="little")
            + (self.g).to_bytes(1, byteorder="little")
            + (self.b).to_bytes(1, byteorder="little")
            + bytes(1)
        )


class HighCmd(object):
    def __init__(self) -> None:
        self.head = bytes.fromhex("FEEF")
        self.level_flag = 0x00
        self.frame_reserve = 0
        self.SN = bytearray(8)
        self.version = bytearray(8)
        self.bandWidth = bytearray(2)
        self.mode = MotorModeHigh.IDLE
        self.gait_type = GaitType.IDLE
        self.speed_level = SpeedLevel.LOW_SPEED
        self.foot_raise_height = 0.0
        self.body_height = 0.0
        self.position = [0.0, 0.0]
        self.euler = [0.0, 0.0, 0.0]
        self.velocity = [0.0, 0.0]
        self.yawSpeed = 0.0
        self.bms = BMSCmd(0, [0, 0, 0])
        self.led = LEDCmd(0, 0, 0)
        self.wireless_remote = bytearray(40)
        self.reserve = bytearray(4)
        self.crc = None

    def build_cmd(
        self, encrypt: bool = False, debug: bool = False
    ) -> bytearray:
        cmd = bytearray(129)
        cmd[0:2] = self.head
        cmd[2] = self.level_flag
        cmd[3] = self.frame_reserve

        cmd[4:12] = self.SN
        cmd[12:20] = self.version
        cmd[20:22] = self.bandWidth

        cmd[22] = self.mode.value
        cmd[23] = self.gait_type.value
        cmd[24] = self.speed_level.value

        cmd[25:29] = float_to_hex(self.foot_raise_height)
        cmd[29:33] = float_to_hex(self.body_height)

        cmd[33:37] = float_to_hex(self.position[0])
        cmd[37:41] = float_to_hex(self.position[1])

        cmd[41:45] = float_to_hex(self.euler[0])
        cmd[45:49] = float_to_hex(self.euler[1])
        cmd[49:53] = float_to_hex(self.euler[2])

        cmd[53:57] = float_to_hex(self.velocity[0])
        cmd[57:61] = float_to_hex(self.velocity[1])

        cmd[61:65] = float_to_hex(self.yawSpeed)
        cmd[65:69] = self.bms.get_bytes()
        cmd[69:73] = self.led.get_bytes()
        cmd[73:113] = self.wireless_remote
        cmd[113:117] = self.reserve

        if encrypt:
            cmd[-4:] = encrypt_crc(gen_crc(cmd[:-5]))
        else:
            cmd[-4:] = gen_crc(cmd[:-5])

        if debug:
            print(f"Send Data ({len(cmd)}): {byte_print(cmd)}")

        return cmd

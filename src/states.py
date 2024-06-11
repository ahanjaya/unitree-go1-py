from typing import Tuple

from src.command import HighCmd
from src.utils.common import (byte_print, decode_sn, decode_version,
                              hex_to_float, sum_total_voltage)
from src.utils.custom_types import (IMU, BMSState, Cartesian, FootForce,
                                    FootPose, FootSpeed, MotorState, Velocity)
from src.utils.modes import GaitType, MotorModeHigh


class HighState(object):
    def __init__(self) -> None:
        """Represent Go1 state in HighLevel mode."""

        self.head: Tuple[str, str]  # reserve
        self.level_flag: int  # reserve
        self.frame_reserve: int  # reserve
        self.serial_number: Tuple[str, str]  # reserve
        self.version: Tuple[str, str]  # reserve
        self.bandwidth: int
        self.imu: IMU
        self.motor_states: Tuple[
            MotorState,
            MotorState,
            MotorState,
            MotorState,
            MotorState,
            MotorState,
            MotorState,
            MotorState,
            MotorState,
            MotorState,
            MotorState,
            MotorState,
            MotorState,
            MotorState,
            MotorState,
            MotorState,
            MotorState,
            MotorState,
            MotorState,
            MotorState,
        ]
        self.bms: BMSState
        self.foot_force: FootForce  # Data from foot airbag sensor
        self.foot_force_est: FootForce  # reserve, typically zero
        self.mode: MotorModeHigh
        self.progress: float  # reserve
        self.gait_type: GaitType
        self.foot_raise_height: (
            float  # (unit m, default: 0.08m), foot up height while walking
        )
        self.position: (
            Cartesian  # (unit m) from own odometry in inertial frame
        )
        self.body_height: float  # (unit: m, default: 0.28m)
        self.velocity: Velocity  # (unit: m/s), vx, vy, vz in body frame
        self.yaw_speed: float  # (unit: rad/s), rotate speed in body frame
        self.range_obstacle: Tuple[
            float, float, float, float
        ]  # Distance to nearest obstacle
        self.foot_position_to_body: FootPose
        self.foot_speed_to_body: FootSpeed
        self.wireless_remote: Tuple[  # Data from Unitree Joystick
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
            int,
        ]
        self.reserve: int

    def data_to_bms_state(self, data) -> BMSState:
        version_h = data[0]
        version_l = data[1]
        bms_status = data[2]
        SOC = data[3]
        current = int.from_bytes(data[4:8], byteorder="little", signed=True)
        cycle = int.from_bytes(data[8:10], byteorder="little")
        BQ_NTC = [data[10], data[11]]
        MCU_NTC = [data[12], data[13]]

        cell_vol = [
            int.from_bytes(
                data[14 + idx * 2 : 16 + idx * 2], byteorder="little"
            )
            for idx in range(10)
        ]
        return BMSState(
            version_h,
            version_l,
            bms_status,
            SOC,
            current,
            cycle,
            BQ_NTC,
            MCU_NTC,
            cell_vol,
        )

    def data_to_IMU(self, data) -> IMU:
        quaternion = [
            hex_to_float(data[0 + idx * 4 : 4 + idx * 4]) for idx in range(4)
        ]
        gyroscope = [
            hex_to_float(data[16 + idx * 4 : 20 + idx * 4]) for idx in range(3)
        ]
        accelerometer = [
            hex_to_float(data[28 + idx * 4 : 32 + idx * 4]) for idx in range(3)
        ]
        rpy = [
            hex_to_float(data[40 + idx * 4 : 44 + idx * 4]) for idx in range(3)
        ]
        temperature = data[52]

        return IMU(quaternion, gyroscope, accelerometer, rpy, temperature)

    def data_to_motor_state(self, data) -> MotorState:
        mode = data[0]
        q = hex_to_float(data[1:5])
        dq = hex_to_float(data[5:9])
        ddq = hex_to_float(data[9:13])
        tauEst = hex_to_float(data[13:17])
        q_raw = hex_to_float(data[17:21])
        dq_raw = hex_to_float(data[21:25])
        ddq_raw = hex_to_float(data[25:29])
        temperature = data[29]
        reserve = [data[30], data[31]]

        return MotorState(
            mode,
            q,
            dq,
            ddq,
            tauEst,
            q_raw,
            dq_raw,
            ddq_raw,
            temperature,
            reserve,
        )

    def parse_data(self, data) -> None:
        if data is None:
            return

        self.head = hex(int.from_bytes(data[0:2], byteorder="little"))
        self.level_flag = data[2]
        self.frame_reserve = data[3]
        self.SN = data[4:12]
        self.version = data[12:20]
        self.bandwidth = int.from_bytes(data[20:22], byteorder="little")
        self.imu = self.data_to_IMU(data[22:75])
        self.motor_states = []
        for idx in range(20):
            self.motor_states.append(
                self.data_to_motor_state(
                    data[(idx * 32) + 75 : (idx * 32) + 32 + 75]
                )
            )
        # FIX FROM HERE!!!
        self.bms = self.data_to_bms_state(data[835:869])
        self.foot_force = FootForce(
            int.from_bytes(data[869:871], byteorder="little"),
            int.from_bytes(data[871:873], byteorder="little"),
            int.from_bytes(data[873:875], byteorder="little"),
            int.from_bytes(data[875:877], byteorder="little"),
        )
        self.foot_force_est = FootForce(
            int.from_bytes(data[877:879], byteorder="little"),
            int.from_bytes(data[879:881], byteorder="little"),
            int.from_bytes(data[881:883], byteorder="little"),
            int.from_bytes(data[883:885], byteorder="little"),
        )
        self.mode = MotorModeHigh(data[885])
        self.progress = hex_to_float(data[886:890])
        self.gait_type = GaitType(data[890])
        self.foot_raise_height = hex_to_float(data[891:895])
        self.position = Cartesian(
            hex_to_float(data[895:899]),
            hex_to_float(data[899:903]),
            hex_to_float(data[903:907]),
        )
        self.body_height = hex_to_float(data[907:911])
        self.velocity = Velocity(
            hex_to_float(data[911:915]),
            hex_to_float(data[915:919]),
            hex_to_float(data[919:923]),
        )
        self.yaw_speed = hex_to_float(data[923:927])
        self.range_obstacle = [
            hex_to_float(data[927:931]),
            hex_to_float(data[931:935]),
            hex_to_float(data[935:939]),
            hex_to_float(data[939:943]),
        ]
        foot_position_to_body = []
        for idx in range(4):
            foot_position_to_body.append(
                Cartesian(
                    hex_to_float(data[(idx * 12) + 943 : (idx * 12) + 947]),
                    hex_to_float(data[(idx * 12) + 947 : (idx * 12) + 951]),
                    hex_to_float(data[(idx * 12) + 951 : (idx * 12) + 955]),
                )
            )
        self.foot_position_to_body = FootPose(*foot_position_to_body)

        foot_speed_to_body = []
        for idx in range(4):
            foot_speed_to_body.append(
                Velocity(
                    hex_to_float(data[(idx * 12) + 991 : (idx * 12) + 995]),
                    hex_to_float(data[(idx * 12) + 995 : (idx * 12) + 999]),
                    hex_to_float(data[(idx * 12) + 999 : (idx * 12) + 1003]),
                )
            )
        self.foot_speed_to_body = FootSpeed(*foot_speed_to_body)

        self.wireless_remote = data[1039:1079]
        self.reserve = data[1079:1083]
        self.crc = data[1083:1087]

    def print_states(self) -> None:
        print(
            "+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+="
        )
        print(f"Head:\t\t\t{self.head}")
        print(f"Level Flag:\t\t{self.level_flag}")
        print(f"Frame Reserve:\t\t{self.frame_reserve}")
        print(f"SN [{byte_print(self.SN)}]:\t{decode_sn(self.SN)}")
        print(
            f"Ver [{byte_print(self.version)}]:\t{decode_version(self.version)}"
        )
        print(f"Bandwidth:\t\t{self.bandwidth}")
        print("IMU")
        print(f"\tQuaternion:\t{self.imu.quaternion}")
        print(f"\tGyroscope:\t{self.imu.gyroscope}")
        print(f"\tAccelerometer:\t{self.imu.accelerometer}")
        print(f"\tRPY:\t\t{self.imu.rpy}")
        print(f"\tTemp.:\t\t{self.imu.temperature}")

        print("Motor State")
        for idx, motor in enumerate(self.motor_states):
            print(
                f"\t{idx} | mode:{motor.mode} q:{motor.q:.5f} dq:{motor.dq:.5f} temp:{motor.temperature}"
            )

        print("Battery Management System")
        print(f"\tSOC:\t\t{self.bms.SOC} %")
        print(f"\tVoltage:\t{sum_total_voltage(self.bms.cell_vol)} volt")
        print(f"\tCurrent:\t{self.bms.current} mA")
        print(f"\tCycles:\t\t{self.bms.cycle}")
        print(f"\tTemps BQ:\t{self.bms.BQ_NTC[0]} °C, {self.bms.BQ_NTC[1]}°C")
        print(
            f"\tTemps MCU:\t{self.bms.MCU_NTC[0]} °C, {self.bms.MCU_NTC[1]}°C"
        )

        print(f"Foot Force:\t\t{self.foot_force}")
        print(f"Foot Force Est:\t\t{self.foot_force_est}")
        print(f"Mode:\t\t\t{self.mode}")
        print(f"Progress:\t\t{self.progress}")
        print(f"Gait Type:\t\t{self.gait_type}")
        print(f"Foot Raise Height:\t{self.foot_raise_height}")
        print(f"Position:\t\t{self.position}")
        print(f"Body Height:\t\t{self.body_height}")
        print(f"Velocity:\t\t{self.velocity}")
        print(f"Yaw Speed:\t\t{self.yaw_speed}")
        print(f"Range Obstacle:\t\t{self.range_obstacle}")

        print("Foot Position to Body")
        print(f"\tfront_right:\t{self.foot_position_to_body.front_right}")
        print(f"\tfront_left:\t{self.foot_position_to_body.front_left}")
        print(f"\trear_right:\t{self.foot_position_to_body.rear_right}")
        print(f"\trear_left:\t{self.foot_position_to_body.rear_left}")

        print("Foot Speed to Body")
        print(f"\tfront_right:\t{self.foot_speed_to_body.front_right}")
        print(f"\tfront_left:\t{self.foot_speed_to_body.front_left}")
        print(f"\trear_right:\t{self.foot_speed_to_body.rear_right}")
        print(f"\trear_left:\t{self.foot_speed_to_body.rear_left}")

        print(f"Wireless Remote:\t{self.wireless_remote}")
        print(f"Reserve:\t\t{self.reserve}")
        print(f"CRC:\t\t\t{self.crc}")
        print(
            "+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+="
        )

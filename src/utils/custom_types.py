from typing import NamedTuple, Tuple


class Velocity(NamedTuple):
    """Represent a veolcity command."""

    vx: float
    vy: float
    vz: float


class Pose(NamedTuple):
    """Represent a pose direction command."""

    lean_left_right: float
    twist_left_right: float
    look_up_down: float
    extend_squat: float


class LED(NamedTuple):
    """Represent a LED RGB values."""

    r: int
    g: int
    b: int


class Cartesian(NamedTuple):
    """Represent a 3 axis values in cartesian."""

    x: float
    y: float
    z: float


class Quaternion(NamedTuple):
    """Represent a quaternion orientation values."""

    w: float
    x: float
    y: float
    z: float


class Euler(NamedTuple):
    """Represent an euler orientation values."""

    roll: float
    pitch: float
    yaw: float


class IMU(NamedTuple):
    """Represent an IMU values."""

    quaternion: Quaternion
    gyroscope: Cartesian
    accelerometer: Cartesian
    rpy: Euler
    temperature: int


class MotorState(NamedTuple):
    """Represent a motor state values."""

    mode: int
    q: float
    dq: float
    ddq: float
    tau_est: float
    q_raw: float
    dq_raw: float
    ddq_raw: float
    temperature: int
    reserve: Tuple[int, int]


class BMSState(NamedTuple):
    """Represent battery management system (BMS) state."""

    version_h: int
    version_l: int
    bms_status: int
    SOC: int
    current: int
    cycle: int
    BQ_NTC: Tuple[int, int]
    MCU_NTC: Tuple[int, int]
    cell_vol: Tuple[int, int, int, int, int, int, int, int, int, int]


class FootForce(NamedTuple):
    """Represent foot force."""

    front_right: int
    front_left: int
    rear_right: int
    rear_left: int


class FootPose(NamedTuple):
    """Represent foot pose."""

    front_right: Cartesian
    front_left: Cartesian
    rear_right: Cartesian
    rear_left: Cartesian


class FootSpeed(NamedTuple):
    """Represent foot velocity."""

    front_right: Velocity
    front_left: Velocity
    rear_right: Velocity
    rear_left: Velocity

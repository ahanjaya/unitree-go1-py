from enum import Enum, StrEnum


class Mode(StrEnum):
    """Available modes in Go1 robot."""

    dance_1 = "dance1"
    dance_2 = "dance2"
    straight_hand = "straightHand1"
    jump_yaw = "jumpYaw"
    damping = "damping"
    stand_up = "standUp"
    stand_down = "standDown"
    recover_stand = "recoverStand"
    stand = "stand"
    walk = "walk"
    run = "run"
    climb = "climb"


class MotorModeHigh(Enum):
    IDLE = 0
    FORCE_STAND = 1
    VEL_WALK = 2
    POS_WALK = 3
    PATH = 4
    STAND_DOWN = 5
    STAND_UP = 6
    DAMPING = 7
    RECOVERY = 8
    BACKFLIP = 9
    JUMPYAW = 10
    STRAIGHTHAND = 11
    DANCE1 = 12
    DANCE2 = 13


class GaitType(Enum):
    IDLE = 0
    TROT = 1
    TROT_RUNNING = 2
    CLIMB_STAIR = 3
    TROT_OBSTACLE = 4


class SpeedLevel(Enum):
    LOW_SPEED = 0
    MEDIUM_SPEED = 1
    HIGH_SPEED = 2


class Motor(Enum):
    FR_0 = 0
    FR_1 = 1
    FR_2 = 2
    FL_0 = 3
    FL_1 = 4
    FL_2 = 5
    RR_0 = 6
    RR_1 = 7
    RR_2 = 8
    RL_0 = 9
    RL_1 = 10
    RL_2 = 11


class RobotType(Enum):
    Laikago = 1
    Aliengo = 2
    A1 = 3
    Go1 = 4
    B1 = 5


class ModelName(Enum):
    AIR = 1
    PRO = 2
    EDU = 3
    PC = 4
    XX = 5

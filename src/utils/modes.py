from enum import StrEnum


class Mode(StrEnum):
    """Available modes in Go1 robot."""

    dance_1 = "dance1"
    dance_2 = "dance2"
    straight_hand = "straightHand1",
    jump_yaw = "jumpYaw"
    damping = "damping",
    stand_up = "standUp",
    stand_down = "standDown",
    recover_stand = "recoverStand",
    stand = "stand",
    walk = "walk",
    run = "run",
    climb = "climb",

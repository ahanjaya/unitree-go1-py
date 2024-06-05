from src.config import Config
from src.utils.connections import Go1Mqtt
from src.utils.custom_types import LED, Pose, Velocity
from src.utils.modes import Mode


class Go1(object):
    def __init__(self, config: Config) -> None:
        self._config = config

        self._go1_client = Go1Mqtt(
            self._config.go1_host,
            self._config.go1_port,
            self._config.go1_keepalive,
        )

    ###########################################
    # Stand command.
    def stand_up(self) -> None:
        self._go1_client.switch_mode(Mode.stand_up)

    def stand_down(self) -> None:
        self._go1_client.switch_mode(Mode.stand_down)

    def recover_stand(self) -> None:
        self._go1_client.switch_mode(Mode.recover_stand)

    ###########################################
    # Go1 Modes
    def set_stand_mode(self) -> None:
        self.pose(Pose(0.0, 0.0, 0.0, 0.0))
        self._go1_client.switch_mode(Mode.stand)

    def set_walk_mode(self) -> None:
        self.walk(Velocity(0.0, 0.0, 0.0))
        self._go1_client.switch_mode(Mode.walk)

    def set_run_mode(self) -> None:
        self.walk(Velocity(0.0, 0.0, 0.0))
        self._go1_client.switch_mode(Mode.run)

    def set_climb_mode(self) -> None:
        self.walk(Velocity(0.0, 0.0, 0.0))
        self._go1_client.switch_mode(Mode.climb)

    def set_damping_mode(self) -> None:
        self._go1_client.switch_mode(Mode.damping)

    ###########################################
    # Entertainment motion
    def dance_1(self) -> None:
        self._go1_client.switch_mode(Mode.dance_1)

    def dance_2(self) -> None:
        self._go1_client.switch_mode(Mode.dance_2)

    def straight_hand(self) -> None:
        self._go1_client.switch_mode(Mode.straight_hand)

    def jump_yaw(self) -> None:
        self._go1_client.switch_mode(Mode.jump_yaw)

    ###########################################
    # Command velocity -> requires walk/run/climb mode to be set.
    def walk(self, cmd_vel: Velocity) -> None:
        self._go1_client.send_cmd_vel(cmd_vel)

    ###########################################
    # Command pose -> requires stand_mode to be set.
    def pose(self, cmd_pose: Pose) -> None:
        self._go1_client.send_cmd_pose(cmd_pose)

    ###########################################
    # Change LED color
    def set_led(self, led: LED) -> None:
        self._go1_client.set_led_color(led)

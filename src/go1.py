import threading
import time

from src.camera import Go1Camera
from src.command import HighCmd
from src.config import Config
from src.connections import Go1Mqtt, Go1UDP
from src.states import HighState
from src.utils.custom_types import LED, Pose, Velocity
from src.utils.modes import Mode


class Go1(object):
    def __init__(self, config: Config) -> None:
        self._config = config

        self._init_com()
        self.high_state = HighState()
        self._init_cam()

    def _init_com(self) -> None:
        """Init communication network with Go1 robot."""
        # MQTT for send high level command.
        self._go1_mqttc = Go1Mqtt(
            self._config.go1_host,
            self._config.go1_mqttc_port,
            self._config.go1_mqttc_keepalive,
        )

        # UDP for receiving high level state.
        self._go1_udp = Go1UDP(
            self._config.go1_host,
            self._config.go1_udp_port_high,
        )

        self._debug = False
        self._polling = threading.Event()
        self._polling_states_thread = threading.Thread(
            target=self._polling_states_thread_func,
            args=(
                self._polling,
                self._debug,
            ),
        )
        self._polling_states_thread.start()

    def _init_cam(self) -> None:
        if not self._config.camera_enable:
            return

        self.cam_front = Go1Camera(
            host=self._config.pc_host, port=self._config.port_front
        )
        self.cam_jaw = Go1Camera(
            host=self._config.pc_host, port=self._config.port_jaw
        )
        self._go1_cam_left = Go1Camera(
            host=self._config.pc_host, port=self._config.port_left
        )
        self._go1_cam_right = Go1Camera(
            host=self._config.pc_host, port=self._config.port_right
        )
        self._go1_cam_belly = Go1Camera(
            host=self._config.pc_host, port=self._config.port_belly
        )

    def _polling_states_thread_func(self, event, debug: bool) -> None:
        high_cmd = HighCmd()
        cmd_bytes = high_cmd.build_cmd()
        self._go1_udp.send(cmd_bytes)
        time.sleep(0.5)

        print("Polling States Thread: Started.")
        while not event.is_set():
            self._go1_udp.send(cmd_bytes)
            self.high_state.parse_data(self._go1_udp.received_bytes)

            if debug:
                self.high_state.print_states()

            time.sleep(0.1)

        print("Polling States Thread: Stopped.")

    def close_all_connection(self) -> None:
        self._polling.set()
        self._polling_states_thread.join()

        self._go1_mqttc.disconnect()
        self._go1_udp.disconnect()

        # Close all camera
        if not self._config.camera_enable:
            return

        self.cam_front.close()
        self.cam_jaw.close()
        self.cam_left.close()
        self.cam_right.close()
        self.cam_belly.close()

    ###########################################
    # Stand command.
    def stand_up(self) -> None:
        self._go1_mqttc.switch_mode(Mode.stand_up)

    def stand_down(self) -> None:
        self._go1_mqttc.switch_mode(Mode.stand_down)

    def recover_stand(self) -> None:
        self._go1_mqttc.switch_mode(Mode.recover_stand)

    ###########################################
    # Go1 Modes
    def set_stand_mode(self) -> None:
        self.pose(Pose(0.0, 0.0, 0.0, 0.0))
        self._go1_mqttc.switch_mode(Mode.stand)

    def set_walk_mode(self) -> None:
        self.walk(Velocity(0.0, 0.0, 0.0))
        self._go1_mqttc.switch_mode(Mode.walk)

    def set_run_mode(self) -> None:
        self.walk(Velocity(0.0, 0.0, 0.0))
        self._go1_mqttc.switch_mode(Mode.run)

    def set_climb_mode(self) -> None:
        self.walk(Velocity(0.0, 0.0, 0.0))
        self._go1_mqttc.switch_mode(Mode.climb)

    def set_damping_mode(self) -> None:
        self._go1_mqttc.switch_mode(Mode.damping)

    ###########################################
    # Entertainment motion
    def dance_1(self) -> None:
        self._go1_mqttc.switch_mode(Mode.dance_1)

    def dance_2(self) -> None:
        self._go1_mqttc.switch_mode(Mode.dance_2)

    def straight_hand(self) -> None:
        self._go1_mqttc.switch_mode(Mode.straight_hand)

    def jump_yaw(self) -> None:
        self._go1_mqttc.switch_mode(Mode.jump_yaw)

    ###########################################
    # Command velocity -> requires walk/run/climb mode to be set.
    def walk(self, cmd_vel: Velocity) -> None:
        self._go1_mqttc.send_cmd_vel(cmd_vel)

    ###########################################
    # Command pose -> requires stand_mode to be set.
    def pose(self, cmd_pose: Pose) -> None:
        self._go1_mqttc.send_cmd_pose(cmd_pose)

    ###########################################
    # Change LED color
    def set_led(self, led: LED) -> None:
        self._go1_mqttc.set_led_color(led)

import random
import struct

import numpy as np
import paho.mqtt.client as mqtt_client

from src.utils.custom_types import LED, Pose, Velocity
from src.utils.modes import Mode
from src.utils.topics import PubTopic


class Go1Mqtt(object):
    """MQTT client communication with Go1 Robot."""

    def __init__(self, host: str, port: int, keepalive: int) -> None:
        """Create an instance of Go1 MQTT client connection.

        Parameters
        ----------

        host: str
            The host name or IP address of Go1 robot.
        port: int
            The network port of the server host to connect to.
        keepalive: int
            Maximum period in seconds between communications with the broker.

        """
        self._host = host
        self._port = port
        self._keepalive = keepalive
        self._client_id = f"python-mqtt-{random.randint(0, 1000)}"
        self._protocol = None

        self._mqttc = mqtt_client.Client(
            client_id=self._client_id,
            callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
        )
        self._connect()

    def _connect(self) -> None:
        def on_connect(client, userdata, flags, rc, properties) -> None:
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print(f"Failed to connect, return code {rc}.")

        self._mqttc.on_connect = on_connect
        self._mqttc.connect(self._host, self._port, self._keepalive)
        self._mqttc.loop_start()

    def _disconnect(self) -> None:
        self._mqttc.disconnect()

    def _clip_cmd_vel(self, cmd_vel: Velocity) -> Velocity:
        cmd_x = np.clip(cmd_vel.vx, -1.0, 1.0)
        cmd_y = np.clip(cmd_vel.vy, -1.0, 1.0)
        cmd_theta = np.clip(cmd_vel.vz, -1.0, 1.0)

        return Velocity(cmd_x, cmd_y, cmd_theta)

    def _clip_cmd_pose(self, cmd_pose: Pose) -> Pose:
        lean_left_right = np.clip(cmd_pose.lean_left_right, -1.0, 1.0)
        twist_left_right = np.clip(cmd_pose.twist_left_right, -1.0, 1.0)
        look_up_down = np.clip(cmd_pose.look_up_down, -1.0, 1.0)
        extend_squat = np.clip(cmd_pose.extend_squat, -1.0, 1.0)

        return Pose(
            lean_left_right,
            twist_left_right,
            look_up_down,
            extend_squat,
        )

    def _clip_led_val(self, led: LED) -> LED:
        r = np.clip(led.r, 0, 255)
        g = np.clip(led.g, 0, 255)
        b = np.clip(led.b, 0, 255)

        return LED(r, g, b)

    def switch_mode(self, mode: Mode) -> None:
        """Switch operation mode.

        Parameters
        ----------

        mode: Mode
            The operation mode name.
        """
        self._mqttc.publish(topic=PubTopic.action, payload=mode, qos=1)

    def send_cmd_vel(self, cmd_vel: Velocity) -> None:
        """Controlling command velocity of the robot.

        Parameters
        ----------

        cmd_vel: Velocity
            Command velocity in linear and angular.
            Vx -> Linear X
            Vy -> Linear Y
            Vz -> Angular Z

        TODO: Zero out the command velocity buffer.
        """
        cmd_vel = self._clip_cmd_vel(cmd_vel)
        cmd_data = [cmd_vel.vy, cmd_vel.vz, 0.0, cmd_vel.vx]
        bytes_data = struct.pack("ffff", *cmd_data)
        self._mqttc.publish(topic=PubTopic.stick, payload=bytes_data, qos=0)

    def send_cmd_pose(self, cmd_pose: Pose) -> None:
        """Controlling command velocity of the robot.

        Parameters
        ----------

        cmd_pose: Pose
            The pose command of robot.

        TODO: Zero out the command pose buffer.
        """
        cmd_pose = self._clip_cmd_pose(cmd_pose)
        cmd_data = [
            cmd_pose.lean_left_right,
            cmd_pose.twist_left_right,
            cmd_pose.look_up_down,
            cmd_pose.extend_squat,
        ]
        bytes_data = struct.pack("ffff", *cmd_data)
        self._mqttc.publish(topic=PubTopic.stick, payload=bytes_data, qos=0)

    def set_led_color(self, led: LED) -> None:
        """Set LED color.

        The alternative command to set LED color.
        self._mqttc.publish(
            topic=PubTopic.code,
            payload=f"child_conn.send('change_light({led.r},{led.g},{led.b})')",
            qos=0
        )

        Parameters
        ----------

        led: LED
            The RGB values with range (0-255).
        """
        led = self._clip_led_val(led)
        self._mqttc.publish(
            topic=PubTopic.led,
            payload=bytes([led.r, led.g, led.b]),
            qos=1,
        )

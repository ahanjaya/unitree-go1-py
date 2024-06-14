import binascii
import random
import socket
import struct
import sys
import threading

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
            """
            Add after rc == 0, for subsribe topic
            client.subscribe(SubTopic.firmware)
            client.subscribe(SubTopic.bms)
            """
            if rc == 0:
                print("Connected to Go1 MQTT Broker!")
            else:
                print(f"Failed to connect, return code {rc}.")

        def on_message(client, userdata, msg) -> None:
            str_payload = str(binascii.hexlify(msg.payload))
            print(f"[Message]: {msg.topic} --> {str_payload}")

        self._mqttc.on_connect = on_connect
        self._mqttc.on_message = on_message
        try:
            self._mqttc.connect(self._host, self._port, self._keepalive)
        except socket.timeout as err:
            print(
                f"[MQTT] TimeoutError: Connection to {self._host}:{self._port} {err}."
            )
            print(
                "[MQTT] Make sure you connected to robot network wireless/wired"
            )
            sys.exit(1)
        self._mqttc.loop_start()

    def disconnect(self) -> None:
        self._mqttc.disconnect()
        self._mqttc.loop_stop()

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

        """
        # Zero out velocity buffer before executing.
        cmd_data = [0.0, 0.0, 0.0, 0.0]
        bytes_data = struct.pack("ffff", *cmd_data)
        self._mqttc.publish(topic=PubTopic.stick, payload=bytes_data, qos=0)

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


class Go1UDP(object):
    """UDP client communication with Go1 Robot."""

    def __init__(self, host: str, port: int) -> None:
        """Create an instance of Go1 UDP client connection.

        Parameters
        ----------

        host: str
            The host name or IP address of Go1 robot.
        port: int
            The network port of the server host to connect to.

        """
        self._host = host
        self._port = port

        self._connect()
        self._run_receive_thread = threading.Event()
        self._receive_thread = threading.Thread(
            target=self._receive_thread_func, args=(self._run_receive_thread,)
        )
        self._receive_thread.daemon = True
        self._receive_thread.start()
        self.received_bytes = None

    def _connect(self) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.settimeout(2.0)
        try:
            self._socket.connect((self._host, self._port))
        except socket.timeout as err:
            print(
                f"[UDP] TimeoutError: Connection to {self._host}:{self._port} {err}."
            )
            self._socket.close()
            print(
                "[UDP] Make sure you connected to robot network wireless/wired"
            )
            sys.exit(1)

    def send(self, cmd) -> None:
        self._socket.sendto(cmd, (self._host, self._port))

    def _receive_thread_func(self, event):
        print("Receive UDP thread: Started.")
        while not event.is_set():
            try:
                self.received_bytes = self._socket.recv(2048)
                # print(f"recv bytes: {self.received_bytes}\n")
            except Exception as e:
                print(f"Receive thread error: {e}")
        print("Receive UDP thread: Stopped.")

    def disconnect(self) -> None:
        self._socket.close()
        self._run_receive_thread.set()
        self._receive_thread.join()

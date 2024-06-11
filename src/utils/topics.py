from enum import StrEnum


class PubTopic(StrEnum):
    """MQTT client publish topic to Go1 robot."""

    action = "controller/action"
    stick = "controller/stick"
    code = "programming/code"
    current_action = "programming/current_action"
    run = "programming/run"
    led = "face_light/color"


class SubTopic(StrEnum):
    """MQTT client subsribe topic from Go1 robot."""

    bms = "bms/state"
    firmware = "firmware/version"
    code = "programming/code"
    action = "programming/action"

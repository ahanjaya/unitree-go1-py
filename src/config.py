import yaml


class Config(object):
    """Read config parameters for running the code."""

    def __init__(self, fn: str) -> None:
        self._fn = fn
        self._load_parameters()

    def _load_parameters(self) -> None:
        with open(self._fn, "r") as f_obj:
            yaml_data = yaml.safe_load(f_obj)

        connections = yaml_data["connection"]
        self.pc_host = connections["pc_host"]
        self.go1_host = connections["go1_host"]

        mqttc = connections["mqttc"]
        self.go1_mqttc_port = mqttc["port"]
        self.go1_mqttc_keepalive = mqttc["keepalive"]
        self.go1_mqttc_pub_freq = mqttc["publish_frequency"]

        udp = connections["udp"]
        self.go1_udp_port_high = udp["port_high"]
        self.go1_udp_port_low = udp["port_low"]

        camera = connections["camera"]
        self.camera_enable = camera["enable"]
        self.port_front = camera["port_front"]
        self.port_jaw = camera["port_jaw"]
        self.port_left = camera["port_left"]
        self.port_right = camera["port_right"]
        self.port_belly = camera["port_belly"]

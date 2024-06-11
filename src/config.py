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
        mqttc = connections["mqttc"]
        self.go1_host = connections["host"]
        self.go1_mqttc_port = mqttc["port"]
        self.go1_mqttc_keepalive = mqttc["keepalive"]
        self.go1_mqttc_pub_freq = mqttc["publish_frequency"]

        udp = connections["udp"]
        self.go1_udp_port_high = udp["port_high"]
        self.go1_udp_port_low = udp["port_low"]

import yaml


class Config(object):
    """ """

    def __init__(self, fn: str) -> None:
        self._fn = fn
        self._load_parameters()

    def _load_parameters(self) -> None:
        with open(self._fn, "r") as f_obj:
            yaml_data = yaml.safe_load(f_obj)

        connections = yaml_data["connection"]
        self.go1_host = connections["host"]
        self.go1_port = connections["port"]
        self.go1_keepalive = connections["keepalive"]
        self.go1_pub_freq = connections["publish_frequency"]

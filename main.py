import time

from IPython import embed

from src.config import Config
from src.go1 import Go1
from src.utils.custom_types import LED, Pose, Velocity

if __name__ == "__main__":
    config = Config("configs/default.yaml")
    go1 = Go1(config)

    time.sleep(1)
    embed()

    go1.close_all_connection()

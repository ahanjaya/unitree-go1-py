from src.config import Config
from src.go1 import Go1

if __name__ == "__main__":
    config = Config("configs/default.yaml")
    go1 = Go1(config)

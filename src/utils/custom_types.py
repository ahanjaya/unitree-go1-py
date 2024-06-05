from typing import NamedTuple


class Velocity(NamedTuple):
    """Represent a veolcity command."""

    vx: float
    vy: float
    vz: float


class Pose(NamedTuple):
    """Represent a pose direction command."""

    lean_left_right: float
    twist_left_right: float
    look_up_down: float
    extend_squat: float


class LED(NamedTuple):
    """Represent a LED RGB values."""

    r: int
    g: int
    b: int

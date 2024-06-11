# Unitree Go1 Python Controller
The High-Level python control for Unitree Go1 non-Edu version. HighLevel commands are sent via the MQTT client protocol, while HighState information is received using the UDP protocol.

<div style="text-align: center;">
    <img src="resources/go1-side-view.jpg" alt="Go1 Robot" width="600"/>
</div>

## Tested
This repository has been tested on real Go1-Pro robot with following firmware version. Moreover, there is no any setting or firmware modification has been applied to robot. It's just turn on the robot, connect laptop to the robot Wi-Fi and run this code.

<div style="text-align: center;">
    <img src="resources/go1-information.PNG" alt="Go1 Robot" width="700"/>
</div>


## Installation
Create a python virtual environment.
```
conda create -n go1 python=3.11
conda activate go1
git clone https://github.com/ahanjaya/unitree-go1-py.git
cd unitree-go1-py/
pip install -r requirements.txt
```

## Usage
```
cd unitree-go1-py/
python main.py
```
---
### Send HighLevel command.

#### Command Velocity
```
go1.set_walk_mode()
go1.walk(Velocity(0.5, 0.0, 0.0)) # X, Y, Theta
```

the other walking gait for velocity control
```
go1.set_run_mode()
go1.set_climb_mode()
```

#### Command Poses
```
go1.set_stand_mode()
go1.Pose(Pose(0.0, 0.0 0.0, 0.5)) # lean_left_right, twist_left_right, look_up_down, extend_squat
```

#### Motions
```
go1.dance_1()
go1.dance_2()
go1.straight_hand()
go1.jump_yaw()
go1.stand_up()
go1.stand_down()
go1.set_damping_mode()
```

#### Set Head LED
```
go1.set_led(LED(255, 255, 255)) # r, g, b
```

---
### Receive HighLevel states.
```
go1.high_state.print_states()
```

## Acknowlegments
Thanks to following repositories:
1. https://github.com/MAVProxyUser/YushuTechUnitreeGo1
2. https://github.com/Bin4ry/free-dog-sdk
3. https://github.com/dbaldwin/go1-js
   
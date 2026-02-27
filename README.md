# Seeed reBot Arm B601 Teleoperator Integration with LeRobot

This repository provides the **Leader Arm (Teleoperator)** integration for the **reBot Arm B601** with the [LeRobot](https://github.com/huggingface/lerobot) framework. It enables the B601 arm to be used for teleoperation - reading human operator movements to control follower robots.

## Supported Hardware

*   **Robot**: Seeed reBot Arm B601 Series (6-DOF + Gripper)
*   **Motors**: Damiao (DM4310 + DM4340), RobStride
*   **Communication**: CAN Bus (via USB-CAN adapter, e.g., derivatives of Candle/slcan or SocketCAN compatible devices)

## Installation

1.  **Install LeRobot**:
    Follow the instructions in the [LeRobot repository](https://github.com/huggingface/lerobot) to install the base library.

2.  **Install this package**:
    Clone this repository and install in editable mode:
    ```bash
    git clone https://github.com/Seeed-Studio/lerobot-teleoperator-seeed-b601.git
    cd lerobot-teleoperator-seeed-b601
    pip install -e .
    ```

    Upon installation, two teleoperator variants are registered:
    *   `seeed_b601_dm_leader`: B601 Leader using Damiao motors (6-DOF + Gripper) - **Fully Implemented**
    *   `seeed_b601_rs_leader`: B601 Leader using RobStride motors (6-DOF + Gripper) - **Placeholder**

## Configuration

The default configuration for B601-DM Leader is located in `lerobot_teleoperator_seeed_b601/config_seeed_b601_dm_leader.py`.

*   **Motor IDs**: 0x01 - 0x07 (send), 0x11 - 0x17 (receive)
*   **Motor Types**:
    *   Joint 1, 4, 5, 6, Gripper: `dm4310`
    *   Joint 2, 3: `dm4340`

Ensure your robot's motor IDs match this configuration.

TODO: Refer to the wiki page for the guide to configure the motors.

## Usage

### Quick Start

A verification script is provided to test the connection and read basic motor states (joint positions).

```bash
# Linux (SocketCAN)
python examples/verification_dm.py --port can0

# macOS (slcan)
python examples/verification_dm.py --port /dev/tty.usbmodemXXX
```

### Use within LeRobot

```bash
lerobot-teleoperate \
    --teleop.type=seeed_b601_dm_leader \
    --teleop.port=can0 \
    --robot.type=<your_follower_robot> \
    --robot.port=can1 \
    --fps=30
```

TODO: Write the full guide to use this teleoperator within LeRobot.

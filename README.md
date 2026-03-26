# Seeed reBot Arm B601 Teleoperator Integration with LeRobot

This repository provides the **Leader Arm (Teleoperator)** integration for the **reBot Arm B601** with the [LeRobot](https://github.com/huggingface/lerobot) framework. It enables the B601 arm to be used for teleoperation - reading human operator movements to control follower robots.

## Supported Hardware

*   **Robot**: Seeed reBot Arm B601 Series (6-DOF + Gripper)
*   **Motors**: Damiao (DM4310 + DM4340), RobStride
*   **Communication**: CAN Bus (via USB-CAN adapter, including Damiao's v3 USB2CAN adapter)

## Installation

1.  **Install LeRobot**:
    Follow the instructions in the [LeRobot repository](https://github.com/huggingface/lerobot) to install the base library. A very quick summary would be like the following.

    ```shell
    conda create -y -n lerobot python=3.12
    conda activate lerobot
    conda install ffmpeg -c conda-forge
    git clone https://github.com/huggingface/lerobot.git
    cd lerobot
    pip install -e .
    ```

2. **Install motorbridge Python Package**

    ```shell
    # goto https://github.com/tianrking/motorbridge/releases
    # find the proper python wheel for your platform
    # e.g. ubuntu x86_64, python3.12, we should download https://github.com/tianrking/motorbridge/releases/download/v0.1.5/motorbridge-0.1.3-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
    # with your conda env activated
    pip install motorbridge-0.1.3-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl

    # TODO: install from pypi
    ```

    You could also install the `motor-cli` tool，a very useful motor tool.

    ```shell
    wget https://github.com/tianrking/motorbridge/releases/download/v0.1.5/motor-cli-v0.1.5-linux-x86_64.tar.gz
    tar zxvf motor-cli-v0.1.5-linux-x86_64.tar.gz
    sudo cp motor-cli-v0.1.5-linux-x86_64/bin/motor_cli /usr/local/bin/
    sudo chmod a+x /usr/local/bin/motor_cli

    ## new version may be released, you should check the lates version

    ```

3.  **Install this package**:
    Clone this repository and install in editable mode:
    ```bash
    git clone https://github.com/Seeed-Projects/lerobot-teleoperator-seeed-b601.git
    cd lerobot-teleoperator-seeed-b601
    pip install -e .
    ```

    Or install from PyPI:
    ```bash
    pip install lerobot-teleoperator-seeed-b601
    ```

    Upon installation, two teleoperator variants are registered:
    *   `seeed_b601_dm_leader`: B601 Leader using Damiao motors (6-DOF + Gripper) - **Fully Implemented**
    *   `seeed_b601_rs_leader`: B601 Leader using RobStride motors (6-DOF + Gripper) - **Placeholder**
   
    ```shell
    # test if the installation is good
    lerobot-teleoperate --help | grep SeeedB601

    # if you see the following you're good
    SeeedB601DMLeaderConfig ['teleop']:
    SeeedB601RSLeaderConfig ['teleop']:
    ```

## Configuration

Default motor mapping for the B601 leader:

*   `shoulder_pan`: master ID `0x01`, feedback ID `0x11`, motor model `dm4340p`
*   `shoulder_lift`: master ID `0x02`, feedback ID `0x12`, motor model `dm4340p`
*   `elbow_flex`: master ID `0x03`, feedback ID `0x13`, motor model `dm4340p`
*   `wrist_flex`: master ID `0x04`, feedback ID `0x14`, motor model `dm4310`
*   `wrist_roll`: master ID `0x05`, feedback ID `0x15`, motor model `dm4310`
*   `wrist_yaw`: master ID `0x06`, feedback ID `0x16`, motor model `dm4310`
*   `gripper`: master ID `0x07`, feedback ID `0x17`, motor model `dm4310`

*   **CAN adapter types**:
    *   `socketcan`: for SocketCAN-compatible adapters such as `can0`
    *   `damiao`: for Damiao serial bridge adapters such as `/dev/ttyACM0`
    *   `robstride`: registered in config, but the dedicated adapter path is not yet supported by the current `motorbridge` Python SDK integration

Ensure your motor names, IDs, wiring, and motor models match this configuration.

TODO: Refer to the wiki page for the guide to configure the motors.

TODO: A script that utilize the motorbridge to configure the deep parameters of the motor.

## Usage

```shell
lerobot-teleoperate \
    --robot.id=follower1 \
    --robot.type=seeed_b601_dm_follower \
    --robot.port=/dev/ttyACM4 \
    --robot.can_adapter=damiao \
    --teleop.type=seeed_b601_dm_leader \
    --teleop.id=leader1 \
    --teleop.port=/dev/ttyACM5 \
    --teleop.can_adapter=damiao
```

Teleoperate with cameras,

```shell
lerobot-teleoperate \
    --robot.type=seeed_b601_dm_follower \
    --robot.port=/dev/ttyACM4 \
    --robot.can_adapter=damiao \
    --robot.id=my_awesome_follower_arm \
    --robot.cameras="{ up: {type: opencv, index_or_path: /dev/video10, width: 640, height: 480, fps: 30}, side: {type: intelrealsense, serial_number_or_name: 233522074606, width: 640, height: 480, fps: 30}}" \
    --teleop.type=seeed_b601_dm_leader \
    --teleop.port=/dev/ttyACM5 \
    --teleop.id=my_awesome_leader_arm \
    --robot.can_adapter=damiao \
    --display_data=true
```

Fore more lerobot operations, please refer to the lerobot official documentation:

https://huggingface.co/docs/lerobot/il_robots



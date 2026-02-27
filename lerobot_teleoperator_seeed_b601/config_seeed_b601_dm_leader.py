from dataclasses import dataclass, field

from lerobot.teleoperators.config import TeleoperatorConfig


@dataclass
class SeeedB601DMLeaderConfigBase:
    """Base configuration for the Seeed B601-DM leader arm with Damiao motors."""

    # CAN interfaces - one per arm (though B601 is single arm usually)
    # Linux: "can0", "can1", etc.
    # Mac: "/dev/tty.usbmodem..." (slcan)
    port: str

    # CAN interface type: "socketcan" (Linux), "slcan" (serial), or "auto" (auto-detect)
    can_interface: str = "auto"

    # CAN FD settings (Use CAN FD by default for Damiao motors)
    use_can_fd: bool = True
    can_bitrate: int = 1000000  # Nominal bitrate (1 Mbps)
    can_data_bitrate: int = 5000000  # Data bitrate for CAN FD (5 Mbps)

    # Manual control mode (Leader arm must be True to allow hand movement)
    manual_control: bool = True

    # Motor configuration for B601-DM (6 DOF + Gripper)
    # Maps motor names to (send_can_id, recv_can_id, motor_type)
    # Based on TRLC-DK1 hardware context and user confirmation:
    # Joint 1, 4-6, Gripper: DM4310
    # Joint 2-3: DM4340
    # IDs: 0x01 - 0x07
    motor_config: dict[str, tuple[int, int, str]] = field(
        default_factory=lambda: {
            "joint_1": (0x01, 0x11, "dm4310"),  # Base (DM4310)
            "joint_2": (0x02, 0x12, "dm4340"),  # Shoulder (DM4340)
            "joint_3": (0x03, 0x13, "dm4340"),  # Elbow (DM4340)
            "joint_4": (0x04, 0x14, "dm4310"),  # Wrist 1 (DM4310)
            "joint_5": (0x05, 0x15, "dm4310"),  # Wrist 2 (DM4310)
            "joint_6": (0x06, 0x16, "dm4310"),  # Wrist 3 (DM4310)
            "gripper": (0x07, 0x17, "dm4310"),  # Gripper (DM4310)
        }
    )


@TeleoperatorConfig.register_subclass("seeed_b601_dm_leader")
@dataclass
class SeeedB601DMLeaderConfig(TeleoperatorConfig, SeeedB601DMLeaderConfigBase):
    pass


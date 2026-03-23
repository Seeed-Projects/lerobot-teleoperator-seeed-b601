from dataclasses import dataclass, field

from lerobot.teleoperators.config import TeleoperatorConfig
from .seeed_b601_leader import SeeedB601LeaderConfigBase

@TeleoperatorConfig.register_subclass("seeed_b601_rs_leader")
@dataclass
class SeeedB601RSLeaderConfig(TeleoperatorConfig, SeeedB601LeaderConfigBase):
    """Configuration for Seeed B601-RS Leader Arm."""
    
    # Placeholder for RobStride specific config
    motor_models: dict[str, str] = field(
        default_factory=lambda: {
            "joint_1": "04",
            "joint_2": "04",
            "joint_3": "04",
            "joint_4": "04",
            "joint_5": "04",
            "joint_6": "04",
            "gripper": "04",
        }
    )

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
            "shoulder_pan":  "04",
            "shoulder_lift": "04",
            "elbow_flex":    "04",
            "wrist_flex":    "04",
            "wrist_roll":    "04",
            "wrist_yaw":     "04",
            "gripper":       "04",
        }
    )

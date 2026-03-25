from dataclasses import dataclass, field

from lerobot.teleoperators.config import TeleoperatorConfig
from .seeed_b601_leader import SeeedB601LeaderConfigBase

@TeleoperatorConfig.register_subclass("seeed_b601_dm_leader")
@dataclass
class SeeedB601DMLeaderConfig(TeleoperatorConfig, SeeedB601LeaderConfigBase):
    """Configuration for Seeed B601-DM Leader Arm."""
    
    motor_models: dict[str, str] = field(
        default_factory=lambda: {
            "shoulder_pan":  "dm4310",  # Base (DM4310)
            "shoulder_lift": "dm4340",  # Shoulder (DM4340)
            "elbow_flex":    "dm4340",  # Elbow (DM4340)
            "wrist_flex":    "dm4310",  # Wrist 1 (DM4310)
            "wrist_roll":    "dm4310",  # Wrist 2 (DM4310)
            "wrist_yaw":     "dm4310",  # Wrist 3 (DM4310)
            "gripper":       "dm4310",  # Gripper (DM4310)
        }
    )

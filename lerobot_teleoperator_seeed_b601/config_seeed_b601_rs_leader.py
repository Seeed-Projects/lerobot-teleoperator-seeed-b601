from dataclasses import dataclass, field

from lerobot.cameras import CameraConfig
from lerobot.teleoperators.config import TeleoperatorConfig


@dataclass
class SeeedB601RSLeaderConfigBase:
    """
    Configuration for Seeed B601-RS (RobStride Motors) leader arm.
    Currently a placeholder.
    """
    port: str
    cameras: dict[str, CameraConfig] = field(default_factory=dict)
    # Add RobStride specific config here later


@TeleoperatorConfig.register_subclass("seeed_b601_rs_leader")
@dataclass
class SeeedB601RSLeaderConfig(TeleoperatorConfig, SeeedB601RSLeaderConfigBase):
    pass

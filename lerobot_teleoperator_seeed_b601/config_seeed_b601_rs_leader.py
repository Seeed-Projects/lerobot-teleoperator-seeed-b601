from dataclasses import dataclass, field

from lerobot.teleoperators.config import TeleoperatorConfig
from .seeed_b601_leader import SeeedB601LeaderConfigBase

@TeleoperatorConfig.register_subclass("seeed_b601_rs_leader")
@dataclass
class SeeedB601RSLeaderConfig(TeleoperatorConfig, SeeedB601LeaderConfigBase):
    """Configuration for Seeed B601-RS Leader Arm."""
    
    pass

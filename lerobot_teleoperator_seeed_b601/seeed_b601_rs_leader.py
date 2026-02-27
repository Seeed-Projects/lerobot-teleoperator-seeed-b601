import logging

from lerobot.processor import RobotAction
from lerobot.teleoperators.teleoperator import Teleoperator

from .config_seeed_b601_rs_leader import SeeedB601RSLeaderConfig

logger = logging.getLogger(__name__)


class SeeedB601RSLeader(Teleoperator):
    """
    Seeed B601-RS Leader Arm (RobStride Motors).
    Placeholder implementation.
    """

    config_class = SeeedB601RSLeaderConfig
    name = "seeed_b601_rs_leader"

    def __init__(self, config: SeeedB601RSLeaderConfig):
        super().__init__(config)
        self.config = config
        logger.warning("SeeedB601RSLeader is currently a placeholder and not implemented.")

    @property
    def _motors_ft(self) -> dict[str, type]:
        return {}

    @property
    def _cameras_ft(self) -> dict[str, tuple]:
        return {}

    @property
    def observation_features(self) -> dict[str, type | tuple]:
        return {}

    @property
    def action_features(self) -> dict[str, type]:
        return {}

    @property
    def is_connected(self) -> bool:
        return False

    def connect(self, calibrate: bool = True) -> None:
        raise NotImplementedError("SeeedB601RSLeader support is not yet implemented.")

    @property
    def is_calibrated(self) -> bool:
        return False

    def calibrate(self) -> None:
        pass

    def configure(self) -> None:
        pass

    def get_observation(self) -> dict:
        raise NotImplementedError

    def send_action(self, action: RobotAction) -> RobotAction:
        raise NotImplementedError

    def disconnect(self) -> None:
        pass

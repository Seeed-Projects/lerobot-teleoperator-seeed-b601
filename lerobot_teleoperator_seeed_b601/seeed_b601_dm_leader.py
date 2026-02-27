import logging
import time
from typing import Any

from lerobot.motors import Motor, MotorCalibration, MotorNormMode
from lerobot.motors.damiao import DamiaoMotorsBus
from lerobot.processor import RobotAction
from lerobot.utils.errors import DeviceAlreadyConnectedError, DeviceNotConnectedError

from lerobot.teleoperators.teleoperator import Teleoperator
from .config_seeed_b601_dm_leader import SeeedB601DMLeaderConfig

logger = logging.getLogger(__name__)


class SeeedB601DMLeader(Teleoperator):
    """
    Seeed B601-DM Leader Arm (6-DOF + Gripper) using Damiao motors.
    Used for teleoperation - reads human operator movements.
    Uses CAN bus communication via DamiaoMotorsBus with torque disabled for manual control.
    """

    config_class = SeeedB601DMLeaderConfig
    name = "seeed_b601_dm_leader"

    def __init__(self, config: SeeedB601DMLeaderConfig):
        super().__init__(config)
        self.config = config

        # Initialize motors based on config
        motors: dict[str, Motor] = {}
        for motor_name, (send_id, recv_id, motor_type_str) in config.motor_config.items():
            motor = Motor(
                send_id, motor_type_str, MotorNormMode.DEGREES
            )  # Always use degrees for Damiao motors
            motor.recv_id = recv_id
            motor.motor_type_str = motor_type_str
            motors[motor_name] = motor

        self.bus = DamiaoMotorsBus(
            port=self.config.port,
            motors=motors,
            calibration=self.calibration,
            can_interface=self.config.can_interface,
            use_can_fd=self.config.use_can_fd,
            bitrate=self.config.can_bitrate,
            data_bitrate=self.config.can_data_bitrate if self.config.use_can_fd else None,
        )

    @property
    def action_features(self) -> dict[str, type]:
        """Features produced by this teleoperator (motor states)."""
        features: dict[str, type] = {}
        for motor in self.bus.motors:
            features[f"{motor}.pos"] = float
            features[f"{motor}.vel"] = float
            features[f"{motor}.torque"] = float
        return features

    @property
    def feedback_features(self) -> dict[str, type]:
        """Feedback features (not implemented for B601 Leader)."""
        return {}

    @property
    def is_connected(self) -> bool:
        """Check if leader arm is connected."""
        return self.bus.is_connected

    def connect(self, calibrate: bool = True) -> None:
        """
        Connect to the leader arm and optionally calibrate.
        """
        if self.is_connected:
            raise DeviceAlreadyConnectedError(f"{self} already connected")

        # Connect to CAN bus
        logger.info(f"Connecting arm on {self.config.port}...")
        self.bus.connect()

        # Run calibration if needed
        if not self.is_calibrated and calibrate:
            logger.info(
                "Mismatch between calibration values in the motor and the calibration file or no calibration file found"
            )
            self.calibrate()

        # Configure motors (disable torque for manual control)
        self.configure()

        # Set zero position if calibrated
        if self.is_calibrated:
            self.bus.set_zero_position()

        logger.info(f"{self} connected.")

    @property
    def is_calibrated(self) -> bool:
        """Check if robot is calibrated."""
        return self.bus.is_calibrated

    def calibrate(self) -> None:
        """
        Calibration procedure for B601-DM.
        Since B601 structure is different from OpenArm (cannot just hang down),
        we assume the user Manually Positions the robot to the Zero Configuration before running this.
        """
        if self.calibration:
            user_input = input(
                f"Press ENTER to use provided calibration file associated with the id {self.id}, or type 'c' and press ENTER to run calibration: "
            )
            if user_input.strip().lower() != "c":
                logger.info(f"Writing calibration file associated with the id {self.id} to the motors")
                self.bus.write_calibration(self.calibration)
                return

        logger.info(f"\nRunning calibration for {self}")
        self.bus.disable_torque()

        # Step 1: Set zero position
        input(
            "\nCalibration: Set Zero Position\n"
            "Position the B601 arm in the following configuration:\n"
            "  - All joints at mechanical zero marks (refer to B601 manual)\n"
            "  - Gripper closed\n"
            "Press ENTER when ready..."
        )

        # Set current position as zero
        self.bus.set_zero_position()
        logger.info("Arm zero position set.")

        logger.info("Setting range: -90° to +90° by default for all joints")
        for motor_name, motor in self.bus.motors.items():
            self.calibration[motor_name] = MotorCalibration(
                id=motor.id,
                drive_mode=0,
                homing_offset=0,
                range_min=-90,
                range_max=90,
            )

        self.bus.write_calibration(self.calibration)
        self._save_calibration()
        print(f"Calibration saved to {self.calibration_fpath}")

    def configure(self) -> None:
        """Configure motors for manual teleoperation (disable torque)."""
        return self.bus.disable_torque() if self.config.manual_control else self.bus.configure_motors()

    def setup_motors(self) -> None:
        """
        Setup motor IDs and configuration.

        For CAN motors, ID configuration is typically done via manufacturer tools.
        This method is required by the Teleoperator base class but not implemented
        for Damiao motors.
        """
        raise NotImplementedError(
            "Motor ID configuration is typically done via manufacturer tools for CAN motors."
        )

    def get_action(self) -> RobotAction:
        """
        Get current action from the leader arm.

        This is the main method for teleoperators - it reads the current state
        of the leader arm and returns it as an action that can be sent to a follower.

        Reads all motor states (pos/vel/torque) in one CAN refresh cycle.

        Returns:
            RobotAction: A flat dictionary representing the teleoperator's current actions.
        """
        start = time.perf_counter()

        if not self.is_connected:
            raise DeviceNotConnectedError(f"{self} is not connected.")

        action_dict: dict[str, Any] = {}

        # Sync read all states (efficient batch reading)
        states = self.bus.sync_read_all_states()

        for motor in self.bus.motors:
            state = states.get(motor, {})
            action_dict[f"{motor}.pos"] = state.get("position")
            action_dict[f"{motor}.vel"] = state.get("velocity")
            action_dict[f"{motor}.torque"] = state.get("torque")

        dt_ms = (time.perf_counter() - start) * 1e3
        logger.debug(f"{self} read state: {dt_ms:.1f}ms")

        return action_dict

    def send_feedback(self, feedback: dict[str, float]) -> None:
        """Send feedback to leader arm (not implemented)."""
        raise NotImplementedError("Feedback is not yet implemented for B601 Leader.")

    def disconnect(self) -> None:
        """Disconnect from leader arm."""
        if not self.is_connected:
            raise DeviceNotConnectedError(f"{self} is not connected.")

        # Disconnect with torque disabled (safe for manual control)
        self.bus.disconnect(disable_torque=self.config.manual_control)

        logger.info(f"{self} disconnected.")

import logging
import math
import time
from dataclasses import dataclass, field
from typing import Any

from lerobot.motors import MotorCalibration
from motorbridge import Controller as MotorBridgeController, Mode as MotorBridgeMode
from lerobot.processor import RobotAction
from lerobot.teleoperators.teleoperator import Teleoperator
from lerobot.utils.errors import DeviceAlreadyConnectedError, DeviceNotConnectedError

logger = logging.getLogger(__name__)

@dataclass
class SeeedB601LeaderConfigBase:
    """Base configuration for the Seeed B601 Leader arm."""
    port: str
    manual_control: bool = True
    # CAN adapter type:
    #   "socketcan"  - SocketCAN based adapters (PCAN, slcan, embedded can controller, etc.)
    #   "damiao"     - Damiao dedicated serial bridge
    #   "robstride"  - RobStride dedicated adapter (placeholder, not yet supported)
    can_adapter: str = "socketcan"
    # Baud rate for Damiao serial bridge (only used when can_adapter="damiao")
    dm_serial_baud: int = 921600
    motor_can_ids: dict[str, tuple[int, int]] = field(
        default_factory=lambda: {
            "joint_1": (0x01, 0x11),
            "joint_2": (0x02, 0x12),
            "joint_3": (0x03, 0x13),
            "joint_4": (0x04, 0x14),
            "joint_5": (0x05, 0x15),
            "joint_6": (0x06, 0x16),
            "gripper": (0x07, 0x17),
        }
    )
    motor_models: dict[str, str] = field(default_factory=dict)

class SeeedB601LeaderBase(Teleoperator):
    """
    Base class for Seeed B601 Leader Arms (DM and RS variants).
    Uses CAN bus communication via motorbridge with torque disabled for manual control.
    """

    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.bus = None
        self.motors = {}
        self.motor_names = list(config.motor_can_ids.keys())

    @property
    def action_features(self) -> dict[str, type]:
        """Features produced by this teleoperator (motor states)."""
        features: dict[str, type] = {}
        for motor in self.motor_names:
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
        return self.bus is not None

    def _add_motors_to_bus(self):
        """Must be implemented by subclasses to add specific motor types to self.bus."""
        raise NotImplementedError

    def connect(self, calibrate: bool = True) -> None:
        """Connect to the leader arm and optionally calibrate."""
        if self.is_connected:
            raise DeviceAlreadyConnectedError(f"{self} already connected")

        logger.info(f"Connecting arm on {self.config.port} (adapter={self.config.can_adapter})...")
        if self.config.can_adapter == "damiao":
            self.bus = MotorBridgeController.from_dm_serial(
                serial_port=self.config.port,
                baud=self.config.dm_serial_baud,
            )
        elif self.config.can_adapter == "robstride":
            raise NotImplementedError(
                "RobStride dedicated USB-to-CAN adapter is not yet supported in motorbridge Python SDK."
            )
        else:
            # Default: socketcan (PCAN, slcan, etc.)
            self.bus = MotorBridgeController(channel=self.config.port)
        
        self._add_motors_to_bus()

        if not self.is_calibrated and calibrate:
            logger.info(
                "Mismatch between calibration values in the motor and the calibration file or no calibration file found"
            )
            self.calibrate()

        self.configure()

        if self.is_calibrated:
            for motor in self.motors.values():
                motor.set_zero_position()

        logger.info(f"{self} connected.")

    @property
    def is_calibrated(self) -> bool:
        """Check if robot is calibrated."""
        return bool(self.calibration)

    def calibrate(self) -> None:
        """Calibration procedure for B601."""
        if self.calibration:
            user_input = input(
                f"Press ENTER to use provided calibration file associated with the id {self.id}, or type 'c' and press ENTER to run calibration: "
            )
            if user_input.strip().lower() != "c":
                logger.info(f"Using calibration file associated with the id {self.id}")
                return

        logger.info(f"\nRunning calibration for {self}")
        
        if self.config.manual_control:
            for motor in self.motors.values():
                motor.disable()

        input(
            "\nCalibration: Set Zero Position\n"
            "Position the B601 arm in the following configuration:\n"
            "  - All joints at mechanical zero marks (refer to B601 manual)\n"
            "  - Gripper closed\n"
            "Press ENTER when ready..."
        )

        for motor in self.motors.values():
            motor.set_zero_position()
        logger.info("Arm zero position set.")

        logger.info("Setting range: -90° to +90° by default for all joints")
        for motor_name, (send_id, recv_id) in self.config.motor_can_ids.items():
            self.calibration[motor_name] = MotorCalibration(
                id=send_id,
                drive_mode=0,
                homing_offset=0,
                range_min=-90,
                range_max=90,
            )

        self._save_calibration()
        print(f"Calibration saved to {self.calibration_fpath}")

    def configure(self) -> None:
        """Configure motors for manual teleoperation (disable torque)."""
        if self.config.manual_control:
            for motor in self.motors.values():
                motor.disable()
        else:
            for motor in self.motors.values():
                motor.enable()
                motor.ensure_mode(MotorBridgeMode.MIT)

    def get_action(self) -> RobotAction:
        """Reads all motor states (pos/vel/torque)."""
        start = time.perf_counter()

        if not self.is_connected:
            raise DeviceNotConnectedError(f"{self} is not connected.")

        action_dict: dict[str, Any] = {}

        if self.config.manual_control:
            for motor in self.motors.values():
                motor.request_feedback()
                
        self.bus.poll_feedback_once()

        for motor_name, motor in self.motors.items():
            state = motor.get_state()
            if state is not None:
                action_dict[f"{motor_name}.pos"] = math.degrees(state.pos)
                action_dict[f"{motor_name}.vel"] = math.degrees(state.vel)
                action_dict[f"{motor_name}.torque"] = state.torq
            else:
                action_dict[f"{motor_name}.pos"] = 0.0
                action_dict[f"{motor_name}.vel"] = 0.0
                action_dict[f"{motor_name}.torque"] = 0.0

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

        if self.config.manual_control:
            for motor in self.motors.values():
                motor.disable()
                
        self.bus.close()
        self.bus = None

        logger.info(f"{self} disconnected.")

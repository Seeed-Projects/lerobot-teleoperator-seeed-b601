"""
Simple verification script for Seeed B601 leader arm (DM or RS).

Usage:
    python examples/angle_reader.py --port can0 --type dm                    # SocketCAN, read once
    python examples/angle_reader.py --port /dev/ttyACM0 --type dm --adapter damiao  # Damiao serial bridge
    python examples/angle_reader.py --port can0 --type dm --loop             # Continuous reading (1s interval)

Expected result:
    Connects to the arm, reads all motor angles, and prints them.
"""

import argparse
import logging
import time

from lerobot_teleoperator_seeed_b601.config_seeed_b601_dm_leader import SeeedB601DMLeaderConfig
from lerobot_teleoperator_seeed_b601.seeed_b601_dm_leader import SeeedB601DMLeader
from lerobot_teleoperator_seeed_b601.config_seeed_b601_rs_leader import SeeedB601RSLeaderConfig
from lerobot_teleoperator_seeed_b601.seeed_b601_rs_leader import SeeedB601RSLeader

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def print_angles(action: dict) -> None:
    """Print joint angles from action dict."""
    print("\n--- Motor Angles ---")
    for key, value in action.items():
        if key.endswith(".pos"):
            motor_name = key.removesuffix(".pos")
            print(f"  {motor_name:12s}: {value:.2f} deg")
    print("--------------------")


def main(port: str, arm_type: str, adapter: str, loop: bool) -> None:
    if arm_type.lower() == "dm":
        config = SeeedB601DMLeaderConfig(port=port, can_adapter=adapter)
        robot = SeeedB601DMLeader(config)
    elif arm_type.lower() == "rs":
        config = SeeedB601RSLeaderConfig(port=port, can_adapter=adapter)
        robot = SeeedB601RSLeader(config)
    else:
        raise ValueError(f"Unknown arm type: {arm_type}. Expected 'dm' or 'rs'.")

    try:
        logger.info(f"Connecting to {arm_type.upper()} arm on port: {port}")
        robot.connect(calibrate=False)
        logger.info("Connected!")

        if loop:
            logger.info("Continuous mode enabled. Press Ctrl+C to stop.")
            try:
                while True:
                    action = robot.get_action()
                    print_angles(action)
                    time.sleep(1.0)
            except KeyboardInterrupt:
                print("\nStopped by user.")
        else:
            action = robot.get_action()
            print_angles(action)

    except Exception as e:
        logger.error(f"Failed: {e}")
        raise
    finally:
        if robot.is_connected:
            robot.disconnect()
            logger.info("Disconnected.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read joint angles from Seeed B601 Leader arm")
    parser.add_argument(
        "--port",
        type=str,
        required=True,
        help="CAN port, e.g. 'can0' (Linux) or '/dev/tty.usbmodemXXX' (macOS)",
    )
    parser.add_argument(
        "--type",
        type=str,
        choices=["dm", "rs"],
        default="dm",
        help="Motor type: 'dm' (Damiao) or 'rs' (RobStride). Defaults to 'dm'.",
    )
    parser.add_argument(
        "--adapter",
        type=str,
        choices=["socketcan", "damiao", "robstride"],
        default="socketcan",
        help="CAN adapter type. Defaults to 'socketcan'.",
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Continuously read motor angles every 1 second. Press Ctrl+C to stop.",
    )
    args = parser.parse_args()
    main(args.port, args.type, args.adapter, args.loop)

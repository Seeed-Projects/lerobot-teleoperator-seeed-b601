"""
Simple verification script for Seeed B601-DM leader arm.

Usage:
    python examples/verification_dm.py --port can0            # Linux (SocketCAN)
    python examples/verification_dm.py --port /dev/tty.usbmodemXXX  # macOS (slcan)

Expected result:
    Connects to the arm, reads all motor angles, and prints them once.
"""

import argparse
import logging

from lerobot_teleoperator_seeed_b601.config_seeed_b601_dm_leader import SeeedB601DMLeaderConfig
from lerobot_teleoperator_seeed_b601.seeed_b601_dm_leader import SeeedB601DMLeader

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main(port: str) -> None:
    config = SeeedB601DMLeaderConfig(port=port)
    robot = SeeedB601DMLeader(config)

    try:
        logger.info(f"Connecting to arm on port: {port}")
        robot.connect(calibrate=False)
        logger.info("Connected!")

        # Read motor states
        action = robot.get_action()

        # Print joint angles (position only)
        print("\n--- Motor Angles ---")
        for key, value in action.items():
            if key.endswith(".pos"):
                motor_name = key.removesuffix(".pos")
                print(f"  {motor_name:12s}: {value:.2f} deg")
        print("--------------------")

    except Exception as e:
        logger.error(f"Failed: {e}")
        raise
    finally:
        if robot.is_connected:
            robot.disconnect()
            logger.info("Disconnected.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify Seeed B601-DM arm connection")
    parser.add_argument(
        "--port",
        type=str,
        required=True,
        help="CAN port, e.g. 'can0' (Linux) or '/dev/tty.usbmodemXXX' (macOS)",
    )
    args = parser.parse_args()
    main(args.port)

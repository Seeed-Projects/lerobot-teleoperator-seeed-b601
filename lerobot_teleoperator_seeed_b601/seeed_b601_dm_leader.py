from .config_seeed_b601_dm_leader import SeeedB601DMLeaderConfig
from .seeed_b601_leader import SeeedB601LeaderBase

class SeeedB601DMLeader(SeeedB601LeaderBase):
    """
    Seeed B601-DM Leader Arm (6-DOF + Gripper) using Damiao motors.
    Used for teleoperation - reads human operator movements.
    Uses CAN bus communication via motorbridge with torque disabled for manual control.
    """

    config_class = SeeedB601DMLeaderConfig
    name = "seeed_b601_dm_leader"

    motor_model_mapping = {
        "shoulder_pan":  "dm4340p",
        "shoulder_lift": "dm4340p",
        "elbow_flex":    "dm4340p",
        "wrist_flex":    "dm4310",
        "wrist_roll":    "dm4310",
        "wrist_yaw":     "dm4310",
        "gripper":       "dm4310",
    }

    def _add_motors_to_bus(self):
        for motor_name, (send_id, recv_id) in self.config.motor_can_ids.items():
            motor_type_str = self.motor_model_mapping[motor_name]
            model_str = motor_type_str.upper().replace("DM", "")
            self.motors[motor_name] = self.bus.add_damiao_motor(send_id, recv_id, model_str)

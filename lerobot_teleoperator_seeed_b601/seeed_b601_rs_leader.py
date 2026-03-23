from .config_seeed_b601_rs_leader import SeeedB601RSLeaderConfig
from .seeed_b601_leader import SeeedB601LeaderBase

class SeeedB601RSLeader(SeeedB601LeaderBase):
    """
    Seeed B601-RS Leader Arm (6-DOF + Gripper) using RobStride motors.
    Used for teleoperation - reads human operator movements.
    Uses CAN bus communication via motorbridge with torque disabled for manual control.
    """

    config_class = SeeedB601RSLeaderConfig
    name = "seeed_b601_rs_leader"

    def _add_motors_to_bus(self):
        for motor_name, (send_id, recv_id) in self.config.motor_can_ids.items():
            motor_type_str = self.config.motor_models[motor_name]
            self.motors[motor_name] = self.bus.add_robstride_motor(send_id, recv_id, motor_type_str)

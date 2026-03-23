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

    def _add_motors_to_bus(self):
        for motor_name, (send_id, recv_id) in self.config.motor_can_ids.items():
            motor_type_str = self.config.motor_models[motor_name]
            model_str = motor_type_str.upper().replace("DM", "")
            self.motors[motor_name] = self.bus.add_damiao_motor(send_id, recv_id, model_str)

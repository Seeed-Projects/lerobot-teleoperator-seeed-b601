# AGENTS.md

Guidelines for AI coding agents working across the Seeed B601 LeRobot workspace.

## Workspace Structure

This project is part of a multi-project workspace rooted at `/Users/Jack/Sync_training_box/`.
The working directory is always `lerobot-teleoperator-seeed-b601/`; agents operate on sibling projects via relative paths.

| Directory | Package | Role |
|---|---|---|
| `lerobot-teleoperator-seeed-b601/` | `lerobot_teleoperator_seeed_b601` | Leader arm (Teleoperator) - DM & RS variants |
| `lerobot-robot-seeed-b601/` | `lerobot_robot_seeed_b601` | Follower arm (Robot) - DM & RS variants |
| `lerobot-robot-dummy/` | `lerobot_robot_dummy` | Debug/dummy follower for testing without hardware |
| `lerobot-teleoperator-rebot-arm-102/` | `lerobot_teleoperator_rebot_arm_102` | Alternative leader using reBot Arm 102 servos |

Workspace file: `/Users/Jack/Sync_training_box/lerobot-robot-seeed-b601.code-workspace`

## Build & Install

```bash
# Install any sub-project in editable mode (run from its directory)
pip install -e .

# Core dependency (install first)
pip install lerobot>=0.4

# motorbridge SDK - install wheel manually from GitHub releases
# https://github.com/tianrking/motorbridge/releases
pip install motorbridge-0.1.3-<platform>.whl
```

No Makefile, tox, or nox. Each project has its own `pyproject.toml` with `setuptools` backend.

## Testing

**No pytest or unittest suites exist.** All testing is hardware-based.

```bash
# Test leader arm CAN connection
python examples/test_leader.py --port can0 --action connect

# Read motor states for 10 seconds
python examples/test_leader.py --port can0 --action read --duration 10

# Run calibration
python examples/test_leader.py --port can0 --action calibrate

# Angle reader (works for both leader/follower)
python examples/angle_reader.py --port can0 --type dm [--loop]
```

Port values: `can0` (Linux socketcan), `/dev/ttyACM*` (Damiao serial), `/dev/tty.usbmodem*` (macOS slcan).

## CI/CD

GitHub Actions workflows exist in teleoperator, robot, and rebot-arm-102 projects:
- Trigger: tag push matching `v*`
- Pipeline: `python -m build` -> `twine check dist/*` -> PyPI publish via trusted publisher
- No CI lint or test steps (hardware-dependent code)

## Linting & Formatting

**No linter or formatter is configured** (no ruff, black, flake8, isort, mypy, pyright configs).
Follow the existing code style described below. Do not introduce new tool configs without explicit request.

## Code Style

### Imports

Order: stdlib -> third-party -> local (relative). Blank line between groups.

```python
import logging
import time
from dataclasses import dataclass, field

import numpy as np
from motorbridge import Controller, Mode

from lerobot.robots.robot import Robot, RobotConfig

from .config_seeed_b601_dm_follower import SeeedB601DMFollowerConfig
```

### Type Annotations

Modern Python 3.10+ syntax throughout. No `from __future__ import annotations`.

```python
# Use built-in generics, not typing module
motors: dict[str, tuple[int, int, str]]
value: float | list[float]
name: str | None = None

# @dataclass fields: always typed
@dataclass
class MyConfig(TeleoperatorConfig):
    port: str = "/dev/ttyACM0"
    motors: dict[str, tuple[int, int, str]] = field(default_factory=lambda: {...})

# Properties and public methods: always have return types
@property
def action_features(self) -> dict[str, type]:
    ...
```

### Naming Conventions

- **Classes**: `PascalCase` - `SeeedB601DMLeader`, `SeeedB601DMFollowerConfig`
- **Functions/methods**: `snake_case` - `sync_read_all_states`, `_add_motors_to_bus`
- **Constants**: `UPPER_SNAKE_CASE` - `LONG_TIMEOUT_SEC = 16`
- **Private**: leading underscore - `_is_connected`, `_add_motors_to_bus`
- **Motor names**: descriptive snake_case - `shoulder_pan`, `elbow_flex`, `gripper`
- **Config registration**: snake_case string - `seeed_b601_dm_leader`

### Class Architecture

Base class + variant pattern used across all projects:

```python
# Base class inherits from LeRobot abstract class
class SeeedB601LeaderBase(Teleoperator):
    def connect(self, calibrate: bool = False): ...
    def get_action(self) -> dict[str, float]: ...
    # Abstract hook for variants:
    def _add_motors_to_bus(self) -> None: ...

# Variant implements the hook
class SeeedB601DMLeader(SeeedB601LeaderBase):
    config_class = SeeedB601DMLeaderConfig
    name = "seeed_b601_dm_leader"
    def _add_motors_to_bus(self) -> None: ...
```

### Config Pattern

```python
@dataclass
class SeeedB601DMLeaderConfig(SeeedB601LeaderBaseConfig, TeleoperatorConfig):
    # Register with LeRobot plugin system
    pass

@TeleoperatorConfig.register_subclass("seeed_b601_dm_leader")
class SeeedB601DMLeaderConfig(SeeedB601DMLeaderConfig):
    pass
```

Mutable defaults always use `field(default_factory=lambda: {...})`.

### Error Handling

```python
# Use LeRobot's device errors for connection state
from lerobot.errors import DeviceAlreadyConnectedError, DeviceNotConnectedError

# Retry pattern for hardware operations
for attempt in range(max_retries):
    try:
        result = hardware_operation()
        break
    except Exception as e:
        logger.warning(f"Attempt {attempt + 1} failed: {e}")
        time.sleep(retry_delay)

# Bare except only for non-critical CAN polling failures
try:
    bus.poll()
except:
    logger.warning("CAN poll timeout")
```

### Logging

Every module uses: `logger = logging.getLogger(__name__)`

Use `logger.info` for connection/calibration events, `logger.warning` for recoverable errors, `logger.debug` for motor state reads.

### Module Exports

Every `__init__.py` uses explicit imports + `__all__`:

```python
from .seeed_b601_dm_leader import SeeedB601DMLeader
from .config_seeed_b601_dm_leader import SeeedB601DMLeaderConfig

__all__ = ["SeeedB601DMLeader", "SeeedB601DMLeaderConfig", ...]
```

### File Naming

- `config_<variant>.py` - Config dataclass
- `<device_name>_<variant>.py` - Implementation class
- `<device_name>_<role>_base.py` or `<device_name>_<role>.py` - Shared base class (if separate file)

## Key Concepts

- **Teleoperator** = leader arm, torque disabled, reads human movement (passive sensor)
- **Robot** = follower arm, torque enabled, executes position commands (active actuator)
- Both share the same motor hardware but opposite control modes
- `manual_control=True` on leader, `manual_control=False` on follower

## Safety Rules

- Leader arm: torque ALWAYS disabled. Never enable torque on a leader.
- Always verify CAN connection before full teleoperation.
- Disconnect must leave torque disabled regardless of error state.
- Test with `calibrate=False` first to verify basic connectivity.

## Cross-Project Editing

When editing sibling projects from this working directory, use relative paths:
```
../lerobot-robot-seeed-b601/lerobot_robot_seeed_b601/...
../lerobot-robot-dummy/lerobot_robot_dummy/...
../lerobot-teleoperator-rebot-arm-102/lerobot_teleoperator_rebot_arm_102/...
```

All four projects share identical patterns. Changes to base class patterns should be reflected consistently across all projects.

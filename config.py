from dataclasses import dataclass


@dataclass(frozen=True)
class LaneConfig:
    x_positions: tuple[float, float, float] = (-2.8, 0.0, 2.8)
    switch_lerp_speed: float = 10.0


@dataclass(frozen=True)
class PlayerConfig:
    y: float = 1.1
    z: float = -6.0
    collision_z_threshold: float = 1.3


@dataclass(frozen=True)
class MovementConfig:
    base_speed: float = 14.0
    speed_acceleration: float = 0.22
    max_speed: float = 32.0
    score_per_second: float = 10.0


@dataclass(frozen=True)
class WorldConfig:
    ground_segment_length: float = 60.0
    ground_segments: int = 4
    obstacle_spawn_z: float = 65.0
    obstacle_cleanup_z: float = -20.0
    road_width: float = 10.0


@dataclass(frozen=True)
class SpawnerConfig:
    min_spawn_interval: float = 0.55
    max_spawn_interval: float = 1.25
    two_obstacle_chance: float = 0.35


@dataclass(frozen=True)
class GameConfig:
    lane: LaneConfig = LaneConfig()
    player: PlayerConfig = PlayerConfig()
    movement: MovementConfig = MovementConfig()
    world: WorldConfig = WorldConfig()
    spawner: SpawnerConfig = SpawnerConfig()


CONFIG = GameConfig()

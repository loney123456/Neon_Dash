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
    start_speed: float = 12.0
    end_speed: float = 22.0
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
    start_min_spawn_interval: float = 0.95
    start_max_spawn_interval: float = 1.35
    end_min_spawn_interval: float = 0.50
    end_max_spawn_interval: float = 0.78
    start_two_obstacle_chance: float = 0.18
    end_two_obstacle_chance: float = 0.58


@dataclass(frozen=True)
class CollectibleConfig:
    start_min_spawn_interval: float = 1.15
    start_max_spawn_interval: float = 1.85
    end_min_spawn_interval: float = 0.72
    end_max_spawn_interval: float = 1.25
    reward_score: int = 5
    min_obstacle_distance_z: float = 8.5
    max_active: int = 7
    y: float = 2.35
    scale: float = 0.72
    pickup_z_threshold: float = 1.2
    bob_amplitude: float = 0.22
    bob_speed: float = 4.2
    spin_speed: float = 170.0
    glow_scale: float = 2.4
    glow_alpha: int = 120


@dataclass(frozen=True)
class DifficultyConfig:
    # 0 -> easy ramp start, 1 -> target hard level.
    # ramp_seconds: float = 150.0
    ramp_seconds: float = 70.0


@dataclass(frozen=True)
class GameConfig:
    lane: LaneConfig = LaneConfig()
    player: PlayerConfig = PlayerConfig()
    movement: MovementConfig = MovementConfig()
    world: WorldConfig = WorldConfig()
    spawner: SpawnerConfig = SpawnerConfig()
    collectible: CollectibleConfig = CollectibleConfig()
    difficulty: DifficultyConfig = DifficultyConfig()


CONFIG = GameConfig()

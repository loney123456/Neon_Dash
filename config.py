from dataclasses import dataclass


@dataclass(frozen=True)
class LaneConfig:
    # X positions for lanes from left to right.
    # Keep exactly 3 values with current obstacle logic.
    # Wider spacing => easier reaction window but longer lane switch travel.
    # Practical range per side: about -4.0 ~ -2.0 and 2.0 ~ 4.0
    x_positions: tuple[float, float, float] = (-2.8, 0.0, 2.8)
    # Horizontal lane-change interpolation speed.
    # Higher value => snappier lane switch.
    # Practical range: 6 ~ 18
    switch_lerp_speed: float = 10.0


@dataclass(frozen=True)
class PlayerConfig:
    # Player height on Y axis.
    # Tune with collectible/obstacle height for clear visuals.
    # Practical range: 0.8 ~ 1.8
    y: float = 1.1
    # Fixed player Z position in relative-movement setup.
    # Usually keep negative so world flows toward player.
    # Practical range: -10.0 ~ -3.0
    z: float = -6.0
    # Obstacle hit threshold on Z axis.
    # Higher value => easier to collide.
    # Practical range: 0.8 ~ 1.8
    collision_z_threshold: float = 1.3


@dataclass(frozen=True)
class MovementConfig:
    # Initial world speed at run start.
    # Practical range: 8 ~ 16
    start_speed: float = 12.0
    # Target world speed after difficulty ramp completes.
    # Should be >= start_speed.
    # Practical range: 16 ~ 30
    end_speed: float = 22.0
    # Passive score gain per second (before pickup bonuses).
    # Practical range: 6 ~ 20
    score_per_second: float = 10.0


@dataclass(frozen=True)
class WorldConfig:
    # Length of one repeating ground segment.
    # Larger value => less frequent repositioning.
    # Practical range: 40 ~ 100
    ground_segment_length: float = 60.0
    # Number of ground segments used in loop.
    # Higher value => longer visible track, slightly more entities.
    # Practical range: 3 ~ 6
    ground_segments: int = 4
    # Z spawn point for obstacles and collectibles.
    # Should be far enough ahead for reaction time.
    # Practical range: 45 ~ 90
    obstacle_spawn_z: float = 65.0
    # Z cleanup line: entities behind this line are destroyed.
    # Keep less than player z.
    # Practical range: -35 ~ -12
    obstacle_cleanup_z: float = -20.0
    # Visual road width.
    # Should cover lane spread comfortably.
    # Practical range: 9 ~ 16
    road_width: float = 10.0


@dataclass(frozen=True)
class SpawnerConfig:
    # Obstacle spawn interval at start difficulty (seconds).
    # Constraint: min <= max and both > 0.
    # Practical range start_min: 0.7 ~ 1.3
    start_min_spawn_interval: float = 0.95
    # Practical range start_max: 1.0 ~ 1.8
    start_max_spawn_interval: float = 1.35
    # Obstacle spawn interval at max difficulty (seconds).
    # Constraint: min <= max and both > 0.
    # Practical range end_min: 0.35 ~ 0.9
    end_min_spawn_interval: float = 0.50
    # Practical range end_max: 0.55 ~ 1.2
    end_max_spawn_interval: float = 0.78
    # Chance to spawn 2-lane obstacle pattern at start difficulty (0~1).
    # Practical range: 0.05 ~ 0.35
    start_two_obstacle_chance: float = 0.18
    # Chance to spawn 2-lane obstacle pattern at max difficulty (0~1).
    # Practical range: 0.35 ~ 0.80
    end_two_obstacle_chance: float = 0.58


@dataclass(frozen=True)
class CollectibleConfig:
    # Collectible spawn interval at start difficulty (seconds).
    # Constraint: min <= max and both > 0.
    # Practical range start_min: 0.8 ~ 1.8
    start_min_spawn_interval: float = 1.15
    # Practical range start_max: 1.1 ~ 2.4
    start_max_spawn_interval: float = 1.85
    # Collectible spawn interval at max difficulty (seconds).
    # Constraint: min <= max and both > 0.
    # Practical range end_min: 0.45 ~ 1.1
    end_min_spawn_interval: float = 0.72
    # Practical range end_max: 0.7 ~ 1.6
    end_max_spawn_interval: float = 1.25
    # Score bonus per collected item.
    # Practical range: 2 ~ 20
    reward_score: int = 5
    # Minimum Z distance from obstacle at spawn lane.
    # Higher value => less visual overlap chance.
    # Practical range: 5.0 ~ 14.0
    min_obstacle_distance_z: float = 8.5
    # Maximum active collectibles at once.
    # Practical range: 3 ~ 14
    max_active: int = 7
    # Baseline collectible height.
    # Keep above obstacles for readability if desired.
    # Practical range: 1.6 ~ 3.2
    y: float = 2.2
    # Collectible overall size multiplier.
    # Bigger value => easier to spot and collect at distance.
    # Too high can look oversized and reduce lane readability.
    # Practical range: 0.55 ~ 1.10
    scale: float = 1.0
    # Z threshold for pickup detection.
    # Higher value => easier pickup window.
    # Practical range: 0.8 ~ 2.0
    pickup_z_threshold: float = 1.2
    # Vertical bob amplitude.
    # Practical range: 0.08 ~ 0.35
    bob_amplitude: float = 0.16
    # Vertical bob speed.
    # Practical range: 1.5 ~ 6.0
    bob_speed: float = 3.0
    # Ring/core rotation speed, in degrees per second.
    # Higher value => stronger sci-fi/energy feel.
    # Too high can look jittery/noisy in motion.
    # Practical range: 90 ~ 220
    spin_speed: float = 140.0
    # Glow quad scale relative to collectible size.
    # Practical range: 1.8 ~ 3.6
    glow_scale: float = 2.6
    # Glow base alpha (opacity), 0~255.
    # Higher value => pickup is more prominent against the track.
    # Lower value => subtler, cleaner look.
    # Practical range: 70 ~ 170
    glow_alpha: int = 105


@dataclass(frozen=True)
class DifficultyConfig:
    # Time in seconds to reach max difficulty interpolation (t=1.0).
    # Lower value => faster difficulty spike.
    # Practical range: 50 ~ 180
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


# ------------------------------------------------------------
# Quick Presets (copy values into fields above)
#
# CASUAL (more forgiving, slower pressure)
# movement.start_speed = 9.5
# movement.end_speed = 17.0
# movement.score_per_second = 9.0
# difficulty.ramp_seconds = 125.0
# spawner.start_min_spawn_interval = 1.10
# spawner.start_max_spawn_interval = 1.60
# spawner.end_min_spawn_interval = 0.70
# spawner.end_max_spawn_interval = 1.10
# spawner.start_two_obstacle_chance = 0.10
# spawner.end_two_obstacle_chance = 0.42
# collectible.start_min_spawn_interval = 0.95
# collectible.start_max_spawn_interval = 1.65
# collectible.end_min_spawn_interval = 0.60
# collectible.end_max_spawn_interval = 1.05
# collectible.reward_score = 6
# collectible.max_active = 9
# collectible.pickup_z_threshold = 1.45
#
# BALANCED (recommended default target feel)
# movement.start_speed = 12.0
# movement.end_speed = 22.0
# movement.score_per_second = 10.0
# difficulty.ramp_seconds = 70.0
# spawner.start_min_spawn_interval = 0.95
# spawner.start_max_spawn_interval = 1.35
# spawner.end_min_spawn_interval = 0.50
# spawner.end_max_spawn_interval = 0.78
# spawner.start_two_obstacle_chance = 0.18
# spawner.end_two_obstacle_chance = 0.58
# collectible.start_min_spawn_interval = 1.15
# collectible.start_max_spawn_interval = 1.85
# collectible.end_min_spawn_interval = 0.72
# collectible.end_max_spawn_interval = 1.25
# collectible.reward_score = 5
# collectible.max_active = 7
# collectible.pickup_z_threshold = 1.20
#
# HARDCORE (high pressure, fast pace, stricter pickups)
# movement.start_speed = 13.5
# movement.end_speed = 27.0
# movement.score_per_second = 12.0
# difficulty.ramp_seconds = 45.0
# spawner.start_min_spawn_interval = 0.78
# spawner.start_max_spawn_interval = 1.05
# spawner.end_min_spawn_interval = 0.35
# spawner.end_max_spawn_interval = 0.58
# spawner.start_two_obstacle_chance = 0.24
# spawner.end_two_obstacle_chance = 0.76
# collectible.start_min_spawn_interval = 1.30
# collectible.start_max_spawn_interval = 2.10
# collectible.end_min_spawn_interval = 0.95
# collectible.end_max_spawn_interval = 1.45
# collectible.reward_score = 4
# collectible.max_active = 5
# collectible.pickup_z_threshold = 1.00
# ------------------------------------------------------------
CONFIG = GameConfig()

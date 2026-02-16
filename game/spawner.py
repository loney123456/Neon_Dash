import random
from typing import AbstractSet, Optional

from ursina import Entity, color, destroy

from config import LaneConfig, SpawnerConfig, WorldConfig


class ObstacleSpawner:
    def __init__(
        self,
        lane_cfg: LaneConfig,
        world_cfg: WorldConfig,
        spawner_cfg: SpawnerConfig,
    ) -> None:
        self.lane_cfg = lane_cfg
        self.world_cfg = world_cfg
        self.spawner_cfg = spawner_cfg
        self.spawn_timer = 0.0
        self.next_interval = self._pick_next_interval(0.0)
        self.obstacles: list[Entity] = []

    @staticmethod
    def _lerp(a: float, b: float, t: float) -> float:
        return a + (b - a) * t

    def _pick_next_interval(self, difficulty_t: float) -> float:
        min_interval = self._lerp(
            self.spawner_cfg.start_min_spawn_interval,
            self.spawner_cfg.end_min_spawn_interval,
            difficulty_t,
        )
        max_interval = self._lerp(
            self.spawner_cfg.start_max_spawn_interval,
            self.spawner_cfg.end_max_spawn_interval,
            difficulty_t,
        )
        return random.uniform(
            min_interval,
            max_interval,
        )

    def reset(self) -> None:
        self.spawn_timer = 0.0
        self.next_interval = self._pick_next_interval(0.0)
        for obstacle in self.obstacles:
            destroy(obstacle)
        self.obstacles.clear()

    def _spawn_obstacle(self, lane_index: int) -> None:
        obstacle = Entity(
            model="cube",
            color=color.rgb(255, 93, 125),
            position=(
                self.lane_cfg.x_positions[lane_index],
                1.0,
                self.world_cfg.obstacle_spawn_z,
            ),
            scale=(1.2, 2.0, 1.4),
            collider="box",
        )
        obstacle.lane_index = lane_index
        self.obstacles.append(obstacle)

    def _spawn_pattern(
        self,
        difficulty_t: float,
        blocked_lanes: Optional[AbstractSet[int]] = None,
    ) -> None:
        blocked_lanes = blocked_lanes or set()
        lanes = [0, 1, 2]
        lanes = [lane for lane in lanes if lane not in blocked_lanes]
        if not lanes:
            return

        two_obstacle_chance = self._lerp(
            self.spawner_cfg.start_two_obstacle_chance,
            self.spawner_cfg.end_two_obstacle_chance,
            difficulty_t,
        )
        lane_count = 1
        if random.random() < two_obstacle_chance:
            lane_count = 2
        lane_count = min(lane_count, len(lanes))
        blocked = random.sample(lanes, k=lane_count)
        for lane in blocked:
            self._spawn_obstacle(lane)

    def update(
        self,
        dt: float,
        speed: float,
        difficulty_t: float,
        blocked_lanes: Optional[AbstractSet[int]] = None,
    ) -> None:
        self.spawn_timer += dt
        if self.spawn_timer >= self.next_interval:
            self.spawn_timer = 0.0
            self.next_interval = self._pick_next_interval(difficulty_t)
            self._spawn_pattern(difficulty_t, blocked_lanes)

        cleanup_z = self.world_cfg.obstacle_cleanup_z
        active_obstacles: list[Entity] = []
        for obstacle in self.obstacles:
            obstacle.z -= speed * dt
            if obstacle.z > cleanup_z:
                active_obstacles.append(obstacle)
            else:
                destroy(obstacle)
        self.obstacles = active_obstacles

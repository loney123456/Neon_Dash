import random
from typing import AbstractSet, Optional

from ursina import Entity, color

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
        self._pool: list[Entity] = []
        self._created_count = 0
        self._pool_max_size = max(1, self.spawner_cfg.pool_max_size)
        self._pool_initial_size = max(0, min(self.spawner_cfg.pool_initial_size, self._pool_max_size))
        self._prewarm_pool()

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

    def _prewarm_pool(self) -> None:
        for _ in range(self._pool_initial_size):
            obstacle = self._create_obstacle_entity()
            obstacle._in_pool = True
            self._pool.append(obstacle)

    def _create_obstacle_entity(self) -> Entity:
        obstacle = Entity(
            model="cube",
            color=color.rgb(255, 93, 125),
            position=(0, -1000, self.world_cfg.obstacle_cleanup_z - 100.0),
            scale=(1.2, 2.0, 1.4),
            collider="box",
            enabled=False,
        )
        obstacle.lane_index = 1
        obstacle._in_pool = False
        self._created_count += 1
        return obstacle

    def _acquire_obstacle(self) -> Optional[Entity]:
        obstacle: Optional[Entity] = None
        if self._pool:
            obstacle = self._pool.pop()
        elif self._created_count < self._pool_max_size:
            obstacle = self._create_obstacle_entity()
        if obstacle is None:
            return None
        obstacle._in_pool = False
        obstacle.enabled = True
        return obstacle

    def _release_obstacle(self, obstacle: Entity) -> None:
        if getattr(obstacle, "_in_pool", False):
            return
        obstacle.enabled = False
        obstacle.position = (0, -1000, self.world_cfg.obstacle_cleanup_z - 100.0)
        obstacle._in_pool = True
        self._pool.append(obstacle)

    def reset(self) -> None:
        self.spawn_timer = 0.0
        self.next_interval = self._pick_next_interval(0.0)
        for obstacle in self.obstacles:
            self._release_obstacle(obstacle)
        self.obstacles.clear()

    def _spawn_obstacle(self, lane_index: int) -> bool:
        obstacle = self._acquire_obstacle()
        if obstacle is None:
            return False
        obstacle.position = (
            self.lane_cfg.x_positions[lane_index],
            1.0,
            self.world_cfg.obstacle_spawn_z,
        )
        obstacle.lane_index = lane_index
        self.obstacles.append(obstacle)
        return True

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
                self._release_obstacle(obstacle)
        self.obstacles = active_obstacles

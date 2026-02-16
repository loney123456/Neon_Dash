import random

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
        self.next_interval = self._pick_next_interval()
        self.obstacles: list[Entity] = []

    def _pick_next_interval(self) -> float:
        return random.uniform(
            self.spawner_cfg.min_spawn_interval,
            self.spawner_cfg.max_spawn_interval,
        )

    def reset(self) -> None:
        self.spawn_timer = 0.0
        self.next_interval = self._pick_next_interval()
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

    def _spawn_pattern(self) -> None:
        lanes = [0, 1, 2]
        lane_count = 1
        if random.random() < self.spawner_cfg.two_obstacle_chance:
            lane_count = 2
        blocked = random.sample(lanes, k=lane_count)
        for lane in blocked:
            self._spawn_obstacle(lane)

    def update(self, dt: float, speed: float) -> None:
        self.spawn_timer += dt
        if self.spawn_timer >= self.next_interval:
            self.spawn_timer = 0.0
            self.next_interval = self._pick_next_interval()
            self._spawn_pattern()

        cleanup_z = self.world_cfg.obstacle_cleanup_z
        active_obstacles: list[Entity] = []
        for obstacle in self.obstacles:
            obstacle.z -= speed * dt
            if obstacle.z > cleanup_z:
                active_obstacles.append(obstacle)
            else:
                destroy(obstacle)
        self.obstacles = active_obstacles


import random
import unittest

from ursina import Entity, Ursina, application, destroy

from config import CollectibleConfig, LaneConfig, SpawnerConfig, WorldConfig
from game.collectibles import CollectibleSystem
from game.spawner import ObstacleSpawner


_TEST_APP = None


def _ensure_test_app() -> None:
    global _TEST_APP
    existing_base = getattr(application, "base", None)
    if existing_base is not None:
        _TEST_APP = existing_base
        return
    if _TEST_APP is None:
        _TEST_APP = Ursina(window_type="offscreen")


class TestObstacleSpawner(unittest.TestCase):
    def setUp(self) -> None:
        _ensure_test_app()
        self.lane_cfg = LaneConfig(x_positions=(-2.0, 0.0, 2.0))
        self.world_cfg = WorldConfig(obstacle_spawn_z=40.0, obstacle_cleanup_z=-10.0)
        self.spawner_cfg = SpawnerConfig(
            start_min_spawn_interval=1.0,
            start_max_spawn_interval=1.0,
            end_min_spawn_interval=1.0,
            end_max_spawn_interval=1.0,
            start_two_obstacle_chance=0.0,
            end_two_obstacle_chance=0.0,
        )
        self.spawner = ObstacleSpawner(self.lane_cfg, self.world_cfg, self.spawner_cfg)
        random.seed(7)

    def tearDown(self) -> None:
        self.spawner.reset()

    def test_spawn_pattern_respects_blocked_lanes(self) -> None:
        self.spawner._spawn_pattern(difficulty_t=0.0, blocked_lanes={1, 2})
        self.assertEqual(len(self.spawner.obstacles), 1)
        self.assertEqual(self.spawner.obstacles[0].lane_index, 0)

    def test_cleanup_removes_obstacles_behind_line(self) -> None:
        self.spawner._spawn_obstacle(0)
        self.spawner.obstacles[0].z = self.world_cfg.obstacle_cleanup_z - 1.0
        self.spawner.update(dt=0.0, speed=0.0, difficulty_t=0.0, blocked_lanes=None)
        self.assertEqual(len(self.spawner.obstacles), 0)

    def test_reset_clears_all_obstacles(self) -> None:
        self.spawner._spawn_obstacle(0)
        self.spawner._spawn_obstacle(2)
        self.assertEqual(len(self.spawner.obstacles), 2)
        self.spawner.reset()
        self.assertEqual(len(self.spawner.obstacles), 0)


class TestCollectibleSystem(unittest.TestCase):
    def setUp(self) -> None:
        _ensure_test_app()
        self.lane_cfg = LaneConfig(x_positions=(-2.0, 0.0, 2.0))
        self.world_cfg = WorldConfig(obstacle_spawn_z=50.0, obstacle_cleanup_z=-10.0)
        self.collectible_cfg = CollectibleConfig(
            start_min_spawn_interval=1.0,
            start_max_spawn_interval=1.0,
            end_min_spawn_interval=1.0,
            end_max_spawn_interval=1.0,
            min_obstacle_distance_z=8.0,
            max_active=2,
            pickup_z_threshold=1.2,
        )
        self.system = CollectibleSystem(self.lane_cfg, self.world_cfg, self.collectible_cfg)
        random.seed(11)

    def tearDown(self) -> None:
        self.system.reset()

    def test_try_spawn_avoids_unsafe_lane(self) -> None:
        obstacle = Entity(model="cube")
        obstacle.lane_index = 0
        obstacle.z = self.world_cfg.obstacle_spawn_z
        self.system._try_spawn([obstacle])
        self.assertEqual(len(self.system.collectibles), 1)
        self.assertIn(self.system.collectibles[0].lane_index, {1, 2})
        destroy(obstacle)

    def test_max_active_limit_is_respected(self) -> None:
        self.system._spawn_collectible(0)
        self.system._spawn_collectible(1)
        self.assertEqual(len(self.system.collectibles), self.collectible_cfg.max_active)
        self.system._try_spawn([])
        self.assertEqual(len(self.system.collectibles), self.collectible_cfg.max_active)

    def test_collect_at_removes_collectible_and_returns_count(self) -> None:
        self.system._spawn_collectible(1)
        self.system.collectibles[0].z = -2.0
        count = self.system.collect_at(player_lane=1, player_z=-2.0, threshold=1.2)
        self.assertEqual(count, 1)
        self.assertEqual(len(self.system.collectibles), 0)

    def test_lanes_blocked_near_spawn(self) -> None:
        self.system._spawn_collectible(0)
        self.system._spawn_collectible(2)
        self.system.collectibles[0].z = self.world_cfg.obstacle_spawn_z - 1.0
        self.system.collectibles[1].z = self.world_cfg.obstacle_spawn_z + 20.0
        blocked = self.system.lanes_blocked_near_spawn(min_distance_z=8.0)
        self.assertEqual(blocked, {0})

    def test_reset_clears_collectibles(self) -> None:
        self.system._spawn_collectible(0)
        self.system._spawn_collectible(2)
        self.assertEqual(len(self.system.collectibles), 2)
        self.system.reset()
        self.assertEqual(len(self.system.collectibles), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

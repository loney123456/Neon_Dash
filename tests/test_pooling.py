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


class TestObstaclePooling(unittest.TestCase):
    def setUp(self) -> None:
        _ensure_test_app()
        random.seed(3)
        lane_cfg = LaneConfig(x_positions=(-2.0, 0.0, 2.0))
        world_cfg = WorldConfig(obstacle_spawn_z=40.0, obstacle_cleanup_z=-10.0)
        spawner_cfg = SpawnerConfig(
            start_min_spawn_interval=1.0,
            start_max_spawn_interval=1.0,
            end_min_spawn_interval=1.0,
            end_max_spawn_interval=1.0,
            start_two_obstacle_chance=0.0,
            end_two_obstacle_chance=0.0,
            pool_initial_size=2,
            pool_max_size=3,
        )
        self.spawner = ObstacleSpawner(lane_cfg, world_cfg, spawner_cfg)

    def tearDown(self) -> None:
        self.spawner.reset()

    def test_prewarm_and_max_capacity(self) -> None:
        self.assertEqual(self.spawner._created_count, 2)
        self.assertEqual(len(self.spawner._pool), 2)

        self.spawner._spawn_obstacle(0)
        self.spawner._spawn_obstacle(1)
        self.spawner._spawn_obstacle(2)
        self.assertEqual(self.spawner._created_count, 3)
        self.assertEqual(len(self.spawner.obstacles), 3)
        self.assertEqual(len(self.spawner._pool), 0)

        # At cap with no idle objects: further spawn should be skipped.
        spawned = self.spawner._spawn_obstacle(0)
        self.assertFalse(spawned)
        self.assertEqual(self.spawner._created_count, 3)
        self.assertEqual(len(self.spawner.obstacles), 3)

    def test_cleanup_and_reset_release_back_to_pool(self) -> None:
        self.spawner._spawn_obstacle(0)
        self.spawner._spawn_obstacle(1)
        self.assertEqual(len(self.spawner.obstacles), 2)

        self.spawner.obstacles[0].z = self.spawner.world_cfg.obstacle_cleanup_z - 1.0
        self.spawner.update(dt=0.0, speed=0.0, difficulty_t=0.0, blocked_lanes=None)
        self.assertEqual(len(self.spawner.obstacles), 1)
        self.assertEqual(len(self.spawner._pool), 1)

        self.spawner.reset()
        self.assertEqual(len(self.spawner.obstacles), 0)
        self.assertEqual(len(self.spawner._pool), self.spawner._created_count)

    def test_blocked_lanes_logic_is_kept(self) -> None:
        self.spawner._spawn_pattern(difficulty_t=0.0, blocked_lanes={0, 1})
        self.assertEqual(len(self.spawner.obstacles), 1)
        self.assertEqual(self.spawner.obstacles[0].lane_index, 2)


class TestCollectiblePooling(unittest.TestCase):
    def setUp(self) -> None:
        _ensure_test_app()
        random.seed(9)
        lane_cfg = LaneConfig(x_positions=(-2.0, 0.0, 2.0))
        world_cfg = WorldConfig(obstacle_spawn_z=50.0, obstacle_cleanup_z=-10.0)
        collectible_cfg = CollectibleConfig(
            start_min_spawn_interval=1.0,
            start_max_spawn_interval=1.0,
            end_min_spawn_interval=1.0,
            end_max_spawn_interval=1.0,
            min_obstacle_distance_z=8.0,
            max_active=2,
            pool_initial_size=1,
            pool_max_size=2,
        )
        self.system = CollectibleSystem(lane_cfg, world_cfg, collectible_cfg)

    def tearDown(self) -> None:
        self.system.reset()

    def test_prewarm_and_max_capacity(self) -> None:
        self.assertEqual(self.system._created_count, 1)
        self.assertEqual(len(self.system._pool), 1)

        self.system._spawn_collectible(0)
        self.system._spawn_collectible(1)
        self.assertEqual(self.system._created_count, 2)
        self.assertEqual(len(self.system.collectibles), 2)
        self.assertEqual(len(self.system._pool), 0)

        # Over max_active: no additional active collectible.
        self.system._spawn_collectible(2)
        self.assertEqual(len(self.system.collectibles), 2)
        self.assertEqual(self.system._created_count, 2)

    def test_collect_and_cleanup_release_back_to_pool(self) -> None:
        self.system._spawn_collectible(1)
        spawned = self.system.collectibles[0]
        spawned.z = -2.0
        collected = self.system.collect_at(player_lane=1, player_z=-2.0, threshold=1.2)
        self.assertEqual(collected, 1)
        self.assertEqual(len(self.system.collectibles), 0)
        self.assertEqual(len(self.system._pool), 1)

        # Re-acquire should reuse pooled object without creating new one.
        created_before = self.system._created_count
        self.system._spawn_collectible(2)
        self.assertEqual(self.system._created_count, created_before)
        self.assertIs(self.system.collectibles[0], spawned)

        self.system.collectibles[0].z = self.system.world_cfg.obstacle_cleanup_z - 1.0
        self.system.update(dt=0.0, speed=0.0, difficulty_t=0.0, obstacles=[])
        self.assertEqual(len(self.system.collectibles), 0)
        self.assertEqual(len(self.system._pool), 1)

    def test_reset_releases_everything(self) -> None:
        self.system._spawn_collectible(0)
        self.system._spawn_collectible(2)
        self.assertEqual(len(self.system.collectibles), 2)
        self.system.reset()
        self.assertEqual(len(self.system.collectibles), 0)
        self.assertEqual(len(self.system._pool), self.system._created_count)

    def test_lanes_blocked_near_spawn_logic_is_kept(self) -> None:
        self.system._spawn_collectible(0)
        self.system._spawn_collectible(1)
        self.system.collectibles[0].z = self.system.world_cfg.obstacle_spawn_z
        self.system.collectibles[1].z = self.system.world_cfg.obstacle_spawn_z + 20.0
        blocked = self.system.lanes_blocked_near_spawn(8.0)
        self.assertEqual(blocked, {0})

        self.system.reset()
        self.system._spawn_collectible(0)
        blocker = Entity(model="cube")
        blocker.lane_index = 2
        blocker.z = self.system.world_cfg.obstacle_spawn_z
        self.system._try_spawn([blocker])
        self.assertNotIn(2, [c.lane_index for c in self.system.collectibles])
        destroy(blocker)


if __name__ == "__main__":
    unittest.main(verbosity=2)

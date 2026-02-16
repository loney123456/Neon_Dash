import random
import math
from typing import Sequence

from ursina import Entity, color, destroy

from config import CollectibleConfig, LaneConfig, WorldConfig


class CollectibleSystem:
    def __init__(
        self,
        lane_cfg: LaneConfig,
        world_cfg: WorldConfig,
        collectible_cfg: CollectibleConfig,
    ) -> None:
        self.lane_cfg = lane_cfg
        self.world_cfg = world_cfg
        self.collectible_cfg = collectible_cfg
        self.spawn_timer = 0.0
        self.next_interval = self._pick_next_interval(0.0)
        self.collectibles: list[Entity] = []
        self._anim_time = 0.0

    @staticmethod
    def _lerp(a: float, b: float, t: float) -> float:
        return a + (b - a) * t

    def _pick_next_interval(self, difficulty_t: float) -> float:
        min_interval = self._lerp(
            self.collectible_cfg.start_min_spawn_interval,
            self.collectible_cfg.end_min_spawn_interval,
            difficulty_t,
        )
        max_interval = self._lerp(
            self.collectible_cfg.start_max_spawn_interval,
            self.collectible_cfg.end_max_spawn_interval,
            difficulty_t,
        )
        return random.uniform(min_interval, max_interval)

    def reset(self) -> None:
        self.spawn_timer = 0.0
        self.next_interval = self._pick_next_interval(0.0)
        for collectible in self.collectibles:
            destroy(collectible)
        self.collectibles.clear()

    def _lane_is_safe_for_spawn(self, lane_index: int, obstacles: Sequence[Entity]) -> bool:
        spawn_z = self.world_cfg.obstacle_spawn_z
        min_distance = self.collectible_cfg.min_obstacle_distance_z
        for obstacle in obstacles:
            if obstacle.lane_index != lane_index:
                continue
            if abs(obstacle.z - spawn_z) < min_distance:
                return False
        return True

    def _spawn_collectible(self, lane_index: int) -> None:
        collectible = Entity(
            model="sphere",
            color=color.rgb(255, 214, 64),
            position=(
                self.lane_cfg.x_positions[lane_index],
                self.collectible_cfg.y,
                self.world_cfg.obstacle_spawn_z,
            ),
            scale=self.collectible_cfg.scale * 0.46,
            collider="box",
        )
        collectible.lane_index = lane_index
        collectible.base_y = self.collectible_cfg.y
        collectible.phase = random.uniform(0.0, math.tau)
        collectible.core = Entity(
            parent=collectible,
            model="sphere",
            color=color.rgb(255, 246, 190),
            scale=0.62,
        )
        collectible.outer_ring = Entity(
            parent=collectible,
            model="quad",
            texture="circle_outlined",
            color=color.rgba(255, 214, 92, 230),
            scale=self.collectible_cfg.scale * 2.2,
            double_sided=True,
        )
        collectible.inner_ring = Entity(
            parent=collectible,
            model="quad",
            texture="circle_outlined",
            color=color.rgba(255, 170, 72, 220),
            scale=self.collectible_cfg.scale * 1.42,
            rotation=(68, 0, 20),
            double_sided=True,
        )
        collectible.glow = Entity(
            parent=collectible,
            model="quad",
            texture="circle",
            color=color.rgba(255, 224, 128, self.collectible_cfg.glow_alpha),
            billboard=True,
            scale=self.collectible_cfg.scale * (self.collectible_cfg.glow_scale + 0.55),
            double_sided=True,
        )
        collectible.spark = Entity(
            parent=collectible,
            model="sphere",
            color=color.rgba(255, 255, 255, 220),
            scale=self.collectible_cfg.scale * 0.15,
            position=(self.collectible_cfg.scale * 1.08, 0, 0),
        )
        collectible.outer_ring_base_scale = collectible.outer_ring.scale
        collectible.inner_ring_base_scale = collectible.inner_ring.scale
        self.collectibles.append(collectible)

    def _try_spawn(self, obstacles: Sequence[Entity]) -> None:
        if len(self.collectibles) >= self.collectible_cfg.max_active:
            return

        lanes = list(range(len(self.lane_cfg.x_positions)))
        random.shuffle(lanes)
        for lane_index in lanes:
            if self._lane_is_safe_for_spawn(lane_index, obstacles):
                self._spawn_collectible(lane_index)
                return

    def collect_at(self, player_lane: int, player_z: float, threshold: float) -> int:
        active_collectibles: list[Entity] = []
        collected_count = 0
        for collectible in self.collectibles:
            same_lane = collectible.lane_index == player_lane
            close_enough = abs(collectible.z - player_z) <= threshold
            if same_lane and close_enough:
                collected_count += 1
                destroy(collectible)
            else:
                active_collectibles.append(collectible)
        self.collectibles = active_collectibles
        return collected_count

    def lanes_blocked_near_spawn(self, min_distance_z: float) -> set[int]:
        spawn_z = self.world_cfg.obstacle_spawn_z
        blocked_lanes: set[int] = set()
        for collectible in self.collectibles:
            if abs(collectible.z - spawn_z) < min_distance_z:
                blocked_lanes.add(collectible.lane_index)
        return blocked_lanes

    def update(
        self,
        dt: float,
        speed: float,
        difficulty_t: float,
        obstacles: Sequence[Entity],
    ) -> None:
        self._anim_time += dt
        cleanup_z = self.world_cfg.obstacle_cleanup_z
        active_collectibles: list[Entity] = []
        for collectible in self.collectibles:
            collectible.rotation_y += self.collectible_cfg.spin_speed * dt
            collectible.outer_ring.rotation_z += self.collectible_cfg.spin_speed * 1.9 * dt
            collectible.inner_ring.rotation_x += self.collectible_cfg.spin_speed * 1.2 * dt
            collectible.inner_ring.rotation_y -= self.collectible_cfg.spin_speed * 0.7 * dt
            orbit_t = self._anim_time * (self.collectible_cfg.bob_speed * 1.8) + collectible.phase
            collectible.spark.x = math.cos(orbit_t) * (self.collectible_cfg.scale * 1.06)
            collectible.spark.y = math.sin(orbit_t) * (self.collectible_cfg.scale * 0.42)
            collectible.y = collectible.base_y + math.sin(
                self._anim_time * self.collectible_cfg.bob_speed + collectible.phase,
            ) * self.collectible_cfg.bob_amplitude
            pulse = 1.0 + 0.18 * math.sin(
                self._anim_time * (self.collectible_cfg.bob_speed * 1.7) + collectible.phase,
            )
            collectible.outer_ring.scale = collectible.outer_ring_base_scale * (0.96 + 0.08 * pulse)
            collectible.inner_ring.scale = collectible.inner_ring_base_scale * (0.94 + 0.10 * pulse)
            collectible.glow.scale = self.collectible_cfg.scale * (self.collectible_cfg.glow_scale + 0.55) * pulse
            glow_alpha = int(
                self.collectible_cfg.glow_alpha
                + 34 * math.sin(self._anim_time * (self.collectible_cfg.bob_speed * 2.1) + collectible.phase),
            )
            glow_alpha = max(45, min(180, glow_alpha))
            collectible.glow.color = color.rgba(255, 224, 128, glow_alpha)
            collectible.z -= speed * dt
            if collectible.z > cleanup_z:
                active_collectibles.append(collectible)
            else:
                destroy(collectible)
        self.collectibles = active_collectibles

        self.spawn_timer += dt
        if self.spawn_timer >= self.next_interval:
            self.spawn_timer = 0.0
            self.next_interval = self._pick_next_interval(difficulty_t)
            self._try_spawn(obstacles)

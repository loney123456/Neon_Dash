from ursina import Entity, color

from config import LaneConfig, WorldConfig


class WorldSystem:
    def __init__(self, world_cfg: WorldConfig, lane_cfg: LaneConfig) -> None:
        self.world_cfg = world_cfg
        self.lane_cfg = lane_cfg
        self.ground_segments: list[Entity] = []
        self.lane_guides: list[Entity] = []
        self._create_ground()
        self._create_lane_guides()

    def _create_ground(self) -> None:
        length = self.world_cfg.ground_segment_length
        for i in range(self.world_cfg.ground_segments):
            segment = Entity(
                model="cube",
                color=color.rgb(17, 20, 30),
                position=(0, 0, i * length),
                scale=(self.world_cfg.road_width, 0.2, length),
            )
            self.ground_segments.append(segment)

    def _create_lane_guides(self) -> None:
        for x in self.lane_cfg.x_positions:
            line = Entity(
                model="cube",
                color=color.rgba(65, 248, 255, 160),
                position=(x, 0.11, 0),
                scale=(0.06, 0.03, self.world_cfg.ground_segment_length * self.world_cfg.ground_segments),
            )
            self.lane_guides.append(line)

    def reset(self) -> None:
        length = self.world_cfg.ground_segment_length
        for i, segment in enumerate(self.ground_segments):
            segment.z = i * length

    def update(self, dt: float, speed: float) -> None:
        length = self.world_cfg.ground_segment_length
        total_length = length * len(self.ground_segments)
        for segment in self.ground_segments:
            segment.z -= speed * dt
            if segment.z < -length:
                segment.z += total_length


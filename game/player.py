from ursina import Entity, color, lerp

from config import LaneConfig, PlayerConfig


class PlayerController:
    def __init__(self, lane_cfg: LaneConfig, player_cfg: PlayerConfig) -> None:
        self.lane_cfg = lane_cfg
        self.player_cfg = player_cfg
        self.lane_index = 1
        self.target_x = self.lane_cfg.x_positions[self.lane_index]
        self.entity = Entity(
            model="cube",
            color=color.cyan,
            position=(self.target_x, self.player_cfg.y, self.player_cfg.z),
            scale=(1.0, 1.0, 2.0),
            collider="box",
        )

    @property
    def x(self) -> float:
        return self.entity.x

    @property
    def z(self) -> float:
        return self.entity.z

    def reset(self) -> None:
        self.lane_index = 1
        self.target_x = self.lane_cfg.x_positions[self.lane_index]
        self.entity.x = self.target_x

    def move_left(self) -> None:
        if self.lane_index > 0:
            self.lane_index -= 1
            self.target_x = self.lane_cfg.x_positions[self.lane_index]

    def move_right(self) -> None:
        if self.lane_index < len(self.lane_cfg.x_positions) - 1:
            self.lane_index += 1
            self.target_x = self.lane_cfg.x_positions[self.lane_index]

    def update(self, dt: float) -> None:
        t = min(1.0, self.lane_cfg.switch_lerp_speed * dt)
        self.entity.x = lerp(self.entity.x, self.target_x, t)

from panda3d.core import ConfigVariableBool, ConfigVariableDouble, ConfigVariableString, loadPrcFileData

# Apply frame pacing config before Ursina/Panda window is created.
loadPrcFileData("", "sync-video true")
loadPrcFileData("", "clock-mode normal")
loadPrcFileData("", "clock-frame-rate 0")

from ursina import Ursina, Vec3, application, camera, color, time, window

from config import CONFIG
from game.collectibles import CollectibleSystem
from game.hud import HudView
from game.player import PlayerController
from game.spawner import ObstacleSpawner
from game.state_machine import GameState, StateMachine
from game.world import WorldSystem


class NeonDashGame:
    def __init__(self) -> None:
        self.state = StateMachine(GameState.START)
        self.player = PlayerController(CONFIG.lane, CONFIG.player)
        self.world = WorldSystem(CONFIG.world, CONFIG.lane)
        self.spawner = ObstacleSpawner(CONFIG.lane, CONFIG.world, CONFIG.spawner)
        self.collectibles = CollectibleSystem(CONFIG.lane, CONFIG.world, CONFIG.collectible)
        self.hud = HudView(resume_countdown_style=CONFIG.hud.resume_countdown_style)
        self.resume_countdown_duration = 3.0
        self.resume_countdown_remaining = 0.0
        self.elapsed_time = 0.0
        self.score = 0

        self._setup_scene()
        self.hud.set_state(self.state.state)

    def _setup_scene(self) -> None:
        window.title = "Neon Dash"
        window.color = color.rgb(8, 10, 17)
        # Keep rendering synced with monitor refresh for stable/credible FPS display.
        if hasattr(window, "vsync"):
            window.vsync = True
        if hasattr(application, "target_frame_rate"):
            application.target_frame_rate = 0
        if hasattr(window, "fps_counter") and window.fps_counter:
            window.fps_counter.enabled = False
        print(
            "[FPS-Config] "
            f"sync-video={bool(ConfigVariableBool('sync-video').getValue())}, "
            f"clock-mode={ConfigVariableString('clock-mode').getValue()}, "
            f"clock-frame-rate={float(ConfigVariableDouble('clock-frame-rate').getValue())}, "
            f"window.vsync={getattr(window, 'vsync', None)}, "
            f"target_frame_rate={getattr(application, 'target_frame_rate', None)}",
        )
        camera.position = Vec3(0, 13, -28)
        camera.rotation_x = 22
        camera.fov = 50

    @staticmethod
    def _lerp(a: float, b: float, t: float) -> float:
        return a + (b - a) * t

    def _difficulty_t(self) -> float:
        ramp = max(CONFIG.difficulty.ramp_seconds, 1.0)
        return min(1.0, self.elapsed_time / ramp)

    def _current_speed(self) -> float:
        t = self._difficulty_t()
        return self._lerp(
            CONFIG.movement.start_speed,
            CONFIG.movement.end_speed,
            t,
        )

    def _set_state(self, new_state: GameState) -> None:
        if self.state.set_state(new_state):
            self.hud.set_state(new_state)

    def _start_run(self) -> None:
        self.elapsed_time = 0.0
        self.score = 0
        self.resume_countdown_remaining = 0.0
        self.player.reset()
        self.world.reset()
        self.spawner.reset()
        self.collectibles.reset()
        self.hud.hide_resume_countdown()
        self.hud.set_score(self.score)
        self.hud.set_elapsed_time(self.elapsed_time)
        self._set_state(GameState.PLAYING)

    def _end_run(self) -> None:
        self._set_state(GameState.GAME_OVER)

    def _start_resume_countdown(self) -> None:
        self.resume_countdown_remaining = self.resume_countdown_duration
        self.hud.start_resume_countdown(self.resume_countdown_duration)
        self._set_state(GameState.RESUMING)

    def _cancel_resume_countdown(self) -> None:
        self.resume_countdown_remaining = 0.0
        self.hud.hide_resume_countdown()
        self._set_state(GameState.PAUSED)

    def input(self, key: str) -> None:
        if key in {"escape", "p"}:
            if self.state.is_state(GameState.PLAYING):
                self._set_state(GameState.PAUSED)
            elif self.state.is_state(GameState.PAUSED):
                self._start_resume_countdown()
            elif self.state.is_state(GameState.RESUMING):
                self._cancel_resume_countdown()
            return

        if self.state.is_state(GameState.START):
            if key == "space":
                self._start_run()
            return

        if self.state.is_state(GameState.GAME_OVER):
            if key in {"r", "space"}:
                self._start_run()
            return

        if not self.state.is_state(GameState.PLAYING):
            return

        if key in {"a", "left arrow"}:
            self.player.move_left()
        elif key in {"d", "right arrow"}:
            self.player.move_right()

    def _check_collision(self) -> bool:
        player_lane = self.player.lane_index
        player_z = self.player.z
        threshold = CONFIG.player.collision_z_threshold

        for obstacle in self.spawner.obstacles:
            same_lane = obstacle.lane_index == player_lane
            close_enough = abs(obstacle.z - player_z) <= threshold
            if same_lane and close_enough:
                return True
        return False

    def update(self) -> None:
        dt = time.dt
        self.hud.update(dt)
        self.hud.set_elapsed_time(self.elapsed_time)

        if self.state.is_state(GameState.RESUMING):
            self.resume_countdown_remaining = max(0.0, self.resume_countdown_remaining - dt)
            self.hud.set_resume_countdown_remaining(self.resume_countdown_remaining)
            if self.resume_countdown_remaining <= 0.0:
                self.hud.hide_resume_countdown()
                self._set_state(GameState.PLAYING)
            return

        if not self.state.is_state(GameState.PLAYING):
            return

        self.player.update(dt)
        self.elapsed_time += dt
        self.hud.set_elapsed_time(self.elapsed_time)
        difficulty_t = self._difficulty_t()
        speed = self._current_speed()
        self.world.update(dt, speed)
        blocked_lanes = self.collectibles.lanes_blocked_near_spawn(
            CONFIG.collectible.min_obstacle_distance_z,
        )
        self.spawner.update(dt, speed, difficulty_t, blocked_lanes=blocked_lanes)
        self.collectibles.update(dt, speed, difficulty_t, self.spawner.obstacles)

        collected_count = self.collectibles.collect_at(
            player_lane=self.player.lane_index,
            player_z=self.player.z,
            threshold=CONFIG.collectible.pickup_z_threshold,
        )
        if collected_count > 0:
            bonus_score = collected_count * CONFIG.collectible.reward_score
            self.score += bonus_score * 10
            self.hud.show_pickup_bonus(f"+{bonus_score}")

        self.score += int(dt * CONFIG.movement.score_per_second * 10)
        self.hud.set_score(self.score // 10)

        if self._check_collision():
            self._end_run()


try:
    app = Ursina(vsync=True)
except TypeError:
    app = Ursina()
game = NeonDashGame()


def update() -> None:
    game.update()


def input(key: str) -> None:
    game.input(key)


app.run()

import math
from ursina import Entity, Text, camera, color, window
from game.state_machine import GameState


class HudView:
    def __init__(self, resume_countdown_style: str = "cyber") -> None:
        self._resume_style = (
            resume_countdown_style if resume_countdown_style in {"cyber", "minimal"} else "cyber"
        )
        self.score_text = Text(
            text="Score: 0",
            origin=(-0.5, 0),
            position=(-0.86, 0.45),
            color=color.azure,
            scale=1.6,
        )
        self.time_text = Text(
            text="Time: 00:00.00",
            origin=(0, 0),
            position=(0.0, 0.46),
            color=color.rgb(178, 228, 255),
            scale=1.35,
        )
        self.fps_text = Text(
            text="fps:0",
            origin=(1.0, 0),
            position=(0.875, 0.46),
            color=color.light_gray,
            scale=1.16,
        )
        self.state_text = Text(
            text="Press SPACE to Start",
            origin=(0, 0),
            position=(0, 0.38),
            color=color.cyan,
            scale=1.6,
        )
        self.hint_text = Text(
            text="Move: A/D or Left/Right | Pause: ESC/P | Restart: R",
            origin=(0, 0),
            position=(0, -0.45),
            color=color.light_gray,
            scale=1.0,
        )
        self._bonus_base_x = 0.0
        self._bonus_base_y = -0.06
        self._bonus_main_scale = 2.15
        self.bonus_text = Text(
            text="",
            origin=(0, 0),
            position=(self._bonus_base_x, self._bonus_base_y),
            color=color.rgba(255, 242, 168, 255),
            scale=self._bonus_main_scale,
        )
        self._bonus_timer = 0.0
        self._bonus_duration = 0.0
        self._current_state = GameState.START
        self._fps_sample_time = 0.0
        self._fps_sample_frames = 0
        self._fps_display_interval = 0.4
        self._resume_countdown_total = 0.0
        self._resume_countdown_remaining = 0.0
        self._resume_panel_base_scale = (0.34, 0.13)
        self._minimal_value_y = 0.345
        self._minimal_value_scale = 2.0
        self._minimal_pulse_strength = 0.085
        self._minimal_pulse_speed = 10.0
        self._last_aspect_ratio = 0.0
        self._hud_top_y = 0.46

        self.resume_panel = Entity(
            parent=camera.ui,
            model="quad",
            position=(0, 0.31),
            scale=self._resume_panel_base_scale,
            color=color.rgba(12, 28, 44, 170),
            enabled=False,
        )
        self.resume_title_text = Text(
            text="Resume In",
            origin=(0, 0),
            position=(0, 0.335),
            color=color.rgb(115, 220, 255),
            scale=1.2,
        )
        self.resume_value_text = Text(
            text="3.0s",
            origin=(0, 0),
            position=(0, 0.283),
            color=color.rgb(255, 236, 140),
            scale=2.1,
        )
        self.resume_accent_line = Entity(
            parent=camera.ui,
            model="quad",
            position=(0, 0.358),
            scale=(0.18, 0.004),
            color=color.rgba(120, 240, 255, 140),
            enabled=False,
        )
        self.resume_title_text.enabled = False
        self.resume_value_text.enabled = False
        self._apply_resume_style()
        self._refresh_layout(force=True)

    @staticmethod
    def _safe_aspect_ratio() -> float:
        try:
            ratio = float(window.aspect_ratio)
        except Exception:
            ratio = 16.0 / 9.0
        return max(1.2, ratio)

    def _refresh_layout(self, force: bool = False) -> None:
        aspect = self._safe_aspect_ratio()
        if not force and abs(aspect - self._last_aspect_ratio) < 0.001:
            return
        self._last_aspect_ratio = aspect

        x_half = aspect * 0.5
        edge_padding = max(0.04, x_half * 0.05)
        scale_factor = max(0.82, min(1.0, aspect / (16.0 / 9.0)))
        top_y = self._hud_top_y

        self.score_text.position = (-x_half + edge_padding, top_y)
        self.time_text.position = (0.0, top_y)
        self.fps_text.position = (x_half - edge_padding, top_y)

        self.score_text.scale = 1.6 * scale_factor
        self.time_text.scale = 1.35 * scale_factor
        self.fps_text.scale = 1.16 * scale_factor

    def set_score(self, score: int) -> None:
        self.score_text.text = f"Score: {score}"

    def set_elapsed_time(self, elapsed_seconds: float) -> None:
        clamped = max(0.0, elapsed_seconds)
        hours = int(clamped // 3600)
        minutes = int((clamped % 3600) // 60)
        seconds = clamped % 60.0
        if hours > 0:
            self.time_text.text = f"Time: {hours:02d}:{minutes:02d}:{seconds:05.2f}"
        else:
            self.time_text.text = f"Time: {minutes:02d}:{seconds:05.2f}"

    def set_fps(self, fps: float) -> None:
        fps_int = max(0, int(round(fps)))
        self.fps_text.text = f"fps:{fps_int}"

    def show_pickup_bonus(self, text: str, duration: float = 0.75) -> None:
        self.bonus_text.text = text
        self._bonus_timer = duration
        self._bonus_duration = duration

    def start_resume_countdown(self, duration: float) -> None:
        self._resume_countdown_total = max(duration, 0.0)
        self._resume_countdown_remaining = self._resume_countdown_total
        self.resume_panel.enabled = self._resume_style == "cyber"
        self.resume_title_text.enabled = self._resume_style == "cyber"
        self.resume_value_text.enabled = True
        self.resume_accent_line.enabled = self._resume_style == "minimal"
        self._refresh_resume_countdown()

    def set_resume_countdown_remaining(self, remaining: float) -> None:
        if self._resume_countdown_total <= 0.0:
            return
        self._resume_countdown_remaining = max(remaining, 0.0)
        self._refresh_resume_countdown()

    def hide_resume_countdown(self) -> None:
        self._resume_countdown_total = 0.0
        self._resume_countdown_remaining = 0.0
        self.resume_panel.enabled = False
        self.resume_title_text.enabled = False
        self.resume_value_text.enabled = False
        self.resume_accent_line.enabled = False

    def _refresh_resume_countdown(self) -> None:
        self.resume_value_text.text = f"{self._resume_countdown_remaining:.1f}s"

    def _apply_resume_style(self) -> None:
        if self._resume_style == "minimal":
            self.resume_panel.color = color.rgba(12, 28, 44, 0)
            self.resume_panel.scale = (0.0, 0.0)
            self.resume_title_text.text = "Resuming"
            self.resume_title_text.position = (0, self._minimal_value_y + 0.032)
            self.resume_title_text.scale = 1.05
            self.resume_title_text.color = color.rgb(120, 235, 255)
            self.resume_value_text.position = (0, self._minimal_value_y)
            self.resume_value_text.scale = self._minimal_value_scale
            self.resume_value_text.color = color.rgb(255, 236, 140)
            self.resume_accent_line.position = (0, self._minimal_value_y - 0.026)
            self.resume_accent_line.scale = (0.18, 0.004)
            self.resume_accent_line.color = color.rgba(120, 240, 255, 140)
            return

        self.resume_panel.color = color.rgba(12, 28, 44, 170)
        self.resume_panel.scale = self._resume_panel_base_scale
        self.resume_title_text.text = "Resume In"
        self.resume_title_text.position = (0, 0.335)
        self.resume_title_text.scale = 1.2
        self.resume_title_text.color = color.rgb(115, 220, 255)
        self.resume_value_text.position = (0, 0.283)
        self.resume_value_text.scale = 2.1
        self.resume_value_text.color = color.rgb(255, 236, 140)

    def update(self, dt: float) -> None:
        self._refresh_layout()

        if self._current_state == GameState.PLAYING:
            clamped_dt = max(0.0, min(dt, 0.25))
            self._fps_sample_time += clamped_dt
            self._fps_sample_frames += 1
            if self._fps_sample_time >= self._fps_display_interval:
                averaged_fps = self._fps_sample_frames / max(self._fps_sample_time, 1e-6)
                self.set_fps(averaged_fps)
                self._fps_sample_time = 0.0
                self._fps_sample_frames = 0

        if self._resume_style == "cyber" and self.resume_panel.enabled:
            pulse = 1.0 + 0.03 * math.sin(self._resume_countdown_remaining * 10.0)
            self.resume_panel.scale = (
                self._resume_panel_base_scale[0] * pulse,
                self._resume_panel_base_scale[1] * pulse,
            )
        elif self._resume_style == "minimal" and self.resume_value_text.enabled:
            pulse = 1.0 + self._minimal_pulse_strength * math.sin(
                self._resume_countdown_remaining * self._minimal_pulse_speed,
            )
            self.resume_value_text.scale = self._minimal_value_scale * pulse

        if self._bonus_timer <= 0.0:
            return

        self._bonus_timer -= dt
        progress = 1.0 - (self._bonus_timer / max(self._bonus_duration, 0.001))
        progress = max(0.0, min(1.0, progress))

        lift = progress * 0.12
        self.bonus_text.position = (self._bonus_base_x, self._bonus_base_y + lift)

        pop = 1.0 + 0.22 * (1.0 - progress)
        self.bonus_text.scale = self._bonus_main_scale * pop

        alpha = int(255 * (1.0 - progress))
        alpha = max(0, min(255, alpha))
        self.bonus_text.color = color.rgba(255, 242, 168, alpha)

        if self._bonus_timer <= 0.0:
            self.bonus_text.text = ""

    def set_state(self, state: GameState) -> None:
        self._current_state = state
        if state != GameState.RESUMING:
            self.hide_resume_countdown()

        if state == GameState.START:
            self.state_text.text = "Press SPACE to Start"
        elif state == GameState.PLAYING:
            self.state_text.text = ""
        elif state == GameState.PAUSED:
            self.state_text.text = "Paused - Press ESC or P"
        elif state == GameState.RESUMING:
            self.state_text.text = ""
        else:
            self.state_text.text = "Game Over - Press R or SPACE"

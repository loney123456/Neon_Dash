from ursina import Text, color

from game.state_machine import GameState


class HudView:
    def __init__(self) -> None:
        self.score_text = Text(
            text="Score: 0",
            origin=(-0.5, 0),
            position=(-0.86, 0.45),
            color=color.azure,
            scale=1.6,
        )
        self.state_text = Text(
            text="Press SPACE to Start",
            origin=(0, 0),
            position=(0, 0.38),
            color=color.cyan,
            scale=1.6,
        )
        self.hint_text = Text(
            text="Move: A/D or Left/Right | Pause: ESC | Restart: R",
            origin=(0, 0),
            position=(0, -0.45),
            color=color.light_gray,
            scale=1.0,
        )
        self.bonus_text = Text(
            text="",
            origin=(-0.5, 0),
            position=(-0.62, 0.39),
            color=color.yellow,
            scale=1.25,
        )
        self._bonus_timer = 0.0

    def set_score(self, score: int) -> None:
        self.score_text.text = f"Score: {score}"

    def show_pickup_bonus(self, text: str, duration: float = 0.6) -> None:
        self.bonus_text.text = text
        self._bonus_timer = duration

    def update(self, dt: float) -> None:
        if self._bonus_timer <= 0.0:
            return
        self._bonus_timer -= dt
        if self._bonus_timer <= 0.0:
            self.bonus_text.text = ""

    def set_state(self, state: GameState) -> None:
        if state == GameState.START:
            self.state_text.text = "Press SPACE to Start"
        elif state == GameState.PLAYING:
            self.state_text.text = ""
        elif state == GameState.PAUSED:
            self.state_text.text = "Paused"
        else:
            self.state_text.text = "Game Over - Press R or SPACE"

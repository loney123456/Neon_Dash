from enum import Enum, auto


class GameState(Enum):
    START = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


class StateMachine:
    def __init__(self, initial_state: GameState = GameState.START) -> None:
        self._state = initial_state

    @property
    def state(self) -> GameState:
        return self._state

    def set_state(self, new_state: GameState) -> bool:
        if self._state == new_state:
            return False
        self._state = new_state
        return True

    def is_state(self, state: GameState) -> bool:
        return self._state == state


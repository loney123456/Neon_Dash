# Neon Dash

A 3D endless runner prototype built with Python + Ursina.

## Current Status

This repository now contains a playable core loop:

- State machine: `Start -> Playing -> Paused -> Resuming -> GameOver`
- 3-lane movement with smooth lane switching
- Relative world movement (player stays in place, world moves backward)
- Random obstacle spawning with no full-lane blockage
- Collectible spawning (coins/energy orbs) with pickup bonus feedback
- Obstacle/collectible object pooling (prewarm + reuse + recycle)
- Time-based difficulty curve (speed + spawn rate + obstacle pressure)
- Collision detection and instant game over
- Restart flow and basic HUD

## Controls

- `SPACE`: start / restart
- `A` / `Left Arrow`: move to left lane
- `D` / `Right Arrow`: move to right lane
- `ESC` / `P`: pause / resume (resume has a 3-second countdown)
- `R`: restart from game over

Countdown UI style can be switched in `config.py`:
- `hud.resume_countdown_style = "cyber"` (panel style)
- `hud.resume_countdown_style = "minimal"` (no panel, timer only)

Low-spec stability profile can be toggled in `config.py`:
- `USE_LOW_SPEC_STABILITY_PROFILE = False` keeps current default config.
- `USE_LOW_SPEC_STABILITY_PROFILE = True` enables lower-load long-run settings.

## Runtime Requirements

- Python `3.9` to `3.11`
- OpenGL-capable graphics driver (Windows/macOS/Linux)

## Install (Windows PowerShell)

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Install (macOS / Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Preflight Check

Run the runtime preflight before launching:

```bash
python scripts/preflight_check.py
```

If this check fails on Linux/macOS, verify OpenGL/graphics drivers first.

## Automated Tests

Run object-pooling specific tests:

```bash
python -m unittest tests.test_pooling -v
```

Run full test suite:

```bash
python -m unittest discover -s tests -v
```

## Manual Long-Run Checklist (3-5 min)

1. Run `python scripts/preflight_check.py` and confirm pass.
2. Run `python -m unittest tests.test_pooling -v` and confirm pass.
3. Launch `python main.py`.
4. Verify controls and flow:
   - `SPACE` start, `ESC/P` pause-resume with countdown, `R/SPACE` restart after game over.
5. During play, observe:
   - Score increases over time.
   - Pickup gives immediate score bonus and `+N` HUD feedback.
   - No obvious obstacle/collectible overlap at spawn.
6. Long-run stability:
   - Play continuously for 3-5 minutes.
   - No crashes, no severe stutter spikes, no logic freeze after repeated restarts.

## Run

```bash
python main.py
```

## Project Structure

```text
.
|-- main.py
|-- config.py
|-- requirements.txt
|-- scripts/
|   `-- preflight_check.py
|-- tests/
|   |-- __init__.py
|   |-- test_pooling.py
|   `-- test_game_systems.py
|-- game/
|   |-- state_machine.py
|   |-- player.py
|   |-- world.py
|   |-- spawner.py
|   |-- collectibles.py
|   `-- hud.py
`-- assets/
```

## Next Milestones

- Add persistent high score and settings
- Add audio and VFX polish

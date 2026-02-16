# Neon Dash

A 3D endless runner prototype built with Python + Ursina.

## Current Status

This repository now contains a playable core loop:

- State machine: `Start -> Playing -> Paused -> GameOver`
- 3-lane movement with smooth lane switching
- Relative world movement (player stays in place, world moves backward)
- Random obstacle spawning with no full-lane blockage
- Collectible spawning (coins/energy orbs) with pickup bonus feedback
- Time-based difficulty curve (speed + spawn rate + obstacle pressure)
- Collision detection and instant game over
- Restart flow and basic HUD

## Controls

- `SPACE`: start / restart
- `A` / `Left Arrow`: move to left lane
- `D` / `Right Arrow`: move to right lane
- `ESC`: pause / resume
- `R`: restart from game over

## Run

1. Install dependency:

```bash
pip install ursina
```

2. Start game:

```bash
python main.py
```

## Project Structure

```text
.
|-- main.py
|-- config.py
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

- Add object pooling for obstacles/collectibles
- Add persistent high score and settings
- Add audio and VFX polish

# Snake

A desktop Snake game built with Python and Pygame. Eat food to grow, avoid the walls and your own body, and fill the board to win.

## Setup and run

You need Python 3 with pip and a desktop environment to display the game window. Run these commands from the project folder:

```sh
python -m pip install -r requirements.txt
python main.py
```

To use an isolated virtual environment on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

## Controls

| Key | Action |
| --- | --- |
| Arrow keys or WASD | Change direction |
| Space | Pause or resume |
| R | Restart the game |
| M | Mute or unmute music and sound effects |
| Esc | Quit |

The game also pauses when its window loses focus. Press Space to resume.

## Gameplay

- Each piece of food adds one point and grows the snake by one cell.
- Movement speeds up every three points, from 10 to a maximum of 20 steps per second.
- Hitting a wall or the snake's body ends the game. You cannot reverse direction directly.
- Filling the 30 by 22 board wins the game.
- The best score is kept during the current session and resets when the application closes.

## Audio and project files

The game includes looping background music and sound effects for eating, crashing, restarting, and winning. Audio files are stored locally, so gameplay works offline after dependencies are installed. Missing audio files or unavailable audio do not prevent playing.

- `main.py`: game logic, rendering, input, and audio.
- `requirements.txt`: Pygame dependency (`>=2.5.2,<3`).
- `assets/sounds/`: music and sound effects.
- [Sound credits](assets/sounds/CREDITS.md): audio sources and licensing details.

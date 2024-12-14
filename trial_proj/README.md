# Flappy Bird Clone

A simple Flappy Bird clone created using Python and Pygame.

## Requirements

- Python 3.x
- Pygame 2.5.2

## Installation

1. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## How to Play

1. Run the game:
```bash
python flappy_bird.py
```

2. Game Controls:
- Press SPACE to make the bird flap/jump
- Press Q to quit at the game over screen
- Press SPACE to restart at the game over screen

## Game Features

- Simple physics-based gameplay
- Randomly generated pipes
- Score tracking
- Game over screen with restart option
- Smooth controls and collision detection

## Game Rules

- Control the blue bird and navigate through the green pipes
- Each successfully passed pipe gives you 1 point
- Hitting pipes or going out of bounds ends the game
- Try to achieve the highest score possible!

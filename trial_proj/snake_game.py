import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen Dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors
BACKGROUND_COLOR = (135, 206, 235)  # Sky Blue
SNAKE_HEAD_COLOR = (34, 139, 34)    # Forest Green
SNAKE_BODY_COLOR = (0, 255, 127)    # Spring Green
EGG_COLOR = (255, 215, 0)           # Golden
GROUND_COLOR = (34, 139, 34)        # Forest Green

# Game Settings
FPS = 5
SNAKE_SPEED = 20

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('3D Snake Game')
clock = pygame.time.Clock()

class SnakeGame:
    def __init__(self):
        # Snake initial setup
        self.snake_body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.snake_direction = (1, 0)
        self.snake_length = 1
        
        # Egg placement
        self.egg_pos = self.place_egg()
        
        # Score
        self.score = 0
        self.font = pygame.font.Font(None, 36)

    def place_egg(self):
        while True:
            egg_pos = (random.randint(0, GRID_WIDTH-1), 
                       random.randint(0, GRID_HEIGHT-1))
            if egg_pos not in self.snake_body:
                return egg_pos

    def draw_background(self):
        # Sky gradient background
        for y in range(SCREEN_HEIGHT):
            # Create a gradient from light blue to darker blue
            r = int(135 * (1 - y / SCREEN_HEIGHT) + 100 * (y / SCREEN_HEIGHT))
            g = int(206 * (1 - y / SCREEN_HEIGHT) + 149 * (y / SCREEN_HEIGHT))
            b = int(235 * (1 - y / SCREEN_HEIGHT) + 192 * (y / SCREEN_HEIGHT))
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Ground
        ground_height = 50
        pygame.draw.rect(screen, GROUND_COLOR, 
                         (0, SCREEN_HEIGHT - ground_height, 
                          SCREEN_WIDTH, ground_height))

    def draw_snake(self):
        for i, segment in enumerate(self.snake_body):
            x, y = segment[0] * GRID_SIZE, segment[1] * GRID_SIZE
            
            if i == 0:  # Head
                # 3D-like head with shading
                head_rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, SNAKE_HEAD_COLOR, head_rect)
                
                # Add some 3D effect to the head
                highlight = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                highlight.fill((255, 255, 255, 50))
                screen.blit(highlight, head_rect)
            else:
                # Body segments with gradient
                body_rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, SNAKE_BODY_COLOR, body_rect)

    def draw_egg(self):
        x, y = self.egg_pos[0] * GRID_SIZE, self.egg_pos[1] * GRID_SIZE
        
        # Draw egg with 3D-like effect
        egg_rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        pygame.draw.ellipse(screen, EGG_COLOR, egg_rect)
        
        # Add highlight for 3D effect
        highlight = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        highlight.fill((255, 255, 255, 100))
        screen.blit(highlight, egg_rect)

    def move_snake(self):
        head = self.snake_body[0]
        new_head = (head[0] + self.snake_direction[0], 
                    head[1] + self.snake_direction[1])
        
        # Check if snake hits screen boundaries
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or 
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            return False
        
        # Check if snake eats egg
        if new_head == self.egg_pos:
            self.snake_length += 1
            self.score += 1
            self.egg_pos = self.place_egg()
        
        # Move snake
        self.snake_body.insert(0, new_head)
        if len(self.snake_body) > self.snake_length:
            self.snake_body.pop()
        
        return True

    def check_collision(self):
        head = self.snake_body[0]
        return head in self.snake_body[1:]

    def run(self):
        game_over = False
        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Snake movement controls
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.snake_direction != (0, 1):
                        self.snake_direction = (0, -1)
                    elif event.key == pygame.K_DOWN and self.snake_direction != (0, -1):
                        self.snake_direction = (0, 1)
                    elif event.key == pygame.K_LEFT and self.snake_direction != (1, 0):
                        self.snake_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and self.snake_direction != (-1, 0):
                        self.snake_direction = (1, 0)
                    elif event.key == pygame.K_r:
                        # Restart game
                        return SnakeGame().run()

            # Clear screen and draw background
            self.draw_background()

            # Move and draw snake
            move_result = self.move_snake()
            if not move_result or self.check_collision():
                # Game over screen
                game_over_text = self.font.render('Game Over! Press R to Restart', True, (255, 0, 0))
                screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 
                                             SCREEN_HEIGHT//2))
                pygame.display.flip()
                
                # Wait for restart
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                            return SnakeGame().run()
                break
            else:
                self.draw_snake()
                self.draw_egg()

            # Display score
            score_text = self.font.render(f'Score: {self.score}', True, (0, 0, 0))
            screen.blit(score_text, (10, 10))

            # Update display
            pygame.display.flip()
            clock.tick(FPS)

# Run the game
if __name__ == '__main__':
    SnakeGame().run()
    pygame.quit()

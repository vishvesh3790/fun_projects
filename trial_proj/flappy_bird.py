import pygame
import sys
import random
import os

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.25
FLAP_STRENGTH = -5
PIPE_SPEED = 3
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # milliseconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird Clone')
clock = pygame.time.Clock()

# Load images
BIRD_IMAGE = pygame.image.load(os.path.join('assets', 'bird.png'))
BACKGROUND_IMAGE = pygame.image.load(os.path.join('assets', 'background.png'))
PIPE_IMAGE = pygame.image.load(os.path.join('assets', 'pipe.png'))

class Bird:
    def __init__(self):
        self.x = SCREEN_WIDTH // 3
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.image = BIRD_IMAGE
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.rotation = 0
        
    def flap(self):
        self.velocity = FLAP_STRENGTH
        
    def move(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.center = (self.x, self.y)
        
        # Rotate bird based on velocity
        self.rotation = max(-30, min(self.velocity * 3, 30))
        
    def draw(self):
        # Rotate the bird image
        rotated_image = pygame.transform.rotate(self.image, -self.rotation)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rotated_rect.topleft)
        
    def check_collision(self, pipes):
        if self.y <= 0 or self.y >= SCREEN_HEIGHT:
            return True
        
        for pipe in pipes:
            if self.rect.colliderect(pipe.top_rect) or self.rect.colliderect(pipe.bottom_rect):
                return True
        return False

class Pipe:
    def __init__(self):
        self.gap_y = random.randint(200, SCREEN_HEIGHT - 200)
        self.x = SCREEN_WIDTH
        self.passed = False
        
        # Create top pipe
        self.top_pipe = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.bottom_pipe = PIPE_IMAGE
        
        # Create rectangles for collision detection
        self.top_rect = self.top_pipe.get_rect(bottomleft=(self.x, self.gap_y - PIPE_GAP // 2))
        self.bottom_rect = self.bottom_pipe.get_rect(topleft=(self.x, self.gap_y + PIPE_GAP // 2))
        
    def move(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x
        
    def draw(self):
        screen.blit(self.top_pipe, self.top_rect)
        screen.blit(self.bottom_pipe, self.bottom_rect)

def main():
    bird = Bird()
    pipes = []
    score = 0
    last_pipe = pygame.time.get_ticks()
    font = pygame.font.Font(None, 36)
    
    while True:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.flap()
                    
        # Generate new pipes
        if current_time - last_pipe > PIPE_FREQUENCY:
            pipes.append(Pipe())
            last_pipe = current_time
            
        # Update game state
        bird.move()
        
        # Update pipes and check for scoring
        for pipe in pipes[:]:
            pipe.move()
            if pipe.x + PIPE_IMAGE.get_width() < 0:
                pipes.remove(pipe)
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                score += 1
                
        # Check for collisions
        if bird.check_collision(pipes):
            return score
            
        # Draw everything
        screen.blit(BACKGROUND_IMAGE, (0, 0))
        for pipe in pipes:
            pipe.draw()
        bird.draw()
        
        # Draw score
        score_surface = font.render(str(score), True, BLACK)
        screen.blit(score_surface, (SCREEN_WIDTH//2, 50))
        
        pygame.display.flip()
        clock.tick(60)

def game_over_screen(score):
    font = pygame.font.Font(None, 48)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                if event.key == pygame.K_q:
                    return False
                    
        screen.blit(BACKGROUND_IMAGE, (0, 0))
        game_over_text = font.render('Game Over!', True, BLACK)
        score_text = font.render(f'Score: {score}', True, BLACK)
        restart_text = font.render('Press SPACE to restart', True, BLACK)
        quit_text = font.render('Press Q to quit', True, BLACK)
        
        screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 
                                   SCREEN_HEIGHT//2 - 100))
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 
                                SCREEN_HEIGHT//2))
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 
                                 SCREEN_HEIGHT//2 + 50))
        screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, 
                               SCREEN_HEIGHT//2 + 100))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    while True:
        score = main()
        if not game_over_screen(score):
            break
    
    pygame.quit()
    sys.exit()

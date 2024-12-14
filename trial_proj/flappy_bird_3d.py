import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random
import numpy as np
import sys

# Initialize Pygame and OpenGL
pygame.init()
glutInit(sys.argv)
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
pygame.display.set_caption('3D Flappy Bird')

# Game constants
GRAVITY = 0.5
FLAP_STRENGTH = -8
PIPE_SPEED = 0.1
PIPE_FREQUENCY = 50  # frames
PIPE_GAP = 5

def setup_lighting():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Set up light position and properties
    glLightfv(GL_LIGHT0, GL_POSITION, (5.0, 5.0, 5.0, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.5, 0.5, 0.5, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))

class Bird:
    def __init__(self):
        self.position = [0, 0, -5]  # x, y, z
        self.velocity = 0
        self.rotation = 0
        
    def flap(self):
        self.velocity = FLAP_STRENGTH
        
    def update(self):
        self.velocity += GRAVITY * 0.1
        self.position[1] += self.velocity * 0.1
        self.rotation = max(-30, min(self.velocity * 3, 30))
        
    def draw(self):
        glPushMatrix()
        glTranslatef(*self.position)
        glRotatef(self.rotation, 1, 0, 0)
        
        # Draw bird body (cube)
        glColor3f(1.0, 0.8, 0.0)  # Bright yellow
        self.draw_cube(0.5)
        
        # Draw wings
        glColor3f(0.9, 0.7, 0.0)  # Slightly darker yellow
        glPushMatrix()
        glTranslatef(-0.3, 0, 0)
        glScalef(0.2, 0.4, 0.4)
        self.draw_cube(0.5)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0.3, 0, 0)
        glScalef(0.2, 0.4, 0.4)
        self.draw_cube(0.5)
        glPopMatrix()
        
        glPopMatrix()
    
    def draw_cube(self, size):
        glutSolidCube(size)

class Pipe:
    def __init__(self, z_pos):
        self.x = 0
        self.z = z_pos
        self.gap_y = random.uniform(-2, 2)
        self.passed = False
        
    def update(self):
        self.z += PIPE_SPEED
        
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, 0, self.z)
        
        # Draw top pipe
        glPushMatrix()
        glTranslatef(0, self.gap_y + PIPE_GAP/2 + 2.5, 0)
        glColor3f(0.0, 0.8, 0.0)  # Bright green
        self.draw_pipe()
        glPopMatrix()
        
        # Draw bottom pipe
        glPushMatrix()
        glTranslatef(0, self.gap_y - PIPE_GAP/2 - 2.5, 0)
        glColor3f(0.0, 0.8, 0.0)  # Bright green
        self.draw_pipe()
        glPopMatrix()
        
        glPopMatrix()
    
    def draw_pipe(self):
        glScale(1, 5, 1)
        glutSolidCube(1)

def draw_background():
    glDisable(GL_LIGHTING)  # Disable lighting for background
    glPushMatrix()
    glTranslatef(0, 0, -15)
    
    # Draw sky
    glBegin(GL_QUADS)
    glColor3f(0.4, 0.6, 1.0)  # Sky blue
    glVertex3f(-15, -15, 0)
    glVertex3f(15, -15, 0)
    glVertex3f(15, 15, 0)
    glVertex3f(-15, 15, 0)
    glEnd()
    
    glPopMatrix()
    glEnable(GL_LIGHTING)  # Re-enable lighting for 3D objects

def draw_text(text, x, y, color=(1, 1, 1)):
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    
    # Save the projection matrix and switch to orthographic projection for 2D text
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, display[0], 0, display[1], -1, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Render text
    font = pygame.font.Font(None, 36)
    text_surface = font.render(text, True, (int(color[0]*255), int(color[1]*255), int(color[2]*255)))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    
    glRasterPos2d(x, display[1] - y)  # Flip y-coordinate
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    
    # Restore matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

def setup_3d():
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    setup_lighting()

def main():
    setup_3d()
    bird = Bird()
    pipes = []
    frame_count = 0
    score = 0
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.flap()
        
        # Update
        bird.update()
        
        # Generate new pipes
        if frame_count % PIPE_FREQUENCY == 0:
            pipes.append(Pipe(-30))
        
        # Update and remove pipes
        for pipe in pipes[:]:
            pipe.update()
            if pipe.z > 5:
                pipes.remove(pipe)
            elif not pipe.passed and pipe.z > -5:
                pipe.passed = True
                score += 1
        
        # Check collisions
        for pipe in pipes:
            if abs(pipe.z - bird.position[2]) < 1:
                if abs(bird.position[1] - pipe.gap_y) > PIPE_GAP/2:
                    return score
        
        # Check boundaries
        if abs(bird.position[1]) > 5:
            return score
        
        # Draw
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        draw_background()
        
        bird.draw()
        for pipe in pipes:
            pipe.draw()
        
        # Draw score
        draw_text(f"Score: {score}", 10, 30)
        
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1

def game_over_screen(score):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                if event.key == pygame.K_q:
                    return False
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        draw_background()
        
        # Draw game over text
        draw_text("Game Over!", display[0]/2 - 100, display[1]/2 - 60)
        draw_text(f"Score: {score}", display[0]/2 - 50, display[1]/2)
        draw_text("Press SPACE to restart", display[0]/2 - 150, display[1]/2 + 40)
        draw_text("Press Q to quit", display[0]/2 - 100, display[1]/2 + 80)
        
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == '__main__':
    while True:
        score = main()
        if not game_over_screen(score):
            break
    
    pygame.quit()

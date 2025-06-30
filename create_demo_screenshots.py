#!/usr/bin/env python3
"""
Create demo screenshots for the blog post
"""

import pygame
import math
import random
import os
from collections import deque

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 128, 0)

def create_demo_screenshots():
    """Create sample screenshots for the blog post"""
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Sherman Tank Snake - Demo Screenshots")
    
    # Create screenshots directory
    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')
    
    # Screenshot 1: Tank with trail
    screen.fill(BLACK)
    
    # Draw tank
    tank_x, tank_y = 400, 300
    tank_size = 20
    pygame.draw.rect(screen, DARK_GREEN, (tank_x-tank_size//2, tank_y-tank_size//2, tank_size, tank_size))
    
    # Draw trail
    trail_points = [
        (350, 300), (320, 310), (290, 320), (260, 330), 
        (230, 340), (200, 350), (170, 360), (140, 370)
    ]
    
    for i, (x, y) in enumerate(trail_points):
        alpha = 255 - (i * 30)  # Fading effect
        color = (0, max(0, 255 - i * 20), 0)  # Green fading
        pygame.draw.circle(screen, color, (x, y), 8)
    
    # Add title
    font = pygame.font.Font(None, 36)
    title = font.render("Sherman Tank Snake - Trail System", True, WHITE)
    screen.blit(title, (10, 10))
    
    pygame.image.save(screen, "screenshots/demo_01_trail_system.png")
    print("📸 Created demo_01_trail_system.png")
    
    # Screenshot 2: Auto-trap activation
    screen.fill(BLACK)
    
    # Draw tank
    pygame.draw.rect(screen, DARK_GREEN, (tank_x-tank_size//2, tank_y-tank_size//2, tank_size, tank_size))
    
    # Draw encircling trail
    trap_points = [
        (300, 250), (350, 240), (400, 250), (450, 270),
        (480, 320), (470, 370), (430, 400), (380, 410),
        (330, 400), (290, 380), (270, 340), (280, 290)
    ]
    
    # Draw trail segments
    for i, (x, y) in enumerate(trap_points):
        pygame.draw.circle(screen, GREEN, (x, y), 8)
    
    # Draw trap polygon outline
    pygame.draw.polygon(screen, RED, trap_points, 3)
    
    # Draw trapped enemies
    enemies = [(350, 300), (380, 320), (360, 340)]
    for ex, ey in enemies:
        pygame.draw.circle(screen, ORANGE, (ex, ey), 6)
    
    # Add trap indicator
    trap_text = font.render("TRAP ACTIVE!", True, RED)
    screen.blit(trap_text, (10, 50))
    
    title = font.render("Sherman Tank Snake - Auto-Trap System", True, WHITE)
    screen.blit(title, (10, 10))
    
    pygame.image.save(screen, "screenshots/demo_02_auto_trap.png")
    print("📸 Created demo_02_auto_trap.png")
    
    # Screenshot 3: Tank damage effects
    screen.fill(BLACK)
    
    # Draw damaged tank
    pygame.draw.rect(screen, DARK_GREEN, (tank_x-tank_size//2, tank_y-tank_size//2, tank_size, tank_size))
    
    # Draw smoke effects
    for i in range(8):
        smoke_x = tank_x + random.randint(-15, 15)
        smoke_y = tank_y + random.randint(-15, 15)
        smoke_size = random.randint(3, 8)
        pygame.draw.circle(screen, GRAY, (smoke_x, smoke_y), smoke_size)
    
    # Draw sparks
    for i in range(5):
        spark_x = tank_x + random.randint(-10, 10)
        spark_y = tank_y + random.randint(-10, 10)
        pygame.draw.circle(screen, ORANGE, (spark_x, spark_y), 2)
    
    # Add damage indicator
    damage_text = font.render("TANK DAMAGED - Level 2/2", True, RED)
    screen.blit(damage_text, (10, 50))
    
    title = font.render("Sherman Tank Snake - Battle Damage", True, WHITE)
    screen.blit(title, (10, 10))
    
    pygame.image.save(screen, "screenshots/demo_03_tank_damage.png")
    print("📸 Created demo_03_tank_damage.png")
    
    # Screenshot 4: Combat scene
    screen.fill(BLACK)
    
    # Draw tank
    pygame.draw.rect(screen, DARK_GREEN, (tank_x-tank_size//2, tank_y-tank_size//2, tank_size, tank_size))
    
    # Draw bullets
    bullets = [(420, 300), (440, 300), (460, 300)]
    for bx, by in bullets:
        pygame.draw.circle(screen, YELLOW, (bx, by), 3)
    
    # Draw enemies
    enemies = [(500, 280), (520, 320), (480, 350), (450, 200)]
    for ex, ey in enemies:
        pygame.draw.circle(screen, RED, (ex, ey), 8)
    
    # Draw trail
    for i, (x, y) in enumerate(trail_points):
        color = (0, max(0, 255 - i * 20), 0)
        pygame.draw.circle(screen, color, (x, y), 8)
    
    title = font.render("Sherman Tank Snake - Combat Action", True, WHITE)
    screen.blit(title, (10, 10))
    
    pygame.image.save(screen, "screenshots/demo_04_combat.png")
    print("📸 Created demo_04_combat.png")
    
    pygame.quit()
    print("\n✅ Created 4 demo screenshots for blog post!")
    print("📁 Screenshots saved in 'screenshots/' directory")

if __name__ == "__main__":
    create_demo_screenshots()

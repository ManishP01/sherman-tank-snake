#!/usr/bin/env python3
"""
Screenshot capture utility for Sherman Tank Snake blog post.
Run this to automatically capture gameplay screenshots.
"""

import pygame
import sys
import os
import math
import random
from collections import deque

# Import all the classes and constants from the main game
exec(open('sherman_tank_snake.py').read())

def capture_gameplay_screenshots():
    """Capture screenshots showing key gameplay features"""
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Sherman Tank Snake - Screenshot Mode")
    clock = pygame.time.Clock()
    
    # Create screenshots directory
    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')
    
    # Initialize game objects
    tank = TankSnake(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    enemies = []
    
    # Add some enemies for demonstration
    for i in range(5):
        enemy = Enemy(random.randint(50, SCREEN_WIDTH - 50), 
                     random.randint(50, SCREEN_HEIGHT - 50))
        enemies.append(enemy)
    
    screenshot_count = 0
    frame_count = 0
    
    print("🎮 Sherman Tank Snake - Screenshot Capture Mode")
    print("Controls:")
    print("  WASD/Arrow Keys: Move tank")
    print("  SPACEBAR: Shoot bullets")
    print("  T: Trigger trap")
    print("  P: Save screenshot")
    print("  D: Add damage to tank")
    print("  E: Add more enemies")
    print("  ESC: Exit")
    print("\n📸 Capture these scenarios:")
    print("1. Tank with trail system visible")
    print("2. Auto-trap activation with enemies")
    print("3. Tank damage effects")
    print("4. Trail fading and blinking effects")
    print("5. Enemy AI behavior")
    
    running = True
    
    while running:
        frame_count += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_p:
                    # Save screenshot (changed to P key)
                    screenshot_count += 1
                    filename = f"screenshots/gameplay_{screenshot_count:02d}.png"
                    pygame.image.save(screen, filename)
                    print(f"📸 Screenshot saved: {filename}")
                elif event.key == pygame.K_d:
                    # Add damage for demonstration
                    tank.take_damage()
                    print(f"🔥 Tank damage level: {tank.damage_level}")
                elif event.key == pygame.K_e:
                    # Add more enemies
                    enemy = Enemy(random.randint(50, SCREEN_WIDTH - 50), 
                                 random.randint(50, SCREEN_HEIGHT - 50))
                    enemies.append(enemy)
                    print(f"👾 Added enemy. Total: {len(enemies)}")
                elif event.key == pygame.K_t:
                    # Manual trap trigger
                    if not tank.trap_active and len(tank.segments) >= 4:
                        tank.trap_active = True
                        tank.trap_timer = tank.trap_duration
                        print("💥 Manual trap activated!")
        
        # Get keys for movement
        keys = pygame.key.get_pressed()
        
        # Update tank
        tank.update_movement(keys)
        tank.update_trail()
        
        # Check for auto-traps periodically
        if frame_count % 30 == 0:  # Check every half second
            tank.check_auto_trap(enemies)
        
        # Update trap system
        if tank.trap_active:
            tank.trap_timer -= 1
            if tank.trap_timer <= 0:
                # Explode trapped enemies
                for enemy in tank.trapped_enemies[:]:
                    if enemy in enemies:
                        enemies.remove(enemy)
                        print(f"💥 Enemy destroyed! Remaining: {len(enemies)}")
                
                tank.trap_active = False
                tank.trapped_enemies = []
        
        # Update enemies
        for enemy in enemies:
            enemy.update_ai(tank.x, tank.y, tank.segments)
            
            # Check collision with tank
            distance = math.sqrt((enemy.x - tank.x)**2 + (enemy.y - tank.y)**2)
            if distance < 25:
                tank.take_damage()
                enemies.remove(enemy)
        
        # Spawn new enemies occasionally
        if len(enemies) < 3 and frame_count % 300 == 0:
            enemy = Enemy(random.randint(50, SCREEN_WIDTH - 50), 
                         random.randint(50, SCREEN_HEIGHT - 50))
            enemies.append(enemy)
        
        # Clear screen
        screen.fill(BLACK)
        
        # Draw trail
        tank.draw_trail(screen)
        
        # Draw trap connections if active
        if tank.trap_active:
            # Draw pulsing red connections between trail segments
            pulse = int(128 + 127 * math.sin(frame_count * 0.2))
            trap_color = (255, pulse // 2, pulse // 2)
            
            trail_points = [(x, y) for x, y, _ in tank.segments]
            if len(trail_points) >= 3:
                pygame.draw.polygon(screen, trap_color, trail_points, 3)
                
                # Draw timer
                font = pygame.font.Font(None, 36)
                timer_text = f"TRAP: {tank.trap_timer // 60 + 1}"
                text_surface = font.render(timer_text, True, RED)
                screen.blit(text_surface, (SCREEN_WIDTH - 150, 50))
        
        # Draw tank
        tank.draw(screen)
        
        # Draw enemies
        for enemy in enemies:
            enemy.draw(screen)
        
        # Draw UI
        font = pygame.font.Font(None, 24)
        
        # Screenshot mode indicator
        mode_text = font.render("SCREENSHOT MODE - Press P to capture", True, YELLOW)
        screen.blit(mode_text, (10, 10))
        
        # Game stats
        stats = [
            f"Screenshots: {screenshot_count}",
            f"Tank Damage: {tank.damage_level}/{tank.max_damage}",
            f"Trail Segments: {len(tank.segments)}",
            f"Enemies: {len(enemies)}",
            f"Trap: {'ACTIVE' if tank.trap_active else 'Ready'}"
        ]
        
        for i, stat in enumerate(stats):
            stat_surface = font.render(stat, True, WHITE)
            screen.blit(stat_surface, (10, 40 + i * 25))
        
        # Controls reminder
        controls = [
            "WASD: Move",
            "SPACE: Shoot",
            "T: Trap",
            "D: Damage",
            "E: Add Enemy",
            "P: Screenshot"
        ]
        
        for i, control in enumerate(controls):
            control_surface = font.render(control, True, CYAN)
            screen.blit(control_surface, (SCREEN_WIDTH - 120, 100 + i * 20))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print(f"\n✅ Captured {screenshot_count} screenshots in 'screenshots/' directory")
    print("🎉 Ready for blog post!")

if __name__ == "__main__":
    capture_gameplay_screenshots()

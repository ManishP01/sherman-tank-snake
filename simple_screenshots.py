#!/usr/bin/env python3
"""
Simple screenshot utility - just adds screenshot capability to the main game
"""

import pygame
import os

def add_screenshot_to_game():
    """Add screenshot functionality to the existing game"""
    
    # Read the main game file
    with open('sherman_tank_snake.py', 'r') as f:
        game_code = f.read()
    
    # Find the main game loop and add screenshot functionality
    screenshot_code = '''
# Screenshot functionality
screenshot_count = 0
if not os.path.exists('screenshots'):
    os.makedirs('screenshots')

def save_screenshot(screen):
    global screenshot_count
    screenshot_count += 1
    filename = f"screenshots/gameplay_{screenshot_count:02d}.png"
    pygame.image.save(screen, filename)
    print(f"📸 Screenshot saved: {filename}")
    return filename
'''
    
    # Add screenshot handling to event loop
    event_addition = '''
                elif event.key == pygame.K_p:
                    # Save screenshot
                    save_screenshot(screen)
'''
    
    # Create modified game file
    modified_code = f"""import os
{screenshot_code}

{game_code}"""
    
    # Add screenshot event handling
    if 'elif event.key == pygame.K_ESCAPE:' in modified_code:
        modified_code = modified_code.replace(
            'elif event.key == pygame.K_ESCAPE:',
            f'{event_addition}                elif event.key == pygame.K_ESCAPE:'
        )
    
    # Write the modified game
    with open('sherman_tank_snake_with_screenshots.py', 'w') as f:
        f.write(modified_code)
    
    print("✅ Created sherman_tank_snake_with_screenshots.py")
    print("🎮 Run it and press P to take screenshots!")

if __name__ == "__main__":
    add_screenshot_to_game()

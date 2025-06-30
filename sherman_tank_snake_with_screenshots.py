import os

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


import pygame
import sys
import math
from collections import deque
import random

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRID_SIZE = 20

# Colors (retro palette)
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

class TankSnake:
    def __init__(self, x, y):
        self.segments = deque([(x, y, 999)])  # Snake body segments with lifetime (x, y, lifetime)
        self.direction = 0  # Angle in degrees
        self.speed = 3
        self.base_speed = 3
        self.segment_size = GRID_SIZE
        self.max_length = 8
        self.tank_color = DARK_GREEN
        self.body_color = GREEN
        self.move_counter = 0
        self.move_threshold = 8  # How often to add new segments
        self.trap_active = False
        self.trap_timer = 0
        self.trap_duration = 180  # 3 seconds at 60 FPS (shorter for better gameplay)
        self.trapped_enemies = []
        self.auto_trap_check_timer = 0  # Check for auto-traps every few frames
        # Tank damage states
        self.damage_level = 0  # 0 = healthy, 1 = damaged, 2 = heavily damaged
        self.max_damage = 2
        self.rotation_speed = 4
        self.base_rotation_speed = 4

    def update(self, keys):
        # Tank-style rotation controls (affected by damage)
        current_rotation_speed = self.rotation_speed * (1.0 - self.damage_level * 0.3)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction -= current_rotation_speed  # Rotate left
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction += current_rotation_speed  # Rotate right
        
        # Keep direction in 0-360 range
        self.direction = self.direction % 360
        
        # Move forward/backward (affected by damage)
        current_speed = self.speed * (1.0 - self.damage_level * 0.4)
        moving = False
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.move_forward(current_speed)
            moving = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.move_backward(current_speed)
            moving = True
        
        # Update segment lifetimes
        self.update_segments()
        
        # Only add segments when moving
        if moving:
            self.move_counter += 1
        
        # Auto-check for traps every 10 frames
        self.auto_trap_check_timer += 1
        if self.auto_trap_check_timer >= 10:
            self.auto_trap_check_timer = 0
            return True  # Signal to check for auto-traps
        
        return False
    
    def update_segments(self):
        """Update segment lifetimes and remove expired ones"""
        for i in range(len(self.segments)):
            if i == 0:  # Skip head
                continue
            x, y, lifetime = self.segments[i]
            new_lifetime = lifetime - 1
            if new_lifetime <= 0:
                # Remove expired segment
                self.segments.remove((x, y, lifetime))
                break
            else:
                # Update lifetime
                self.segments[i] = (x, y, new_lifetime)
    
    def move_forward(self, speed):
        head_x, head_y, _ = self.segments[0]
        
        # Calculate new head position based on direction
        rad = math.radians(self.direction)
        new_x = head_x + math.cos(rad) * speed
        new_y = head_y + math.sin(rad) * speed
        
        # Keep on screen (wrap around)
        new_x = new_x % SCREEN_WIDTH
        new_y = new_y % SCREEN_HEIGHT
        
        # Add new segment periodically
        if self.move_counter >= self.move_threshold:
            # Much longer lifetime for better trap planning
            segment_lifetime = 300 + (self.max_length * 15)  # 5+ seconds base + length bonus
            self.segments.appendleft((new_x, new_y, segment_lifetime))
            self.move_counter = 0
            
            # Remove tail if too long
            if len(self.segments) > self.max_length:
                self.segments.pop()
        else:
            # Update head position
            self.segments[0] = (new_x, new_y, self.segments[0][2])
    
    def move_backward(self, speed):
        head_x, head_y, _ = self.segments[0]
        
        # Move in opposite direction
        rad = math.radians(self.direction + 180)
        new_x = head_x + math.cos(rad) * speed
        new_y = head_y + math.sin(rad) * speed
        
        # Keep on screen (wrap around)
        new_x = new_x % SCREEN_WIDTH
        new_y = new_y % SCREEN_HEIGHT
        
        # Add new segment periodically
        if self.move_counter >= self.move_threshold:
            segment_lifetime = 300 + (self.max_length * 15)  # 5+ seconds base + length bonus
            self.segments.appendleft((new_x, new_y, segment_lifetime))
            self.move_counter = 0
            
            # Remove tail if too long
            if len(self.segments) > self.max_length:
                self.segments.pop()
        else:
            # Update head position
            self.segments[0] = (new_x, new_y, self.segments[0][2])
    
    def take_damage(self):
        """Tank takes damage - loses capabilities instead of dying"""
        if self.damage_level < self.max_damage:
            self.damage_level += 1
            # Reduce capabilities
            self.speed = self.base_speed * (1.0 - self.damage_level * 0.4)
            self.rotation_speed = self.base_rotation_speed * (1.0 - self.damage_level * 0.3)
            return False  # Not destroyed
        return True  # Destroyed only at max damage
    
    def check_auto_trap(self, enemies):
        """Automatically check if we've encircled enemies and activate trap"""
        if self.trap_active or len(self.segments) < 6:  # Need minimum segments to form a trap
            return False
        
        # Check if any enemies are trapped by our current trail
        trapped_enemies = []
        for enemy in enemies:
            if self.is_enemy_trapped(enemy):
                trapped_enemies.append(enemy)
        
        # If we have trapped enemies, auto-activate the trap
        if trapped_enemies:
            self.trap_active = True
            self.trap_timer = 0
            self.trapped_enemies = trapped_enemies
            for enemy in trapped_enemies:
                enemy.trapped = True
            print(f"Auto-trap activated! {len(trapped_enemies)} enemies trapped!")
            return True
        
        return False
    
    def activate_trap(self):
        """Manual trap activation (for T key) - now just detonates early if trap is active"""
        if self.trap_active:
            # Early detonation
            destroyed_enemies = self.trapped_enemies.copy()
            self.detonate_trap()
            print("Manual detonation!")
            return destroyed_enemies
        return []
    
    def update_trap(self, enemies):
        """Update trap logic"""
        if not self.trap_active:
            return []
        
        self.trap_timer += 1
        
        # Check if enemies are inside the trap
        newly_trapped = []
        for enemy in enemies:
            if self.is_enemy_trapped(enemy) and enemy not in self.trapped_enemies:
                self.trapped_enemies.append(enemy)
                newly_trapped.append(enemy)
                enemy.trapped = True
        
        # Detonate after timer expires
        if self.trap_timer >= self.trap_duration:
            destroyed_enemies = self.trapped_enemies.copy()
            self.detonate_trap()
            return destroyed_enemies
        
        return []
    
    def is_enemy_trapped(self, enemy):
        """Check if enemy is inside the snake trail polygon using a more reliable method"""
        if len(self.segments) < 6:  # Need minimum segments to form a meaningful enclosure
            return False
        
        # Only use segments that are still visible and form a reasonable trail
        visible_segments = [(x, y) for x, y, lifetime in self.segments if lifetime > 120]  # More lenient visibility
        
        if len(visible_segments) < 6:
            return False
        
        # Check if the enemy is reasonably enclosed by checking distance to trail segments
        enemy_x, enemy_y = enemy.x, enemy.y
        
        # Simple enclosure test: if enemy is surrounded by trail segments in multiple directions
        directions_blocked = 0
        check_directions = [0, 45, 90, 135, 180, 225, 270, 315]  # 8 directions
        
        for angle in check_directions:
            # Cast a ray in this direction and see if it hits our trail
            rad = math.radians(angle)
            ray_length = 100  # Maximum distance to check
            
            for distance in range(20, ray_length, 10):  # Check every 10 pixels
                check_x = enemy_x + math.cos(rad) * distance
                check_y = enemy_y + math.sin(rad) * distance
                
                # Check if this point is close to any of our trail segments
                for seg_x, seg_y in visible_segments:
                    if math.sqrt((check_x - seg_x)**2 + (check_y - seg_y)**2) < self.segment_size:
                        directions_blocked += 1
                        break
                else:
                    continue
                break
        
        # If at least 6 out of 8 directions are blocked, consider the enemy trapped
        return directions_blocked >= 6
    
    def detonate_trap(self):
        """Detonate the trap and reset"""
        self.trap_active = False
        self.trap_timer = 0
        self.trapped_enemies = []
        return True
    
    def grow(self):
        """Make the snake longer (like eating food)"""
        self.max_length += 2
    
    def get_trap_blast_radius(self):
        """Get the center and radius of trap explosion"""
        if not self.segments:
            return None, 0
        
        # Calculate center of trap using visible segments
        visible_segments = [(x, y) for x, y, lifetime in self.segments if lifetime > 0]
        if not visible_segments:
            return None, 0
        
        center_x = sum(x for x, y in visible_segments) / len(visible_segments)
        center_y = sum(y for x, y in visible_segments) / len(visible_segments)
        
        # Blast radius based on trap size
        radius = len(visible_segments) * 15
        return (center_x, center_y), radius
    
    def check_blast_damage(self, blast_center, blast_radius):
        """Tank is immune to its own trap explosions - removed self-damage"""
        return False  # Tank never takes damage from own traps
    
    def check_self_collision(self):
        """Check if tank head hits its own body"""
        if len(self.segments) < 4:
            return False
        
        head_x, head_y, _ = self.segments[0]
        for i in range(2, len(self.segments)):  # Skip head and first body segment
            x, y, lifetime = self.segments[i]
            if lifetime > 0:  # Only check visible segments
                distance = math.sqrt((head_x - x)**2 + (head_y - y)**2)
                if distance < self.segment_size:
                    return True
        return False
    def draw_realistic_tank(self, screen, x, y):
        """Draw a more realistic tank"""
        # Tank body (main hull)
        tank_width = self.segment_size + 4
        tank_height = self.segment_size - 2
        
        # Calculate tank corners based on rotation
        rad = math.radians(self.direction)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        
        # Tank body corners
        corners = [
            (-tank_width//2, -tank_height//2),
            (tank_width//2, -tank_height//2),
            (tank_width//2, tank_height//2),
            (-tank_width//2, tank_height//2)
        ]
        
        # Rotate and translate corners
        rotated_corners = []
        for cx, cy in corners:
            rx = cx * cos_a - cy * sin_a + x
            ry = cx * sin_a + cy * cos_a + y
            rotated_corners.append((rx, ry))
        
        # Tank color based on damage
        if self.damage_level == 0:
            hull_color = DARK_GREEN
            detail_color = GREEN
        elif self.damage_level == 1:
            hull_color = (100, 100, 0)  # Yellowish
            detail_color = (150, 150, 0)
        else:
            hull_color = (100, 50, 0)  # Brownish
            detail_color = (150, 75, 0)
        
        # Draw tank hull
        pygame.draw.polygon(screen, hull_color, rotated_corners)
        pygame.draw.polygon(screen, WHITE, rotated_corners, 2)
        
        # Draw tank turret (smaller circle on top)
        turret_size = self.segment_size // 3
        pygame.draw.circle(screen, detail_color, (int(x), int(y)), turret_size)
        pygame.draw.circle(screen, WHITE, (int(x), int(y)), turret_size, 1)
        
        # Draw tank barrel (thicker and more detailed)
        barrel_length = self.segment_size * 1.8
        barrel_width = 4
        end_x = x + math.cos(rad) * barrel_length
        end_y = y + math.sin(rad) * barrel_length
        
        # Draw barrel shadow/outline
        pygame.draw.line(screen, BLACK, (int(x), int(y)), (int(end_x), int(end_y)), barrel_width + 2)
        # Draw main barrel
        pygame.draw.line(screen, GRAY, (int(x), int(y)), (int(end_x), int(end_y)), barrel_width)
        # Draw barrel highlight
        pygame.draw.line(screen, WHITE, (int(x), int(y)), (int(end_x), int(end_y)), 1)
        
        # Draw tracks/treads (small rectangles on sides)
        track_positions = [
            (-tank_width//2 - 2, 0),
            (tank_width//2 + 2, 0)
        ]
        
        for tx, ty in track_positions:
            # Rotate track position
            track_x = tx * cos_a - ty * sin_a + x
            track_y = tx * sin_a + ty * cos_a + y
            
            # Draw track segments
            for i in range(-2, 3):
                seg_x = track_x + i * 3 * sin_a
                seg_y = track_y - i * 3 * cos_a
                pygame.draw.circle(screen, (60, 60, 60), (int(seg_x), int(seg_y)), 2)
        
        # Draw damage indicators
        if self.damage_level > 0:
            # Smoke effect for damaged tank
            for _ in range(self.damage_level * 2):
                smoke_x = x + random.randint(-8, 8)
                smoke_y = y + random.randint(-8, 8)
                smoke_size = random.randint(2, 4)
                smoke_alpha = random.randint(50, 100)
                smoke_color = (smoke_alpha, smoke_alpha, smoke_alpha)
                pygame.draw.circle(screen, smoke_color, (int(smoke_x), int(smoke_y)), smoke_size)
    
    def draw(self, screen):
        # Draw snake body segments (from tail to head)
        for i in reversed(range(len(self.segments))):
            x, y, lifetime = self.segments[i]
            
            if i == 0:  # Head (tank)
                self.draw_realistic_tank(screen, x, y)
            else:  # Body segments
                if lifetime > 0:  # Only draw visible segments
                    # Make segments smaller as they go back and fade based on lifetime
                    base_size = max(self.segment_size // 2 - (i * 2), 6)
                    
                    # Calculate alpha based on lifetime (fade out effect)
                    max_lifetime = 300 + (self.max_length * 15)  # Updated to match new lifetime
                    alpha_factor = min(1.0, lifetime / 120.0)  # Fade in last 2 seconds
                    
                    # Blinking effect when lifetime is low
                    if lifetime < 120:  # Blink in last 2 seconds
                        blink_factor = math.sin(lifetime * 0.2) * 0.5 + 0.5
                        alpha_factor *= blink_factor
                    
                    # Change color based on trap status
                    if self.trap_active:
                        # Pulsing red color for active trap
                        pulse = int(128 + 127 * math.sin(self.trap_timer * 0.2))
                        trap_color = (int(pulse * alpha_factor), 0, 0)
                        pygame.draw.circle(screen, trap_color, (int(x), int(y)), base_size)
                        if alpha_factor > 0.3:
                            pygame.draw.circle(screen, WHITE, (int(x), int(y)), base_size, 2)
                    else:
                        # Normal trail color with fading
                        trail_color = (int(self.body_color[0] * alpha_factor), 
                                     int(self.body_color[1] * alpha_factor), 
                                     int(self.body_color[2] * alpha_factor))
                        pygame.draw.circle(screen, trail_color, (int(x), int(y)), base_size)
                        if alpha_factor > 0.3:
                            pygame.draw.circle(screen, WHITE, (int(x), int(y)), base_size, 1)
        
        # Draw trap connections when active
        if self.trap_active and len(self.segments) > 3:
            visible_segments = [(x, y) for x, y, lifetime in self.segments if lifetime > 120]  # Updated visibility threshold
            if len(visible_segments) > 3:
                # Draw lines connecting the segments to show the trap area
                for i in range(len(visible_segments)):
                    start_pos = visible_segments[i]
                    end_pos = visible_segments[(i + 1) % len(visible_segments)]
                    
                    # Pulsing trap lines
                    pulse = int(64 + 63 * math.sin(self.trap_timer * 0.3))
                    line_color = (pulse, pulse, 0)
                    pygame.draw.line(screen, line_color, start_pos, end_pos, 3)
        
        # Draw trap timer indicator
        if self.trap_active:
            head_x, head_y, _ = self.segments[0]
            timer_progress = self.trap_timer / self.trap_duration
            timer_length = 40
            timer_width = int(timer_length * (1 - timer_progress))
            
            # Timer bar above tank
            pygame.draw.rect(screen, RED, (head_x - timer_length//2, head_y - 45, timer_length, 8))
            pygame.draw.rect(screen, GREEN, (head_x - timer_length//2, head_y - 45, timer_width, 8))
            pygame.draw.rect(screen, WHITE, (head_x - timer_length//2, head_y - 45, timer_length, 8), 2)
        
        # Draw damage indicator
        if self.damage_level > 0:
            head_x, head_y, _ = self.segments[0]
            damage_text = ["DAMAGED", "CRITICAL"][min(self.damage_level - 1, 1)]
            font = pygame.font.Font(None, 20)
            color = YELLOW if self.damage_level == 1 else RED
            text_surface = font.render(damage_text, True, color)
            screen.blit(text_surface, (head_x - 30, head_y - 60))

class Food:
    def __init__(self):
        self.respawn()
        self.color = YELLOW
        self.size = GRID_SIZE // 3
    
    def respawn(self):
        self.x = random.randint(50, SCREEN_WIDTH - 50)
        self.y = random.randint(50, SCREEN_HEIGHT - 50)
    
    def draw(self, screen):
        # Draw ammo box
        pygame.draw.rect(screen, self.color, (self.x - self.size, self.y - self.size, self.size * 2, self.size * 2))
        pygame.draw.rect(screen, BLACK, (self.x - self.size, self.y - self.size, self.size * 2, self.size * 2), 2)

class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 8
        self.color = RED
        self.size = 3
    
    def update(self):
        rad = math.radians(self.direction)
        self.x += math.cos(rad) * self.speed
        self.y += math.sin(rad) * self.speed
    
    def is_off_screen(self):
        return (self.x < 0 or self.x > SCREEN_WIDTH or 
                self.y < 0 or self.y > SCREEN_HEIGHT)
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
class Enemy:
    def __init__(self, x, y, enemy_type="basic"):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.health = 1
        self.size = 15
        self.speed = 1
        self.direction = random.randint(0, 360)
        self.change_direction_timer = 0
        self.color = RED
        self.trapped = False
        self.panic_mode = False
        
        if enemy_type == "fast":
            self.speed = 2
            self.color = ORANGE
            self.size = 12
        elif enemy_type == "tank":
            self.health = 3
            self.speed = 0.5
            self.color = (139, 69, 19)  # Brown
            self.size = 20
    
    def update(self, player_pos):
        # If trapped, move frantically
        if self.trapped:
            self.panic_mode = True
            self.speed *= 1.5  # Move faster when trapped
            self.direction += random.randint(-90, 90)  # Erratic movement
        
        # Change direction occasionally
        self.change_direction_timer += 1
        direction_change_freq = 60 if self.panic_mode else 120
        
        if self.change_direction_timer > direction_change_freq:
            self.change_direction_timer = 0
            if self.enemy_type == "basic":
                self.direction = random.randint(0, 360)
            elif self.enemy_type == "fast":
                # Fast enemies move more erratically
                self.direction += random.randint(-45, 45)
            elif self.enemy_type == "tank":
                # Tank enemies slowly turn toward player
                player_x, player_y = player_pos
                angle_to_player = math.degrees(math.atan2(player_y - self.y, player_x - self.x))
                self.direction += (angle_to_player - self.direction) * 0.1
        
        # Move
        rad = math.radians(self.direction)
        current_speed = self.speed * (1.5 if self.panic_mode else 1.0)
        self.x += math.cos(rad) * current_speed
        self.y += math.sin(rad) * current_speed
        
        # Wrap around screen
        self.x = self.x % SCREEN_WIDTH
        self.y = self.y % SCREEN_HEIGHT
    
    def take_damage(self):
        self.health -= 1
        return self.health <= 0
    
    def check_collision_with_player(self, player_segments):
        """Check if enemy collides with player tank or trail"""
        for segment_data in player_segments:
            if len(segment_data) == 3:
                segment_x, segment_y, lifetime = segment_data
                if lifetime <= 0:  # Skip invisible segments
                    continue
            else:
                segment_x, segment_y = segment_data
            
            distance = math.sqrt((self.x - segment_x)**2 + (self.y - segment_y)**2)
            if distance < self.size + GRID_SIZE // 2:
                return True
        return False
    
    def draw(self, screen):
        # Add visual effects for trapped enemies
        base_color = self.color
        if self.trapped:
            # Flashing effect for trapped enemies
            flash = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.01))
            base_color = (min(255, self.color[0] + flash//2), self.color[1], self.color[2])
        
        if self.enemy_type == "basic":
            pygame.draw.circle(screen, base_color, (int(self.x), int(self.y)), self.size)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size, 2)
            if self.trapped:
                # Add exclamation mark for trapped enemies
                font = pygame.font.Font(None, 20)
                text = font.render("!", True, WHITE)
                screen.blit(text, (int(self.x) - 3, int(self.y) - 25))
        elif self.enemy_type == "fast":
            # Draw as triangle
            points = []
            for i in range(3):
                angle = math.radians(self.direction + i * 120)
                px = self.x + math.cos(angle) * self.size
                py = self.y + math.sin(angle) * self.size
                points.append((px, py))
            pygame.draw.polygon(screen, base_color, points)
            pygame.draw.polygon(screen, WHITE, points, 2)
            if self.trapped:
                font = pygame.font.Font(None, 20)
                text = font.render("!", True, WHITE)
                screen.blit(text, (int(self.x) - 3, int(self.y) - 25))
        elif self.enemy_type == "tank":
            # Draw as square with health indicator
            rect = pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)
            pygame.draw.rect(screen, base_color, rect)
            pygame.draw.rect(screen, WHITE, rect, 2)
            
            # Health bar
            health_width = (self.health / 3) * (self.size * 2)
            health_rect = pygame.Rect(self.x - self.size, self.y - self.size - 8, health_width, 4)
            pygame.draw.rect(screen, GREEN, health_rect)
            
            if self.trapped:
                font = pygame.font.Font(None, 20)
                text = font.render("!", True, WHITE)
                screen.blit(text, (int(self.x) - 3, int(self.y) - 35))

class Explosion:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.max_radius = radius
        self.current_radius = 0
        self.duration = 30  # frames
        self.timer = 0
        self.colors = [YELLOW, ORANGE, RED]
    
    def update(self):
        self.timer += 1
        progress = self.timer / self.duration
        self.current_radius = self.max_radius * progress
        return self.timer >= self.duration
    
    def draw(self, screen):
        if self.current_radius > 0:
            # Draw multiple circles for explosion effect
            for i, color in enumerate(self.colors):
                radius = max(1, int(self.current_radius - i * 5))
                if radius > 0:
                    pygame.draw.circle(screen, color, (int(self.x), int(self.y)), radius)
            
            # Add some spark effects
            for i in range(8):
                angle = i * 45
                spark_length = self.current_radius * 0.8
                end_x = self.x + math.cos(math.radians(angle)) * spark_length
                end_y = self.y + math.sin(math.radians(angle)) * spark_length
                pygame.draw.line(screen, WHITE, (int(self.x), int(self.y)), (int(end_x), int(end_y)), 2)
def main():
    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Sherman Tank Snake - WWII Edition")
    clock = pygame.time.Clock()
    
    # Create game objects
    tank_snake = TankSnake(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    food = Food()
    bullets = []
    enemies = []
    explosions = []
    score = 0
    game_over = False
    enemy_spawn_timer = 0
    enemy_spawn_delay = 180  # 3 seconds at 60 FPS
    wave = 1
    
    # Spawn initial enemies
    for _ in range(3):
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(50, SCREEN_HEIGHT - 50)
        # Make sure enemy doesn't spawn too close to player
        while abs(x - SCREEN_WIDTH//2) < 100 and abs(y - SCREEN_HEIGHT//2) < 100:
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
        enemies.append(Enemy(x, y, "basic"))
    
    # Game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE and not game_over:
                    # Shoot bullet
                    head_x, head_y, _ = tank_snake.segments[0]
                    bullet = Bullet(head_x, head_y, tank_snake.direction)
                    bullets.append(bullet)
                elif event.key == pygame.K_t and not game_over:
                    # Manual detonation if trap is active
                    if tank_snake.trap_active:
                        destroyed_by_manual = tank_snake.activate_trap()
                        if destroyed_by_manual:
                            # Create explosion
                            blast_center, blast_radius = tank_snake.get_trap_blast_radius()
                            if blast_center:
                                explosions.append(Explosion(blast_center[0], blast_center[1], blast_radius))
                                
                                # Tank is now immune to own explosions - no damage check needed
                                print("Manual detonation - Tank is safe from own explosions!")
                                for enemy in destroyed_by_manual:
                                    if enemy in enemies:
                                        enemies.remove(enemy)
                                        # Bonus points for trap kills
                                        if enemy.enemy_type == "basic":
                                            score += 40
                                        elif enemy.enemy_type == "fast":
                                            score += 60
                                        elif enemy.enemy_type == "tank":
                                            score += 100
                elif event.key == pygame.K_r and game_over:
                    # Restart game
                    tank_snake = TankSnake(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                    food = Food()
                    bullets = []
                    enemies = []
                    explosions = []
                    score = 0
                    game_over = False
                    enemy_spawn_timer = 0
                    wave = 1
                    # Spawn initial enemies
                    for _ in range(3):
                        x = random.randint(50, SCREEN_WIDTH - 50)
                        y = random.randint(50, SCREEN_HEIGHT - 50)
                        enemies.append(Enemy(x, y, "basic"))
        
        if not game_over:
            # Get pressed keys
            keys = pygame.key.get_pressed()
            
            # Update game objects
            should_check_traps = tank_snake.update(keys)
            
            # Auto-check for traps when enemies are encircled
            if should_check_traps:
                tank_snake.check_auto_trap(enemies)
            
            # Update trap system
            destroyed_by_trap = tank_snake.update_trap(enemies)
            if destroyed_by_trap:
                # Create explosion
                blast_center, blast_radius = tank_snake.get_trap_blast_radius()
                if blast_center:
                    explosions.append(Explosion(blast_center[0], blast_center[1], blast_radius))
                    
                    # Tank is immune to own explosions - no self-damage
                    print("Auto-trap detonated - Tank is safe from own explosions!")
                    for enemy in destroyed_by_trap:
                        if enemy in enemies:
                            enemies.remove(enemy)
                            # Bonus points for trap kills
                            if enemy.enemy_type == "basic":
                                score += 40  # Double points for trap kills
                            elif enemy.enemy_type == "fast":
                                score += 60
                            elif enemy.enemy_type == "tank":
                                score += 100
            
            # Update bullets
            for bullet in bullets[:]:
                bullet.update()
                if bullet.is_off_screen():
                    bullets.remove(bullet)
            
            # Update enemies
            player_pos = tank_snake.segments[0][:2]  # Get x, y from (x, y, lifetime)
            for enemy in enemies[:]:
                enemy.update(player_pos)
                
                # Check if enemy collides with player
                if enemy.check_collision_with_player(tank_snake.segments):
                    enemies.remove(enemy)
                    # Tank takes damage instead of instant death
                    if tank_snake.take_damage():
                        game_over = True
                    print(f"Tank damaged! Damage level: {tank_snake.damage_level}")
            
            # Update explosions
            for explosion in explosions[:]:
                if explosion.update():
                    explosions.remove(explosion)
            
            # Check bullet-enemy collisions
            for bullet in bullets[:]:
                for enemy in enemies[:]:
                    distance = math.sqrt((bullet.x - enemy.x)**2 + (bullet.y - enemy.y)**2)
                    if distance < bullet.size + enemy.size:
                        bullets.remove(bullet)
                        if enemy.take_damage():
                            enemies.remove(enemy)
                            # Score based on enemy type
                            if enemy.enemy_type == "basic":
                                score += 20
                            elif enemy.enemy_type == "fast":
                                score += 30
                            elif enemy.enemy_type == "tank":
                                score += 50
                        break
            
            # Spawn new enemies
            enemy_spawn_timer += 1
            if enemy_spawn_timer >= enemy_spawn_delay:
                enemy_spawn_timer = 0
                # Spawn enemy away from player
                spawn_attempts = 0
                while spawn_attempts < 10:
                    x = random.randint(50, SCREEN_WIDTH - 50)
                    y = random.randint(50, SCREEN_HEIGHT - 50)
                    player_x, player_y, _ = tank_snake.segments[0]
                    if abs(x - player_x) > 150 or abs(y - player_y) > 150:
                        # Choose enemy type based on wave
                        enemy_types = ["basic"]
                        if wave >= 2:
                            enemy_types.append("fast")
                        if wave >= 3:
                            enemy_types.append("tank")
                        
                        enemy_type = random.choice(enemy_types)
                        enemies.append(Enemy(x, y, enemy_type))
                        break
                    spawn_attempts += 1
                
                # Increase wave every 10 enemies killed
                if score > 0 and score % 300 == 0:
                    wave += 1
                    enemy_spawn_delay = max(60, enemy_spawn_delay - 10)  # Spawn faster each wave
            
            # Check collision with food
            head_x, head_y, _ = tank_snake.segments[0]
            if abs(head_x - food.x) < GRID_SIZE and abs(head_y - food.y) < GRID_SIZE:
                tank_snake.grow()
                food.respawn()
                score += 10
            
            # Check self collision
            if tank_snake.check_self_collision():
                # Self collision damages tank instead of instant death
                if tank_snake.take_damage():
                    game_over = True
        
        # Draw everything
        screen.fill(BLACK)
        
        # Draw grid (retro effect)
        for x in range(0, SCREEN_WIDTH, GRID_SIZE * 2):
            pygame.draw.line(screen, (20, 20, 20), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE * 2):
            pygame.draw.line(screen, (20, 20, 20), (0, y), (SCREEN_WIDTH, y))
        
        if not game_over:
            # Draw game objects
            food.draw(screen)
            tank_snake.draw(screen)
            
            # Draw enemies
            for enemy in enemies:
                enemy.draw(screen)
            
            # Draw bullets
            for bullet in bullets:
                bullet.draw(screen)
            
            # Draw explosions
            for explosion in explosions:
                explosion.draw(screen)
        
        # Draw UI
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"SCORE: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        length_text = font.render(f"LENGTH: {len(tank_snake.segments)}", True, WHITE)
        screen.blit(length_text, (10, 50))
        
        wave_text = font.render(f"WAVE: {wave}", True, WHITE)
        screen.blit(wave_text, (10, 90))
        
        # Tank condition display
        condition_text = ["HEALTHY", "DAMAGED", "CRITICAL"][tank_snake.damage_level]
        condition_color = [GREEN, YELLOW, RED][tank_snake.damage_level]
        health_text = font.render(f"TANK: {condition_text}", True, condition_color)
        screen.blit(health_text, (10, 130))
        
        enemies_text = font.render(f"ENEMIES: {len(enemies)}", True, WHITE)
        screen.blit(enemies_text, (10, 170))
        
        # Trap status
        if tank_snake.trap_active:
            trap_text = font.render("TRAP ACTIVE!", True, RED)
            screen.blit(trap_text, (SCREEN_WIDTH//2 - 80, 10))
        
        if game_over:
            # Game over screen
            game_over_text = font.render("GAME OVER!", True, RED)
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2))
        
        # Controls text
        font_small = pygame.font.Font(None, 24)
        controls = [
            "WASD/Arrows: Move & Rotate",
            "Space: Shoot",
            "T: Manual Detonate (if trap active)",
            "ESC: Quit"
        ]
        for i, text in enumerate(controls):
            control_text = font_small.render(text, True, GRAY)
            screen.blit(control_text, (10, SCREEN_HEIGHT - 100 + i * 20))
        
        # Enhanced features info
        font_tiny = pygame.font.Font(None, 18)
        features_text = [
            "ENHANCED FEATURES:",
            "• Realistic tank with treads & turret",
            "• AUTO-TRAP: Encircle enemies to trap them!",
            "• LONGER TRAILS: 5+ seconds for better planning",
            "• TANK IMMUNITY: Your explosions won't hurt you",
            "• Progressive damage from enemy contact only",
            "• Press T for manual detonation"
        ]
        for i, text in enumerate(features_text):
            color = WHITE if i == 0 else GRAY
            features_surface = font_tiny.render(text, True, color)
            screen.blit(features_surface, (SCREEN_WIDTH - 280, 50 + i * 18))
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

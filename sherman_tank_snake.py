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
        self.max_length = 12  # Increased for better trapping
        self.tank_color = DARK_GREEN
        self.body_color = GREEN
        self.move_counter = 0
        self.move_threshold = 6  # Reduced for more frequent segments
        self.trap_active = False
        self.trap_timer = 0
        self.trap_duration = 240  # 4 seconds at 60 FPS (longer for better gameplay)
        self.trapped_enemies = []
        self.auto_trap_check_timer = 0
        # Tank damage states
        self.damage_level = 0  # 0 = healthy, 1 = damaged, 2 = heavily damaged
        self.max_damage = 2
        self.rotation_speed = 4
        self.base_rotation_speed = 4
        
    def update_movement(self, keys):
        """Update tank movement based on input"""
        # Handle rotation
        rotation_change = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            rotation_change = -self.rotation_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            rotation_change = self.rotation_speed
        
        # Apply damage effects to rotation
        if self.damage_level > 0:
            rotation_change *= (1 - self.damage_level * 0.2)  # 20% slower per damage level
        
        self.direction = (self.direction + rotation_change) % 360
        
        # Handle movement
        moving = False
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.move_forward(self.speed)
            moving = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.move_forward(-self.speed * 0.6)  # Slower reverse
            moving = True
        
        # Update segment lifetimes
        self.update_segments()
        
        # FIXED: Allow tank to wrap around screen edges like classic Snake
        head_x, head_y, lifetime = self.segments[0]
        
        # Wrap around screen edges
        if head_x < 0:
            head_x = SCREEN_WIDTH
        elif head_x > SCREEN_WIDTH:
            head_x = 0
            
        if head_y < 0:
            head_y = SCREEN_HEIGHT
        elif head_y > SCREEN_HEIGHT:
            head_y = 0
        
        self.segments[0] = (head_x, head_y, lifetime)
    
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
        """Move tank forward/backward"""
        head_x, head_y, _ = self.segments[0]
        
        # Calculate new position
        new_x = head_x + math.cos(math.radians(self.direction)) * speed
        new_y = head_y + math.sin(math.radians(self.direction)) * speed
        
        # Update head position
        self.segments[0] = (new_x, new_y, 999)
        self.move_counter += 1
        
        # Add new segment periodically with MUCH longer lifetime
        if self.move_counter >= self.move_threshold:
            # Extended lifetime for better trap planning - 10+ seconds!
            segment_lifetime = 600 + (self.max_length * 20)  # 10+ seconds base + length bonus
            self.segments.appendleft((new_x, new_y, segment_lifetime))
            self.move_counter = 0
            
            # Limit trail length
            if len(self.segments) > self.max_length:
                self.segments.pop()
    
    def move_backward(self, speed):
        """Move tank backward"""
        head_x, head_y, _ = self.segments[0]
        
        # Calculate new position (opposite direction)
        new_x = head_x - math.cos(math.radians(self.direction)) * speed
        new_y = head_y - math.sin(math.radians(self.direction)) * speed
        
        # Update head position
        self.segments[0] = (new_x, new_y, 999)
        self.move_counter += 1
        
        # Add new segment periodically
        if self.move_counter >= self.move_threshold:
            segment_lifetime = 600 + (self.max_length * 20)  # Extended lifetime
            self.segments.appendleft((new_x, new_y, segment_lifetime))
            self.move_counter = 0
            
            # Limit trail length
            if len(self.segments) > self.max_length:
                self.segments.pop()
    
    def take_damage(self):
        """Tank takes damage"""
        if self.damage_level < self.max_damage:
            self.damage_level += 1
            print(f"Tank damaged! Damage level: {self.damage_level}")
            
            # Apply damage effects
            if self.damage_level >= 1:
                self.speed = self.base_speed * (1 - self.damage_level * 0.15)
                self.rotation_speed = self.base_rotation_speed * (1 - self.damage_level * 0.2)
            
            if self.damage_level >= self.max_damage:
                return True  # Tank destroyed
        return False
    
    def check_auto_trap(self, enemies):
        """Automatically check if we've encircled enemies and activate trap"""
        if self.trap_active or len(self.segments) < 8:  # Need more segments for reliable trapping
            return False
        
        # Check if any enemies are trapped by our current trail
        trapped_enemies = []
        for enemy in enemies:
            if self.is_enemy_trapped(enemy):
                trapped_enemies.append(enemy)
        
        # If we have trapped enemies, auto-activate the trap
        if trapped_enemies:
            self.trap_active = True
            self.trap_timer = self.trap_duration
            self.trapped_enemies = trapped_enemies
            for enemy in trapped_enemies:
                enemy.trapped = True
            print(f"🎯 Auto-trap activated! {len(trapped_enemies)} enemies trapped!")
            return True
        
        return False
    
    def is_enemy_trapped(self, enemy):
        """Check if an enemy is trapped inside our trail using point-in-polygon"""
        if len(self.segments) < 8:
            return False
        
        # Only use segments that are still visible and form a reasonable trail
        visible_segments = [(x, y) for x, y, lifetime in self.segments if lifetime > 180]  # More lenient visibility
        
        if len(visible_segments) < 8:
            return False
        
        # Use point-in-polygon algorithm (ray casting)
        return self.point_in_polygon((enemy.x, enemy.y), visible_segments)
    
    def point_in_polygon(self, point, polygon):
        """Ray casting algorithm to determine if point is inside polygon"""
        if len(polygon) < 3:
            return False
        
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def activate_trap(self):
        """Manual trap activation (for T key)"""
        if self.trap_active:
            # Early detonation
            destroyed_enemies = self.trapped_enemies.copy()
            self.detonate_trap()
            print("💥 Manual detonation!")
            return destroyed_enemies
        return []
    
    def update_trap(self, enemies):
        """Update trap logic"""
        if not self.trap_active:
            return []
        
        self.trap_timer -= 1
        
        if self.trap_timer <= 0:
            # Detonate trap
            destroyed_enemies = self.trapped_enemies.copy()
            self.detonate_trap()
            return destroyed_enemies
        
        return []
    
    def detonate_trap(self):
        """Detonate the active trap"""
        self.trap_active = False
        self.trap_timer = 0
        self.trapped_enemies = []
    
    def get_trap_center_and_radius(self):
        """Calculate trap center and radius for explosion effect"""
        if not self.segments:
            return None, 0
        
        # Calculate center of trap using visible segments
        visible_segments = [(x, y) for x, y, lifetime in self.segments if lifetime > 0]
        if not visible_segments:
            return None, 0
        
        center_x = sum(x for x, y in visible_segments) / len(visible_segments)
        center_y = sum(y for x, y in visible_segments) / len(visible_segments)
        
        # Calculate radius as distance to furthest segment
        max_distance = 0
        for x, y in visible_segments:
            distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            max_distance = max(max_distance, distance)
        
        return (center_x, center_y), max_distance
    
    def check_self_collision(self):
        """DISABLED - Tank should never take damage from its own trail"""
        # Tank immunity to own trail - this is a key fix!
        return False
    
    def draw(self, screen):
        """Draw the tank and its trail"""
        # Draw snake body segments (from tail to head)
        for i in reversed(range(len(self.segments))):
            x, y, lifetime = self.segments[i]
            
            if i == 0:  # Head (tank)
                # Draw tank
                self.draw_realistic_tank(screen, x, y)
            else:  # Body segments
                if lifetime > 0:  # Only draw visible segments
                    # Make segments smaller as they go back and fade based on lifetime
                    base_size = max(self.segment_size // 2 - (i * 1), 8)  # Larger segments
                    
                    # Calculate alpha based on lifetime (fade out effect)
                    max_lifetime = 600 + (self.max_length * 20)  # Updated to match new lifetime
                    alpha_factor = min(1.0, lifetime / 180.0)  # Fade in last 3 seconds
                    
                    # Blinking effect when lifetime is low
                    if lifetime < 180:  # Blink in last 3 seconds
                        blink_factor = math.sin(lifetime * 0.15) * 0.5 + 0.5
                        alpha_factor *= blink_factor
                    
                    # Create color with alpha
                    alpha = int(255 * alpha_factor)
                    color = (*self.body_color, alpha)
                    
                    # Create surface for alpha blending
                    segment_surface = pygame.Surface((base_size * 2, base_size * 2))
                    segment_surface.set_alpha(alpha)
                    segment_surface.fill(self.body_color)
                    
                    # Draw segment
                    screen.blit(segment_surface, (x - base_size, y - base_size))
        
        # Draw trap connections when active
        if self.trap_active and len(self.segments) > 3:
            visible_segments = [(x, y) for x, y, lifetime in self.segments if lifetime > 180]  # Updated visibility threshold
            if len(visible_segments) > 3:
                # Draw pulsing red outline to show trap area
                pulse = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.01))
                trap_color = (255, pulse // 2, pulse // 2)
                
                try:
                    pygame.draw.polygon(screen, trap_color, visible_segments, 3)
                except:
                    pass  # Skip if polygon is invalid
                
                # Draw timer
                font = pygame.font.Font(None, 36)
                timer_seconds = (self.trap_timer // 60) + 1
                timer_text = f"TRAP: {timer_seconds}s"
                text_surface = font.render(timer_text, True, RED)
                screen.blit(text_surface, (SCREEN_WIDTH - 150, 50))
        
        # Draw damage effects
        if self.damage_level > 0:
            self.draw_damage_effects(screen)
    
    def draw_realistic_tank(self, screen, x, y):
        """Draw a more realistic Sherman tank"""
        # Tank body (main hull)
        tank_rect = pygame.Rect(x - 12, y - 8, 24, 16)
        pygame.draw.rect(screen, self.tank_color, tank_rect)
        pygame.draw.rect(screen, WHITE, tank_rect, 2)
        
        # Tank turret
        turret_rect = pygame.Rect(x - 8, y - 6, 16, 12)
        pygame.draw.rect(screen, self.tank_color, turret_rect)
        pygame.draw.rect(screen, WHITE, turret_rect, 1)
        
        # Tank cannon (pointing in direction)
        cannon_length = 20
        cannon_end_x = x + math.cos(math.radians(self.direction)) * cannon_length
        cannon_end_y = y + math.sin(math.radians(self.direction)) * cannon_length
        pygame.draw.line(screen, WHITE, (x, y), (cannon_end_x, cannon_end_y), 3)
        
        # Tank tracks
        track_color = GRAY
        left_track = pygame.Rect(x - 14, y - 10, 4, 20)
        right_track = pygame.Rect(x + 10, y - 10, 4, 20)
        pygame.draw.rect(screen, track_color, left_track)
        pygame.draw.rect(screen, track_color, right_track)
    
    def draw_damage_effects(self, screen):
        """Draw damage effects like smoke and sparks"""
        head_x, head_y, _ = self.segments[0]
        
        if self.damage_level >= 1:
            # Smoke effects
            for i in range(self.damage_level * 3):
                smoke_x = head_x + random.randint(-15, 15)
                smoke_y = head_y + random.randint(-15, 15)
                smoke_size = random.randint(3, 8)
                pygame.draw.circle(screen, GRAY, (int(smoke_x), int(smoke_y)), smoke_size)
        
        if self.damage_level >= 2:
            # Sparks/fire effects
            for i in range(5):
                spark_x = head_x + random.randint(-10, 10)
                spark_y = head_y + random.randint(-10, 10)
                pygame.draw.circle(screen, ORANGE, (int(spark_x), int(spark_y)), 2)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 1.5
        self.size = 8
        self.color = RED
        self.trapped = False
        self.avoidance_radius = 50  # Increased for better trail avoidance
        
    def update(self, player_pos):
        """Update enemy AI - avoid trail segments and pursue player"""
        if self.trapped:
            return  # Don't move if trapped
        
        player_x, player_y = player_pos
        
        # Calculate distance to player (accounting for screen wrapping)
        dx = player_x - self.x
        dy = player_y - self.y
        
        # Handle screen wrapping for shortest path
        if abs(dx) > SCREEN_WIDTH / 2:
            if dx > 0:
                dx -= SCREEN_WIDTH
            else:
                dx += SCREEN_WIDTH
                
        if abs(dy) > SCREEN_HEIGHT / 2:
            if dy > 0:
                dy -= SCREEN_HEIGHT
            else:
                dy += SCREEN_HEIGHT
        
        distance_to_player = math.sqrt(dx*dx + dy*dy)
        
        # Move towards player but avoid getting too close
        if distance_to_player > 30:
            # Normalize direction vector
            if distance_to_player > 0:
                move_x = (dx / distance_to_player) * self.speed
                move_y = (dy / distance_to_player) * self.speed
                
                self.x += move_x
                self.y += move_y
        
        # Handle screen wrapping for enemies too
        if self.x < 0:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = 0
            
        if self.y < 0:
            self.y = SCREEN_HEIGHT
        elif self.y > SCREEN_HEIGHT:
            self.y = 0
    
    def avoid_trail_segments(self, player_segments):
        """Make enemy avoid trail segments"""
        for segment_data in player_segments:
            if len(segment_data) == 3:
                segment_x, segment_y, lifetime = segment_data
                if lifetime <= 0:  # Skip invisible segments
                    continue
            else:
                segment_x, segment_y = segment_data[:2]
            
            # Calculate distance to this segment
            dx = self.x - segment_x
            dy = self.y - segment_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # If too close to a segment, move away
            if distance < self.avoidance_radius and distance > 0:
                # Calculate avoidance vector
                avoid_x = dx / distance
                avoid_y = dy / distance
                
                # Apply avoidance force
                avoidance_strength = (self.avoidance_radius - distance) / self.avoidance_radius
                self.x += avoid_x * avoidance_strength * self.speed * 2
                self.y += avoid_y * avoidance_strength * self.speed * 2
    
    def draw(self, screen):
        """Draw the enemy"""
        color = ORANGE if self.trapped else self.color
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size, 2)

class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 8
        self.size = 3
        self.color = YELLOW
        
    def update(self):
        """Update bullet position"""
        self.x += math.cos(math.radians(self.direction)) * self.speed
        self.y += math.sin(math.radians(self.direction)) * self.speed
        
        # Check if bullet is off screen
        return (self.x < 0 or self.x > SCREEN_WIDTH or 
                self.y < 0 or self.y > SCREEN_HEIGHT)
    
    def draw(self, screen):
        """Draw the bullet"""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

def main():
    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Sherman Tank Snake - Competitive Edition")
    clock = pygame.time.Clock()
    
    # Create game objects
    tank_snake = TankSnake(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    enemies = []
    bullets = []
    
    # Spawn initial enemies
    for i in range(4):
        enemy = Enemy(random.randint(50, SCREEN_WIDTH - 50), 
                     random.randint(50, SCREEN_HEIGHT - 50))
        enemies.append(enemy)
    
    # Game state
    running = True
    frame_count = 0
    last_shot_time = 0
    shot_cooldown = 15  # Frames between shots
    
    print("🎮 Sherman Tank Snake - Competitive Edition")
    print("🔧 Latest Fixes:")
    print("   ✅ Extended trail lifetime (10+ seconds)")
    print("   ✅ Tank immune to own trail")
    print("   ✅ Screen edge wrapping (like classic Snake)")
    print("   ✅ Competitive enemy collision damage")
    print("   ✅ Working trap system")
    print("\nControls:")
    print("   WASD/Arrows: Move tank")
    print("   SPACEBAR: Shoot")
    print("   T: Manual trap trigger")
    print("   ESC: Quit")
    print("\n🎯 Strategy Tips:")
    print("   • Use screen edges to escape enemies")
    print("   • Encircle enemies with your trail to trap them")
    print("   • Avoid direct enemy contact - it damages your tank!")
    print("   • Use manual trap trigger (T) for tactical detonations")
    
    while running:
        frame_count += 1
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_t:
                    # Manual trap activation
                    destroyed = tank_snake.activate_trap()
                    for enemy in destroyed:
                        if enemy in enemies:
                            enemies.remove(enemy)
        
        # Get pressed keys
        keys = pygame.key.get_pressed()
        
        # Handle shooting
        if keys[pygame.K_SPACE] and frame_count - last_shot_time > shot_cooldown:
            head_x, head_y, _ = tank_snake.segments[0]
            bullet = Bullet(head_x, head_y, tank_snake.direction)
            bullets.append(bullet)
            last_shot_time = frame_count
        
        # Update tank
        tank_snake.update_movement(keys)
        
        # Auto-check for traps every 30 frames (0.5 seconds)
        if frame_count % 30 == 0:
            tank_snake.check_auto_trap(enemies)
        
        # Update trap system
        destroyed_enemies = tank_snake.update_trap(enemies)
        for enemy in destroyed_enemies:
            if enemy in enemies:
                enemies.remove(enemy)
                print(f"💥 Enemy destroyed by trap! Remaining: {len(enemies)}")
        
        # Update bullets
        for bullet in bullets[:]:
            if bullet.update():
                bullets.remove(bullet)
            else:
                # Check bullet-enemy collisions
                for enemy in enemies[:]:
                    distance = math.sqrt((bullet.x - enemy.x)**2 + (bullet.y - enemy.y)**2)
                    if distance < bullet.size + enemy.size:
                        bullets.remove(bullet)
                        enemies.remove(enemy)
                        print(f"🎯 Enemy shot! Remaining: {len(enemies)}")
                        break
        
        # Update enemies
        player_pos = tank_snake.segments[0][:2]  # Get x, y from (x, y, lifetime)
        for enemy in enemies[:]:
            enemy.avoid_trail_segments(tank_snake.segments)
            enemy.update(player_pos)
            
            # FIXED: Proper enemy-tank collision with damage
            head_x, head_y, _ = tank_snake.segments[0]
            distance = math.sqrt((enemy.x - head_x)**2 + (enemy.y - head_y)**2)
            if distance < 25:  # Tank body collision
                print(f"💥 Tank hit by enemy! Distance: {distance:.1f}")
                if tank_snake.take_damage():
                    print("💀 Tank destroyed!")
                    running = False
                    break
                # Don't remove enemy immediately - let them bounce off
                # Push enemy away to prevent multiple hits
                if distance > 0:
                    push_x = (enemy.x - head_x) / distance * 30
                    push_y = (enemy.y - head_y) / distance * 30
                    enemy.x += push_x
                    enemy.y += push_y
                    
                    # Keep enemy on screen after push
                    enemy.x = max(enemy.size, min(SCREEN_WIDTH - enemy.size, enemy.x))
                    enemy.y = max(enemy.size, min(SCREEN_HEIGHT - enemy.size, enemy.y))
        
        # Spawn new enemies occasionally
        if len(enemies) < 6 and frame_count % 300 == 0:  # Every 5 seconds
            enemy = Enemy(random.randint(50, SCREEN_WIDTH - 50), 
                         random.randint(50, SCREEN_HEIGHT - 50))
            enemies.append(enemy)
        
        # Draw everything
        screen.fill(BLACK)
        
        # Draw tank and trail
        tank_snake.draw(screen)
        
        # Draw enemies
        for enemy in enemies:
            enemy.draw(screen)
        
        # Draw bullets
        for bullet in bullets:
            bullet.draw(screen)
        
        # Draw UI
        font = pygame.font.Font(None, 36)
        
        # Game stats
        stats_text = f"Enemies: {len(enemies)} | Damage: {tank_snake.damage_level}/{tank_snake.max_damage}"
        if tank_snake.trap_active:
            stats_text += f" | TRAP ACTIVE: {(tank_snake.trap_timer // 60) + 1}s"
        
        text_surface = font.render(stats_text, True, WHITE)
        screen.blit(text_surface, (10, 10))
        
        # Instructions
        if frame_count < 300:  # Show for first 5 seconds
            instruction_font = pygame.font.Font(None, 24)
            instructions = [
                "WASD: Move | SPACE: Shoot | T: Manual Trap",
                "Encircle enemies with your trail to auto-trap them!",
                "Tank is immune to its own trail!"
            ]
            for i, instruction in enumerate(instructions):
                inst_surface = instruction_font.render(instruction, True, YELLOW)
                screen.blit(inst_surface, (10, SCREEN_HEIGHT - 80 + i * 25))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

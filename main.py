import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.6
JUMP_STRENGTH = 15
PLAYER_SPEED = 5

# ===== CYBERPUNK GRID THEME =====
# Dark mode first - near-black backgrounds
BG_DARK = (5, 5, 15)           # #050508
BG_DARKER = (10, 10, 20)       # #0a0a14
GRID_LINE_COLOR = (20, 25, 50) # Subtle dark grid

# Neon accent colors
NEON_CYAN = (0, 255, 255)      # Bright cyan
NEON_MAGENTA = (255, 0, 255)   # Bright magenta
NEON_PURPLE = (180, 0, 255)    # Electric purple
NEON_BLUE = (0, 150, 255)      # Electric blue
NEON_GREEN = (0, 255, 100)     # Neon green
NEON_PINK = (255, 0, 127)      # Hot pink

# Glow and accent colors
GLOW_INTENSITY = 2             # For multiple glow layers
SCANLINE_ALPHA = 15            # Subtle scanlines

# Theme toggle flag
USE_CYBERPUNK_THEME = False

# Legacy colors (for reference/fallback)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 200)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 60), pygame.SRCALPHA)
        # Cyberpunk player: neon cyan core with magenta outline
        if USE_CYBERPUNK_THEME:
            # Draw main body with cyan
            pygame.draw.rect(self.image, NEON_CYAN, (10, 10, 20, 40))
            # Add magenta border for glow effect
            pygame.draw.rect(self.image, NEON_MAGENTA, (8, 8, 24, 44), 2)
            # Add accent lines
            pygame.draw.line(self.image, NEON_PURPLE, (5, 20), (35, 20), 1)
            pygame.draw.line(self.image, NEON_PURPLE, (5, 40), (35, 40), 1)
        else:
            self.image.fill(RED)
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.vel_x = 0
        self.is_jumping = False
        self.glow_time = 0  # For animation effects
        self.facing_right = True  # Track which direction player is facing
        self.last_laser_time = 0  # Cooldown for laser firing
        self.laser_cooldown = 30  # Frames between laser shots (0.5 seconds at 60 FPS)
    
    def handle_input(self, keys, mouse_buttons=None):
        if keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
        elif keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True
        else:
            self.vel_x = 0
        
        # Jump with spacebar
        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.vel_y = -JUMP_STRENGTH
            self.is_jumping = True
    
    def fire_laser(self):
        """Return a new laser in the direction the player is facing"""
        self.last_laser_time = self.laser_cooldown
        # Fire from the center of the player
        direction = 1 if self.facing_right else -1
        return Laser(self.rect.centerx, self.rect.centery, direction)
    
    def apply_gravity(self):
        self.vel_y += GRAVITY
        if self.vel_y > 20:
            self.vel_y = 20
    
    def update(self, platforms):
        self.apply_gravity()
        self.glow_time += 1  # Increment glow animation
        
        # Decrement laser cooldown
        if self.last_laser_time > 0:
            self.last_laser_time -= 1
        
        # Move horizontally first and check collisions
        self.rect.x += self.vel_x
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right
        
        # Move vertically and check collisions
        self.rect.y += self.vel_y
        self.is_jumping = True
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.is_jumping = False
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
        
        # Fall off screen
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.topleft = (100, 100)
            self.vel_y = 0

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, left_bound, right_bound, can_shoot=False):
        super().__init__()
        self.image = pygame.Surface((35, 35), pygame.SRCALPHA)
        # Cyberpunk enemy: neon magenta with purple glow
        if USE_CYBERPUNK_THEME:
            # Main body
            pygame.draw.circle(self.image, NEON_MAGENTA, (17, 17), 15)
            # Glow outline
            pygame.draw.circle(self.image, NEON_PURPLE, (17, 17), 17, 2)
            # Inner detail
            pygame.draw.line(self.image, NEON_CYAN, (10, 17), (24, 17), 2)
        else:
            self.image.fill(GREEN)
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x = 2
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.can_shoot = can_shoot  # Whether this enemy can shoot
        self.last_shoot_time = 0  # Cooldown for shooting
        self.shoot_cooldown = 120  # Frames between shots (2 seconds at 60 FPS)
    
    def shoot(self):
        """Return a new enemy laser in a random direction towards player"""
        self.last_shoot_time = self.shoot_cooldown
        # Fire towards the player direction (randomly left or right)
        direction = 1 if self.vel_x > 0 else -1
        return EnemyLaser(self.rect.centerx, self.rect.centery, direction)
    
    def update(self):
        self.rect.x += self.vel_x
        if self.rect.left <= self.left_bound or self.rect.right >= self.right_bound:
            self.vel_x *= -1
        
        # Decrement shoot cooldown
        if self.last_shoot_time > 0:
            self.last_shoot_time -= 1

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
        # Cyberpunk boss: massive neon pink square with intense glow
        if USE_CYBERPUNK_THEME:
            # Main body - neon pink
            pygame.draw.rect(self.image, NEON_PINK, (10, 10, 60, 60))
            # Multiple glow borders for intense effect
            pygame.draw.rect(self.image, NEON_MAGENTA, (10, 10, 60, 60), 3)
            pygame.draw.rect(self.image, NEON_PURPLE, (5, 5, 70, 70), 2)
            # Danger indicator X
            pygame.draw.line(self.image, NEON_CYAN, (20, 20), (60, 60), 2)
            pygame.draw.line(self.image, NEON_CYAN, (60, 20), (20, 60), 2)
        else:
            self.image.fill(PURPLE)
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x = 1  # Slower movement than regular enemies
        self.vel_y = 0
        self.left_bound = x - 200  # Boss patrol range (narrower)
        self.right_bound = x + 200
        self.health = 5  # Boss takes 5 hits to defeat
        self.last_shoot_time = 0
        self.shoot_cooldown = 60  # Shoots more frequently (1 second at 60 FPS)
        self.hit_flash_time = 0  # Frames to flash red after being hit
        self.hit_flash_duration = 10  # Duration of red flash (10 frames)
    
    def take_damage(self):
        """Called when hit by player laser"""
        self.health -= 1
        self.hit_flash_time = self.hit_flash_duration  # Trigger red flash
        return self.health <= 0  # Return True if boss is defeated
    
    def shoot(self):
        """Return a new enemy laser"""
        self.last_shoot_time = self.shoot_cooldown
        direction = 1 if self.vel_x > 0 else -1
        return EnemyLaser(self.rect.centerx, self.rect.centery, direction)
    
    def update(self):
        # Patrol movement
        self.rect.x += self.vel_x
        if self.rect.left <= self.left_bound or self.rect.right >= self.right_bound:
            self.vel_x *= -1
        
        # Decrement shoot cooldown
        if self.last_shoot_time > 0:
            self.last_shoot_time -= 1
        
        # Decrement hit flash time
        if self.hit_flash_time > 0:
            self.hit_flash_time -= 1
        
        # Redraw sprite with flash effect if hit
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
        if self.hit_flash_time > 0:
            # Flash red when hit
            if USE_CYBERPUNK_THEME:
                pygame.draw.rect(self.image, RED, (10, 10, 60, 60))  # Red fill
                pygame.draw.rect(self.image, (255, 100, 100), (10, 10, 60, 60), 3)  # Light red border
                pygame.draw.rect(self.image, (255, 150, 150), (5, 5, 70, 70), 2)  # Light red outer
                pygame.draw.line(self.image, (255, 200, 200), (20, 20), (60, 60), 2)
                pygame.draw.line(self.image, (255, 200, 200), (60, 20), (20, 60), 2)
            else:
                self.image.fill(RED)
        else:
            # Normal boss appearance
            if USE_CYBERPUNK_THEME:
                # Main body - neon pink
                pygame.draw.rect(self.image, NEON_PINK, (10, 10, 60, 60))
                # Multiple glow borders for intense effect
                pygame.draw.rect(self.image, NEON_MAGENTA, (10, 10, 60, 60), 3)
                pygame.draw.rect(self.image, NEON_PURPLE, (5, 5, 70, 70), 2)
                # Danger indicator X
                pygame.draw.line(self.image, NEON_CYAN, (20, 20), (60, 60), 2)
                pygame.draw.line(self.image, NEON_CYAN, (60, 20), (20, 60), 2)
            else:
                self.image.fill(PURPLE)

class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((15, 15), pygame.SRCALPHA)
        # Cyberpunk collectible: neon cyan diamond/star with glow
        if USE_CYBERPUNK_THEME:
            # Star/diamond shape with glow
            pygame.draw.polygon(self.image, NEON_CYAN, 
                              [(7, 0), (10, 8), (15, 10), (8, 13), (10, 15), (7, 10), (0, 10), (5, 8)])
            # Glow effect - draw slightly larger version in purple
            pygame.draw.polygon(self.image, NEON_PURPLE, 
                              [(7, 0), (10, 8), (15, 10), (8, 13), (10, 15), (7, 10), (0, 10), (5, 8)], 1)
        else:
            self.image.fill(YELLOW)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.bob_offset = 0  # For bobbing animation
        self.original_y = y
    
    def update(self):
        # Gentle bobbing animation
        self.bob_offset = math.sin(pygame.time.get_ticks() * 0.003) * 3
        self.rect.y = self.original_y + self.bob_offset

class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y, direction=1):
        super().__init__()
        self.speed = 12  # Laser speed
        self.direction = direction  # 1 for right, -1 for left
        
        # Create laser visual
        self.image = pygame.Surface((20, 5), pygame.SRCALPHA)
        if USE_CYBERPUNK_THEME:
            # Neon green laser beam with glow
            pygame.draw.rect(self.image, NEON_GREEN, (0, 0, 20, 5))
            pygame.draw.rect(self.image, NEON_CYAN, (0, 0, 20, 5), 1)  # Glow border
        else:
            self.image.fill(YELLOW)
        
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self):
        # Move laser in the direction it was fired
        self.rect.x += self.speed * self.direction
        
        # Remove laser if it goes off screen or past level end
        if self.rect.right < 0 or self.rect.left > 7000:  # Allow laser to travel full level width (supports up to 7000px)
            self.kill()

class EnemyLaser(pygame.sprite.Sprite):
    def __init__(self, x, y, direction=1):
        super().__init__()
        self.speed = 8  # Enemy laser speed (slower than player laser)
        self.direction = direction  # 1 for right, -1 for left
        
        # Create enemy laser visual (red instead of green)
        self.image = pygame.Surface((20, 5), pygame.SRCALPHA)
        if USE_CYBERPUNK_THEME:
            # Neon red laser beam with glow
            pygame.draw.rect(self.image, (255, 50, 50), (0, 0, 20, 5))  # Red color
            pygame.draw.rect(self.image, (255, 150, 150), (0, 0, 20, 5), 1)  # Light red glow border
        else:
            self.image.fill((200, 0, 0))  # Dark red
        
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self):
        # Move laser in the direction it was fired
        self.rect.x += self.speed * self.direction
        
        # Remove laser if it goes off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH + 500:
            self.kill()

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=None):
        super().__init__()
        # Use cyberpunk colors if theme enabled, otherwise use provided color
        if USE_CYBERPUNK_THEME:
            if color is None:
                color = NEON_BLUE
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            # Main platform body
            pygame.draw.rect(self.image, color, (0, 0, width, height))
            # Neon glow border
            pygame.draw.rect(self.image, NEON_CYAN, (0, 0, width, height), 2)
            # Subtle accent lines for grid effect
            if width > 40:
                for i in range(1, width // 40):
                    pygame.draw.line(self.image, GRID_LINE_COLOR, (i * 40, 0), (i * 40, height), 1)
        else:
            if color is None:
                color = BLACK
            self.image = pygame.Surface((width, height))
            self.image.fill(color)
        
        self.rect = self.image.get_rect(topleft=(x, y))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Cyberpunk Grid Platformer" if USE_CYBERPUNK_THEME else "Pygame Platformer")
        self.clock = pygame.time.Clock()
        self.running = True
        self.score = 0
        self.level = 1
        
        # Cyberpunk theme fonts
        if USE_CYBERPUNK_THEME:
            try:
                # Try to use monospace font for futuristic feel
                self.font_large = pygame.font.Font(None, 48)
                self.font_medium = pygame.font.Font(None, 36)
                self.font_small = pygame.font.Font(None, 24)
            except:
                self.font_large = pygame.font.Font(None, 48)
                self.font_medium = pygame.font.Font(None, 36)
                self.font_small = pygame.font.Font(None, 24)
        else:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 24)
        
        # Camera
        self.camera_x = 0
        
        # Animation counter for effects
        self.frame_count = 0
        
        # Sprite groups
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()
        self.lasers = pygame.sprite.Group()  # NEW: Laser group
        self.enemy_lasers = pygame.sprite.Group()  # NEW: Enemy laser group
        self.bosses = pygame.sprite.Group()  # NEW: Boss group
        self.all_sprites = pygame.sprite.Group()
        
        # Create level
        self.create_level()
        
        # Create player
        self.player = Player(100, 100)
        self.all_sprites.add(self.player)
    
    def create_level(self):
        if self.level == 1:
            self.create_level_1()
        elif self.level == 2:
            self.create_level_2()
        elif self.level == 3:
            self.create_level_3()
    
    def create_level_1(self):
        # Ground - extended length
        ground = Platform(0, SCREEN_HEIGHT - 40, 4000, 40)
        self.platforms.add(ground)
        self.all_sprites.add(ground)
        
        # Extended platforms
        platforms_data = [
            (200, 450, 150, 20),
            (500, 400, 150, 20),
            (300, 300, 150, 20),
            (600, 250, 150, 20),
            (900, 350, 150, 20),
            (1200, 300, 150, 20),
            (1500, 250, 150, 20),
            (1800, 350, 150, 20),
            (2100, 300, 150, 20),
            (2400, 250, 150, 20),
            (2700, 350, 150, 20),
            (3000, 300, 150, 20),
            (3300, 250, 150, 20),
            (3600, 350, 150, 20),
        ]
        
        for x, y, w, h in platforms_data:
            platform = Platform(x, y, w, h)
            self.platforms.add(platform)
            self.all_sprites.add(platform)
        
        # Extended enemies (some can shoot)
        # Position enemies on platforms (platform_y - 35 to sit on top)
        enemies_data = [
            (275, 415, 200, 350, False),   # On platform at y=450
            (575, 365, 500, 650, True),    # On platform at y=400
            (375, 265, 300, 450, False),   # On platform at y=300
            (675, 215, 600, 750, True),    # On platform at y=250
            (975, 315, 900, 1050, False),  # On platform at y=350
            (1275, 265, 1200, 1350, True), # On platform at y=300
            (1575, 215, 1500, 1650, False),# On platform at y=250
            (1875, 315, 1800, 1950, True), # On platform at y=350
            (2175, 265, 2100, 2250, False),# On platform at y=300
            (2475, 215, 2400, 2550, True), # On platform at y=250
            (2775, 315, 2700, 2850, False),# On platform at y=350
            (3075, 265, 3000, 3150, True), # On platform at y=300
            (3375, 215, 3300, 3450, False),# On platform at y=250
        ]
        
        for x, y, left, right, can_shoot in enemies_data:
            enemy = Enemy(x, y, left, right, can_shoot)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
        
        # Extended collectibles
        collectibles_data = [
            (275, 430), (575, 380), (375, 280), (675, 220),
            (975, 320), (1275, 270), (1575, 220), (1875, 320),
            (2175, 270), (2475, 220), (2775, 320), (3075, 270),
            (3375, 220), (3675, 320)
        ]
        for cx, cy in collectibles_data:
            collectible = Collectible(cx, cy)
            self.collectibles.add(collectible)
            self.all_sprites.add(collectible)
    
    def create_level_2(self):
        # Ground - even longer
        ground = Platform(0, SCREEN_HEIGHT - 40, 5000, 40)
        self.platforms.add(ground)
        self.all_sprites.add(ground)
        
        # More challenging platforms with smaller gaps
        platforms_data = [
            (200, 450, 100, 20),
            (350, 400, 100, 20),
            (500, 350, 100, 20),
            (650, 300, 100, 20),
            (800, 400, 100, 20),
            (950, 350, 100, 20),
            (1100, 300, 100, 20),
            (1250, 380, 100, 20),
            (1400, 320, 100, 20),
            (1550, 280, 100, 20),
            (1700, 360, 100, 20),
            (1850, 300, 100, 20),
            (2000, 250, 100, 20),
            (2150, 340, 100, 20),
            (2300, 290, 100, 20),
            (2450, 350, 100, 20),
            (2600, 300, 100, 20),
            (2750, 260, 100, 20),
            (2900, 320, 100, 20),
            (3050, 380, 100, 20),
            (3200, 310, 100, 20),
            (3350, 270, 100, 20),
            (3500, 340, 100, 20),
            (3650, 290, 100, 20),
            (3800, 350, 100, 20),
            (3950, 300, 100, 20),
        ]
        
        for x, y, w, h in platforms_data:
            platform = Platform(x, y, w, h)
            self.platforms.add(platform)
            self.all_sprites.add(platform)
        
        # More enemies (some can shoot)
        # Position enemies on platforms (platform_y - 35 to sit on top)
        enemies_data = [
            (250, 415, 200, 300, True),    # On platform at y=450, can shoot
            (400, 365, 350, 450, False),   # On platform at y=400
            (550, 315, 500, 600, True),    # On platform at y=350, can shoot
            (700, 265, 650, 750, False),   # On platform at y=300
            (850, 365, 800, 900, True),    # On platform at y=400, can shoot
            (1000, 315, 950, 1050, False), # On platform at y=350
            (1150, 265, 1100, 1200, True), # On platform at y=300, can shoot
            (1300, 345, 1250, 1350, False),# On platform at y=380
            (1450, 285, 1400, 1500, True), # On platform at y=320, can shoot
            (1600, 245, 1550, 1650, False),# On platform at y=280
            (1750, 325, 1700, 1800, True), # On platform at y=360, can shoot
            (1900, 265, 1850, 1950, False),# On platform at y=300
            (2050, 215, 2000, 2100, True), # On platform at y=250, can shoot
            (2200, 305, 2150, 2250, False),# On platform at y=340
            (2350, 255, 2300, 2400, True), # On platform at y=290, can shoot
            (2500, 315, 2450, 2550, False),# On platform at y=350
            (2650, 265, 2600, 2700, True), # On platform at y=300, can shoot
            (2800, 225, 2750, 2850, False),# On platform at y=260
            (2950, 285, 2900, 3000, True), # On platform at y=320, can shoot
            (3100, 345, 3050, 3150, False),# On platform at y=380
            (3250, 275, 3200, 3300, True), # On platform at y=310, can shoot
            (3400, 235, 3350, 3450, False),# On platform at y=270
            (3550, 305, 3500, 3600, True), # On platform at y=340, can shoot
            (3700, 255, 3650, 3750, False),# On platform at y=290
            (3850, 315, 3800, 3900, True), # On platform at y=350, can shoot
            (3950, 265, 3900, 4000, False),# On platform at y=300
        ]
        
        for x, y, left, right, can_shoot in enemies_data:
            enemy = Enemy(x, y, left, right, can_shoot)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
        
        # More collectibles
        collectibles_data = [
            (200, 430), (350, 380), (500, 330), (650, 280),
            (800, 380), (950, 330), (1100, 280), (1250, 360),
            (1400, 310), (1550, 270), (1700, 340), (1850, 290),
            (2000, 240), (2150, 330), (2300, 280), (2450, 340),
            (2600, 290), (2750, 250), (2900, 310), (3050, 370),
            (3200, 300), (3350, 260), (3500, 330), (3650, 280),
            (3800, 340), (3950, 290)
        ]
        for cx, cy in collectibles_data:
            collectible = Collectible(cx, cy)
            self.collectibles.add(collectible)
            self.all_sprites.add(collectible)
    
    def create_level_3(self):
        """Final boss level - shorter but with intense boss challenge"""
        # Ground
        ground = Platform(0, SCREEN_HEIGHT - 40, 7000, 40)
        self.platforms.add(ground)
        self.all_sprites.add(ground)
        
        # Boss arena platforms - fewer but taller for tactical movement
        platforms_data = [
            (200, 450, 150, 20),
            (450, 350, 150, 20),
            (700, 250, 150, 20),
            (950, 350, 150, 20),
            (1200, 200, 150, 20),
            (1500, 350, 150, 20),
            (1800, 250, 150, 20),
            (2100, 400, 150, 20),
            (2400, 300, 150, 20),
            (2700, 200, 150, 20),
            (3000, 350, 150, 20),
            (3300, 250, 150, 20),
            (3600, 400, 150, 20),
            (3900, 300, 150, 20),
            (4200, 150, 150, 20),  # Challenging access to boss
            (4500, 300, 150, 20),
            (4800, 200, 150, 20),
            (5100, 350, 150, 20),
            (5400, 300, 150, 20),
            (5700, 200, 150, 20),
            (5900, 450, 300, 20),  # Wide platform for boss battle
        ]
        
        for x, y, w, h in platforms_data:
            platform = Platform(x, y, w, h)
            self.platforms.add(platform)
            self.all_sprites.add(platform)
        
        # Fewer enemies before boss
        enemies_data = [
            (275, 415, 200, 350, False),   # On platform at y=450
            (525, 315, 450, 600, True),    # On platform at y=350
            (775, 215, 700, 850, False),   # On platform at y=250
            (1025, 315, 950, 1100, True),  # On platform at y=350
            (1275, 165, 1200, 1350, False),# On platform at y=200
            (1575, 315, 1500, 1650, True), # On platform at y=350
            (1875, 215, 1800, 1950, False),# On platform at y=250
            (2175, 365, 2100, 2250, True), # On platform at y=400
            (2475, 265, 2400, 2550, False),# On platform at y=300
            (2775, 165, 2700, 2850, True), # On platform at y=200
        ]
        
        for x, y, left, right, can_shoot in enemies_data:
            enemy = Enemy(x, y, left, right, can_shoot)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
        
        # Boss at the end (on the wide platform)
        boss = Boss(5950, 370)  # 370 = 450 - 80 (platform_y - boss_height)
        self.bosses.add(boss)
        self.all_sprites.add(boss)
        
        # Fewer collectibles, more spread out
        collectibles_data = [
            (200, 430), (450, 330), (700, 230), (950, 330),
            (1200, 180), (1500, 330), (1800, 230), (2100, 380),
            (2400, 280), (2700, 180), (3000, 330), (3300, 230),
            (3600, 380), (3900, 280), (4200, 130), (4500, 280),
            (4800, 180), (5100, 330), (5400, 280), (5700, 180)
        ]
        for cx, cy in collectibles_data:
            collectible = Collectible(cx, cy)
            self.collectibles.add(collectible)
            self.all_sprites.add(collectible)
    
    def update_camera(self):
        # Camera follows player, keeps player centered in middle of screen
        self.camera_x = self.player.rect.centerx - SCREEN_WIDTH // 2
        self.camera_x = max(0, self.camera_x)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
    
    def load_next_level(self):
        # Clear all sprites
        self.platforms.empty()
        self.enemies.empty()
        self.collectibles.empty()
        self.lasers.empty()  # Clear lasers
        self.enemy_lasers.empty()  # Clear enemy lasers
        self.bosses.empty()  # Clear bosses
        self.all_sprites.empty()
        
        # Move to next level
        self.level += 1
        self.camera_x = 0
        self.player.rect.topleft = (100, 100)
        self.player.vel_y = 0
        self.player.vel_x = 0
        
        # Create new level
        self.create_level()
        self.all_sprites.add(self.player)
    
    def update(self):
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        self.player.handle_input(keys, mouse_buttons)
        
        # Handle laser firing with left mouse click
        if mouse_buttons[0] and self.player.last_laser_time <= 0:  # Left mouse button (index 0)
            new_laser = self.player.fire_laser()
            self.lasers.add(new_laser)
            self.all_sprites.add(new_laser)
        
        self.player.update(self.platforms)
        self.enemies.update()
        
        # Handle enemy shooting
        import random
        for enemy in self.enemies:
            if enemy.can_shoot and enemy.last_shoot_time <= 0:
                # Randomly decide if enemy shoots this frame (~0.8% chance per frame)
                if random.random() < 0.008:
                    new_enemy_laser = enemy.shoot()
                    self.enemy_lasers.add(new_enemy_laser)
                    self.all_sprites.add(new_enemy_laser)
        
        # Handle boss shooting (more aggressive)
        for boss in self.bosses:
            if boss.last_shoot_time <= 0:
                # Boss shoots more frequently (~3% chance per frame)
                if random.random() < 0.03:
                    new_boss_laser = boss.shoot()
                    self.enemy_lasers.add(new_boss_laser)
                    self.all_sprites.add(new_boss_laser)
        
        self.collectibles.update()  # Update collectible animations
        self.lasers.update()  # Update lasers
        self.enemy_lasers.update()  # Update enemy lasers
        self.bosses.update()  # Update bosses
        self.update_camera()
        self.frame_count += 1  # Increment frame counter for effects
        
        # Check if player reached end of level (or defeated boss)
        if self.level == 3:
            # Level 3: Check if boss is defeated
            if len(self.bosses) == 0:
                self.load_next_level()
        else:
            # Levels 1-2: Check if player reached end
            level_end_x = 4000 if self.level == 1 else 5000
            if self.player.rect.x > level_end_x - 50:
                self.load_next_level()
        
        # Collect items
        collected = pygame.sprite.spritecollide(self.player, self.collectibles, True)
        self.score += len(collected) * 10
        
        # Laser collisions with enemies
        for laser in self.lasers:
            enemies_hit = pygame.sprite.spritecollide(laser, self.enemies, False)
            for enemy in enemies_hit:
                enemy.kill()
                laser.kill()
                self.score += 50  # Score for laser kill
            
            # Laser collisions with boss
            bosses_hit = pygame.sprite.spritecollide(laser, self.bosses, False)
            for boss in bosses_hit:
                laser.kill()
                if boss.take_damage():
                    # Boss defeated
                    boss.kill()
                    self.score += 500  # Massive score for defeating boss
                else:
                    self.score += 100  # Score for each hit on boss
        
        # Enemy laser collisions with player - damage
        enemy_lasers_hit = pygame.sprite.spritecollide(self.player, self.enemy_lasers, True)
        if enemy_lasers_hit:
            # Player hit by enemy laser - reset
            self.player.rect.topleft = (100, 100)
            self.camera_x = 0
            self.score = 0
        
        # Enemy collision - kill by jumping on them or with lasers
        enemies_hit = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in enemies_hit:
            if self.player.vel_y > 0 and self.player.rect.bottom - self.player.vel_y <= enemy.rect.centery:
                # Player jumped on enemy from above
                enemy.kill()
                self.player.vel_y = -JUMP_STRENGTH
                self.score += 50
            else:
                # Player hit enemy from side or below - reset
                self.player.rect.topleft = (100, 100)
                self.camera_x = 0
                self.score = 0
        
        # Boss collision - cannot be jumped on, touching boss resets player
        bosses_hit = pygame.sprite.spritecollide(self.player, self.bosses, False)
        if bosses_hit:
            # Player hit boss - reset
            self.player.rect.topleft = (100, 100)
            self.camera_x = 0
            self.score = 0
    
    def draw_grid_background(self):
        """Draw animated grid background for cyberpunk theme"""
        if not USE_CYBERPUNK_THEME:
            return
        
        grid_size = 50
        offset_x = -(self.camera_x % grid_size)
        
        # Draw vertical grid lines
        x = offset_x
        while x < SCREEN_WIDTH:
            pygame.draw.line(self.screen, GRID_LINE_COLOR, (x, 0), (x, SCREEN_HEIGHT), 1)
            x += grid_size
        
        # Draw horizontal grid lines
        for y in range(0, SCREEN_HEIGHT, grid_size):
            pygame.draw.line(self.screen, GRID_LINE_COLOR, (0, y), (SCREEN_WIDTH, y), 1)
        
        # Animated horizontal scanlines
        scanline_y = (self.frame_count * 2) % SCREEN_HEIGHT
        for y in range(0, SCREEN_HEIGHT, 4):
            opacity_color = tuple(int(c * 0.1) for c in GRID_LINE_COLOR)
            pygame.draw.line(self.screen, opacity_color, (0, (y + scanline_y) % SCREEN_HEIGHT), 
                           (SCREEN_WIDTH, (y + scanline_y) % SCREEN_HEIGHT), 1)
    
    def draw_ui_panel(self, text, x, y, text_color, bg_color, padding=10, glow=True):
        """Draw a neon UI panel with glow effect"""
        if not USE_CYBERPUNK_THEME:
            rendered_text = self.font_medium.render(text, True, text_color)
            self.screen.blit(rendered_text, (x, y))
            return
        
        rendered_text = self.font_medium.render(text, True, text_color)
        text_width, text_height = rendered_text.get_size()
        
        # Draw background panel
        panel_rect = pygame.Rect(x - padding, y - padding, 
                                 text_width + padding * 2, text_height + padding * 2)
        pygame.draw.rect(self.screen, bg_color, panel_rect)
        
        # Draw glow border
        if glow:
            pygame.draw.rect(self.screen, text_color, panel_rect, 2)
        
        # Draw text
        self.screen.blit(rendered_text, (x, y))
    
    def draw(self):
        # Cyberpunk dark background
        if USE_CYBERPUNK_THEME:
            self.screen.fill(BG_DARK)
            self.draw_grid_background()
        else:
            self.screen.fill(WHITE)
        
        # Draw sprites with camera offset
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y))
        
        # Draw HUD - Score and Level
        if USE_CYBERPUNK_THEME:
            # Animated glow color for HUD
            glow_color = NEON_CYAN if (self.frame_count // 10) % 2 == 0 else NEON_BLUE
            
            # Draw score panel
            score_text = f"SCORE: {self.score:06d}"
            score_surface = self.font_medium.render(score_text, True, NEON_CYAN)
            score_rect = score_surface.get_rect(topright=(SCREEN_WIDTH - 15, 15))
            
            # Glow effect for score
            glow_rect = score_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (0, 50, 50), glow_rect)  # Subtle background
            pygame.draw.rect(self.screen, NEON_CYAN, glow_rect, 2)  # Border glow
            self.screen.blit(score_surface, score_rect)
            
            # Draw level panel
            level_text = f"LEVEL: {self.level}"
            level_surface = self.font_medium.render(level_text, True, NEON_MAGENTA)
            level_rect = level_surface.get_rect(topleft=(15, 15))
            
            # Glow effect for level
            level_glow_rect = level_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (50, 0, 50), level_glow_rect)  # Subtle background
            pygame.draw.rect(self.screen, NEON_MAGENTA, level_glow_rect, 2)  # Border glow
            self.screen.blit(level_surface, level_rect)
        else:
            score_text = self.font_medium.render(f"Score: {self.score}", True, BLACK)
            level_text = self.font_medium.render(f"Level: {self.level}", True, BLACK)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(level_text, (10, 50))
        
        # Draw boss health bar if boss exists
        if len(self.bosses) > 0:
            boss = list(self.bosses)[0]  # Get the first (and only) boss
            
            # Health bar positioning
            bar_x = SCREEN_WIDTH // 2 - 100
            bar_y = 20
            bar_width = 200
            bar_height = 30
            
            # Calculate health percentage
            health_percentage = boss.health / 5.0  # Boss has 5 max health
            
            if USE_CYBERPUNK_THEME:
                # Background panel
                pygame.draw.rect(self.screen, (50, 0, 0), (bar_x - 5, bar_y - 5, bar_width + 10, bar_height + 10))
                pygame.draw.rect(self.screen, NEON_MAGENTA, (bar_x - 5, bar_y - 5, bar_width + 10, bar_height + 10), 2)
                
                # Boss name
                boss_text = self.font_small.render("BOSS HEALTH", True, NEON_MAGENTA)
                self.screen.blit(boss_text, (bar_x, bar_y - 25))
                
                # Health bar background
                pygame.draw.rect(self.screen, (30, 0, 0), (bar_x, bar_y, bar_width, bar_height))
                
                # Health bar fill (red to green gradient based on health)
                if health_percentage > 0.5:
                    bar_color = (int(255 * (1 - health_percentage)), 255, 0)  # Green to yellow
                elif health_percentage > 0.25:
                    bar_color = (255, 200, 0)  # Yellow
                else:
                    bar_color = (255, 0, 0)  # Red
                
                pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, int(bar_width * health_percentage), bar_height))
                
                # Health bar border
                pygame.draw.rect(self.screen, NEON_MAGENTA, (bar_x, bar_y, bar_width, bar_height), 2)
                
                # Health text
                health_text = self.font_small.render(f"{boss.health}/5", True, bar_color)
                health_rect = health_text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
                self.screen.blit(health_text, health_rect)
            else:
                # Classic mode
                pygame.draw.rect(self.screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(self.screen, RED, (bar_x, bar_y, int(bar_width * health_percentage), bar_height))
                pygame.draw.rect(self.screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
                
                health_text = self.font_small.render(f"Boss: {boss.health}/5", True, BLACK)
                self.screen.blit(health_text, (bar_x, bar_y - 20))
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()

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
        self.laser_cooldown = 10  # Frames between laser shots
    
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
    def __init__(self, x, y, left_bound, right_bound):
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
    
    def update(self):
        self.rect.x += self.vel_x
        if self.rect.left <= self.left_bound or self.rect.right >= self.right_bound:
            self.vel_x *= -1

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
        if self.rect.right < 0 or self.rect.left > 5000:  # Allow laser to travel full level width
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
        
        # Extended enemies
        enemies_data = [
            (275, 430, 200, 350),
            (575, 380, 500, 650),
            (375, 280, 300, 450),
            (675, 230, 600, 750),
            (975, 330, 900, 1050),
            (1275, 280, 1200, 1350),
            (1575, 230, 1500, 1650),
            (1875, 330, 1800, 1950),
            (2175, 280, 2100, 2250),
            (2475, 230, 2400, 2550),
            (2775, 330, 2700, 2850),
            (3075, 280, 3000, 3150),
            (3375, 230, 3300, 3450),
        ]
        
        for x, y, left, right in enemies_data:
            enemy = Enemy(x, y, left, right)
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
        
        # More enemies
        enemies_data = [
            (250, 430, 200, 300),
            (400, 380, 350, 450),
            (550, 330, 500, 600),
            (700, 280, 650, 750),
            (850, 330, 800, 900),
            (1000, 360, 950, 1050),
            (1150, 300, 1100, 1200),
            (1300, 340, 1250, 1350),
            (1450, 280, 1400, 1500),
            (1600, 320, 1550, 1650),
            (1750, 360, 1700, 1800),
            (1900, 300, 1850, 1950),
            (2050, 330, 2000, 2100),
            (2200, 390, 2150, 2250),
            (2350, 320, 2300, 2400),
            (2500, 280, 2450, 2550),
            (2650, 350, 2600, 2700),
            (2800, 300, 2750, 2850),
            (2950, 360, 2900, 3000),
            # Added enemies for more challenge
            (3100, 340, 3050, 3150),
            (3250, 300, 3200, 3300),
            (3400, 360, 3350, 3450),
            (3550, 320, 3500, 3600),
            (3700, 380, 3650, 3750),
            (3850, 310, 3800, 3900),
            (3950, 350, 3900, 4000),
        ]
        
        for x, y, left, right in enemies_data:
            enemy = Enemy(x, y, left, right)
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
        self.collectibles.update()  # Update collectible animations
        self.lasers.update()  # Update lasers
        self.update_camera()
        self.frame_count += 1  # Increment frame counter for effects
        
        # Check if player reached end of level
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

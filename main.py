import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize sound mixer

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
NEON_RED = (255, 0, 50)        # Neon red

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

# Space colors
DEEP_SPACE = (10, 5, 20)       # Deep space background
STAR_COLOR = (255, 255, 200)   # Warm star color
ALIEN_GLOW_1 = (100, 255, 200) # Cyan alien bioluminescence
ALIEN_GLOW_2 = (200, 100, 255) # Purple alien bioluminescence
ROBOT_CHROME = (200, 200, 220) # Chrome robot color

class Star:
    """Static star in the background"""
    def __init__(self, x, y, brightness=0.5):
        self.x = x
        self.y = y
        self.brightness = brightness
        self.max_brightness = brightness
        self.twinkle_speed = random.uniform(0.01, 0.05)
        self.twinkle_phase = random.uniform(0, 6.28)
    
    def update(self):
        # Twinkling effect
        self.twinkle_phase += self.twinkle_speed
        self.brightness = self.max_brightness * (0.5 + 0.5 * math.sin(self.twinkle_phase))
    
    def draw(self, surface, camera_x):
        size = max(1, int(self.brightness * 3))
        color = tuple(int(c * self.brightness) for c in STAR_COLOR)
        pygame.draw.circle(surface, color, (int(self.x - camera_x), int(self.y)), size)

class Asteroid:
    """Parallax asteroid in background"""
    def __init__(self, x, y, depth=0.5):
        self.x = x
        self.y = y
        self.depth = depth  # 0-1, lower = farther away, slower parallax
        self.size = random.randint(3, 15)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        self.color = (120 + int(depth * 80), 100, 140)
    
    def update(self):
        self.rotation += self.rotation_speed
    
    def draw(self, surface, camera_x):
        # Parallax: asteroids move slower based on depth
        screen_x = self.x - camera_x * self.depth
        
        # Only draw if on screen
        if -50 < screen_x < SCREEN_WIDTH + 50:
            pygame.draw.circle(surface, self.color, (int(screen_x), int(self.y)), self.size)
            # Add a small glow
            pygame.draw.circle(surface, tuple(min(255, c + 50) for c in self.color), 
                              (int(screen_x), int(self.y)), self.size, 1)

class DistantExplosion:
    """Distant spaceship explosion in background"""
    def __init__(self, x, y, max_duration=60):
        self.x = x
        self.y = y
        self.age = 0
        self.max_duration = max_duration
        self.size = random.randint(5, 15)
        self.depth = random.uniform(0.3, 0.8)  # Parallax depth
        self.color = random.choice([NEON_RED, NEON_MAGENTA, NEON_PINK])
    
    def update(self):
        self.age += 1
    
    def is_alive(self):
        return self.age < self.max_duration
    
    def draw(self, surface, camera_x):
        progress = self.age / self.max_duration
        
        # Parallax effect
        screen_x = self.x - camera_x * self.depth
        
        if -50 < screen_x < SCREEN_WIDTH + 50:
            # Expanding explosion with fade
            current_size = int(self.size * (1 + progress * 2))
            alpha = int(255 * (1 - progress))
            
            # Main explosion glow
            explosion_surface = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, alpha)
            pygame.draw.circle(explosion_surface, color_with_alpha, (current_size, current_size), current_size)
            surface.blit(explosion_surface, (int(screen_x) - current_size, int(self.y) - current_size))
            
            # Secondary glow (dimmer, larger)
            if current_size > 3:
                pygame.draw.circle(explosion_surface, (*self.color, int(alpha * 0.5)), 
                                  (current_size, current_size), int(current_size * 1.5), 2)

class AlienShip:
    """Distant alien organic ship with bioluminescent glow"""
    def __init__(self, x, y, depth=0.5):
        self.x = x
        self.y = y
        self.depth = depth
        self.size = random.randint(15, 35)
        self.glow_phase = random.uniform(0, 6.28)
        self.glow_speed = random.uniform(0.02, 0.05)
        self.bob_offset = 0
        self.bob_speed = random.uniform(0.01, 0.03)
        self.color1 = ALIEN_GLOW_1
        self.color2 = ALIEN_GLOW_2
    
    def update(self):
        self.glow_phase += self.glow_speed
        self.bob_offset = math.sin(self.glow_phase * 0.5) * 5
    
    def draw(self, surface, camera_x):
        screen_x = self.x - camera_x * self.depth
        
        if -50 < screen_x < SCREEN_WIDTH + 50:
            screen_y = self.y + self.bob_offset
            
            # Glow intensity based on animation
            glow_intensity = 0.5 + 0.5 * math.sin(self.glow_phase)
            
            # Organic curved ship shape
            # Main body (oval) - clamp color values to 0-255
            color1 = tuple(min(255, int(c * glow_intensity)) for c in self.color1)
            pygame.draw.ellipse(surface, color1,
                              (int(screen_x) - self.size, int(screen_y) - self.size // 2,
                               self.size * 2, self.size))
            
            # Glowing veins/accents - clamp color values to 0-255
            color2 = tuple(min(255, int(c * min(1.0, glow_intensity + 0.3))) for c in self.color2)
            pygame.draw.ellipse(surface, color2,
                              (int(screen_x) - self.size, int(screen_y) - self.size // 2,
                               self.size * 2, self.size), 2)
            
            # Bright glow spots
            spot_color = (255, 255, 100)
            pygame.draw.circle(surface, spot_color, (int(screen_x) - self.size // 2, int(screen_y)), 3)
            pygame.draw.circle(surface, spot_color, (int(screen_x) + self.size // 2, int(screen_y)), 2)

class RobotWarship:
    """Distant robot metallic warship"""
    def __init__(self, x, y, depth=0.5):
        self.x = x
        self.y = y
        self.depth = depth
        self.size = random.randint(15, 35)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-1, 1)
    
    def update(self):
        self.rotation += self.rotation_speed
    
    def draw(self, surface, camera_x):
        screen_x = self.x - camera_x * self.depth
        
        if -50 < screen_x < SCREEN_WIDTH + 50:
            screen_y = self.y
            
            # Angular chrome warship shape (wedge/arrow pointing right)
            points = [
                (int(screen_x) + self.size, int(screen_y)),  # Tip
                (int(screen_x) - self.size, int(screen_y) - self.size // 2),  # Top rear
                (int(screen_x) - self.size, int(screen_y) + self.size // 2),  # Bottom rear
            ]
            pygame.draw.polygon(surface, ROBOT_CHROME, points)
            pygame.draw.polygon(surface, (100, 100, 150), points, 2)  # Dark outline
            
            # Weapon ports (small circles)
            pygame.draw.circle(surface, (255, 100, 50), (int(screen_x), int(screen_y) - self.size // 4), 2)
            pygame.draw.circle(surface, (255, 100, 50), (int(screen_x), int(screen_y) + self.size // 4), 2)

class SoundManager:
    """Manages all game sounds and music"""
    def __init__(self):
        self.sounds = {}
        self.music_playing = False
        self.sound_enabled = True
        self.music_enabled = True
        self.volume = 0.7
        
        # Try to load sounds from assets folder
        self.load_sounds()
    
    def load_sounds(self):
        """Load all sound effects from assets folder"""
        sound_files = {
            'laser': 'assets/laser.wav',
            'bullet': 'assets/bullet.wav',
            'explosion': 'assets/explosion.wav',
            'enemy_hit': 'assets/enemy_hit.wav',
            'boss_hit': 'assets/boss_hit.wav',
            'boss_defeated': 'assets/boss_defeated.wav',
            'game_over': 'assets/game_over.wav',
            'victory': 'assets/victory.wav',
            'jump': 'assets/jump.wav',
            'collect': 'assets/collect.wav',
        }
        
        for sound_name, file_path in sound_files.items():
            try:
                sound = pygame.mixer.Sound(file_path)
                sound.set_volume(self.volume)
                self.sounds[sound_name] = sound
            except Exception as e:
                # Sound file not found - that's ok, we'll just skip it
                pass
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if not self.sound_enabled or sound_name not in self.sounds:
            return
        
        try:
            self.sounds[sound_name].play()
        except Exception as e:
            pass
    
    def play_music(self, file_path, loops=-1):
        """Play background music (loops infinitely by default)"""
        if not self.music_enabled:
            return
        
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(self.volume * 0.8)  # Music slightly quieter
            pygame.mixer.music.play(loops)
            self.music_playing = True
        except Exception as e:
            pass
    
    def stop_music(self):
        """Stop background music"""
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False
    
    def set_volume(self, volume):
        """Set volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.set_volume(self.volume)
        
        # Update all loaded sounds
        for sound in self.sounds.values():
            sound.set_volume(self.volume)
    
    def toggle_sound(self):
        """Toggle sound effects on/off"""
        self.sound_enabled = not self.sound_enabled
    
    def toggle_music(self):
        """Toggle music on/off"""
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.stop_music()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Player sprite dimensions
        PLAYER_WIDTH = 50
        PLAYER_HEIGHT = 75
        
        # Load sprite images from assets
        try:
            self.idle_image = pygame.transform.scale(
                pygame.image.load("assets/blast.png").convert_alpha(),
                (PLAYER_WIDTH, PLAYER_HEIGHT)
            )
            self.walk1_image = pygame.transform.scale(
                pygame.image.load("assets/walk1.png").convert_alpha(),
                (PLAYER_WIDTH, PLAYER_HEIGHT)
            )
            self.jump_image = pygame.transform.scale(
                pygame.image.load("assets/jump.png").convert_alpha(),
                (PLAYER_WIDTH, PLAYER_HEIGHT)
            )
            self.shooting_image = pygame.transform.scale(
                pygame.image.load("assets/blast (1).png").convert_alpha(),
                (PLAYER_WIDTH, PLAYER_HEIGHT)
            )
            # Fallback: use blast image as all-purpose sprite
            self.image = self.idle_image
        except Exception as e:
            # Fallback to drawn sprite if images not found
            print(f"Warning: Could not load player images ({e}). Using fallback sprite.")
            self.image = pygame.Surface((50, 75), pygame.SRCALPHA)
            if USE_CYBERPUNK_THEME:
                pygame.draw.rect(self.image, NEON_CYAN, (13, 12, 24, 51))
                pygame.draw.rect(self.image, NEON_MAGENTA, (10, 10, 30, 55), 2)
                pygame.draw.line(self.image, NEON_PURPLE, (7, 25), (43, 25), 1)
                pygame.draw.line(self.image, NEON_PURPLE, (7, 50), (43, 50), 1)
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
        self.last_bullet_time = 0  # Cooldown for bullet firing
        self.bullet_cooldown = 15  # Frames between bullet shots (0.25 seconds at 60 FPS)
        # Animation state variables
        self.shooting_anim_time = 0  # Current frame of shooting animation
        self.shooting_anim_duration = 8  # Total frames for shooting animation
        self.walking_frame = 0  # Current frame of walk cycle (0 or 1)
        self.walk_anim_counter = 0  # Counter for walk animation timing
        self.walk_frame_duration = 10  # Frames per step (0.167 seconds at 60 FPS)
    
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
        self.shooting_anim_time = self.shooting_anim_duration  # Trigger shooting animation
        # Fire from the center of the player
        direction = 1 if self.facing_right else -1
        return Laser(self.rect.centerx, self.rect.centery, direction)
    
    def fire_bullet(self):
        """Return a new bullet in the direction the player is facing"""
        self.last_bullet_time = self.bullet_cooldown
        self.shooting_anim_time = self.shooting_anim_duration  # Trigger shooting animation
        # Fire from the center of the player
        direction = 1 if self.facing_right else -1
        return Bullet(self.rect.centerx, self.rect.centery, direction)
    
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
        
        # Decrement bullet cooldown
        if self.last_bullet_time > 0:
            self.last_bullet_time -= 1

        # Decrement shooting animation counter
        if self.shooting_anim_time > 0:
            self.shooting_anim_time -= 1
        
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
        
        # Update sprite image based on current state
        self.redraw()

    def redraw(self):
        """Redraw the player sprite, showing appropriate animation state"""
        # Determine which image to use based on player state
        if self.shooting_anim_time > 0:
            # Show shooting pose
            self.image = self.shooting_image
        elif self.is_jumping or self.vel_y != 0:
            # Show jumping pose when airborne
            self.image = self.jump_image
        else:
            # Show walking pose for both moving and idle (standing still)
            self.image = self.walk1_image
        
        # Flip image if facing left
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, left_bound, right_bound, can_shoot=False):
        super().__init__()
        # Enemy sprite dimensions
        ENEMY_WIDTH = 40
        ENEMY_HEIGHT = 40
        
        # Load enemy sprite images from assets
        try:
            self.left_image = pygame.transform.scale(
                pygame.image.load("assets/left.png").convert_alpha(),
                (ENEMY_WIDTH, ENEMY_HEIGHT)
            )
            self.right_image = pygame.transform.scale(
                pygame.image.load("assets/right.png").convert_alpha(),
                (ENEMY_WIDTH, ENEMY_HEIGHT)
            )
            # Use right as default pose
            self.image = self.right_image
        except Exception as e:
            # Fallback to drawn sprite if images not found
            print(f"Warning: Could not load enemy images ({e}). Using fallback sprite.")
            # Create fallback images
            self.left_image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT), pygame.SRCALPHA)
            self.right_image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT), pygame.SRCALPHA)
            if USE_CYBERPUNK_THEME:
                # Cyberpunk enemy: neon magenta with purple glow
                pygame.draw.circle(self.left_image, NEON_MAGENTA, (20, 20), 15)
                pygame.draw.circle(self.left_image, NEON_PURPLE, (20, 20), 17, 2)
                pygame.draw.line(self.left_image, NEON_CYAN, (10, 20), (30, 20), 2)
                
                pygame.draw.circle(self.right_image, NEON_MAGENTA, (20, 20), 15)
                pygame.draw.circle(self.right_image, NEON_PURPLE, (20, 20), 17, 2)
                pygame.draw.line(self.right_image, NEON_CYAN, (10, 20), (30, 20), 2)
            else:
                self.left_image.fill(GREEN)
                self.right_image.fill(GREEN)
            self.image = self.right_image
        
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
    
    def update_sprite(self):
        """Update sprite image based on movement direction"""
        if self.vel_x > 0:
            # Moving right - use right-facing image
            self.image = self.right_image
        else:
            # Moving left - use left-facing image
            self.image = self.left_image
    
    def update(self):
        self.rect.x += self.vel_x
        if self.rect.left <= self.left_bound or self.rect.right >= self.right_bound:
            self.vel_x *= -1
        
        # Update sprite image based on direction
        self.update_sprite()
        
        # Decrement shoot cooldown
        if self.last_shoot_time > 0:
            self.last_shoot_time -= 1


class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, player=None):
        super().__init__()
        # Boss sprite dimensions
        BOSS_WIDTH = 80
        BOSS_HEIGHT = 80
        
        # Load boss sprite images from assets
        self.images_loaded = False
        try:
            self.left_image = pygame.transform.scale(
                pygame.image.load("assets/boss_left.png").convert_alpha(),
                (BOSS_WIDTH, BOSS_HEIGHT)
            )
            self.right_image = pygame.transform.scale(
                pygame.image.load("assets/boss_right.png").convert_alpha(),
                (BOSS_WIDTH, BOSS_HEIGHT)
            )
            # Use right as default pose
            self.image = self.right_image
            self.images_loaded = True
        except Exception as e:
            # Fallback to drawn sprite if images not found
            print(f"Warning: Could not load boss images ({e}). Using fallback sprite.")
            self.left_image = pygame.Surface((BOSS_WIDTH, BOSS_HEIGHT), pygame.SRCALPHA)
            self.right_image = pygame.Surface((BOSS_WIDTH, BOSS_HEIGHT), pygame.SRCALPHA)
            if USE_CYBERPUNK_THEME:
                # Cyberpunk boss: massive neon pink square with intense glow
                # Main body - neon pink
                pygame.draw.rect(self.left_image, NEON_PINK, (10, 10, 60, 60))
                pygame.draw.rect(self.right_image, NEON_PINK, (10, 10, 60, 60))
                # Multiple glow borders for intense effect
                pygame.draw.rect(self.left_image, NEON_MAGENTA, (10, 10, 60, 60), 3)
                pygame.draw.rect(self.right_image, NEON_MAGENTA, (10, 10, 60, 60), 3)
                pygame.draw.rect(self.left_image, NEON_PURPLE, (5, 5, 70, 70), 2)
                pygame.draw.rect(self.right_image, NEON_PURPLE, (5, 5, 70, 70), 2)
                # Danger indicator X
                pygame.draw.line(self.left_image, NEON_CYAN, (20, 20), (60, 60), 2)
                pygame.draw.line(self.left_image, NEON_CYAN, (60, 20), (20, 60), 2)
                pygame.draw.line(self.right_image, NEON_CYAN, (20, 20), (60, 60), 2)
                pygame.draw.line(self.right_image, NEON_CYAN, (60, 20), (20, 60), 2)
            else:
                self.left_image.fill(PURPLE)
                self.right_image.fill(PURPLE)
            self.image = self.right_image
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x = 2  # Faster movement (was 1)
        self.vel_y = 0
        self.left_bound = x - 300  # Wider patrol range
        self.right_bound = x + 300
        self.health = 15  # MUCH harder: 15 hits to defeat (was 5)
        self.last_laser_time = 0
        self.last_bullet_time = 0
        self.laser_cooldown = 30  # Fires laser every 0.5 seconds (was 60)
        self.bullet_cooldown = 40  # Fires bullets every ~0.67 seconds (NEW)
        self.hit_flash_time = 0  # Frames to flash red after being hit
        self.hit_flash_duration = 10  # Duration of red flash (10 frames)
        self.player = player  # Reference to player for tracking laser
        self.tracker_laser = None  # Will hold the tracking laser
        self.attack_pattern = 0  # Attack pattern counter
        self.game = None  # Reference to game for adding bullets
    
    def take_damage(self):
        """Called when hit by player laser"""
        self.health -= 1
        self.hit_flash_time = self.hit_flash_duration  # Trigger red flash
        return self.health <= 0  # Return True if boss is defeated
    
    def shoot_laser(self):
        """Fire the tracking laser that was locked onto the player"""
        self.last_laser_time = self.laser_cooldown
        if self.tracker_laser and not self.tracker_laser.is_fired:
            self.tracker_laser.fire()
            return self.tracker_laser
        return None
    
    def shoot_bullets(self):
        """Fire bullets at the player from the boss - NEW ATTACK TYPE"""
        self.last_bullet_time = self.bullet_cooldown
        bullets = []
        
        # Calculate direction to player
        if self.player:
            dx = self.player.rect.centerx - self.rect.centerx
            dy = self.player.rect.centery - self.rect.centery
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 0:
                # Normalize
                dx /= dist
                dy /= dist
                
                # Fire multiple bullets in a spread pattern for more challenge
                for angle_offset in [-0.3, 0, 0.3]:  # 3 bullets in spread
                    # Rotate direction by angle_offset
                    new_dx = dx * math.cos(angle_offset) - dy * math.sin(angle_offset)
                    new_dy = dx * math.sin(angle_offset) + dy * math.cos(angle_offset)
                    
                    bullet = BossBullet(
                        self.rect.centerx,
                        self.rect.centery,
                        new_dx,
                        new_dy
                    )
                    bullets.append(bullet)
        
        return bullets
    
    def update(self):
        # Faster patrol movement
        self.rect.x += self.vel_x
        if self.rect.left <= self.left_bound or self.rect.right >= self.right_bound:
            self.vel_x *= -1
        
        # Update sprite image based on direction (using loaded PNGs)
        if self.vel_x > 0:
            # Moving right - use right-facing image
            self.image = self.right_image
        else:
            # Moving left - use left-facing image
            self.image = self.left_image
        
        # Update or create tracking laser
        if self.player:
            if not self.tracker_laser or self.tracker_laser.is_fired:
                # Create new tracking laser if none exists or previous one was fired
                self.tracker_laser = TrackerLaser(self, self.player)
        
        # Decrement shoot cooldowns
        if self.last_laser_time > 0:
            self.last_laser_time -= 1
        if self.last_bullet_time > 0:
            self.last_bullet_time -= 1
        
        # Decrement hit flash time
        if self.hit_flash_time > 0:
            self.hit_flash_time -= 1
        
        # Apply red flash overlay if hit (only if images are loaded)
        if self.images_loaded and self.hit_flash_time > 0:
            # Create a red-tinted version of the sprite
            flashed_image = self.image.copy()
            red_overlay = pygame.Surface((80, 80), pygame.SRCALPHA)
            red_overlay.fill((255, 0, 0, 100))  # Red with some transparency
            flashed_image.blit(red_overlay, (0, 0))
            self.image = flashed_image

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

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction=1):
        super().__init__()
        self.speed = 15  # Bullet speed (faster than laser)
        self.direction = direction  # 1 for right, -1 for left
        
        # Create bullet visual (small round projectile)
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        if USE_CYBERPUNK_THEME:
            # Neon yellow bullet with glow
            pygame.draw.circle(self.image, NEON_GREEN, (4, 4), 4)
            pygame.draw.circle(self.image, NEON_CYAN, (4, 4), 4, 1)  # Glow border
        else:
            # Classic yellow bullet
            pygame.draw.circle(self.image, YELLOW, (4, 4), 4)
            pygame.draw.circle(self.image, BLACK, (4, 4), 4, 1)  # Border
        
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self):
        # Move bullet in the direction it was fired
        self.rect.x += self.speed * self.direction
        
        # Remove bullet if it goes off screen or past level end
        if self.rect.right < 0 or self.rect.left > 7000:
            self.kill()

class TrackerLaser(pygame.sprite.Sprite):
    """A tracking beam that locks onto the player until the boss fires"""
    def __init__(self, boss, player):
        super().__init__()
        self.boss = boss
        self.player = player
        self.is_fired = False
        self.fired_direction_x = 0
        self.fired_direction_y = 0
        self.speed = 6  # Speed after firing
        self.fired_laser_rect = None  # The actual fired laser rect
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
    
    def calculate_direction(self):
        """Calculate direction vector to player"""
        dx = self.player.rect.centerx - self.boss.rect.centerx
        dy = self.player.rect.centery - self.boss.rect.centery
        
        # Normalize direction
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            return dx / dist, dy / dist
        return 0, 0
    
    def fire(self):
        """Fire the laser in the direction it was tracking"""
        self.is_fired = True
        self.fired_direction_x, self.fired_direction_y = self.calculate_direction()
        self.fired_laser_rect = pygame.Rect(
            self.boss.rect.centerx,
            self.boss.rect.centery,
            25, 8
        )
    
    def update(self):
        if self.is_fired:
            # Move laser after firing
            if self.fired_laser_rect:
                self.fired_laser_rect.x += self.speed * self.fired_direction_x
                self.fired_laser_rect.y += self.speed * self.fired_direction_y
                
                # Remove laser if it goes off screen
                if self.fired_laser_rect.right < 0 or self.fired_laser_rect.left > SCREEN_WIDTH + 500 or \
                   self.fired_laser_rect.bottom < 0 or self.fired_laser_rect.top > SCREEN_HEIGHT + 500:
                    self.kill()
        else:
            # Tracking mode: update position to boss center
            self.rect.center = self.boss.rect.center
    
    def draw(self, surface, camera_x):
        """Draw the tracking beam and/or fired laser"""
        if self.is_fired and self.fired_laser_rect:
            # Draw fired laser as a neon pink bolt
            pygame.draw.rect(surface, NEON_PINK, 
                           (self.fired_laser_rect.x - camera_x, self.fired_laser_rect.y, 
                            self.fired_laser_rect.width, self.fired_laser_rect.height))
            pygame.draw.rect(surface, NEON_MAGENTA, 
                           (self.fired_laser_rect.x - camera_x, self.fired_laser_rect.y, 
                            self.fired_laser_rect.width, self.fired_laser_rect.height), 1)
        else:
            # Draw tracking beam as a neon cyan line from boss to player
            if USE_CYBERPUNK_THEME:
                pygame.draw.line(surface, NEON_CYAN, 
                               (self.boss.rect.centerx - camera_x, self.boss.rect.centery),
                               (self.player.rect.centerx - camera_x, self.player.rect.centery), 2)
                # Add glow effect with thicker purple line underneath
                pygame.draw.line(surface, NEON_PURPLE, 
                               (self.boss.rect.centerx - camera_x, self.boss.rect.centery),
                               (self.player.rect.centerx - camera_x, self.player.rect.centery), 1)

class BossLaser(pygame.sprite.Sprite):
    def __init__(self, x, y, direction=1):
        super().__init__()
        self.speed = 7  # Boss laser speed (slower than regular enemy laser)
        self.direction = direction  # 1 for right, -1 for left
        
        # Create boss laser visual (massive neon pink laser)
        self.image = pygame.Surface((25, 8), pygame.SRCALPHA)
        if USE_CYBERPUNK_THEME:
            # Massive neon pink laser beam with intense glow
            pygame.draw.rect(self.image, NEON_PINK, (0, 0, 25, 8))  # Pink color
            pygame.draw.rect(self.image, NEON_MAGENTA, (0, 0, 25, 8), 2)  # Magenta glow border
            pygame.draw.rect(self.image, (255, 100, 200), (0, 0, 25, 8), 1)  # Extra glow
        else:
            self.image.fill((255, 100, 100))  # Light red
        
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self):
        # Move laser in the direction it was fired
        self.rect.x += self.speed * self.direction
        
        # Remove laser if it goes off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH + 500:
            self.kill()


class BossBullet(pygame.sprite.Sprite):
    """Boss bullet projectile - faster and more aggressive than regular bullets"""
    def __init__(self, x, y, dx, dy):
        super().__init__()
        self.speed = 12  # Boss bullet speed (faster than player bullets)
        self.dx = dx  # Direction x (normalized)
        self.dy = dy  # Direction y (normalized)
        
        # Create boss bullet visual (large neon red bullet)
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        if USE_CYBERPUNK_THEME:
            # Large neon red bullet with glow
            pygame.draw.circle(self.image, (255, 50, 50), (6, 6), 6)  # Red core
            pygame.draw.circle(self.image, NEON_MAGENTA, (6, 6), 6, 2)  # Magenta glow
            pygame.draw.circle(self.image, (255, 100, 100), (6, 6), 5, 1)  # Extra glow
        else:
            # Classic red bullet
            pygame.draw.circle(self.image, (200, 0, 0), (6, 6), 6)
            pygame.draw.circle(self.image, BLACK, (6, 6), 6, 1)  # Border
        
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self):
        # Move bullet in the calculated direction
        self.rect.x += self.speed * self.dx
        self.rect.y += self.speed * self.dy
        
        # Remove bullet if it goes off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH + 500 or \
           self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT + 500:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size=40, duration=15):
        super().__init__()
        self.x = x
        self.y = y
        self.size = size
        self.duration = duration
        self.age = 0
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.update()
    
    def update(self):
        self.age += 1
        
        # Calculate fade effect (shrink and fade out)
        progress = self.age / self.duration
        current_size = int(self.size * (1 - progress))
        alpha = int(255 * (1 - progress))
        
        # Recreate surface for this frame
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        if USE_CYBERPUNK_THEME:
            # Cyberpunk explosion: bright neon with expanding rings
            center = self.size // 2
            
            # Outer ring (yellow/orange)
            if current_size > 0:
                pygame.draw.circle(self.image, (*NEON_MAGENTA[:3], alpha), (center, center), current_size)
            
            # Middle ring (cyan)
            if current_size > 5:
                pygame.draw.circle(self.image, (*NEON_CYAN[:3], alpha), (center, center), max(1, current_size - 5))
            
            # Inner bright core (yellow)
            if current_size > 10:
                pygame.draw.circle(self.image, (255, 255, 0, alpha), (center, center), max(1, current_size - 10))
            
            # Spark rays
            if current_size > 3:
                spark_radius = current_size + 5
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    end_x = center + spark_radius * math.cos(rad)
                    end_y = center + spark_radius * math.sin(rad)
                    pygame.draw.line(self.image, (NEON_CYAN[0], NEON_CYAN[1], NEON_CYAN[2], alpha),
                                   (center, center), (int(end_x), int(end_y)), 2)
        else:
            # Classic explosion: red/orange expanding circle
            center = self.size // 2
            if current_size > 0:
                pygame.draw.circle(self.image, (255, 100, 0), (center, center), current_size)
            if current_size > 5:
                pygame.draw.circle(self.image, (255, 200, 0), (center, center), max(1, current_size - 5))
        
        # Remove when animation is done
        if self.age >= self.duration:
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
        pygame.display.set_caption("Alien vs Robots")
        self.clock = pygame.time.Clock()
        self.running = True
        self.score = 0
        self.level = 1
        self.lives = 3
        self.game_over = False
        self.victory = False  # Track if player won vs lost
        self.title_screen = True  # Start on title screen
        
        # Sound Manager
        self.sound_manager = SoundManager()
        
        # Music playback state
        self.music_playing = False
        self.current_music = None
        
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
        
        # Restart button (created in draw method, initialized here)
        self.restart_button_rect = pygame.Rect(0, 0, 0, 0)
        
        # Start button (created in draw method, initialized here)
        self.start_button_rect = pygame.Rect(0, 0, 0, 0)
        
        # Sprite groups
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()
        self.lasers = pygame.sprite.Group()  # NEW: Laser group
        self.bullets = pygame.sprite.Group()  # NEW: Bullet group
        self.enemy_lasers = pygame.sprite.Group()  # NEW: Enemy laser group
        self.bosses = pygame.sprite.Group()  # NEW: Boss group
        self.explosions = pygame.sprite.Group()  # NEW: Explosion effects
        self.all_sprites = pygame.sprite.Group()
        
        # Background space elements
        self.stars = []
        self.asteroids = []
        self.distant_explosions = []
        self.alien_ships = []
        self.robot_warships = []
        self.initialize_background()
        
        # Create level
        self.create_level()
        
        # Create player
        self.player = Player(100, 100)
        self.all_sprites.add(self.player)
    
    def initialize_background(self):
        """Initialize background space elements"""
        # Create stars scattered throughout
        for _ in range(80):
            x = random.randint(0, 7000)
            y = random.randint(0, SCREEN_HEIGHT)
            brightness = random.uniform(0.3, 1.0)
            self.stars.append(Star(x, y, brightness))
        
        # Create asteroids at various depths
        for _ in range(30):
            x = random.randint(0, 7000)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            depth = random.uniform(0.3, 0.9)
            self.asteroids.append(Asteroid(x, y, depth))
        
        # Create distant alien ships
        for _ in range(5):
            x = random.randint(0, 7000)
            y = random.randint(30, 150)
            depth = random.uniform(0.4, 0.8)
            self.alien_ships.append(AlienShip(x, y, depth))
        
        # Create distant robot warships
        for _ in range(5):
            x = random.randint(0, 7000)
            y = random.randint(SCREEN_HEIGHT - 150, SCREEN_HEIGHT - 30)
            depth = random.uniform(0.4, 0.8)
            self.robot_warships.append(RobotWarship(x, y, depth))
    
    def create_level(self):
        if self.level == 1:
            self.create_level_1()
        elif self.level == 2:
            self.create_level_2()
        elif self.level == 3:
            self.create_level_3()
        elif self.level == 4:
            self.create_level_boss()
    
    def create_level_1(self):
        # Ground - extended length (not collidable - only platforms can be stood on)
        ground = Platform(0, SCREEN_HEIGHT - 40, 4000, 40)
        # Don't add ground to collision platforms
        self.all_sprites.add(ground)  # Still visible but not collidable
        
        # Extended platforms
        platforms_data = [
            (50, 500, 150, 20),    # Starting platform near spawn point
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
            (275, 415, 200, 350, True),    # On platform at y=450
            (575, 365, 500, 650, True),    # On platform at y=400
            (375, 265, 300, 450, True),    # On platform at y=300
            (675, 215, 600, 750, True),    # On platform at y=250
            (975, 315, 900, 1050, True),   # On platform at y=350
            (1275, 265, 1200, 1350, True), # On platform at y=300
            (1575, 215, 1500, 1650, True), # On platform at y=250
            (1875, 315, 1800, 1950, True), # On platform at y=350
            (2175, 265, 2100, 2250, True), # On platform at y=300
            (2475, 215, 2400, 2550, True), # On platform at y=250
            (2775, 315, 2700, 2850, True), # On platform at y=350
            (3075, 265, 3000, 3150, True), # On platform at y=300
            (3375, 215, 3300, 3450, True), # On platform at y=250
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
        # Ground - even longer (not collidable - only platforms can be stood on)
        ground = Platform(0, SCREEN_HEIGHT - 40, 5000, 40)
        # Don't add ground to collision platforms
        self.all_sprites.add(ground)  # Still visible but not collidable
        
        # More challenging platforms with smaller gaps
        platforms_data = [
            (50, 500, 100, 20),    # Starting platform near spawn point
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
            (400, 365, 350, 450, True),    # On platform at y=400
            (550, 315, 500, 600, True),    # On platform at y=350, can shoot
            (700, 265, 650, 750, True),    # On platform at y=300
            (850, 365, 800, 900, True),    # On platform at y=400, can shoot
            (1000, 315, 950, 1050, True),  # On platform at y=350
            (1150, 265, 1100, 1200, True), # On platform at y=300, can shoot
            (1300, 345, 1250, 1350, True), # On platform at y=380
            (1450, 285, 1400, 1500, True), # On platform at y=320, can shoot
            (1600, 245, 1550, 1650, True), # On platform at y=280
            (1750, 325, 1700, 1800, True), # On platform at y=360, can shoot
            (1900, 265, 1850, 1950, True), # On platform at y=300
            (2050, 215, 2000, 2100, True), # On platform at y=250, can shoot
            (2200, 305, 2150, 2250, True), # On platform at y=340
            (2350, 255, 2300, 2400, True), # On platform at y=290, can shoot
            (2500, 315, 2450, 2550, True), # On platform at y=350
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
        """Level 3 - challenging platforming leading to boss level"""
        # Ground (not collidable - only platforms can be stood on)
        ground = Platform(0, SCREEN_HEIGHT - 40, 6000, 40)
        # Don't add ground to collision platforms
        self.all_sprites.add(ground)  # Still visible but not collidable
        
        # Challenging platforms
        platforms_data = [
            (50, 500, 150, 20),    # Starting platform near spawn point
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
            (4200, 150, 150, 20),  # Challenging access to boss entrance
            (4500, 300, 150, 20),
            (4800, 200, 150, 20),
            (5100, 350, 150, 20),
            (5400, 300, 150, 20),
        ]
        
        for x, y, w, h in platforms_data:
            platform = Platform(x, y, w, h)
            self.platforms.add(platform)
            self.all_sprites.add(platform)
        
        # Enemies throughout the level - SIGNIFICANTLY INCREASED for more challenge
        enemies_data = [
            # First section (200-600)
            (275, 415, 200, 350, True),    # On platform at y=450
            (325, 415, 250, 400, False),   # Additional enemy nearby
            (525, 315, 450, 600, True),    # On platform at y=350
            (575, 315, 480, 630, False),   # Additional enemy
            
            # Second section (600-1100)
            (775, 215, 700, 850, True),    # On platform at y=250
            (825, 215, 730, 880, False),   # Additional enemy
            (1025, 315, 950, 1100, True),  # On platform at y=350
            (975, 315, 920, 1050, False),  # Additional enemy
            
            # Third section (1100-1700)
            (1275, 165, 1200, 1350, True), # On platform at y=200
            (1225, 165, 1150, 1300, False),# Additional enemy
            (1575, 315, 1500, 1650, True), # On platform at y=350
            (1625, 315, 1540, 1700, False),# Additional enemy
            
            # Fourth section (1700-2300)
            (1875, 215, 1800, 1950, True), # On platform at y=250
            (1825, 215, 1750, 1900, False),# Additional enemy
            (2175, 365, 2100, 2250, True), # On platform at y=400
            (2225, 365, 2150, 2300, False),# Additional enemy
            
            # Fifth section (2300-2900)
            (2475, 265, 2400, 2550, True), # On platform at y=300
            (2525, 265, 2450, 2600, False),# Additional enemy
            (2775, 165, 2700, 2850, True), # On platform at y=200
            (2725, 165, 2650, 2800, False),# Additional enemy
            
            # Sixth section (3000-3900) - NEW
            (3075, 315, 3000, 3150, True), # On platform at y=350
            (3125, 315, 3050, 3200, False),# Additional enemy
            (3375, 215, 3300, 3450, True), # On platform at y=250
            (3425, 215, 3350, 3500, False),# Additional enemy
            
            # Seventh section (3900-4800) - NEW
            (3975, 365, 3900, 4050, True), # On platform at y=400
            (4025, 365, 3950, 4100, False),# Additional enemy
            (4275, 115, 4200, 4350, True), # On platform at y=150 (challenging)
            (4325, 115, 4250, 4400, False),# Additional enemy
            
            # Final section (4800-5400) - NEW - INTENSE
            (4575, 265, 4500, 4650, True), # On platform at y=300
            (4625, 265, 4550, 4700, False),# Additional enemy
            (4875, 165, 4800, 4950, True), # On platform at y=200
            (4925, 165, 4850, 5000, False),# Additional enemy
            (5175, 315, 5100, 5250, True), # On platform at y=350
            (5225, 315, 5150, 5300, False),# Additional enemy
        ]
        
        for x, y, left, right, can_shoot in enemies_data:
            enemy = Enemy(x, y, left, right, can_shoot)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
        
        # Collectibles
        collectibles_data = [
            (200, 430), (450, 330), (700, 230), (950, 330),
            (1200, 180), (1500, 330), (1800, 230), (2100, 380),
            (2400, 280), (2700, 180), (3000, 330), (3300, 230),
            (3600, 380), (3900, 280), (4200, 130), (4500, 280),
            (4800, 180), (5100, 330), (5400, 280)
        ]
        for cx, cy in collectibles_data:
            collectible = Collectible(cx, cy)
            self.collectibles.add(collectible)
            self.all_sprites.add(collectible)
    
    def create_level_boss(self):
        """Boss Arena - dedicated boss battle level"""
        # Ground (not collidable - only platforms can be stood on)
        ground = Platform(0, SCREEN_HEIGHT - 40, 2000, 40)
        # Don't add ground to collision platforms
        self.all_sprites.add(ground)  # Still visible but not collidable
        
        # Boss arena platforms - designed for tactical boss battle
        platforms_data = [
            (50, 500, 150, 20),     # Starting platform
            (250, 450, 150, 20),    # Left side lower
            (500, 350, 150, 20),    # Left-center middle
            (750, 250, 150, 20),    # Left-center high
            (1000, 350, 150, 20),   # Center
            (1250, 450, 150, 20),   # Center lower
            (1500, 350, 150, 20),   # Right-center middle
            (1750, 250, 150, 20),   # Right side high
            (1350, 500, 400, 20),   # Wide arena platform for boss
        ]
        
        for x, y, w, h in platforms_data:
            platform = Platform(x, y, w, h)
            self.platforms.add(platform)
            self.all_sprites.add(platform)
        
        # No regular enemies in boss arena - just the boss
        # Boss at the center of the arena
        boss = Boss(1550, 370, player=self.player)  # 370 = 500 - 130 (arena platform_y - safe distance)
        self.bosses.add(boss)
        self.all_sprites.add(boss)
        
        # Some collectibles scattered around the arena for combat
        collectibles_data = [
            (250, 430), (500, 330), (750, 230),
            (1000, 330), (1250, 430), (1500, 330), (1750, 230)
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
            elif event.type == pygame.MOUSEBUTTONDOWN and self.title_screen:
                # Check if start button was clicked
                mouse_pos = pygame.mouse.get_pos()
                if self.start_button_rect.collidepoint(mouse_pos):
                    self.start_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and self.game_over:
                # Check if restart button was clicked
                mouse_pos = pygame.mouse.get_pos()
                if self.restart_button_rect.collidepoint(mouse_pos):
                    self.restart_game()
            elif event.type == pygame.KEYDOWN:
                if self.title_screen and event.key == pygame.K_s:
                    # Press S to start game
                    self.start_game()
                elif self.game_over and event.key == pygame.K_r:
                    # Press R to restart
                    self.restart_game()
    
    def start_game(self):
        """Start the game from title screen"""
        self.title_screen = False
        self.score = 0
        self.level = 1
        self.lives = 3
        self.game_over = False
        self.victory = False
        self.camera_x = 0
        
        # Stop menu music and play battle music
        pygame.mixer.music.stop()
        self.play_level_music()
        
        # Clear all sprite groups
        self.platforms.empty()
        self.enemies.empty()
        self.collectibles.empty()
        self.lasers.empty()
        self.bullets.empty()
        self.enemy_lasers.empty()
        self.bosses.empty()
        self.all_sprites.empty()
        
        # Create player
        self.player = Player(100, 100)
        self.all_sprites.add(self.player)
        
        # Create level
        self.create_level()
    
    def play_level_music(self):
        """Play appropriate music based on current level"""
        try:
            if self.level == 4:
                # Boss level gets epic boss music
                if self.current_music != "boss":
                    pygame.mixer.music.load('assets/boss_music.wav')
                    pygame.mixer.music.play(-1)  # Loop indefinitely
                    self.current_music = "boss"
            else:
                # Regular levels get battle music
                if self.current_music != "battle":
                    pygame.mixer.music.load('assets/battle_music.wav')
                    pygame.mixer.music.play(-1)  # Loop indefinitely
                    self.current_music = "battle"
        except pygame.error as e:
            print(f"Could not load music: {e}")
        except Exception as e:
            print(f"Music error: {e}")
    
    def restart_game(self):
        """Restart the current level (keep same level, reset lives and enemies)"""
        # Clear all sprites
        self.platforms.empty()
        self.enemies.empty()
        self.collectibles.empty()
        self.lasers.empty()
        self.bullets.empty()
        self.enemy_lasers.empty()
        self.bosses.empty()
        self.all_sprites.empty()
        
        # Reset game state (keep current level, reset score and lives)
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.victory = False
        self.camera_x = 0
        
        # Create player
        self.player = Player(100, 100)
        self.all_sprites.add(self.player)
        
        # Recreate the same level
        self.create_level()
    
    def load_next_level(self):
        # Clear all sprites
        self.platforms.empty()
        self.enemies.empty()
        self.collectibles.empty()
        self.lasers.empty()  # Clear lasers
        self.bullets.empty()  # Clear bullets
        self.enemy_lasers.empty()  # Clear enemy lasers
        self.bosses.empty()  # Clear bosses
        self.all_sprites.empty()
        
        # Move to next level
        self.level += 1
        self.camera_x = 0
        self.player.rect.topleft = (100, 100)
        self.player.vel_y = 0
        self.player.vel_x = 0
        
        # Play music for new level
        self.play_level_music()
        
        # Create new level
        self.create_level()
        self.all_sprites.add(self.player)
    
    def update(self):
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        self.player.handle_input(keys, mouse_buttons)
        
        # Update background elements
        for star in self.stars:
            star.update()
        for asteroid in self.asteroids:
            asteroid.update()
        for alien_ship in self.alien_ships:
            alien_ship.update()
        for robot_ship in self.robot_warships:
            robot_ship.update()
        
        # Randomly spawn distant explosions
        if random.random() < 0.01:  # 1% chance per frame
            explosion = DistantExplosion(random.randint(0, 7000), random.randint(30, 200))
            self.distant_explosions.append(explosion)
        
        # Update and clean up distant explosions
        for explosion in self.distant_explosions[:]:
            explosion.update()
            if not explosion.is_alive():
                self.distant_explosions.remove(explosion)
        
        # Handle laser firing with left mouse click OR Ctrl key
        if (mouse_buttons[0] or keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) and self.player.last_laser_time <= 0:
            new_laser = self.player.fire_laser()
            self.lasers.add(new_laser)
            self.all_sprites.add(new_laser)
            self.sound_manager.play_sound('laser')
        
        # Handle bullet firing with right mouse click OR E key
        if (mouse_buttons[2] or keys[pygame.K_e]) and self.player.last_bullet_time <= 0:  # Right mouse button (index 2) or E key
            new_bullet = self.player.fire_bullet()
            self.bullets.add(new_bullet)
            self.all_sprites.add(new_bullet)
            self.sound_manager.play_sound('bullet')
        
        self.player.update(self.platforms)
        self.player.redraw()  # Update shooting animation
        self.enemies.update()
        self.explosions.update()  # Update explosion animations
        self.bullets.update()  # Update bullets
        
        # Handle enemy shooting
        for enemy in self.enemies:
            if enemy.can_shoot and enemy.last_shoot_time <= 0:
                # Randomly decide if enemy shoots this frame (~2% chance per frame for more frequent fire)
                if random.random() < 0.02:
                    new_enemy_laser = enemy.shoot()
                    self.enemy_lasers.add(new_enemy_laser)
                    self.all_sprites.add(new_enemy_laser)
        
        # Handle boss shooting (more aggressive with multiple attack types)
        for boss in self.bosses:
            # Update tracking laser in Game loop
            if boss.tracker_laser:
                boss.tracker_laser.update()
            
            # Boss shoots lasers frequently
            if boss.last_laser_time <= 0:
                # Boss shoots laser more frequently (~5% chance per frame, was 3%)
                if random.random() < 0.05:
                    new_boss_laser = boss.shoot_laser()
                    # Don't add TrackerLaser to sprite groups - it uses custom drawing
            
            # Boss also shoots bullets at the player (NEW - MUCH HARDER!)
            if boss.last_bullet_time <= 0:
                # Boss shoots bullets frequently (~4% chance per frame)
                if random.random() < 0.04:
                    new_bullets = boss.shoot_bullets()
                    for bullet in new_bullets:
                        self.enemy_lasers.add(bullet)  # Add to enemy lasers group for collision
                        self.all_sprites.add(bullet)
        
        self.collectibles.update()  # Update collectible animations
        self.lasers.update()  # Update lasers
        self.enemy_lasers.update()  # Update enemy lasers
        self.bosses.update()  # Update bosses
        self.update_camera()
        self.frame_count += 1  # Increment frame counter for effects
        
        # Check if player reached end of level (or defeated boss)
        if self.level == 3:
            # Level 3: Check if player reached the end
            if self.player.rect.x > 5400 - 50:
                self.load_next_level()
        elif self.level == 4:
            # Level 4 (Boss): Check if boss is defeated
            if len(self.bosses) == 0:
                # Boss defeated - game complete!
                self.victory = True
                self.game_over = True  # Show victory screen
                self.sound_manager.play_sound('victory')
        else:
            # Levels 1-2: Check if player reached end
            level_end_x = 3600 if self.level == 1 else 4000 if self.level == 2 else 5400
            if self.player.rect.x > level_end_x - 50:
                self.load_next_level()
        
        # Collect items
        collected = pygame.sprite.spritecollide(self.player, self.collectibles, True)
        for _ in collected:
            self.sound_manager.play_sound('collect')
        self.score += len(collected) * 10
        
        # Laser collisions with enemies
        for laser in self.lasers:
            enemies_hit = pygame.sprite.spritecollide(laser, self.enemies, False)
            for enemy in enemies_hit:
                # Create explosion at enemy position
                explosion = Explosion(enemy.rect.centerx, enemy.rect.centery, size=50, duration=15)
                self.explosions.add(explosion)
                enemy.kill()
                laser.kill()
                self.score += 50  # Score for laser kill
                self.sound_manager.play_sound('enemy_hit')
            
            # Laser collisions with boss
            bosses_hit = pygame.sprite.spritecollide(laser, self.bosses, False)
            for boss in bosses_hit:
                # Create explosion at boss hit location
                explosion = Explosion(boss.rect.centerx, boss.rect.centery, size=70, duration=20)
                self.explosions.add(explosion)
                laser.kill()
                if boss.take_damage():
                    # Boss defeated - larger explosion
                    big_explosion = Explosion(boss.rect.centerx, boss.rect.centery, size=100, duration=25)
                    self.explosions.add(big_explosion)
                    boss.kill()
                    self.score += 500  # Massive score for defeating boss
                    self.sound_manager.play_sound('boss_defeated')
                else:
                    self.score += 100  # Score for each hit on boss
                    self.sound_manager.play_sound('boss_hit')
        
        # Enemy laser collisions with player - damage
        enemy_lasers_hit = pygame.sprite.spritecollide(self.player, self.enemy_lasers, True)
        
        # Also check tracker laser collision with player
        for boss in self.bosses:
            if boss.tracker_laser and boss.tracker_laser.is_fired and boss.tracker_laser.fired_laser_rect:
                if self.player.rect.colliderect(boss.tracker_laser.fired_laser_rect):
                    enemy_lasers_hit.append(boss.tracker_laser)  # Treat as laser hit
                    boss.tracker_laser.kill()
        
        if enemy_lasers_hit:
            # Player hit by enemy laser - lose a life
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
                self.sound_manager.play_sound('game_over')
            else:
                self.player.rect.topleft = (100, 100)
                self.camera_x = 0
        
        # Bullet collisions with enemies
        for bullet in self.bullets:
            enemies_hit = pygame.sprite.spritecollide(bullet, self.enemies, False)
            for enemy in enemies_hit:
                # Create explosion at enemy position
                explosion = Explosion(enemy.rect.centerx, enemy.rect.centery, size=50, duration=15)
                self.explosions.add(explosion)
                enemy.kill()
                bullet.kill()
                self.score += 75  # Score for bullet kill (more than laser)
                self.sound_manager.play_sound('enemy_hit')
            
            # Bullet collisions with boss
            bosses_hit = pygame.sprite.spritecollide(bullet, self.bosses, False)
            for boss in bosses_hit:
                # Create explosion at boss hit location
                explosion = Explosion(boss.rect.centerx, boss.rect.centery, size=70, duration=20)
                self.explosions.add(explosion)
                bullet.kill()
                if boss.take_damage():
                    # Boss defeated - larger explosion
                    big_explosion = Explosion(boss.rect.centerx, boss.rect.centery, size=100, duration=25)
                    self.explosions.add(big_explosion)
                    boss.kill()
                    self.score += 500  # Massive score for defeating boss
                    self.sound_manager.play_sound('boss_defeated')
                else:
                    self.score += 150  # Score for each hit on boss with bullet (more than laser)
                    self.sound_manager.play_sound('boss_hit')
        
        # Enemy collision - kill by jumping on them or with lasers
        enemies_hit = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in enemies_hit:
            if self.player.vel_y > 0 and self.player.rect.bottom - self.player.vel_y <= enemy.rect.centery:
                # Player jumped on enemy from above
                # Create explosion at enemy position
                explosion = Explosion(enemy.rect.centerx, enemy.rect.centery, size=45, duration=15)
                self.explosions.add(explosion)
                enemy.kill()
                self.player.vel_y = -JUMP_STRENGTH
                self.score += 50
            else:
                # Player hit enemy from side or below - lose a life
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                else:
                    self.player.rect.topleft = (100, 100)
                    self.camera_x = 0
        
        # Boss collision - cannot be jumped on, touching boss resets player
        bosses_hit = pygame.sprite.spritecollide(self.player, self.bosses, False)
        if bosses_hit:
            # Player hit boss - lose a life
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self.player.rect.topleft = (100, 100)
                self.camera_x = 0
    
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
    
    def draw_title_screen(self):
        """Draw the title screen with game name, start button, and credits"""
        # Background
        if USE_CYBERPUNK_THEME:
            self.screen.fill(BG_DARK)
            self.draw_grid_background()
        else:
            self.screen.fill(WHITE)
        
        # Game title
        if USE_CYBERPUNK_THEME:
            title_text = self.font_large.render("ALIEN vs ROBOTS", True, NEON_CYAN)
            title_color = NEON_CYAN
            start_color = NEON_GREEN
            start_bg = (0, 50, 0)
            credits_color = NEON_MAGENTA
        else:
            title_text = self.font_large.render("ALIEN vs ROBOTS", True, BLUE)
            title_color = BLUE
            start_color = GREEN
            start_bg = (200, 200, 200)
            credits_color = (200, 0, 200)
        
        # Title position
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Start button
        start_text = self.font_medium.render("START", True, start_color)
        self.start_button_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.start_button_rect.inflate_ip(40, 20)  # Add padding
        
        pygame.draw.rect(self.screen, start_bg, self.start_button_rect)
        pygame.draw.rect(self.screen, start_color, self.start_button_rect, 2)  # Border
        self.screen.blit(start_text, start_text.get_rect(center=self.start_button_rect.center))
        
        # Instructions
        if USE_CYBERPUNK_THEME:
            instructions_color = NEON_BLUE
        else:
            instructions_color = BLUE
        
        instructions_text = self.font_small.render("Press S or Click to Start", True, instructions_color)
        instructions_rect = instructions_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(instructions_text, instructions_rect)
        
        # Credits
        credits_text = self.font_small.render("By Ethan Harp", True, credits_color)
        credits_rect = credits_text.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
        self.screen.blit(credits_text, credits_rect)
    
    def draw_victory_screen(self):
        """Draw the victory screen when boss is defeated"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Victory text
        if USE_CYBERPUNK_THEME:
            victory_text = self.font_large.render("VICTORY!", True, NEON_GREEN)
            completion_text = self.font_medium.render("YOU DEFEATED THE BOSS!", True, NEON_CYAN)
            final_score_text = self.font_medium.render(f"Final Score: {self.score}", True, NEON_CYAN)
            restart_text = self.font_medium.render("CONTINUE", True, NEON_GREEN)
            restart_color = NEON_GREEN
            restart_bg = (0, 50, 0)
        else:
            victory_text = self.font_large.render("VICTORY!", True, GREEN)
            completion_text = self.font_medium.render("YOU DEFEATED THE BOSS!", True, BLUE)
            final_score_text = self.font_medium.render(f"Final Score: {self.score}", True, BLACK)
            restart_text = self.font_medium.render("CONTINUE", True, GREEN)
            restart_color = GREEN
            restart_bg = (200, 200, 200)
        
        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        completion_rect = completion_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        
        # Continue button
        self.restart_button_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120))
        self.restart_button_rect.inflate_ip(40, 20)  # Add padding around button
        
        # Draw button background
        pygame.draw.rect(self.screen, restart_bg, self.restart_button_rect)
        pygame.draw.rect(self.screen, restart_color, self.restart_button_rect, 2)  # Button border
        
        # Draw text
        self.screen.blit(victory_text, victory_rect)
        self.screen.blit(completion_text, completion_rect)
        self.screen.blit(final_score_text, final_score_rect)
        self.screen.blit(restart_text, restart_text.get_rect(center=self.restart_button_rect.center))
    
    def draw_game_over_screen(self):
        """Draw the game over screen when player loses all lives"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        if USE_CYBERPUNK_THEME:
            game_over_text = self.font_large.render("GAME OVER", True, NEON_RED)
            final_score_text = self.font_medium.render(f"Final Score: {self.score}", True, NEON_CYAN)
            restart_text = self.font_medium.render("RESTART", True, NEON_GREEN)
            restart_color = NEON_GREEN
            restart_bg = (0, 50, 0)
        else:
            game_over_text = self.font_large.render("GAME OVER", True, RED)
            final_score_text = self.font_medium.render(f"Final Score: {self.score}", True, BLACK)
            restart_text = self.font_medium.render("RESTART", True, GREEN)
            restart_color = GREEN
            restart_bg = (200, 200, 200)
        
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        
        # Restart button
        self.restart_button_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 130))
        self.restart_button_rect.inflate_ip(40, 20)  # Add padding around button
        
        # Draw button background
        pygame.draw.rect(self.screen, restart_bg, self.restart_button_rect)
        pygame.draw.rect(self.screen, restart_color, self.restart_button_rect, 2)  # Button border
        
        # Draw text
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(final_score_text, final_score_rect)
        self.screen.blit(restart_text, restart_text.get_rect(center=self.restart_button_rect.center))
    
    def draw(self):
        # Draw title screen
        if self.title_screen:
            # Play title screen music (once)
            if self.current_music != "menu":
                try:
                    pygame.mixer.music.load('assets/menu_music.wav')
                    pygame.mixer.music.play(-1)  # Loop indefinitely
                    self.current_music = "menu"
                except:
                    pass  # Continue without music if file missing
            self.draw_title_screen()
            pygame.display.flip()
            return
        
        # Space background with deep colors
        self.screen.fill(DEEP_SPACE)
        
        # Draw background space elements
        # Draw distant explosions first (farthest back)
        for explosion in self.distant_explosions:
            explosion.draw(self.screen, self.camera_x)
        
        # Draw asteroids
        for asteroid in self.asteroids:
            asteroid.draw(self.screen, self.camera_x)
        
        # Draw distant alien ships
        for alien_ship in self.alien_ships:
            alien_ship.draw(self.screen, self.camera_x)
        
        # Draw distant robot warships
        for robot_ship in self.robot_warships:
            robot_ship.draw(self.screen, self.camera_x)
        
        # Draw stars (foreground)
        for star in self.stars:
            star.draw(self.screen, self.camera_x)
        
        # Draw grid if cyberpunk theme enabled
        if USE_CYBERPUNK_THEME:
            self.draw_grid_background()
        
        # Draw sprites with camera offset
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y))
        
        # Draw explosions with camera offset
        for explosion in self.explosions:
            self.screen.blit(explosion.image, (explosion.x - self.camera_x, explosion.y))
        
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
            
            # Draw lives panel
            lives_text = f"LIVES: {self.lives}"
            lives_surface = self.font_medium.render(lives_text, True, NEON_GREEN)
            lives_rect = lives_surface.get_rect(topleft=(15, 60))
            
            # Glow effect for lives
            lives_glow_rect = lives_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (0, 50, 0), lives_glow_rect)  # Subtle background
            pygame.draw.rect(self.screen, NEON_GREEN, lives_glow_rect, 2)  # Border glow
            self.screen.blit(lives_surface, lives_rect)
        else:
            score_text = self.font_medium.render(f"Score: {self.score}", True, BLACK)
            level_text = self.font_medium.render(f"Level: {self.level}", True, BLACK)
            lives_text = self.font_medium.render(f"Lives: {self.lives}", True, BLACK)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(level_text, (10, 50))
            self.screen.blit(lives_text, (10, 90))
        
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
        
        # Draw tracker lasers (visual beams from boss to player)
        for boss in self.bosses:
            if boss.tracker_laser:
                boss.tracker_laser.draw(self.screen, self.camera_x)
        
        # Draw game over or victory screen
        if self.game_over:
            if self.victory:
                self.draw_victory_screen()
            else:
                self.draw_game_over_screen()
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            if self.title_screen:
                # Show title screen
                self.handle_events()
                self.draw()
            elif self.game_over:
                # Show victory or game over screen
                self.handle_events()  # Check for continue/restart button click
                self.draw()
            else:
                self.handle_events()
                self.update()
                self.draw()
            
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()

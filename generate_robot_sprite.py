#!/usr/bin/env python3
"""
Combat Robot Sprite Sheet Generator
Generates pixel art sprite sheet for "Alien vs Robots" platformer
Creates multiple animation frames for idle, walk, run, jump, attack, etc.
"""

import numpy as np
from PIL import Image, ImageDraw
import math

# Color palette (sci-fi themed)
TRANSPARENT = (0, 0, 0, 0)
METAL_DARK = (40, 40, 50)      # Dark metallic body
METAL_LIGHT = (120, 120, 140)  # Light highlights
METAL_MID = (80, 80, 100)      # Mid-tone metal
VISOR_RED = (255, 50, 80)      # Glowing red visor
VISOR_BRIGHT = (255, 150, 150) # Bright visor glow
ENERGY_BLUE = (50, 150, 255)   # Energy weapon
ENERGY_BRIGHT = (100, 200, 255)# Bright energy glow
JOINT_ORANGE = (255, 150, 50)  # Joint connections
SCRATCH_DARK = (60, 60, 70)    # Battle scars
OUTLINE = (20, 20, 25)         # Outline color

# Frame dimensions
FRAME_WIDTH = 64
FRAME_HEIGHT = 96
SPRITE_SCALE = 2  # Pixel size multiplier for crisp look

class RobotSpriteGenerator:
    def __init__(self, width=FRAME_WIDTH, height=FRAME_HEIGHT, scale=SPRITE_SCALE):
        self.width = width
        self.height = height
        self.scale = scale
        self.pixel_width = width * scale
        self.pixel_height = height * scale
        
    def create_base_frame(self):
        """Create transparent base frame with RGBA"""
        return Image.new('RGBA', (self.pixel_width, self.pixel_height), TRANSPARENT)
    
    def draw_robot_idle(self, base_offset=0):
        """Draw robot in idle stance (neutral position)"""
        img = self.create_base_frame()
        pixels = img.load()
        
        # Offset for idle animation (breathing motion)
        y_offset = int(math.sin(base_offset * 0.1) * 2)
        
        # Head (visor prominently displayed)
        head_x, head_y = self.width // 2, self.height // 4 + y_offset
        self._draw_head(pixels, head_x, head_y, intensity=1.0)
        
        # Torso (armored body)
        torso_x, torso_y = self.width // 2, self.height // 2 + y_offset
        self._draw_torso(pixels, torso_x, torso_y)
        
        # Arms (relaxed at sides)
        self._draw_arm(pixels, torso_x - 12, torso_y + 5, -10, side='left')
        self._draw_arm(pixels, torso_x + 12, torso_y + 5, -10, side='right')
        
        # Legs (standing stance)
        self._draw_leg(pixels, torso_x - 8, torso_y + 25, side='left')
        self._draw_leg(pixels, torso_x + 8, torso_y + 25, side='right')
        
        return img
    
    def draw_robot_walk(self, frame=0):
        """Draw walking animation cycle (4 frames)"""
        img = self.create_base_frame()
        pixels = img.load()
        
        # Walking cycle positions
        cycle_frames = [
            {'body_y': 0, 'left_leg_angle': -15, 'right_leg_angle': 15, 'left_arm_angle': 15, 'right_arm_angle': -15},
            {'body_y': -2, 'left_leg_angle': -5, 'right_leg_angle': 5, 'left_arm_angle': 5, 'right_arm_angle': -5},
            {'body_y': 0, 'left_leg_angle': 15, 'right_leg_angle': -15, 'left_arm_angle': -15, 'right_arm_angle': 15},
            {'body_y': -2, 'left_leg_angle': 5, 'right_leg_angle': -5, 'left_arm_angle': -5, 'right_arm_angle': 5},
        ]
        
        pose = cycle_frames[frame % len(cycle_frames)]
        
        head_x, head_y = self.width // 2, self.height // 4 + pose['body_y']
        self._draw_head(pixels, head_x, head_y, intensity=0.9)
        
        torso_x, torso_y = self.width // 2, self.height // 2 + pose['body_y']
        self._draw_torso(pixels, torso_x, torso_y)
        
        self._draw_arm(pixels, torso_x - 12, torso_y + 5, pose['left_arm_angle'], side='left')
        self._draw_arm(pixels, torso_x + 12, torso_y + 5, pose['right_arm_angle'], side='right')
        
        self._draw_leg(pixels, torso_x - 8, torso_y + 25, angle_offset=pose['left_leg_angle'], side='left')
        self._draw_leg(pixels, torso_x + 8, torso_y + 25, angle_offset=pose['right_leg_angle'], side='right')
        
        return img
    
    def draw_robot_run(self, frame=0):
        """Draw running animation cycle (faster, more dynamic)"""
        img = self.create_base_frame()
        pixels = img.load()
        
        cycle_frames = [
            {'body_y': -1, 'left_leg_angle': -25, 'right_leg_angle': 25, 'left_arm_angle': 25, 'right_arm_angle': -25},
            {'body_y': 2, 'left_leg_angle': 0, 'right_leg_angle': 0, 'left_arm_angle': 0, 'right_arm_angle': 0},
            {'body_y': -1, 'left_leg_angle': 25, 'right_leg_angle': -25, 'left_arm_angle': -25, 'right_arm_angle': 25},
            {'body_y': 2, 'left_leg_angle': 0, 'right_leg_angle': 0, 'left_arm_angle': 0, 'right_arm_angle': 0},
        ]
        
        pose = cycle_frames[frame % len(cycle_frames)]
        
        head_x, head_y = self.width // 2, self.height // 4 + pose['body_y']
        self._draw_head(pixels, head_x, head_y, intensity=0.8)
        
        torso_x, torso_y = self.width // 2, self.height // 2 + pose['body_y']
        self._draw_torso(pixels, torso_x, torso_y, lean=5)
        
        self._draw_arm(pixels, torso_x - 12, torso_y + 5, pose['left_arm_angle'], side='left')
        self._draw_arm(pixels, torso_x + 12, torso_y + 5, pose['right_arm_angle'], side='right')
        
        self._draw_leg(pixels, torso_x - 8, torso_y + 25, angle_offset=pose['left_leg_angle'], side='left')
        self._draw_leg(pixels, torso_x + 8, torso_y + 25, angle_offset=pose['right_leg_angle'], side='right')
        
        return img
    
    def draw_robot_jump(self, phase=0):
        """Draw jumping animation (takeoff and mid-air)"""
        img = self.create_base_frame()
        pixels = img.load()
        
        # Jump arc motion
        jump_height = -20 if phase == 1 else -10 if phase == 0 else 0
        
        head_x, head_y = self.width // 2, self.height // 4 + jump_height
        self._draw_head(pixels, head_x, head_y, intensity=0.85)
        
        torso_x, torso_y = self.width // 2, self.height // 2 + jump_height
        self._draw_torso(pixels, torso_x, torso_y)
        
        # Arms up for jump
        self._draw_arm(pixels, torso_x - 12, torso_y + 5, -45, side='left')
        self._draw_arm(pixels, torso_x + 12, torso_y + 5, -45, side='right')
        
        # Legs tucked or extended
        if phase == 1:  # Mid-air
            self._draw_leg(pixels, torso_x - 8, torso_y + 25, angle_offset=-30, side='left')
            self._draw_leg(pixels, torso_x + 8, torso_y + 25, angle_offset=-30, side='right')
        else:  # Landing
            self._draw_leg(pixels, torso_x - 8, torso_y + 25, angle_offset=0, side='left')
            self._draw_leg(pixels, torso_x + 8, torso_y + 25, angle_offset=0, side='right')
        
        return img
    
    def draw_robot_shoot(self):
        """Draw robot shooting energy blast"""
        img = self.create_base_frame()
        pixels = img.load()
        
        head_x, head_y = self.width // 2, self.height // 4
        self._draw_head(pixels, head_x, head_y, intensity=1.2)  # Brighter visor
        
        torso_x, torso_y = self.width // 2, self.height // 2
        self._draw_torso(pixels, torso_x, torso_y, lean=3)
        
        # Left arm (aiming forward)
        self._draw_arm_cannon(pixels, torso_x - 12, torso_y + 5, side='left')
        
        # Right arm (support pose)
        self._draw_arm(pixels, torso_x + 12, torso_y + 5, -20, side='right')
        
        # Legs (shooting stance)
        self._draw_leg(pixels, torso_x - 8, torso_y + 25, angle_offset=-5, side='left')
        self._draw_leg(pixels, torso_x + 8, torso_y + 25, angle_offset=5, side='right')
        
        # Energy blast effect
        self._draw_energy_blast(pixels, torso_x - 20, torso_y + 8, direction='left')
        
        return img
    
    def draw_robot_slash(self):
        """Draw robot performing melee energy slash"""
        img = self.create_base_frame()
        pixels = img.load()
        
        head_x, head_y = self.width // 2, self.height // 4
        self._draw_head(pixels, head_x, head_y, intensity=0.95)
        
        torso_x, torso_y = self.width // 2, self.height // 2
        self._draw_torso(pixels, torso_x, torso_y, lean=-8)
        
        # Slash pose - raised arm
        self._draw_arm_slash(pixels, torso_x - 12, torso_y + 5, side='left')
        
        # Support arm
        self._draw_arm(pixels, torso_x + 12, torso_y + 5, 45, side='right')
        
        # Lunging stance
        self._draw_leg(pixels, torso_x - 8, torso_y + 25, angle_offset=-20, side='left')
        self._draw_leg(pixels, torso_x + 8, torso_y + 25, angle_offset=15, side='right')
        
        # Energy sword effect
        self._draw_energy_slash(pixels, torso_x - 15, torso_y)
        
        return img
    
    def draw_robot_hit(self):
        """Draw robot taking damage"""
        img = self.create_base_frame()
        pixels = img.load()
        
        head_x, head_y = self.width // 2, self.height // 4 - 2
        self._draw_head(pixels, head_x, head_y, intensity=0.7)  # Dimmer visor
        
        torso_x, torso_y = self.width // 2, self.height // 2 - 2
        self._draw_torso(pixels, torso_x, torso_y, lean=-5)
        
        # Recoil pose
        self._draw_arm(pixels, torso_x - 12, torso_y + 5, 20, side='left')
        self._draw_arm(pixels, torso_x + 12, torso_y + 5, -20, side='right')
        
        self._draw_leg(pixels, torso_x - 8, torso_y + 25, angle_offset=10, side='left')
        self._draw_leg(pixels, torso_x + 8, torso_y + 25, angle_offset=-10, side='right')
        
        # Damage indicators
        self._draw_damage_sparks(pixels, torso_x, torso_y)
        
        return img
    
    def draw_robot_death(self, frame=0):
        """Draw death animation (collapse/explosion)"""
        img = self.create_base_frame()
        pixels = img.load()
        
        if frame < 2:  # Falling
            head_x, head_y = self.width // 2 - 5, self.height // 4 + frame * 8
            torso_x, torso_y = self.width // 2 - 5, self.height // 2 + frame * 8
            
            self._draw_head(pixels, head_x, head_y, intensity=0.3)
            self._draw_torso(pixels, torso_x, torso_y, lean=-15)
            
            self._draw_arm(pixels, torso_x - 12, torso_y + 5, 90, side='left')
            self._draw_arm(pixels, torso_x + 12, torso_y + 5, 90, side='right')
            
            self._draw_leg(pixels, torso_x - 8, torso_y + 25, angle_offset=45, side='left')
            self._draw_leg(pixels, torso_x + 8, torso_y + 25, angle_offset=45, side='right')
        else:  # Explosion
            self._draw_explosion(pixels, self.width // 2, self.height // 2)
        
        return img
    
    def _draw_head(self, pixels, x, y, intensity=1.0):
        """Draw robot head with glowing visor"""
        # Head shape (rounded)
        for dy in range(-8, 9):
            for dx in range(-6, 7):
                if dx*dx + dy*dy <= 36:
                    px, py = int((x + dx) * self.scale), int((y + dy) * self.scale)
                    if 0 <= px < self.pixel_width and 0 <= py < self.pixel_height:
                        # Head color
                        color = self._interpolate(METAL_DARK, METAL_MID, 0.5)
                        pixels[px, py] = color + (255,)
        
        # Visor (glowing red)
        visor_intensity = min(1.0, intensity)
        visor_color = self._interpolate(VISOR_RED, VISOR_BRIGHT, visor_intensity)
        
        for dy in range(-4, 5):
            for dx in range(-5, 6):
                if abs(dx) <= 4 and abs(dy) <= 3:
                    px, py = int((x - 1 + dx) * self.scale), int((y + dy) * self.scale)
                    if 0 <= px < self.pixel_width and 0 <= py < self.pixel_height:
                        pixels[px, py] = visor_color + (255,)
        
        # Visor glow effect
        for dy in range(-6, 7):
            for dx in range(-6, 7):
                dist = math.sqrt(dx*dx + dy*dy)
                if 4 < dist <= 6:
                    alpha = int(150 * (1 - (dist - 4) / 2))
                    px, py = int((x - 1 + dx) * self.scale), int((y + dy) * self.scale)
                    if 0 <= px < self.pixel_width and 0 <= py < self.pixel_height:
                        current = pixels[px, py]
                        blended = self._blend_alpha(current, visor_color, alpha)
                        pixels[px, py] = blended
    
    def _draw_torso(self, pixels, x, y, lean=0):
        """Draw armored torso"""
        # Main body
        for dy in range(-12, 13):
            for dx in range(-8, 9):
                if abs(dx) <= 7 - abs(dy) // 3:
                    px = int((x + dx + lean * dy / 24) * self.scale)
                    py = int((y + dy) * self.scale)
                    if 0 <= px < self.pixel_width and 0 <= py < self.pixel_height:
                        # Shaded body
                        shade = 0.3 + 0.7 * (abs(dx) / 8)
                        color = self._interpolate(METAL_DARK, METAL_MID, shade)
                        pixels[px, py] = color + (255,)
        
        # Armor plates (highlights)
        for dy in range(-10, 11):
            for dx in range(-4, 5):
                if abs(dx) <= 3:
                    px = int((x - 5 + dx) * self.scale)
                    py = int((y + dy) * self.scale)
                    if 0 <= px < self.pixel_width and 0 <= py < self.pixel_height:
                        if random.random() > 0.7:
                            pixels[px, py] = METAL_LIGHT + (200,)
    
    def _draw_arm(self, pixels, x, y, angle_offset=0, side='left'):
        """Draw robot arm"""
        # Upper arm
        length = 8
        rad = math.radians(angle_offset)
        
        for i in range(length):
            px = int((x + i * math.cos(rad)) * self.scale)
            py = int((y + i * math.sin(rad)) * self.scale)
            
            if 0 <= px < self.pixel_width and 0 <= py < self.pixel_height:
                pixels[px, py] = METAL_MID + (255,)
        
        # Joint
        px = int((x + length * math.cos(rad)) * self.scale)
        py = int((y + length * math.sin(rad)) * self.scale)
        if 0 <= px < self.pixel_width and 0 <= py < self.pixel_height:
            pixels[px, py] = JOINT_ORANGE + (255,)
    
    def _draw_arm_cannon(self, pixels, x, y, side='left'):
        """Draw arm with energy cannon"""
        # Cannon barrel
        for i in range(10):
            px = int((x - i - 5) * self.scale)
            py = int((y) * self.scale)
            
            if 0 <= px < self.pixel_width and 0 <= py < self.pixel_height:
                pixels[px, py] = METAL_MID + (255,)
    
    def _draw_arm_slash(self, pixels, x, y, side='left'):
        """Draw arm holding energy sword"""
        # Raised arm
        for i in range(12):
            px = int((x) * self.scale)
            py = int((y - i) * self.scale)
            
            if 0 <= px < self.pixel_width and 0 <= py < self.pixel_height:
                pixels[px, py] = METAL_MID + (255,)
    
    def _draw_leg(self, pixels, x, y, angle_offset=0, side='left'):
        """Draw robot leg"""
        # Leg segment
        for i in range(12):
            px = int((x + i * math.sin(math.radians(angle_offset)) * 0.5) * self.scale)
            py = int((y + i) * self.scale)
            
            if 0 <= px < self.pixel_width and 0 <= py < self.pixel_height:
                pixels[px, py] = METAL_MID + (255,)
    
    def _draw_energy_blast(self, pixels, x, y, direction='left'):
        """Draw energy weapon blast effect"""
        if direction == 'left':
            for i in range(1, 6):
                for j in range(-2, 3):
                    px = int((x - i * 3 - 5) * self.scale)
                    py = int((y + j) * self.scale)
                    
                    if 0 <= px < self.pixel_width and 0 <= py < self.pixel_height:
                        alpha = int(200 * (1 - i / 6))
                        color = self._blend_alpha((0, 0, 0, 0), ENERGY_BRIGHT, alpha)
                        pixels[px, py] = color
    
    def _draw_energy_slash(self, pixels, x, y):
        """Draw energy sword slash visual effect"""
        # Diagonal slash
        for i in range(-10, 10):
            for j in range(-2, 3):
                px = int((x + i) * self.scale)
                py = int((y + i * 0.5 + j) * self.scale)
                
                if 0 <= px < self.pixel_width and 0 <= py < self.pixel_height:
                    alpha = int(180 * (1 - abs(i) / 10))
                    if alpha > 0:
                        pixels[px, py] = ENERGY_BLUE + (alpha,)
    
    def _draw_damage_sparks(self, pixels, x, y):
        """Draw damage/spark effects"""
        import random
        for _ in range(4):
            spark_x = int((x + random.randint(-8, 8)) * self.scale)
            spark_y = int((y + random.randint(-8, 8)) * self.scale)
            
            if 0 <= spark_x < self.pixel_width and 0 <= spark_y < self.pixel_height:
                pixels[spark_x, spark_y] = ENERGY_BRIGHT + (200,)
    
    def _draw_explosion(self, pixels, x, y):
        """Draw explosion effect"""
        import random
        for _ in range(20):
            dx = random.randint(-15, 15)
            dy = random.randint(-15, 15)
            px = int((x + dx) * self.scale)
            py = int((y + dy) * self.scale)
            
            if 0 <= px < self.pixel_width and 0 <= py < self.pixel_height:
                dist = math.sqrt(dx*dx + dy*dy)
                alpha = int(255 * max(0, 1 - dist / 15))
                if alpha > 0:
                    pixels[px, py] = JOINT_ORANGE + (alpha,)
    
    def _interpolate(self, color1, color2, t):
        """Interpolate between two colors"""
        return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(color1, color2))
    
    def _blend_alpha(self, bg, fg, alpha):
        """Blend foreground color onto background with alpha"""
        if len(bg) < 4:
            bg = bg + (255,)
        if len(fg) < 4:
            fg = fg + (255,)
        
        alpha_normalized = alpha / 255.0
        return tuple(
            int(bg[i] * (1 - alpha_normalized) + fg[i] * alpha_normalized)
            for i in range(3)
        ) + (255,)


def generate_sprite_sheet():
    """Generate complete sprite sheet with all animations"""
    
    print("=" * 60)
    print("Generating Combat Robot Sprite Sheet")
    print("=" * 60)
    print()
    
    generator = RobotSpriteGenerator()
    
    # Create sprite frames
    frames = []
    frame_names = []
    
    # Idle (1 frame with breathing animation)
    print("Generating IDLE animation...")
    idle_img = generator.draw_robot_idle(base_offset=0)
    frames.append(idle_img)
    frame_names.append("Idle")
    
    # Walk cycle (4 frames)
    print("Generating WALK cycle (4 frames)...")
    for i in range(4):
        walk_img = generator.draw_robot_walk(frame=i)
        frames.append(walk_img)
        frame_names.append(f"Walk_{i+1}")
    
    # Run cycle (4 frames)
    print("Generating RUN cycle (4 frames)...")
    for i in range(4):
        run_img = generator.draw_robot_run(frame=i)
        frames.append(run_img)
        frame_names.append(f"Run_{i+1}")
    
    # Jump (2 frames)
    print("Generating JUMP poses (2 frames)...")
    for i in range(2):
        jump_img = generator.draw_robot_jump(phase=i)
        frames.append(jump_img)
        frame_names.append(f"Jump_{i+1}")
    
    # Shoot (1 frame)
    print("Generating SHOOT pose...")
    shoot_img = generator.draw_robot_shoot()
    frames.append(shoot_img)
    frame_names.append("Shoot")
    
    # Slash (1 frame)
    print("Generating SLASH pose...")
    slash_img = generator.draw_robot_slash()
    frames.append(slash_img)
    frame_names.append("Slash")
    
    # Hit/Damage (1 frame)
    print("Generating HIT/DAMAGE pose...")
    hit_img = generator.draw_robot_hit()
    frames.append(hit_img)
    frame_names.append("Hit")
    
    # Death (3 frames)
    print("Generating DEATH animation (3 frames)...")
    for i in range(3):
        death_img = generator.draw_robot_death(frame=i)
        frames.append(death_img)
        frame_names.append(f"Death_{i+1}")
    
    print()
    print(f"✓ Generated {len(frames)} sprite frames")
    print()
    
    # Create sprite sheet
    print("Creating sprite sheet...")
    sheet_width = FRAME_WIDTH * 4 * SPRITE_SCALE
    sheet_height = FRAME_HEIGHT * 4 * SPRITE_SCALE
    
    sprite_sheet = Image.new('RGBA', (sheet_width * 4, sheet_height * 3), TRANSPARENT)
    
    # Place frames on sheet
    col, row = 0, 0
    for idx, (frame, name) in enumerate(zip(frames, frame_names)):
        x = col * (FRAME_WIDTH * SPRITE_SCALE)
        y = row * (FRAME_HEIGHT * SPRITE_SCALE)
        sprite_sheet.paste(frame, (x, y), frame)
        
        col += 1
        if col >= 4:
            col = 0
            row += 1
    
    # Save sprite sheet
    output_path = 'assets/robot_sprite_sheet.png'
    sprite_sheet.save(output_path)
    print(f"✓ Sprite sheet saved: {output_path}")
    print(f"  Sheet dimensions: {sprite_sheet.width}x{sprite_sheet.height}")
    print()
    
    # Save individual frames for reference
    print("Saving individual frames...")
    for idx, (frame, name) in enumerate(zip(frames, frame_names)):
        frame_path = f'assets/robot_{name.lower().replace("_", "")}.png'
        frame.save(frame_path)
        print(f"  ✓ {frame_path}")
    
    print()
    print("=" * 60)
    print("✓ Sprite Sheet Generation Complete!")
    print("=" * 60)
    print()
    print("Frames generated:")
    for i, name in enumerate(frame_names):
        print(f"  {i+1}. {name}")
    print()
    print("Ready to use in your game! Update main.py to load:")
    print("  - assets/robot_sprite_sheet.png (full sheet)")
    print("  - Individual frame files for specific animations")
    print()


import random

if __name__ == "__main__":
    generate_sprite_sheet()

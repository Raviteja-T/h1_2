# Author: Raviteja Tirumalapudi
# Email: t.raviteja@gmail.com

#!/usr/bin/env python3
import math
import numpy as np
from enum import Enum

class GaitState(Enum):
    DOUBLE_SUPPORT = 0
    LEFT_SWING = 1
    RIGHT_SWING = 2
    TRANSITION = 3

class BipedalGaitController:
    def __init__(self):
        # Gait parameters
        self.step_length = 0.15
        self.step_height = 0.08
        self.step_duration = 1.0  # seconds
        self.stance_width = 0.25
        
        # Gait state
        self.state = GaitState.DOUBLE_SUPPORT
        self.phase = 0.0
        self.swing_leg = 'right'  # Starting swing leg
        
        # Robot state
        self.com_offset = [0.0, 0.0, 0.0]  # Center of Mass offset
        self.foot_positions = {
            'left': [0.0, self.stance_width/2, 0.0],
            'right': [0.0, -self.stance_width/2, 0.0]
        }
        
        # Walking commands
        self.walk_velocity = [0.0, 0.0, 0.0]  # [forward, lateral, rotational]
        self.is_walking = False
        
    def update(self, dt, walk_commands=None):
        """Update gait controller"""
        if walk_commands:
            self.walk_velocity = walk_commands
            self.is_walking = any(abs(v) > 0.1 for v in walk_commands)
        
        if not self.is_walking:
            self.phase = 0.0
            self.state = GaitState.DOUBLE_SUPPORT
            return self.generate_standing_pose()
        
        # Update phase
        self.phase += dt / self.step_duration
        if self.phase >= 1.0:
            self.phase = 0.0
            self.swing_leg = 'left' if self.swing_leg == 'right' else 'right'
        
        # Update state based on phase
        if self.phase < 0.1:
            self.state = GaitState.DOUBLE_SUPPORT
        elif self.phase < 0.6:
            self.state = GaitState.LEFT_SWING if self.swing_leg == 'left' else GaitState.RIGHT_SWING
        else:
            self.state = GaitState.TRANSITION
        
        return self.generate_walking_trajectories()
    
    def generate_standing_pose(self):
        """Generate joint positions for standing pose"""
        joints = [0.0] * 27
        
        # Legs - standing position
        # Left leg
        joints[1] = -0.4   # Left hip pitch
        joints[3] = 0.8    # Left knee  
        joints[4] = -0.4   # Left ankle pitch
        
        # Right leg
        joints[7] = -0.4   # Right hip pitch
        joints[9] = 0.8    # Right knee
        joints[10] = -0.4  # Right ankle pitch
        
        return joints
    
    def generate_walking_trajectories(self):
        """Generate joint positions for walking"""
        joints = self.generate_standing_pose()
        
        # Calculate foot trajectories based on phase and swing leg
        if self.state == GaitState.LEFT_SWING:
            joints = self.calculate_swing_trajectory(joints, 'left')
        elif self.state == GaitState.RIGHT_SWING:
            joints = self.calculate_swing_trajectory(joints, 'right')
        
        # Apply COM shifting for balance
        joints = self.apply_balance_control(joints)
        
        return joints
    
    def calculate_swing_trajectory(self, joints, swing_leg):
        """Calculate foot trajectory for swinging leg"""
        # Cycloid trajectory for smooth motion
        t = self.phase * 2.0 - 0.2  # Scale phase for swing period
        t = max(0.0, min(1.0, t))
        
        # Horizontal motion (cycloid)
        x = self.step_length * (t - math.sin(2 * math.pi * t) / (2 * math.pi))
        
        # Vertical motion (simple parabola)
        z = self.step_height * 4 * t * (1 - t)
        
        # Apply based on swing leg
        if swing_leg == 'left':
            # Left leg swings forward
            joints[1] = -0.4 + x * 2.0  # Hip pitch
            joints[5] = z * 10.0        # Ankle roll for balance
        else:
            # Right leg swings forward
            joints[7] = -0.4 + x * 2.0  # Hip pitch
            joints[11] = z * 10.0       # Ankle roll for balance
            
        return joints
    
    def apply_balance_control(self, joints):
        """Apply simple balance control using ankle strategy"""
        # Simple COM shifting based on gait phase
        balance_offset = math.sin(self.phase * 2 * math.pi) * 0.1
        
        if self.swing_leg == 'left':
            # Shift COM to right during left swing
            joints[8] += balance_offset  # Right hip roll
            joints[11] += balance_offset  # Right ankle roll
        else:
            # Shift COM to left during right swing
            joints[2] += balance_offset  # Left hip roll
            joints[5] += balance_offset  # Left ankle roll
            
        return joints
    
    def set_gait_parameters(self, step_length=None, step_height=None, duration=None):
        """Update gait parameters dynamically"""
        if step_length:
            self.step_length = step_length
        if step_height:
            self.step_height = step_height
        if duration:
            self.step_duration = duration
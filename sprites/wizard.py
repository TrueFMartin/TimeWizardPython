import os

from sprites.movingsprite import MovingSprite
from sprites.pipe import Pipe
from pygame import Rect


class Wizard(MovingSprite):
    time_in_air: int  # number of frames since sprite has hit ground/platform
    is_moving: bool  # true if sprite should move next turn
    next_horiz_cord: int  # an int value of X pos of sprite

    def __init__(self, x, y):
        super().__init__(Rect(x, y, 60, 95), 8, "resources/wizard/wizard")
        self.time_in_air = 0
        self.is_moving = False
        self.is_jumping = False
        self.next_horiz_cord = self.rect.left

    def update(self) -> bool:
        super().update()
        return True

    def update_move(self) -> None:
        if self.is_moving:
            self.rect.left = self.next_horiz_cord
            self.current_image_num += 1
            self.current_image_num %= (len(self.images) * 2)
        if self.is_jumping and self.time_in_air < 8:
            self.vert_velocity -= self.get_base_speed() * .75
        self.is_moving = False
        self.is_jumping = False

    def update_gravity(self) -> None:
        super().update_gravity()
        if self.is_below_ground():
            self.time_in_air = 0
        else:
            self.time_in_air += 1

    # noinspection PyTypeChecker
    def set_wizard_move(self, is_move_right: bool) -> None:  # FIXME if collision, may not detect time to move
        if self.rect.left == self.next_horiz_cord:
            self.is_moving = True
            if is_move_right:
                self.next_horiz_cord = self.next_horiz_cord + self.get_base_speed()
                self.horiz_flip = False
            else:
                self.next_horiz_cord = self.next_horiz_cord - self.get_base_speed()
                self.horiz_flip = True

    def set_wizard_jump(self):
        self.is_jumping = True

    def collision_detector(self, other_sprite) -> None:
        if isinstance(other_sprite, Pipe) and super().collision_detector(other_sprite):
            self.collision_handler(other_sprite)

    def top_collision_helper(self, other_sprite):
        super().top_collision_helper(other_sprite)
        self.time_in_air = 0

    def bottom_collision_helper(self, other_sprite):
        super().bottom_collision_helper(other_sprite)
        self.time_in_air = 8

    def left_collision_helper(self, other_sprite):
        super().left_collision_helper(other_sprite)
        self.next_horiz_cord = self.rect.left

    def right_collision_helper(self, other_sprite):
        super().right_collision_helper(other_sprite)
        self.next_horiz_cord = self.rect.left

from pygame import Rect
from sprites.pipe import Pipe
from sprites.fireball import Fireball
from sprites.movingsprite import MovingSprite


class Skeleton(MovingSprite):
    is_moving_right: bool  # true if sprite is moving right
    is_alive: bool  # true while alive, false when hit by fireball and dies for 30 frames
    has_loaded_dead_images = bool  # once dead, update will rewrite images list ONCE
    num_frames_dead = int  # keeps track of how long sprite has been dead before removal

    def __init__(self, x, y):
        super().__init__(Rect(x, y, 60, 95), 12, "resources/skeleton/skeleton alive")
        self.is_moving_right = True
        self.is_alive = True
        self.has_loaded_dead_images = False
        self.num_frames_dead = 0

    def update(self) -> bool:
        super().update()
        # ----If alive, move skeleton, update current image num----
        if self.is_alive:
            self.update_move()
            self.current_image_num = (self.current_image_num + 1) \
                                     % len(self.images)
        # ----If dead, load images list with dead skeleton png's---
        else:
            if not self.has_loaded_dead_images:
                self.init_load_dead_images()
                self.has_loaded_dead_images = True
            self.num_frames_dead = self.num_frames_dead + 1
            # ------Increment image number until final of dead skeleton-----
            self.current_image_num += 1 if self.current_image_num < self.num_images - 1 else 0
        # ----If skeleton has been dead >= 30 frames, remove from sprite list
        return self.num_frames_dead < 30

    def update_move(self):
        if self.is_alive:
            self.rect.left += (self.get_base_speed() * 0.5
                               if self.is_moving_right
                               else self.get_base_speed() * -0.5)

    def init_load_dead_images(self):
        self.images.clear()
        self.image_url_prefix = "resources/skeleton/skeleton dead"
        self.num_images = 13
        self.load_images()
        self.current_image_num = -1

    def collision_detector(self, other_sprite) -> None:
        if isinstance(other_sprite, Pipe) and super().collision_detector(other_sprite):
            self.collision_handler(other_sprite)
        elif isinstance(other_sprite, Fireball) and super().collision_detector(other_sprite):
            self.is_alive = False

    def left_collision_helper(self, other_sprite):
        super().left_collision_helper(other_sprite)
        self.horiz_flip = True
        self.is_moving_right = False

    def right_collision_helper(self, other_sprite):
        super().right_collision_helper(other_sprite)
        self.horiz_flip = False
        self.is_moving_right = True
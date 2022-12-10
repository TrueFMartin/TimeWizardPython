from sprites.movingsprite import MovingSprite
import pygame


class Fireball(MovingSprite):
    time_in_air: int
    is_moving_right: bool
    is_alive: bool
    num_frames_alive: 0  # Used to find when all old images have updated to new size

    def __init__(self, x, y, is_moving_right: bool):
        super().__init__(pygame.Rect(x, y, 50, 50), 61, "resources/fireball/fireball")
        self.is_moving_right = is_moving_right
        self.time_in_air = 0
        self.is_alive = True
        self.num_frames_alive = 0

    def draw_sprite(self, screen: pygame.Surface, scroll_x: int, scroll_y: int) -> None:
        # -----Increase scale of current image with new dimensions---
        self.current_image_num += 1
        self.current_image_num %= self.num_images
        if self.num_frames_alive < 2 * self.num_images:
            self.images[self.current_image_num] = \
                (
                    pygame.transform.scale(
                        self.images[self.current_image_num],
                        (self.rect.w, self.rect.h))
                )

        super().draw_sprite(screen, scroll_x, scroll_y)

    def update(self) -> bool:
        if self.rect.w < 100:
            self.rect.w += 1.5
            self.rect.h += 1.5
        self.num_frames_alive += 1
        super().update()
        return self.is_alive

    def update_move(self) -> None:
        temp_direction = 1 if self.is_moving_right else -1
        self.rect.left += temp_direction * self.get_base_speed() * 2
        if self.time_in_air < 15:
            self.vert_velocity -= self.get_base_speed() * .4

    def update_gravity(self) -> None:
        super().update_gravity()
        if self.is_below_ground():
            self.time_in_air = 0
        else:
            self.time_in_air += 1

    def set_kill(self):
        self.is_alive = False

import pygame
from sprites.sprite import Sprite


class MovingSprite(Sprite):
    images: [pygame.image]
    num_images: int
    image_url_prefix: str
    current_image_num: int
    prev_x: int
    prev_y = int
    vert_velocity: float
    horiz_flip: bool

    def __init__(self, rect, num_images: int, image_url_prefix: str):
        super().__init__(rect)
        self.images = []
        self.num_images = num_images
        self.image_url_prefix = image_url_prefix
        self.load_images()
        self.current_image_num = 0
        self.image = self.images[self.current_image_num]
        self.prev_x = self.rect.left
        self.prev_y = self.rect.top
        self.vert_velocity = 0
        self.horiz_flip = False

    def draw_sprite(self, screen: pygame.Surface, scroll_x: int, scroll_y: int) -> None:
        self.image = self.images[self.current_image_num // 2]
        # ------If sprite is walking to left, invert image-----
        if self.horiz_flip:
            pygame.Surface.blit(screen, pygame.transform.flip(self.image, True, False),
                                (self.rect.left - scroll_x,
                                 self.rect.top - scroll_y))
        else:
            pygame.Surface.blit(screen, self.image,
                                (self.rect.left - scroll_x,
                                 self.rect.top - scroll_y))

    # ----Takes file name and returns list of image file names--
    def load_images(self) -> None:
        # ------Fill images list with images from url helper method------
        try:
            temp_image_url_list = self.__fill_image_urls()
            for url in temp_image_url_list:
                self.images.append(pygame.image.load(url))
        except pygame.error:
            raise SystemExit(f"Image load failed: {pygame.get_error()}")
        # -----Scale images to proper size--------
        for i in range(len(self.images)):
            self.images[i] = (pygame.transform.scale(self.images[i], (
                self.rect.w, self.rect.h)))

    # ------Helper method, fills temp list with image URLs
    def __fill_image_urls(self) -> []:
        img_url_list = []
        for i in range(1, self.num_images + 1):
            img_url_list.append(f"{self.image_url_prefix} ({i}).png")
        return img_url_list

    def update(self) -> bool:
        self.prev_x = self.rect.left
        self.prev_y = self.rect.top
        self.update_move()
        self.update_gravity()
        return True

    def update_move(self) -> None:
        ...

    def update_gravity(self) -> None:
        self.vert_velocity += self.get_base_speed() * .25
        self.rect.top += self.vert_velocity
        if self.is_below_ground():
            self.vert_velocity = 0
            self.rect.bottom = self.get_ground_level()

    def collision_detector(self, other_sprite) -> bool:
        return not (self.rect.right < other_sprite.rect.left
                    or self.rect.left > other_sprite.rect.right
                    or self.rect.top > other_sprite.rect.bottom
                    or self.rect.bottom < other_sprite.rect.top)

    def collision_handler(self, other_sprite):
        # ------One/two of sprites shoulder is inside of other_sprite----
        shoulders_inside = self.rect.left < other_sprite.rect.right \
                           or self.rect.right > other_sprite.rect.left
        if (
                self.prev_y < self.rect.top
                and self.prev_y + self.rect.h <= other_sprite.rect.top
                and shoulders_inside
        ):
            self.top_collision_helper(other_sprite)

        elif (
                self.prev_y > self.rect.top
                and self.prev_y >= other_sprite.rect.bottom
                and shoulders_inside
        ):
            self.bottom_collision_helper(other_sprite)

        elif self.prev_x < self.rect.left:
            self.left_collision_helper(other_sprite)

        elif self.prev_x > self.rect.left:
            self.right_collision_helper(other_sprite)

    # -----Helper methods that handle collision outcomes----
    def top_collision_helper(self, other_sprite):
        self.vert_velocity = 0
        self.rect.bottom = other_sprite.rect.top

    def bottom_collision_helper(self, other_sprite):
        self.vert_velocity = 0
        self.rect.top = other_sprite.rect.bottom

    def left_collision_helper(self, other_sprite):
        self.rect.right = other_sprite.rect.left

    def right_collision_helper(self, other_sprite):
        self.rect.left = other_sprite.rect.right
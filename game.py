from __future__ import annotations
from typing import Union

import pygame
from pygame.locals import *
from pygame.rect import Rect, RectType


def get_screen_w() -> int:
    return 1300


def get_screen_h() -> int:
    return 816


class Model:
    # noinspection PyCompatibility
    sprites: [Sprite]  # Holds all sprites
    # noinspection PyCompatibility
    wizard: MovingSprite  # wizard() type, used for commands on wizard

    def __init__(self) -> None:
        self.sprites = []
        self.wizard = Wizard(0, 100)
        self.sprites.append(self.wizard)
        self.sprites.append(Pipe(200, 500))
        self.sprites.append(Pipe(800, 200))
        self.sprites.append(Pipe(600, 400))
        self.sprites.append(Pipe(1100, 400))
        self.sprites.append(Skeleton(400, 200))
        self.sprites.append(Skeleton(300, 500))
        self.sprites.append(Skeleton(900, 400))
        for i in range(10):
            self.sprites.append(Pipe(1300 + 400 * i, 500))
            self.sprites.append(Skeleton(1400 + 400 * i, 500))

    # -------Update all sprites, remove if update() fails, run collision-----
    def update(self) -> None:
        # -----List used to hold indexes of sprties to remove------
        remove_these_indexes = []
        # -----Run nested loop with inn/outer sprites------
        for index, outer_sprite in enumerate(self.sprites):
            # ------If fails update, remove sprite-----
            if not outer_sprite.update():
                remove_these_indexes.append(index)
            for inner_sprite in self.sprites:
                # -----Preform collision check on inner & outer sprite----
                inner_sprite.collision_detector(outer_sprite)
            # -----If is a fireball------
            if isinstance(outer_sprite, Fireball):  # STYLE used two if condt's, one was ugly
                # ----And is out of screen,-----
                if get_screen_w() < abs(outer_sprite.rect.left - self.wizard.rect.left):
                    # ------Remove fireball------
                    remove_these_indexes.append(index)
        # ----Pop index from remove list, pop associated sprite----
        while len(remove_these_indexes):
            self.sprites.pop(remove_these_indexes.pop())

    def add_sprite(self, x: int, y: int, is_add_pipe: bool) -> None:
        # ---If not in pipe mode, add skeleton---
        if not is_add_pipe:
            self.sprites.append(Skeleton(x, y))
        # ---Since pipe, see if pipe is present already---
        elif not self.check_for_pipe(x, y):
            self.sprites.append(Pipe(x, y))

    def check_for_pipe(self, x: int, y: int) -> bool:
        for sprite in self.sprites:
            # ----Check through all sprites to see if pipe at click location---
            if isinstance(sprite, Pipe) and sprite.rect.collidepoint(x, y):
                self.sprites.remove(sprite)
                return True  # Pipe is present
        return False  # Pipe not present

    # ----Create fireball at wizards location, moving left/right
    def create_fireball(self) -> None:
        x, y = self.wizard.rect.midright
        self.sprites.append(Fireball(x, y, not self.wizard.horiz_flip))


class View:
    __scroll_x: int
    __scroll_y: int
    __background: pygame.image
    __ground: pygame.image
    __text: [pygame.font, pygame.font]
    __button: pygame.Rect

    def __init__(self, model: Model):
        __screen_size = (get_screen_w(), get_screen_h())
        self.__screen = pygame.display.set_mode(__screen_size, 32)
        self.__model = model
        self.__scroll_x = 0
        self.__scroll_y = 0
        # ----Load background, ground, and text-----
        self.__background = pygame.image.load("resources/background/background.png")
        self.__background = pygame.transform.scale(self.__background, (get_screen_w(), get_screen_h()))
        self.__background.convert_alpha(self.__background)
        self.__ground = pygame.image.load("resources/background/ground.png")
        self.__ground = pygame.transform.scale(self.__ground, (300, 351))
        self.__ground.convert_alpha(self.__ground)
        # ----Font and button style----
        font = pygame.font.SysFont(pygame.font.get_default_font(), 40)
        text_color = Color(0, 0, 0)
        self.__button_color = Color(200, 60, 200)
        self.__text = [font.render("Click to Switch", False, text_color),
                       font.render("Sprite to Add", False, text_color)]
        self.__button = Rect(get_screen_w() / 2 - 110, 0, 220, 100)
        self.__button_border = Rect(get_screen_w() / 2 - 115, 0, 230, 105)

    def update(self) -> None:
        # -----Set position for camera relative to wizard -----
        self.__scroll_x = self.__model.wizard.rect.left - 200
        self.__scroll_y = (self.__model.wizard.rect.top - 300
                           if self.__model.wizard.rect.top < 300
                           else 0)
        # ----Draw background and ground------
        self.__screen.blit(self.__background, (0, 0))
        for i in range(-2, 20):
            self.__screen.blit(self.__ground, (300 * i - self.__scroll_x, 300 - self.__scroll_y))
        # ----Call each sprite's draw function----
        for sprite in self.__model.sprites:
            sprite.draw_sprite(self.__screen, self.__scroll_x, self.__scroll_y)
        # ----Draw button and text-----
        pygame.draw.rect(self.__screen, Color(0, 0, 0), self.__button_border)
        pygame.draw.rect(self.__screen, self.__button_color, self.__button)
        self.__screen.blit(self.__text[0], (get_screen_w() / 2 - 100, 10))
        self.__screen.blit(self.__text[1], (get_screen_w() / 2 - 100, 50))
        # ----Render display -------
        pygame.display.flip()

    # ----Return list with scroll x, y-----
    def get_scroll_pos(self) -> [int, int]:
        return [self.__scroll_x, self.__scroll_y]


class Controller:
    model: Model
    view: View
    keep_going: bool
    is_add_pipe: bool
    wizard: pygame.sprite

    def __init__(self, model: Model, view: View):
        assert isinstance(model, Model)
        self.model = model
        assert isinstance(view, View)
        self.view = view
        self.keep_going = True
        self.is_add_pipe = True

    def update(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.keep_going = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_q:
                    self.keep_going = False
            elif event.type == KEYUP:
                if event.key == K_RCTRL or event.key == K_LCTRL:
                    self.model.create_fireball()
            elif event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                if self.view.__button.collidepoint(x, y):
                    self.is_add_pipe = not self.is_add_pipe
                else:
                    scroll_x, scroll_y = self.view.get_scroll_pos()
                    self.model.add_sprite(x + scroll_x, y + scroll_y, self.is_add_pipe)
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            self.model.wizard.set_wizard_move(False)
        if keys[K_RIGHT]:
            self.model.wizard.set_wizard_move(True)
        if keys[K_SPACE]:
            self.model.wizard.set_wizard_jump()


class Sprite(pygame.sprite.Sprite):
    image: pygame.image
    rect: pygame.rect

    __BASE_SPEED = 5  # Base speed that sprites move off of (e.g. gravity = base speed * .25
    __GROUND = 590  # Level of ground

    def __init__(self, rect: pygame.rect) -> None:
        super().__init__()
        self.rect = rect

    def draw_sprite(self, screen: pygame.display, scroll_x: int, scroll_y: int) -> None:
        pygame.Surface.blit(screen, self.image,
                            (self.rect.left - scroll_x,
                             self.rect.top - scroll_y))

    def update(self) -> bool:
        ...

    def collision_detector(self, other_sprite) -> bool:
        ...

    def is_below_ground(self):
        return self.__GROUND <= self.rect.bottom

    def get_ground_level(self):
        return self.__GROUND

    def get_base_speed(self):
        return self.__BASE_SPEED


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
        self.image = self.images[self.current_image_num]
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
            self.current_image_num = (self.current_image_num + 1) \
                                     % len(self.images)
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


class Pipe(Sprite):

    def __init__(self, x, y):
        super().__init__(Rect(x, y, 60, 240))
        self.image = pygame.image.load("resources/background/deadpipe.png")
        self.image = pygame.transform.scale(self.image, (self.rect.w, self.rect.h))

    def update(self):
        return True

    def collision_detector(self, other_sprite) -> None:
        pass


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


class Fireball(MovingSprite):
    time_in_air: int
    is_moving_right: bool
    is_alive: bool
    num_frames_alive: 0  # Used to find when all old images have updated to new size

    def __init__(self, x, y, is_moving_right: bool):
        super().__init__(Rect(x, y, 50, 50), 61, "resources/fireball/fireball")
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

    def collision_detector(self, other_sprite) -> bool:
        if isinstance(other_sprite, Skeleton) and super().collision_detector(other_sprite):
            self.is_alive = False


print("Use the arrow keys to move. Press Esc to quit.")
pygame.init()
m = Model()
v = View(m)
c = Controller(m, v)
clock = pygame.time.Clock()
while c.keep_going:
    c.update()
    m.update()
    v.update()
    clock.tick(25)

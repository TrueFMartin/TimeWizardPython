from __future__ import annotations
from sprites import fireball, skeleton, pipe, sprite, wizard
import pygame
from pygame.locals import *
from pygame.rect import Rect


def get_screen_w() -> int:
    return 1300


def get_screen_h() -> int:
    return 816


class Model:
    # noinspection PyCompatibility
    sprites: [sprite.Sprite]  # Holds all sprites
    # noinspection PyCompatibility
    wizard: wizard.Wizard  # wizard() type, used for commands on wizard

    def __init__(self) -> None:
        self.sprites = []
        self.wizard = wizard.Wizard(0, 100)
        self.sprites.append(self.wizard)
        self.sprites.append(pipe.Pipe(200, 500))
        self.sprites.append(pipe.Pipe(800, 200))
        self.sprites.append(pipe.Pipe(600, 400))
        self.sprites.append(pipe.Pipe(1100, 400))
        self.sprites.append(skeleton.Skeleton(400, 200))
        self.sprites.append(skeleton.Skeleton(300, 500))
        self.sprites.append(skeleton.Skeleton(900, 400))
        for i in range(10):
            self.sprites.append(pipe.Pipe(1300 + 400 * i, 500))
            self.sprites.append(skeleton.Skeleton(1400 + 400 * i, 500))

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
                if (isinstance(inner_sprite, fireball.Fireball)
                        and isinstance(outer_sprite, skeleton.Skeleton)
                        and inner_sprite.collision_detector(outer_sprite)):
                    inner_sprite.set_kill()
            # -----If is a fireball------
            if isinstance(outer_sprite, fireball.Fireball):  # STYLE used two if condt's, one was ugly
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
            self.sprites.append(skeleton.Skeleton(x, y))
        # ---Since pipe, see if pipe is present already---
        elif not self.check_for_pipe(x, y):
            self.sprites.append(pipe.Pipe(x, y))

    def check_for_pipe(self, x: int, y: int) -> bool:
        for sprite in self.sprites:
            # ----Check through all sprites to see if pipe at click location---
            if isinstance(sprite, pipe.Pipe) and sprite.rect.collidepoint(x, y):
                self.sprites.remove(sprite)
                return True  # Pipe is present
        return False  # Pipe not present

    # ----Create fireball at wizards location, moving left/right
    def create_fireball(self) -> None:
        x, y = self.wizard.rect.midright
        self.sprites.append(fireball.Fireball(x, y, not self.wizard.horiz_flip))


class View:
    __scroll_x: int
    __scroll_y: int
    __background: pygame.image
    __ground: pygame.image
    __text: [pygame.font, pygame.font]
    _button: pygame.Rect

    def __init__(self, model: Model):
        __screen_size = (get_screen_w(), get_screen_h())
        self.__screen = pygame.display.set_mode(__screen_size, 32)
        self.__model = model
        self.__scroll_x = 0
        self.__scroll_y = 0
        # ----Load background, ground, and text-----
        self.__background = pygame.image.load("TimeWizardPython/resources/background/background.png")
        self.__background = pygame.transform.scale(self.__background, (get_screen_w(), get_screen_h()))
        self.__background.convert_alpha(self.__background)
        self.__ground = pygame.image.load("TimeWizardPython/resources/background/ground.png")
        self.__ground = pygame.transform.scale(self.__ground, (300, 351))
        self.__ground.convert_alpha(self.__ground)
        # ----Font and button style----
        font = pygame.font.SysFont(pygame.font.get_default_font(), 40)
        text_color = Color(0, 0, 0)
        self.__button_color = Color(200, 60, 200)
        self.__text = [font.render("Click to Switch", False, text_color),
                       font.render("Sprite to Add", False, text_color)]
        self._button = Rect(get_screen_w() / 2 - 110, 0, 220, 100)
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
        pygame.draw.rect(self.__screen, self.__button_color, self._button)
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
                if self.view._button.collidepoint(x, y):
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

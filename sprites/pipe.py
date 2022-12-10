from sprites.sprite import Sprite
from sprites.imageloader import ImageController
import pygame


class Pipe(Sprite):
    img = pygame.transform.scale(pygame.image.load("resources/background/deadpipe.jpg"), (60, 240))

    def __init__(self, x, y):
        super().__init__(pygame.Rect(x, y, 60, 240))
        self.image = Pipe.img

    def update(self):
        return True

    def collision_detector(self, other_sprite) -> None:
        ...

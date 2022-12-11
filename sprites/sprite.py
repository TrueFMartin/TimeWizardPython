import pygame as pygame


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

    def save_helper(self):
        return {"x": self.rect.left, "y":self.rect.top, "type":self.__class__.__name__}

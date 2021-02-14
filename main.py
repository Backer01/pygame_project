from drawing import Drawing
from sprites import *
import pygame

pygame.init()

screen = pygame.display.set_mode(size)
minimap_screen = pygame.Surface(minisize)  # Мини-карта
drawing = Drawing(screen, minimap_screen)  # Модуль отрисовки

while True:
    if drawing.is_menu:
        drawing.menu()
    elif drawing.is_pause:
        drawing.pause()
    elif drawing.running:
        drawing.game()
    elif drawing.is_win:
        drawing.win()
    elif drawing.is_dead:
        drawing.death()

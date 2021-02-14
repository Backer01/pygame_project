from settings import *
from map import collision_walls
import math
import pygame


class Player:
    def __init__(self):
        self.x, self.y = player_position
        self.angle = player_angle
        self.sensitivity = 0.001
        # Параметры для просчёта столкновений
        self.side = 50
        self.rect = pygame.Rect(*self.get_pos(), self.side, self.side)
        # Переменные читов
        self.noclip = False
        self.speedhack = False
        self.god = False
        self.xray = False

        self.shot = False

        sound = pygame.mixer.Sound
        self.death_sounds = [sound('sounds/player_death/player_death1.mp3'),
                             sound('sounds/player_death/player_death2.mp3'),
                             ]

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_pos(self):
        return self.x, self.y

    def detect_collision(self, dx, dy):  # Функция, проверяющая столконовение игрока со стенами
        next_rect = self.rect.copy()
        next_rect.move_ip(dx, dy)
        hits = next_rect.collidelistall(collision_walls)

        if hits and not self.noclip:
            delta_x, delta_y = 0, 0
            for hit in hits:
                hit_rect = collision_walls[hit]
                if dx > 0:
                    delta_x += next_rect.right - hit_rect.left
                else:
                    delta_x += hit_rect.right - next_rect.left
                if dy > 0:
                    delta_y += next_rect.bottom - hit_rect.top
                else:
                    delta_y += hit_rect.bottom - next_rect.top

            if abs(delta_x - delta_y) < 10:
                dx, dy = 0, 0
            elif delta_x > delta_y:
                dy = 0
            elif delta_y > delta_x:
                dx = 0
        if self.speedhack:
            self.x += dx * 10
            self.y += dy * 10
        else:
            self.x += dx
            self.y += dy

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            dx = player_velocity * math.cos(self.angle)
            dy = player_velocity * math.sin(self.angle)
            self.detect_collision(dx, dy)
        if keys[pygame.K_s]:
            dx = -player_velocity * math.cos(self.angle)
            dy = -player_velocity * math.sin(self.angle)
            self.detect_collision(dx, dy)
        if keys[pygame.K_a]:
            dx = player_velocity * math.sin(self.angle)
            dy = -player_velocity * math.cos(self.angle)
            self.detect_collision(dx, dy)
        if keys[pygame.K_d]:
            dx = -player_velocity * math.sin(self.angle)
            dy = player_velocity * math.cos(self.angle)
            self.detect_collision(dx, dy)
        if keys[pygame.K_LEFT]:
            self.angle -= 0.02
        if keys[pygame.K_RIGHT]:
            self.angle += 0.02

        self.angle %= double_pi
        self.rect.center = self.x, self.y

    def mouse_control(self):
        if pygame.mouse.get_focused():
            diff = pygame.mouse.get_pos()[0] - half_width
            pygame.mouse.set_pos((half_width, half_height))
            self.angle += diff * self.sensitivity

from settings import *
from map import world_map
from ray_casting import mapping
import math
import pygame
import random
from numba import njit


@njit(fastmath=True, cache=True)
def ray_casting_npc(npc_x, npc_y, world_map, player_pos):  # Выпускакем луч из игрока и проверяем попал ли он в npc
    ox, oy = player_pos
    xm, ym = mapping(ox, oy)
    delta_x, delta_y = ox - npc_x, oy - npc_y
    cur_angle = math.atan2(delta_y, delta_x)
    cur_angle += math.pi

    sin_a = math.sin(cur_angle)
    sin_a = sin_a if sin_a else 0.000001
    cos_a = math.cos(cur_angle)
    cos_a = cos_a if cos_a else 0.000001

    x, dx = (xm + tile_size, 1) if cos_a >= 0 else (xm, -1)
    for i in range(0, int(abs(delta_x)) // tile_size):
        depth_v = (x - ox) / cos_a
        yv = oy + depth_v * sin_a
        tile_v = mapping(x + dx, yv)
        if tile_v in world_map:
            return False
        x += dx * tile_size

    y, dy = (ym + tile_size, 1) if sin_a >= 0 else (ym, -1)
    for i in range(0, int(abs(delta_y)) // tile_size):
        depth_h = (y - oy) / sin_a
        xh = ox + depth_h * cos_a
        tile_h = mapping(xh, y + dy)
        if tile_h in world_map:
            return False
        y += dy * tile_size
    return True


class Interaction:
    def __init__(self, player, sprites, drawing):
        self.player = player
        self.sprites = sprites
        self.drawing = drawing

    def interaction_objects(self):  # Проверяем попали ли мы в npc, если да, то убиваем его
        if self.player.shot and self.drawing.shot_animation_trigger:
            for obj in sorted(filter(lambda x: not x.is_dead, self.sprites.list_of_objects),
                              key=lambda obj: obj.distance_to_sprite):
                if obj.is_on_fire[1]:
                    if not obj.is_dead and not obj.is_immortal:
                        if ray_casting_npc(obj.x, obj.y, world_map, self.player.get_pos()):
                            death_sound = random.choice(obj.death_sound)
                            dist = obj.object_locate(self.player)[0]
                            death_sound.set_volume(300 / dist)
                            death_sound.play()
                            obj.is_dead = True
                            obj.play_death_animation()
                            self.drawing.shot_animation_trigger = False
                            self.check_win()
                    break

    def check_win(self):  # Проверка на победу
        if not list(filter(lambda x: x.type == 'npc' and not x.is_dead, self.sprites.list_of_objects)):
            self.drawing.running = False
            self.drawing.is_win = True
            pygame.mixer.Sound('sounds/win/win.mp3').play()

    # Движение врагов к игроку по прямой
    def npc_move(self, obj):
        if abs(sum(((obj.x - self.player.x) ** 2, (obj.y - self.player.y) ** 2)) ** 0.5) > tile_size * 0.4:
            dx = obj.x - self.player.get_pos()[0]
            dy = obj.y - self.player.get_pos()[1]
            obj.x = obj.x + 3 if dx < 0 else obj.x - 3
            obj.y = obj.y + 3 if dy < 0 else obj.y - 3
        else:
            if not self.player.god:
                random.choice(self.player.death_sounds).play()
                self.drawing.is_dead = True
                self.drawing.running = False

    def npc_action(self):  # Запускаем движение врагов
        for obj in self.sprites.list_of_objects:
            if obj.type == 'npc' and not obj.is_dead and ray_casting_npc(obj.x, obj.y, world_map,
                                                                         self.player.get_pos()):
                self.npc_move(obj)

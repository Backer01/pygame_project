import pygame
from collections import deque
from settings import *


class Sprites:
    def __init__(self):
        sound = pygame.mixer.Sound
        # Словарь типов спрайтов с их параметрами
        self.sprite_parameters = {
            'barrel': {
                'sprite': pygame.image.load('sprites/barrel/0.png').convert_alpha(),
                'viewing_angles': False,
                'shift': 1.8,
                'scale': (0.4, 0.4),
                'animation': False,
                'animation_dist': None,
                'animation_speed': None,
                'type': 'decor',
                'side': 20,
                'is_immortal': True,
                'death_animation': None,
                'death_sound': None,
            },
            'rock1': {
                'sprite': pygame.image.load('sprites/rocks/rock1.png').convert_alpha(),
                'viewing_angles': False,
                'shift': 2.8,
                'scale': (0.5, 0.35,),
                'animation': False,
                'animation_dist': None,
                'animation_speed': None,
                'type': 'decor',
                'side': 10,
                'is_immortal': True,
                'death_animation': None,
                'death_sound': None,
            },
            'rock2': {
                'sprite': pygame.image.load('sprites/rocks/rock2.png').convert_alpha(),
                'viewing_angles': False,
                'shift': 3.0,
                'scale': (0.35, 0.25,),
                'animation': False,
                'animation_dist': None,
                'animation_speed': None,
                'type': 'decor',
                'side': 10,
                'is_immortal': True,
                'death_animation': None,
                'death_sound': None,
            },
            'fire': {
                'sprite': pygame.image.load('sprites/fire/0.png').convert_alpha(),
                'viewing_angles': False,
                'shift': 3.0,
                'scale': (0.6, 0.6),
                'animation': deque(pygame.image.load(f'sprites/fire/{i}.png').convert_alpha() for i in range(60)),
                'animation_dist': 800,
                'animation_speed': 1,
                'type': 'decor',
                'side': 20,
                'is_immortal': True,
                'death_animation': None,
                'death_sound': None,
            },
            'pizza_monster': {
                'sprite': pygame.image.load('sprites/enemies/pizza_monster/base/pizza_monster.png').convert_alpha(),
                'viewing_angles': False,
                'shift': 0.4,
                'scale': (1.5, 0.85),
                'animation': False,
                'animation_dist': 800,
                'animation_speed': 5,
                'type': 'npc',
                'side': 40,
                'is_immortal': False,
                'death_animation': deque(
                    pygame.image.load(f'sprites/enemies/pizza_monster/death_animation/{i}.png').convert_alpha() for i in
                    range(4)),
                'death_sound': [sound('sounds/monster_death/death_sound1.mp3'),
                                sound('sounds/monster_death/death_sound2.mp3'),
                                sound('sounds/monster_death/death_sound3.mp3'),
                                sound('sounds/monster_death/death_sound4.mp3'),
                                ],
            },
            'soldier': {
                'sprite': pygame.image.load('sprites/enemies/soldier/base/enemy_soldier.png').convert_alpha(),
                'viewing_angles': False,
                'shift': 0.7,
                'scale': (1.3, 0.7),
                'animation': False,
                'animation_dist': 800,
                'animation_speed': 5,
                'type': 'npc',
                'side': 40,
                'is_immortal': False,
                'death_animation': deque(
                    pygame.image.load(f'sprites/enemies/soldier/death_animation/{i}.png').convert_alpha() for i in
                    range(4)),
                'death_sound': [sound('sounds/soldier_death/death_sound1.mp3'),
                                sound('sounds/soldier_death/death_sound2.mp3'),
                                ],
            },
        }
        # Спрайты расположенные на карте
        self.list_of_objects = [
            SpriteObject(self.sprite_parameters['barrel'], (3.1, 1.1)),
            SpriteObject(self.sprite_parameters['fire'], (3.1, 1.1), 0.1),
            SpriteObject(self.sprite_parameters['barrel'], (3.1, 1.9)),
            SpriteObject(self.sprite_parameters['barrel'], (20.1, 1.1)),
            SpriteObject(self.sprite_parameters['fire'], (20.1, 1.1), 0.1),
            SpriteObject(self.sprite_parameters['barrel'], (20.1, 1.9)),
            SpriteObject(self.sprite_parameters['fire'], (20.1, 1.9), 0.1),
            SpriteObject(self.sprite_parameters['fire'], (10.1, 1.1), shift=1, scale=(1.5, 0.6)),
            SpriteObject(self.sprite_parameters['rock1'], (4.1, 1.8)),
            SpriteObject(self.sprite_parameters['rock2'], (5.5, 1.1)),
            SpriteObject(self.sprite_parameters['rock2'], (6.7, 1.9)),
            SpriteObject(self.sprite_parameters['rock2'], (13, 4)),
            SpriteObject(self.sprite_parameters['rock2'], (5.6, 3.9)),
            SpriteObject(self.sprite_parameters['rock2'], (10.4, 7.9)),
            SpriteObject(self.sprite_parameters['rock2'], (9.7, 10.9)),
            SpriteObject(self.sprite_parameters['rock1'], (7.5, 1.1)),
            SpriteObject(self.sprite_parameters['rock1'], (21.1, 3.1)),
            SpriteObject(self.sprite_parameters['rock1'], (17.1, 6.1)),
            SpriteObject(self.sprite_parameters['rock1'], (4.1, 9.1)),
            SpriteObject(self.sprite_parameters['rock1'], (7.1, 7.1)),
            SpriteObject(self.sprite_parameters['rock1'], (8.1, 12.1)),

            SpriteObject(self.sprite_parameters['soldier'], (6.1, 1.5)),
            SpriteObject(self.sprite_parameters['pizza_monster'], (16.1, 1.5)),
            SpriteObject(self.sprite_parameters['pizza_monster'], (5.1, 3.5)),
            SpriteObject(self.sprite_parameters['pizza_monster'], (2, 9.0)),
            SpriteObject(self.sprite_parameters['pizza_monster'], (3, 5)),
            SpriteObject(self.sprite_parameters['pizza_monster'], (7, 6)),
            SpriteObject(self.sprite_parameters['pizza_monster'], (20, 10)),
            SpriteObject(self.sprite_parameters['pizza_monster'], (18, 6)),
            SpriteObject(self.sprite_parameters['soldier'], (10, 11)),
            SpriteObject(self.sprite_parameters['soldier'], (18, 12)),
            SpriteObject(self.sprite_parameters['soldier'], (22, 14)),
            SpriteObject(self.sprite_parameters['pizza_monster'], (22, 11)),
        ]

    @property
    def sprite_shot(self):
        return min([obj.is_on_fire for obj in filter(lambda x: not x.is_dead, self.list_of_objects)],
                   default=(float('inf'), 0))


class SpriteObject:
    def __init__(self, parameters, pos, shift=None, scale=None, is_dead=False):
        self.object = parameters['sprite']
        self.viewing_angles = parameters['viewing_angles']
        self.pos = pos[0] * tile_size, pos[1] * tile_size
        self.x, self.y = pos[0] * tile_size, pos[1] * tile_size
        self.is_dead = is_dead
        self.is_immortal = parameters['is_immortal']
        self.type = parameters['type']
        self.side = parameters['side']

        if shift:
            self.shift = shift
        else:
            self.shift = parameters['shift']
        if scale:
            self.scale = scale
        else:
            self.scale = parameters['scale']

        if parameters['animation']:
            self.animation = parameters['animation'].copy()
        else:
            self.animation = parameters['animation']
        self.animation_dist = parameters['animation_dist']
        self.animation_speed = parameters['animation_speed']
        self.animation_count = 0

        self.death_animation_count = 0
        if parameters['death_animation']:
            self.death_animation = parameters['death_animation'].copy()
        else:
            self.death_animation = parameters['death_animation']
        self.death_sound = parameters['death_sound']

        if self.viewing_angles:
            self.sprite_angles = [frozenset(range(i, i + 45)) for i in range(0, 360, 45)]
            self.sprite_positions = {angle: pos for angle, pos in zip(self.sprite_angles, self.object)}

    @property
    def is_on_fire(self):
        if center_ray - self.side // 2 < self.current_ray < center_ray + self.side // 2:
            return self.distance_to_sprite, self.proj_height
        return float('inf'), None

    def pos(self):
        return self.x - self.side // 2, self.y - self.side // 2

    def object_locate(self, player):
        dx, dy = self.x - player.x, self.y - player.y
        self.distance_to_sprite = (dx ** 2 + dy ** 2) ** 0.5

        self.theta = math.atan2(dy, dx)
        gamma = self.theta - player.angle
        if dx > 0 and 180 <= math.degrees(player.angle) <= 360 or dx < 0 and dy < 0:
            gamma += double_pi
        self.theta -= 1.4 * gamma

        delta_rays = int(gamma / delta_angle)
        self.current_ray = center_ray + delta_rays
        self.distance_to_sprite *= math.cos(half_fov - self.current_ray * delta_angle)

        fake_ray = self.current_ray + fake_rays
        if 0 <= fake_ray <= fake_rays_range and self.distance_to_sprite > 30:
            self.proj_height = min(int(proj_coeff / self.distance_to_sprite), height)
            sprite_width = int(self.proj_height * self.scale[0])
            sprite_height = int(self.proj_height * self.scale[1])
            half_sprite_width = sprite_width // 2
            half_sprite_height = sprite_height // 2
            shift = half_sprite_height * self.shift

            if self.is_dead:
                sprite_object = self.play_death_animation()
            else:
                sprite_object = self.sprite_animation()

            sprite_pos = (self.current_ray * scale_coeff - half_sprite_width, half_height - half_sprite_height + shift)
            sprite = pygame.transform.scale(sprite_object, (sprite_width, sprite_height))
            return self.distance_to_sprite, sprite, sprite_pos
        else:
            return False,

    def sprite_animation(self):
        if self.animation and self.distance_to_sprite < self.animation_dist:
            sprite_object = self.animation[0]
            if self.animation_count < self.animation_speed:
                self.animation_count += 1
            else:
                self.animation.rotate()
                self.animation_count = 0
            return sprite_object
        return self.object

    def play_death_animation(self):
        if len(self.death_animation):
            if self.death_animation_count < self.animation_speed:
                self.death_sprite = self.death_animation[0]
                self.death_animation_count += 1
            else:
                self.death_sprite = self.death_animation.popleft()
                self.death_animation_count = 0
        else:
            self.death_sprite = pygame.image.load('sprites/death/death.png')
        return self.death_sprite

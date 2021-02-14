from ray_casting import ray_casting_textures
from player import Player
from interactions import Interaction
from sprites import Sprites
from settings import *
from map import mini_map
from collections import deque
import sys
import datetime
import pygame


class Drawing:
    def __init__(self, screen, minimap_screen):
        self.screen = screen
        self.minimap_screen = minimap_screen
        self.font_fps = pygame.font.SysFont('Courier new', 36, bold=True)
        self.font_coords = pygame.font.SysFont('Courier new', 14, bold=True)
        # Список текстур игры
        self.textures = {
            1: pygame.image.load('textures/wall1.png').convert(),
            2: pygame.image.load('textures/wall2.png').convert(),
            3: pygame.image.load('textures/wooden_box.png').convert(),
            4: pygame.image.load('textures/mossy_wall1.png').convert(),
            5: pygame.image.load('textures/far_texture.png').convert(),
            'S1': pygame.image.load('textures/sky1.png').convert(),
            'S2': pygame.image.load('textures/sky2.png').convert(),
        }

        self.start_gun_sprite = pygame.image.load('sprites/gun/0.png').convert_alpha()
        self.gun_animation = deque(pygame.image.load(f'sprites/gun/{i}.png').convert_alpha() for i in range(15))
        self.shot_animation_count = 0
        self.shot_animation_length = 0
        self.shot_animation_speed = 3
        self.shot_animation_trigger = True
        self.shot_sound = pygame.mixer.Sound('sounds/gun/shot.mp3')

        self.explode = deque(pygame.image.load(f'sprites/explode_hit/{i}.png').convert_alpha() for i in range(7))
        self.explode_animation_count = 0

        self.player = Player()
        self.sprites = Sprites()
        self.interaction = Interaction(self.player, self.sprites, self)

        self.is_menu = True
        self.is_pause = False
        self.running = False
        self.is_win = False
        self.is_dead = False

    def new_game(self):
        self.gun_animation = deque(pygame.image.load(f'sprites/gun/{i}.png').convert_alpha() for i in range(15))
        self.shot_animation_count = 0
        self.shot_animation_length = 0
        self.shot_animation_speed = 3
        self.shot_animation_trigger = True

        self.explode = deque(pygame.image.load(f'sprites/explode_hit/{i}.png').convert_alpha() for i in range(7))
        self.explode_animation_count = 0

        self.player = Player()
        self.sprites = Sprites()
        self.interaction = Interaction(self.player, self.sprites, self)

    def background(self, angle):
        sky_offset = -10 * math.degrees(angle) % width  # накладывание текстуры неба
        self.screen.blit(self.textures['S1'], (sky_offset, 0))
        self.screen.blit(self.textures['S1'], (sky_offset - width, 0))
        pygame.draw.rect(self.screen, (48, 44, 40), (0, half_height, width, half_height))  # земля

    def walls(self, world_objects):  # Отрисовка игровых объектов (стен, спрайтов)
        for obj in sorted(world_objects, key=lambda x: x[0], reverse=True):
            if obj[0]:
                _, entity, entity_pos = obj
                self.screen.blit(entity, entity_pos)

    def fps(self, clock):
        render = self.font_fps.render(str(int(clock.get_fps())), True, pygame.Color('green'))
        self.screen.blit(render, (width - 60, 5))

    def coords(self, player):
        # Координаты игрока
        render1 = self.font_coords.render(str((round(player.x, 2), round(player.y, 2))), True, pygame.Color('black'))
        # Координаты клетки, в которой находится игрок
        render2 = self.font_coords.render(str((int(player.x) // tile_size, int(player.y) // tile_size)), True,
                                          pygame.Color('black'))
        self.screen.blit(render1, (minimap_width, 0))
        self.screen.blit(render2, (minimap_width, render1.get_height()))

    def minimap(self, player):
        self.minimap_screen.fill(pygame.Color('black'))
        for x, y in mini_map:  # Отрисовка мини-карты
            pygame.draw.rect(self.minimap_screen, pygame.Color('gray'), (x, y, mini_tile, mini_tile))

        pygame.draw.circle(self.minimap_screen, pygame.Color('green'),  # Отрисовка игрока на мини-карте
                           (player.x // map_scale // world_scale, player.y // map_scale // world_scale),
                           player_radius // map_scale // world_scale)
        # Отрисовка направления взгляда игрока на мини-карте
        pygame.draw.line(self.minimap_screen, pygame.Color('green'),
                         (player.x // map_scale // world_scale, player.y // map_scale // world_scale),
                         ((player.x // map_scale // world_scale + mini_tile * math.cos(player.angle),
                           player.y // map_scale // world_scale + mini_tile * math.sin(player.angle))))
        self.screen.blit(self.minimap_screen, (0, 0))

    def scope(self):
        pygame.draw.line(self.screen, pygame.Color('red'), (half_width - 5, half_height), (half_width + 5, half_height))
        pygame.draw.line(self.screen, pygame.Color('red'), (half_width, half_height - 5), (half_width, half_height + 5))

    def shot(self, player, shots):
        if player.shot:
            if self.shot_animation_length == 0:
                self.shot_sound.play()
            self.shot_proj = min(shots)[1] // 2
            self.bullet_explode()
            shot_sprite = self.gun_animation[0]
            self.screen.blit(shot_sprite, (half_width, height - shot_sprite.get_height()))
            self.shot_animation_count += 1
            if self.shot_animation_count == self.shot_animation_speed:
                self.shot_animation_count = 0
                self.shot_animation_length += 1
                self.gun_animation.rotate(-1)
                self.shot_animation_trigger = False
            if self.shot_animation_length == len(self.gun_animation):
                self.shot_animation_length = 0
                self.explode_animation_count = 0
                self.shot_animation_trigger = True
                player.shot = False
        else:
            self.screen.blit(self.start_gun_sprite, (half_width, height - self.start_gun_sprite.get_height()))

    def bullet_explode(self):
        if self.explode_animation_count < len(self.explode):
            explode = pygame.transform.scale(self.explode[0], (self.shot_proj, self.shot_proj))
            explode_rect = explode.get_rect()
            self.screen.blit(explode, (half_width - explode_rect.w // 2, half_height - explode_rect.h // 2))
            self.explode_animation_count += 1
            self.explode.rotate(-1)

    def menu(self):
        pygame.mouse.set_visible(True)
        background = pygame.image.load('textures/start_screen.png')
        title_font = pygame.font.Font('font/font.ttf', 150)
        title_render = title_font.render('PizzaHunt', True, pygame.Color('yellow'))
        button_font = pygame.font.Font('font/font1.otf', 100)
        start = button_font.render('Start', True, pygame.Color('white'))
        start_button = pygame.Rect(0, 0, 300, 125)
        start_button.center = half_width, half_height - 100
        end = button_font.render('Exit', True, pygame.Color('white'))
        end_button = pygame.Rect(0, 0, 300, 125)
        end_button.center = half_width, half_height + 75

        self.new_game()

        mouse_click = False

        clock = pygame.time.Clock()

        while self.is_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                    mouse_click = True

            self.screen.blit(background, (0, 0))
            self.screen.blit(title_render, (half_width - title_render.get_width() // 2, 0))

            pygame.draw.rect(self.screen, pygame.Color('orange'), start_button, border_radius=25, width=10)
            self.screen.blit(start, (start_button.center[0] - start.get_width() // 2,
                                     start_button.center[1] - start.get_height() // 2))

            pygame.draw.rect(self.screen, pygame.Color('orange'), end_button, border_radius=25, width=10)
            self.screen.blit(end, (end_button.center[0] - end.get_width() // 2,
                                   end_button.center[1] - end.get_height() // 2))

            mouse_pos = pygame.mouse.get_pos()

            if start_button.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, pygame.Color('orange'), start_button, border_radius=25)
                self.screen.blit(start, (start_button.center[0] - start.get_width() // 2,
                                         start_button.center[1] - start.get_height() // 2))
                if mouse_click:
                    self.running = True
                    self.is_menu = False

            elif end_button.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, pygame.Color('orange'), end_button, border_radius=25)
                self.screen.blit(end, (end_button.center[0] - end.get_width() // 2,
                                       end_button.center[1] - end.get_height() // 2))
                if mouse_click:
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()
            clock.tick(fps)

    def pause(self):
        pygame.mouse.set_visible(True)
        background = pygame.image.load('textures/start_screen.png')
        title_font = pygame.font.Font('font/font.ttf', 150)
        title_render = title_font.render('Pause', True, pygame.Color('yellow'))
        button_font = pygame.font.Font('font/font1.otf', 65)
        cont = button_font.render('Continue', True, pygame.Color('white'))
        cont_button = pygame.Rect(0, 0, 300, 125)
        cont_button.center = half_width, half_height - 100
        back_to_menu = button_font.render('Back to menu', True, pygame.Color('white'))
        back_to_menu_button = pygame.Rect(0, 0, 450, 125)
        back_to_menu_button.center = half_width, half_height + 75
        end = button_font.render('Exit', True, pygame.Color('white'))
        end_button = pygame.Rect(0, 0, 200, 125)
        end_button.center = half_width, half_height + 250

        mouse_click = False

        clock = pygame.time.Clock()

        while self.is_pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                    mouse_click = True

            self.screen.blit(background, (0, 0))
            self.screen.blit(title_render, (half_width - title_render.get_width() // 2, 0))

            pygame.draw.rect(self.screen, pygame.Color('orange'), cont_button, border_radius=25, width=10)
            self.screen.blit(cont, (cont_button.center[0] - cont.get_width() // 2,
                                    cont_button.center[1] - cont.get_height() // 2))

            pygame.draw.rect(self.screen, pygame.Color('orange'), back_to_menu_button, border_radius=25, width=10)
            self.screen.blit(back_to_menu, (back_to_menu_button.center[0] - back_to_menu.get_width() // 2,
                                            back_to_menu_button.center[1] - back_to_menu.get_height() // 2))

            pygame.draw.rect(self.screen, pygame.Color('orange'), end_button, border_radius=25, width=10)
            self.screen.blit(end, (end_button.center[0] - end.get_width() // 2,
                                   end_button.center[1] - end.get_height() // 2))

            mouse_pos = pygame.mouse.get_pos()

            if cont_button.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, pygame.Color('orange'), cont_button, border_radius=25)
                self.screen.blit(cont, (cont_button.center[0] - cont.get_width() // 2,
                                        cont_button.center[1] - cont.get_height() // 2))
                if mouse_click:
                    self.running = True
                    self.is_pause = False
            elif back_to_menu_button.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, pygame.Color('orange'), back_to_menu_button, border_radius=25)
                self.screen.blit(back_to_menu, (back_to_menu_button.center[0] - back_to_menu.get_width() // 2,
                                                back_to_menu_button.center[1] - back_to_menu.get_height() // 2))
                if mouse_click:
                    self.is_pause = False
                    self.is_menu = True
            elif end_button.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, pygame.Color('orange'), end_button, border_radius=25)
                self.screen.blit(end, (end_button.center[0] - end.get_width() // 2,
                                       end_button.center[1] - end.get_height() // 2))
                if mouse_click:
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()
            clock.tick(fps)

    def win(self):
        pygame.mouse.set_visible(True)
        background = pygame.image.load('textures/start_screen.png')
        title_font = pygame.font.Font('font/font.ttf', 150)
        title_render = title_font.render('You win!', True, pygame.Color('yellow'))
        button_font = pygame.font.Font('font/font1.otf', 65)
        cont = button_font.render('Continue', True, pygame.Color('white'))
        cont_button = pygame.Rect(0, 0, 300, 125)
        cont_button.center = half_width, half_height - 100
        back_to_menu = button_font.render('Back to menu', True, pygame.Color('white'))
        back_to_menu_button = pygame.Rect(0, 0, 450, 125)
        back_to_menu_button.center = half_width, half_height + 75
        end = button_font.render('Exit', True, pygame.Color('white'))
        end_button = pygame.Rect(0, 0, 200, 125)
        end_button.center = half_width, half_height + 250

        mouse_click = False

        clock = pygame.time.Clock()

        while self.is_win:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                    mouse_click = True

            self.screen.blit(background, (0, 0))
            self.screen.blit(title_render, (half_width - title_render.get_width() // 2, 0))

            pygame.draw.rect(self.screen, pygame.Color('orange'), cont_button, border_radius=25, width=10)
            self.screen.blit(cont, (cont_button.center[0] - cont.get_width() // 2,
                                    cont_button.center[1] - cont.get_height() // 2))

            pygame.draw.rect(self.screen, pygame.Color('orange'), back_to_menu_button, border_radius=25, width=10)
            self.screen.blit(back_to_menu, (back_to_menu_button.center[0] - back_to_menu.get_width() // 2,
                                            back_to_menu_button.center[1] - back_to_menu.get_height() // 2))

            pygame.draw.rect(self.screen, pygame.Color('orange'), end_button, border_radius=25, width=10)
            self.screen.blit(end, (end_button.center[0] - end.get_width() // 2,
                                   end_button.center[1] - end.get_height() // 2))

            mouse_pos = pygame.mouse.get_pos()

            if cont_button.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, pygame.Color('orange'), cont_button, border_radius=25)
                self.screen.blit(cont, (cont_button.center[0] - cont.get_width() // 2,
                                        cont_button.center[1] - cont.get_height() // 2))
                if mouse_click:
                    self.running = True
                    self.is_win = False
            elif back_to_menu_button.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, pygame.Color('orange'), back_to_menu_button, border_radius=25)
                self.screen.blit(back_to_menu, (back_to_menu_button.center[0] - back_to_menu.get_width() // 2,
                                                back_to_menu_button.center[1] - back_to_menu.get_height() // 2))
                if mouse_click:
                    self.is_win = False
                    self.is_menu = True
            elif end_button.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, pygame.Color('orange'), end_button, border_radius=25)
                self.screen.blit(end, (end_button.center[0] - end.get_width() // 2,
                                       end_button.center[1] - end.get_height() // 2))
                if mouse_click:
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()
            clock.tick(fps)

    def death(self):
        pygame.mouse.set_visible(True)
        background = pygame.image.load('textures/start_screen.png')
        title_font = pygame.font.Font('font/font.ttf', 150)
        title_render = title_font.render('You died!', True, pygame.Color('yellow'))
        button_font = pygame.font.Font('font/font1.otf', 65)
        back_to_menu = button_font.render('Back to menu', True, pygame.Color('white'))
        back_to_menu_button = pygame.Rect(0, 0, 450, 125)
        back_to_menu_button.center = half_width, half_height - 100
        end = button_font.render('Exit', True, pygame.Color('white'))
        end_button = pygame.Rect(0, 0, 300, 125)
        end_button.center = half_width, half_height + 75

        self.new_game()

        mouse_click = False

        clock = pygame.time.Clock()

        while self.is_dead:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
                    mouse_click = True

            self.screen.blit(background, (0, 0))
            self.screen.blit(title_render, (half_width - title_render.get_width() // 2, 0))

            pygame.draw.rect(self.screen, pygame.Color('orange'), back_to_menu_button, border_radius=25, width=10)
            self.screen.blit(back_to_menu, (back_to_menu_button.center[0] - back_to_menu.get_width() // 2,
                                            back_to_menu_button.center[1] - back_to_menu.get_height() // 2))

            pygame.draw.rect(self.screen, pygame.Color('orange'), end_button, border_radius=25, width=10)
            self.screen.blit(end, (end_button.center[0] - end.get_width() // 2,
                                   end_button.center[1] - end.get_height() // 2))

            mouse_pos = pygame.mouse.get_pos()

            if back_to_menu_button.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, pygame.Color('orange'), back_to_menu_button, border_radius=25)
                self.screen.blit(back_to_menu, (back_to_menu_button.center[0] - back_to_menu.get_width() // 2,
                                                back_to_menu_button.center[1] - back_to_menu.get_height() // 2))
                if mouse_click:
                    self.is_dead = False
                    self.is_menu = True

            elif end_button.collidepoint(mouse_pos):
                pygame.draw.rect(self.screen, pygame.Color('orange'), end_button, border_radius=25)
                self.screen.blit(end, (end_button.center[0] - end.get_width() // 2,
                                       end_button.center[1] - end.get_height() // 2))
                if mouse_click:
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()
            clock.tick(fps)

    def game(self):
        mouse_control = False
        clock = pygame.time.Clock()

        while self.running:

            self.screen.fill(pygame.Color('black'))
            self.background(self.player.angle)  # Отрисовка земли и неба
            walls, wall_shot = ray_casting_textures(self.player, self.textures)
            self.walls(walls + [obj.object_locate(self.player) for obj in self.sprites.list_of_objects])
            self.minimap(self.player)  # Отрисовка мини-карты
            self.coords(self.player)  # Отрисовка координта игрока
            self.fps(clock)  # Отрисовка фпс
            self.shot(self.player, [wall_shot, self.sprites.sprite_shot])  # Отрисовка взрыва от попадания
            self.scope()  # Отрисовка прицела

            self.interaction.interaction_objects()  # Взаимодействие с npc
            self.interaction.npc_action()  # Передвижение npc

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                    self.is_pause = True

                # Выключение и включение управления мышью
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_RIGHT:
                    mouse_control = not mouse_control
                    pygame.mouse.set_visible(not pygame.mouse.get_visible())

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT and not self.player.shot:
                    self.player.shot = True

                # Читы
                if event.type == pygame.KEYDOWN and event.key == pygame.K_z:  # noclip - прохождение через стены
                    self.player.noclip = not self.player.noclip
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:  # speedhack - ускорение
                    self.player.speedhack = not self.player.speedhack
                if event.type == pygame.KEYDOWN and event.key == pygame.K_g:  # god - бессметрие
                    self.player.god = not self.player.god
                if event.type == pygame.KEYDOWN and event.key == pygame.K_x:  # xray - прозрачные стены
                    self.player.xray = not self.player.xray
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:  # Автопобеда
                    for el in self.sprites.list_of_objects:
                        if el.type == 'npc':
                            el.is_dead = True
                    self.interaction.check_win()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F2:  # Создание скриншота
                    pygame.image.save(self.screen, f'screenshots/{str(datetime.datetime.now()).replace(":", ".")}.png')

            self.player.move()
            if mouse_control:
                self.player.mouse_control()

            pygame.display.flip()
            clock.tick(fps)

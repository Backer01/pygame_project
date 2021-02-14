import math

# game settings
width, height = 1200, 800
size = width, height
half_width = width // 2
half_height = height // 2
tile_size = 100
fps = 60

# player settings
player_position = tile_size * 1.5, tile_size * 1.5
player_velocity = 5
player_angle = 0
player_radius = 30

# texture settings
texture_width = 1200
texture_height = 1200
texture_scale = texture_width // tile_size

# minimap settings
world_scale = 2  # Во сколько раз мир больше стандартного (12х8)
map_scale = 5
minimap_width = width // map_scale
minimap_height = height // map_scale
minisize = minimap_width, minimap_height
mini_tile = tile_size // map_scale // world_scale

# ray casting settings
fov = math.pi / 3
half_fov = fov / 2
# Кол-во выпускаемых лучей из игрока для проецирования, чем больше тем лучше качество, но ниже фпс, от этого числа
# зависит размер проекции стен
num_rays = 600
delta_angle = fov / num_rays
distance = 1 * num_rays / (2 * math.tan(half_fov))  # Меняет размер проекции стен
proj_coeff = distance * tile_size
scale_coeff = width // num_rays

# sprite settings
double_pi = math.pi * 2
center_ray = num_rays // 2 - 1
fake_rays = 100  # Нужны, чтобы спрайты не пропадали после того как их половина вне экрана
fake_rays_range = num_rays - 1 + 2 * num_rays

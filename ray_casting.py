from settings import *
from map import world_map, map_height, map_width
from numba import njit
import pygame


@njit(fastmath=True, cache=True)
def mapping(x, y):  # Функция для расчёта левого верхнего угла клетки
    return (x // tile_size) * tile_size, (y // tile_size) * tile_size


# Возвращает параметры стен для их дальнейшей отрисовки
# njit нужен для ускорения вычислений, numba не работает с классами, поэтому делим функцию на 2 части: с тяжёлыми
# расчётами и с расчётами связанными с текстурами
@njit(fastmath=True, cache=True)
def ray_casting(player_pos, player_angle, world_map):
    calculated_walls = []
    texture_vert, texture_hor = 5, 5  # Текстуры, которые должны отрисоваваться, если не хватает прорисовки
    angle = player_angle - half_fov
    start_x, start_y = player_pos
    xm, ym = mapping(start_x, start_y)
    for ray in range(num_rays):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        # Находим пересечения с вертикалями
        x, direct_x = (xm + tile_size, 1) if cos_a >= 0 else (xm, -1)
        for i in range(0, map_width, tile_size):  # От значения map_width зависит дальность прорисовки
            depth_vert = (x - start_x) / cos_a
            y_vert = start_y + depth_vert * sin_a
            tile_vert = mapping(x + direct_x, y_vert)
            if tile_vert in world_map:
                texture_vert = world_map[tile_vert]
                break
            x += direct_x * tile_size

        # Находим пересечения с горизонталями
        y, direct_y = (ym + tile_size, 1) if sin_a >= 0 else (ym, -1)
        for i in range(0, map_height, tile_size):  # От значения map_height зависит дальность прорисовки
            depth_hor = (y - start_y) / sin_a
            x_hor = start_x + depth_hor * cos_a
            tile_hor = mapping(x_hor, y + direct_y)
            if tile_hor in world_map:
                texture_hor = world_map[tile_hor]
                break
            y += direct_y * tile_size

        # Проецируем 3d на 2d
        depth, offset, texture = (depth_vert, y_vert, texture_vert) if depth_vert < depth_hor \
            else (depth_hor, x_hor, texture_hor)
        offset = int(offset) % tile_size
        depth *= math.cos(player_angle - angle)
        depth = max(depth, 0.00001)
        proj_height = int(proj_coeff / depth)

        calculated_walls.append((depth, offset, proj_height, texture))
        angle += delta_angle
    return calculated_walls


def ray_casting_textures(player, textures):
    calculated_walls = ray_casting(player.get_pos(), player.angle, world_map)
    wall_shot = calculated_walls[center_ray][0], calculated_walls[center_ray][2]
    walls = []
    for ray, calculated_values in enumerate(calculated_walls):
        depth, offset, proj_height, texture = calculated_values

        if proj_height > height:
            coeff = proj_height / height
            texture_proj_height = texture_height / coeff
            wall_column = textures[texture].subsurface(offset * texture_scale,
                                                       texture_height // 2 - texture_proj_height // 2, texture_scale,
                                                       texture_proj_height)
            wall_column = pygame.transform.scale(wall_column, (scale_coeff, height))
            wall_pos = (ray * scale_coeff, 0)
        else:
            wall_column = textures[texture].subsurface(offset * texture_scale, 0, texture_scale, texture_height)
            wall_column = pygame.transform.scale(wall_column, (scale_coeff, proj_height))
            wall_pos = (ray * scale_coeff, half_height - proj_height // 2)
        if player.xray:
            wall_column.set_alpha(50)

        walls.append((depth, wall_column, wall_pos))
    return walls, wall_shot

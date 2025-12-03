import math
import time
import os
import sys
import random

def rotate_x(y, z, angle):
    rad = angle * math.pi / 180
    cosa = math.cos(rad)
    sina = math.sin(rad)
    return y * cosa - z * sina, y * sina + z * cosa

def rotate_y(x, z, angle):
    rad = angle * math.pi / 180
    cosa = math.cos(rad)
    sina = math.sin(rad)
    return x * cosa - z * sina, x * sina + z * cosa

def draw_line(buffer, x0, y0, x1, y1, width, height, char):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        if 0 <= x0 < width and 0 <= y0 < height:
            buffer[y0][x0] = char
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

def create_matrix_rain(width, height, rain_drops):
    for drop in rain_drops:
        if random.random() < 0.08:
            drop['x'] = random.randint(0, width - 1)
            drop['y'] = 0
            drop['length'] = random.randint(3, 8)
            drop['speed'] = random.uniform(0.3, 1.5)
        drop['y'] += drop['speed']
        if drop['y'] > height + drop['length']:
            drop['y'] = -drop['length']

def draw_matrix_rain(buffer, width, height, rain_drops):
    matrix_chars = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789"
    green_shades = ["\033[2;32m", "\033[32m", "\033[1;32m"]
    
    for drop in rain_drops:
        for i in range(drop['length']):
            y = int(drop['y'] - i)
            x = drop['x']
            if 0 <= y < height and 0 <= x < width and buffer[y][x] == ' ':
                char = random.choice(matrix_chars)
                color = green_shades[min(i, len(green_shades) - 1)]
                buffer[y][x] = f"{color}{char}\033[0m"

def main():
    width, height = 80, 30
    radius, lat_steps, lon_steps = 2.0, 10, 14
    
    vertices, edges = [], []
    for i in range(lat_steps + 1):
        phi = math.pi * i / lat_steps
        for j in range(lon_steps):
            theta = 2 * math.pi * j / lon_steps
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.sin(phi) * math.sin(theta)
            z = radius * math.cos(phi)
            vertices.append([x, y, z])
            
            p_idx = i * lon_steps + j
            next_j = (j + 1) % lon_steps
            edges.append((p_idx, i * lon_steps + next_j))
            if i < lat_steps:
                edges.append((p_idx, (i + 1) * lon_steps + j))

    bright_green, green, dim_green, reset = "\033[1;32m", "\033[32m", "\033[2;32m", "\033[0m"
    
    rain_drops = [{'x': random.randint(0, width - 1), 'y': random.randint(-15, height), 
                   'length': random.randint(3, 8), 'speed': random.uniform(0.3, 1.5)} 
                  for _ in range(width // 4)]
    
    angle_x = angle_y = 0
    
    try:
        while True:
            buffer = [[' '] * width for _ in range(height)]
            create_matrix_rain(width, height, rain_drops)
            draw_matrix_rain(buffer, width, height, rain_drops)
            
            projected_points = []
            for v in vertices:
                x, y, z = v
                y, z = rotate_x(y, z, angle_x)
                x, z = rotate_y(x, z, angle_y)
                z_dist = z + 4
                if z_dist <= 0: z_dist = 0.1
                xp = int(x * 12 / z_dist) + width // 2
                yp = int(y * 6 / z_dist) + height // 2
                projected_points.append((xp, yp))
            
            for i, edge in enumerate(edges):
                p1, p2 = projected_points[edge[0]], projected_points[edge[1]]
                if (0 <= p1[0] < width or 0 <= p2[0] < width) and (0 <= p1[1] < height or 0 <= p2[1] < height):
                    color = [dim_green, green, bright_green][i % 3]
                    char = ['░', '▒', '█'][i % 3]
                    draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height, color + char + reset)
            
            for p in projected_points:
                if 0 <= p[0] < width and 0 <= p[1] < height:
                    buffer[p[1]][p[0]] = f"{bright_green}◉{reset}"

            output = ["\033[H\033[2J", f"{bright_green}{'█' * 15} MATRIX SPHERE {'█' * 15}{reset}".center(width + 20),
                     f"{green}Reality is not what it seems...{reset}".center(width + 20), ""]
            output.extend("".join(row) for row in buffer)
            
            sys.stdout.write("\n".join(output))
            sys.stdout.flush()
            
            angle_x += 1.2
            angle_y += 1.8
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print(f"\n{bright_green}>>> MATRIX SPHERE TERMINATED <<<{reset}")

if __name__ == "__main__":
    os.system('clear')
    main()

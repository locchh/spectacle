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
    matrix_chars = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789"
    
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
            
            if 0 <= y < height and 0 <= x < width:
                if buffer[y][x] == ' ':
                    char = random.choice(matrix_chars)
                    color_idx = min(i, len(green_shades) - 1)
                    color = green_shades[color_idx]
                    buffer[y][x] = f"{color}{char}\033[0m"

def main():
    width, height = 80, 30
    
    radius = 1.8
    thickness = 0.25
    steps = 16
    
    vertices_front = []
    vertices_back = []
    
    for i in range(steps):
        theta = 2 * math.pi * i / steps
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        vertices_front.append([x, y, thickness])
        vertices_back.append([x, y, -thickness])
    
    all_vertices = vertices_front + vertices_back
    
    # Matrix colors
    bright_green = "\033[1;32m"
    green = "\033[32m"
    dim_green = "\033[2;32m"
    reset = "\033[0m"
    
    # Initialize matrix rain
    rain_drops = []
    for _ in range(width // 4):
        rain_drops.append({
            'x': random.randint(0, width - 1),
            'y': random.randint(-15, height),
            'length': random.randint(3, 8),
            'speed': random.uniform(0.3, 1.5)
        })
    
    angle_x = angle_y = 0
    
    try:
        while True:
            buffer = [[' '] * width for _ in range(height)]
            
            # Draw matrix rain first
            create_matrix_rain(width, height, rain_drops)
            draw_matrix_rain(buffer, width, height, rain_drops)
            
            projected_points = []
            for v in all_vertices:
                x, y, z = v
                y, z = rotate_x(y, z, angle_x)
                x, z = rotate_y(x, z, angle_y)
                
                z_dist = z + 4
                if z_dist <= 0: z_dist = 0.1
                
                xp = int(x * 15 / z_dist) + width // 2
                yp = int(y * 8 / z_dist) + height // 2
                
                projected_points.append((xp, yp))
            
            proj_front = projected_points[:steps]
            proj_back = projected_points[steps:]
            
            for i in range(steps):
                next_i = (i + 1) % steps
                
                # Front face - bright green
                p1, p2 = proj_front[i], proj_front[next_i]
                draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height, bright_green + '█' + reset)
                
                # Back face - dim green
                p3, p4 = proj_back[i], proj_back[next_i]
                draw_line(buffer, p3[0], p3[1], p4[0], p4[1], width, height, dim_green + '░' + reset)
                
                # Connecting edges
                draw_line(buffer, p1[0], p1[1], p3[0], p3[1], width, height, green + '▓' + reset)

            # Matrix UI
            output = []
            output.append("\033[H\033[2J")
            
            title = f"{bright_green}{'█' * 15} MATRIX COIN {'█' * 15}{reset}"
            subtitle = f"{green}Wake up, Neo... The coin has you...{reset}"
            
            output.append(title.center(width + 20))
            output.append(subtitle.center(width + 20))
            output.append("")
            
            for row in buffer:
                output.append("".join(row))
            
            sys.stdout.write("\n".join(output))
            sys.stdout.flush()
            
            angle_x += 4
            angle_y += 1.8
            
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print(f"\n{bright_green}>>> DISCONNECTED FROM MATRIX <<<{reset}")

if __name__ == "__main__":
    os.system('clear')
    main()

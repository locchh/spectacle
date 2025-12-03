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

def rotate_z(x, y, angle):
    rad = angle * math.pi / 180
    cosa = math.cos(rad)
    sina = math.sin(rad)
    return x * cosa - y * sina, x * sina + y * cosa

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
    """Create falling matrix characters"""
    matrix_chars = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789"
    
    for drop in rain_drops:
        if random.random() < 0.1:  # New drop
            drop['x'] = random.randint(0, width - 1)
            drop['y'] = 0
            drop['length'] = random.randint(5, 15)
            drop['speed'] = random.uniform(0.5, 2.0)
        
        drop['y'] += drop['speed']
        
        if drop['y'] > height + drop['length']:
            drop['y'] = -drop['length']

def draw_matrix_rain(buffer, width, height, rain_drops):
    """Draw the matrix rain effect"""
    matrix_chars = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789"
    green_shades = ["\033[2;32m", "\033[32m", "\033[1;32m", "\033[1;37m"]
    
    for drop in rain_drops:
        for i in range(drop['length']):
            y = int(drop['y'] - i)
            x = drop['x']
            
            if 0 <= y < height and 0 <= x < width:
                if buffer[y][x] == ' ':  # Don't overwrite cube
                    char = random.choice(matrix_chars)
                    # Brighter at the head of the drop
                    color_idx = min(i, len(green_shades) - 1)
                    color = green_shades[color_idx]
                    buffer[y][x] = f"{color}{char}\033[0m"

def main():
    width, height = 90, 35
    
    vertices = [
        [-1.2, -1.2, -1.2], [1.2, -1.2, -1.2], [1.2, 1.2, -1.2], [-1.2, 1.2, -1.2],
        [-1.2, -1.2, 1.2], [1.2, -1.2, 1.2], [1.2, 1.2, 1.2], [-1.2, 1.2, 1.2]
    ]
    
    edges = [
        (0,1), (1,2), (2,3), (3,0),
        (4,5), (5,6), (6,7), (7,4),
        (0,4), (1,5), (2,6), (3,7)
    ]
    
    # Matrix colors
    bright_green = "\033[1;32m"
    green = "\033[32m"
    dim_green = "\033[2;32m"
    white = "\033[1;37m"
    reset = "\033[0m"
    
    # Initialize matrix rain
    rain_drops = []
    for _ in range(width // 3):
        rain_drops.append({
            'x': random.randint(0, width - 1),
            'y': random.randint(-20, height),
            'length': random.randint(5, 15),
            'speed': random.uniform(0.5, 2.0)
        })
    
    angle_x = angle_y = angle_z = 0
    
    try:
        while True:
            buffer = [[' '] * width for _ in range(height)]
            
            # Draw matrix rain first
            create_matrix_rain(width, height, rain_drops)
            draw_matrix_rain(buffer, width, height, rain_drops)
            
            projected_points = []
            for v in vertices:
                x, y, z = v
                y, z = rotate_x(y, z, angle_x)
                x, z = rotate_y(x, z, angle_y)
                x, y = rotate_z(x, y, angle_z)
                
                z_dist = z + 4
                if z_dist <= 0: z_dist = 0.1
                
                xp = int(x * 20 / z_dist) + width // 2
                yp = int(y * 10 / z_dist) + height // 2
                
                projected_points.append((xp, yp))
            
            # Draw cube with matrix styling
            for i, edge in enumerate(edges):
                p1, p2 = projected_points[edge[0]], projected_points[edge[1]]
                
                # Matrix-style cube rendering
                if i < 4:  # Back face - dimmer
                    char = f"{dim_green}░{reset}"
                elif i < 8:  # Front face - brighter
                    char = f"{bright_green}█{reset}"
                else:  # Connecting edges
                    char = f"{green}▓{reset}"
                
                draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height, char)
                
            # Matrix-style vertices
            for p in projected_points:
                if 0 <= p[0] < width and 0 <= p[1] < height:
                    buffer[p[1]][p[0]] = f"{white}◉{reset}"

            # Matrix UI
            output = []
            output.append("\033[H\033[2J")
            
            # Matrix-style title
            title = f"{bright_green}{'█' * 20} THE MATRIX CUBE {'█' * 20}{reset}"
            subtitle = f"{green}Wake up, Neo... The cube has you...{reset}"
            
            output.append(title.center(width + 20))
            output.append(subtitle.center(width + 20))
            output.append("")
            
            for row in buffer:
                output.append("".join(row))
            
            # Matrix-style status
            status = f"{dim_green}REALITY.EXE LOADING... ANGLE_X: {angle_x:.1f}°{reset}"
            output.append("")
            output.append(status.center(width + 20))
            
            sys.stdout.write("\n".join(output))
            sys.stdout.flush()
            
            angle_x += 1.5
            angle_y += 2.2
            angle_z += 0.8
            
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print(f"\n{bright_green}>>> DISCONNECTED FROM THE MATRIX <<<{reset}")

if __name__ == "__main__":
    os.system('clear')
    main()

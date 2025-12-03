import math
import time
import os
import sys

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

def draw_line(buffer, x0, y0, x1, y1, width, height, char='.'):
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

def main():
    width, height = 80, 25
    
    radius = 1.8
    lat_steps = 8
    lon_steps = 12
    
    vertices = []
    edges = []
    
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

    # Retro colors
    amber = "\033[33m"
    green = "\033[32m"
    reset = "\033[0m"
    
    angle_x = angle_y = angle_z = 0
    frame = 0
    
    try:
        while True:
            buffer = [[' '] * width for _ in range(height)]
            
            projected_points = []
            for v in vertices:
                x, y, z = v
                y, z = rotate_x(y, z, angle_x)
                x, z = rotate_y(x, z, angle_y)
                x, y = rotate_z(x, y, angle_z)
                
                z_dist = z + 4
                if z_dist <= 0: z_dist = 0.1
                
                xp = int(x * 12 / z_dist) + width // 2
                yp = int(y * 6 / z_dist) + height // 2
                
                projected_points.append((xp, yp))
            
            # Draw edges with retro styling
            for i, edge in enumerate(edges):
                p1, p2 = projected_points[edge[0]], projected_points[edge[1]]
                
                if (0 <= p1[0] < width or 0 <= p2[0] < width) and \
                   (0 <= p1[1] < height or 0 <= p2[1] < height):
                    
                    color = amber if i % 2 == 0 else green
                    char = '*' if i % 3 == 0 else '.'
                    draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height, color + char + reset)
            
            for p in projected_points:
                if 0 <= p[0] < width and 0 <= p[1] < height:
                    buffer[p[1]][p[0]] = amber + 'o' + reset

            # Retro UI
            output = []
            output.append("\033[H\033[2J")
            
            title = f"{green}╔══════════════════════════════════════════════════════════════════════════════╗{reset}"
            subtitle = f"{green}║{amber}                           >>> RETRO SPHERE v1.0 <<<                          {green}║{reset}"
            status = f"{green}║{amber}                          FRAME: {frame:06d} | ROTATING...                         {green}║{reset}"
            bottom = f"{green}╚══════════════════════════════════════════════════════════════════════════════╝{reset}"
            
            output.append(title)
            output.append(subtitle)
            output.append(status)
            output.append(bottom)
            
            for row in buffer:
                output.append("".join(row))
            
            sys.stdout.write("\n".join(output))
            sys.stdout.flush()
            
            angle_x += 1
            angle_y += 1.5
            angle_z += 0.5
            frame += 1
            
            time.sleep(0.08)
            
    except KeyboardInterrupt:
        print(f"\n{amber}>>> SPHERE ROTATION HALTED <<<{reset}")

if __name__ == "__main__":
    os.system('clear')
    main()

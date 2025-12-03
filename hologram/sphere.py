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

def draw_line(buffer, x0, y0, x1, y1, width, height, char, glitch_phase):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        if 0 <= x0 < width and 0 <= y0 < height:
            if random.random() < 0.05:
                glitch_chars = ['▓', '▒', '░', '█', '▄', '▀']
                buffer[y0][x0] = random.choice(glitch_chars)
            else:
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

def add_hologram_interference(buffer, width, height, phase):
    for y in range(height):
        for x in range(width):
            if buffer[y][x] == ' ' and random.random() < 0.02:
                interference = math.sin(x * 0.3 + phase * 0.1) * math.sin(y * 0.2 + phase * 0.08)
                if interference > 0.8:
                    buffer[y][x] = '░'

def add_scan_lines(buffer, width, height, phase):
    scan_line = int(phase * 0.5) % height
    for x in range(width):
        if buffer[scan_line][x] == ' ':
            buffer[scan_line][x] = '─'

def main():
    width, height = 75, 30
    radius, lat_steps, lon_steps = 2.2, 10, 14
    
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

    holo_colors = {
        'bright': "\033[1;96m",
        'normal': "\033[36m", 
        'dim': "\033[2;36m",
        'flicker': "\033[5;96m"
    }
    reset = "\033[0m"
    
    angle_x = angle_y = glitch_phase = 0
    stability = 1.0
    
    try:
        while True:
            buffer = [[' '] * width for _ in range(height)]
            
            if random.random() < 0.02:
                stability = random.uniform(0.3, 1.0)
            else:
                stability = min(1.0, stability + 0.01)
            
            add_hologram_interference(buffer, width, height, glitch_phase)
            add_scan_lines(buffer, width, height, glitch_phase)
            
            projected_points = []
            for v in vertices:
                x, y, z = v
                
                if stability < 0.8:
                    x += random.uniform(-0.1, 0.1)
                    y += random.uniform(-0.1, 0.1)
                    z += random.uniform(-0.1, 0.1)
                
                y, z = rotate_x(y, z, angle_x)
                x, z = rotate_y(x, z, angle_y)
                z_dist = z + 4.5
                if z_dist <= 0: z_dist = 0.1
                xp = int(x * 13 / z_dist) + width // 2
                yp = int(y * 6 / z_dist) + height // 2
                projected_points.append((xp, yp))
            
            for i, edge in enumerate(edges):
                p1, p2 = projected_points[edge[0]], projected_points[edge[1]]
                
                if (0 <= p1[0] < width or 0 <= p2[0] < width) and (0 <= p1[1] < height or 0 <= p2[1] < height):
                    if stability > 0.9:
                        color = holo_colors['bright']
                        char = '█'
                    elif stability > 0.7:
                        color = holo_colors['normal']
                        char = '▓'
                    elif stability > 0.5:
                        color = holo_colors['dim']
                        char = '▒'
                    else:
                        color = holo_colors['flicker']
                        char = '░'
                    
                    if random.random() < (1 - stability) * 0.3:
                        continue
                    
                    draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height, 
                             color + char + reset, glitch_phase)
                
            for i, p in enumerate(projected_points):
                if 0 <= p[0] < width and 0 <= p[1] < height:
                    if random.random() < stability:
                        vertex_color = holo_colors['bright'] if stability > 0.8 else holo_colors['normal']
                        vertex_char = '◉' if stability > 0.7 else '○'
                        buffer[p[1]][p[0]] = f"{vertex_color}{vertex_char}{reset}"

            output = ["\033[H\033[2J"]
            
            title_color = holo_colors['bright'] if stability > 0.8 else holo_colors['flicker']
            if stability < 0.5 and random.random() < 0.3:
                title = f"{title_color}H0L0GR4M SPH3R3 PR0J3CT10N{reset}"
            else:
                title = f"{title_color}HOLOGRAM SPHERE PROJECTION{reset}"
            
            subtitle = f"{holo_colors['normal']}◊ Quantum Orb Display Technology ◊{reset}"
            
            output.append(title.center(width + 20))
            output.append(subtitle.center(width + 20))
            output.append("")
            output.extend("".join(row) for row in buffer)
            
            stability_bar = "█" * int(stability * 10) + "░" * (10 - int(stability * 10))
            status_color = holo_colors['bright'] if stability > 0.8 else holo_colors['dim']
            
            status = f"{status_color}STABILITY: [{stability_bar}] {stability*100:.1f}%{reset}"
            projection = f"{holo_colors['normal']}SPHERE PROJECTION: ACTIVE | VERTICES: {len(vertices)}{reset}"
            
            output.append("")
            output.append(status.center(width + 20))
            output.append(projection.center(width + 20))
            
            if random.random() < 0.01:
                messages = ["RECALIBRATING SPHERE MATRIX...", "QUANTUM FIELD FLUCTUATION...", 
                           "STABILIZING ORB PROJECTION...", "DIMENSIONAL SYNC COMPLETE..."]
                msg = random.choice(messages)
                output.append(f"{holo_colors['flicker']}{msg}{reset}".center(width + 20))
            
            sys.stdout.write("\n".join(output))
            sys.stdout.flush()
            
            speed_mod = stability * 0.5 + 0.5
            angle_x += 1.5 * speed_mod
            angle_y += 2.2 * speed_mod
            glitch_phase += 1
            
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print(f"\n{holo_colors['flicker']}>>> HOLOGRAM SPHERE TERMINATED <<<{reset}")

if __name__ == "__main__":
    os.system('clear')
    main()

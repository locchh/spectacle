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

def get_plasma_color(x, y, time_phase):
    wave1 = math.sin(x * 0.1 + time_phase * 0.05)
    wave2 = math.sin(y * 0.08 + time_phase * 0.03)
    wave3 = math.sin((x + y) * 0.06 + time_phase * 0.04)
    plasma_value = (wave1 + wave2 + wave3) / 3
    
    if plasma_value > 0.6:
        return "\033[38;5;226m"
    elif plasma_value > 0.3:
        return "\033[38;5;208m"
    elif plasma_value > 0:
        return "\033[38;5;196m"
    elif plasma_value > -0.3:
        return "\033[38;5;129m"
    else:
        return "\033[38;5;21m"

def draw_line(buffer, x0, y0, x1, y1, width, height, time_phase):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        if 0 <= x0 < width and 0 <= y0 < height:
            color = get_plasma_color(x0, y0, time_phase)
            wave_val = math.sin(x0 * 0.1 + y0 * 0.08 + time_phase * 0.05)
            char = '█' if wave_val > 0.5 else '▓' if wave_val > 0 else '▒' if wave_val > -0.5 else '░'
            buffer[y0][x0] = f"{color}{char}\033[0m"
        
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
    width, height = 85, 32
    radius, lat_steps, lon_steps = 2.3, 12, 16
    
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

    angle_x = angle_y = time_phase = 0
    
    try:
        while True:
            buffer = [[' '] * width for _ in range(height)]
            
            # Plasma background
            for y in range(0, height, 2):
                for x in range(0, width, 3):
                    if buffer[y][x] == ' ':
                        color = get_plasma_color(x, y, time_phase)
                        intensity = abs(math.sin(x * 0.05 + y * 0.03 + time_phase * 0.02))
                        if intensity > 0.7:
                            buffer[y][x] = f"{color}·\033[0m"
            
            projected_points = []
            for v in vertices:
                x, y, z = v
                y, z = rotate_x(y, z, angle_x)
                x, z = rotate_y(x, z, angle_y)
                z_dist = z + 4.5
                if z_dist <= 0: z_dist = 0.1
                xp = int(x * 14 / z_dist) + width // 2
                yp = int(y * 7 / z_dist) + height // 2
                projected_points.append((xp, yp))
            
            for edge in edges:
                p1, p2 = projected_points[edge[0]], projected_points[edge[1]]
                if (0 <= p1[0] < width or 0 <= p2[0] < width) and (0 <= p1[1] < height or 0 <= p2[1] < height):
                    draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height, time_phase)
                
            for i, p in enumerate(projected_points):
                if 0 <= p[0] < width and 0 <= p[1] < height:
                    vertex_color = get_plasma_color(p[0], p[1], time_phase + i * 10)
                    pulse = abs(math.sin(time_phase * 0.1 + i))
                    char = '◉' if pulse > 0.7 else '●' if pulse > 0.3 else '○'
                    buffer[p[1]][p[0]] = f"{vertex_color}{char}\033[0m"

            output = ["\033[H\033[2J"]
            
            # Plasma title
            title_colors = []
            title_text = "PLASMA SPHERE FIELD"
            for i, char in enumerate(title_text):
                color = get_plasma_color(i * 5, 0, time_phase)
                title_colors.append(f"{color}{char}")
            
            title = "".join(title_colors) + "\033[0m"
            subtitle_color = get_plasma_color(50, 0, time_phase + 20)
            subtitle = f"{subtitle_color}~ Flowing Energy Orb ~\033[0m"
            
            output.append(title.center(width + 30))
            output.append(subtitle.center(width + 30))
            output.append("")
            output.extend("".join(row) for row in buffer)
            
            energy_level = abs(math.sin(time_phase * 0.05)) * 100
            status_color = get_plasma_color(time_phase, 0, time_phase)
            status = f"{status_color}⚡ PLASMA ENERGY: {energy_level:.1f}% | PHASE: {time_phase} ⚡\033[0m"
            output.append("")
            output.append(status.center(width + 30))
            
            sys.stdout.write("\n".join(output))
            sys.stdout.flush()
            
            angle_x += 1.8
            angle_y += 2.5
            time_phase += 1
            time.sleep(0.04)
            
    except KeyboardInterrupt:
        plasma_color = get_plasma_color(50, 25, time_phase)
        print(f"\n{plasma_color}>>> PLASMA SPHERE DISSIPATED <<<\033[0m")

if __name__ == "__main__":
    os.system('clear')
    main()

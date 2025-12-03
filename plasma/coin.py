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
    wave1 = math.sin(x * 0.15 + time_phase * 0.08)
    wave2 = math.sin(y * 0.12 + time_phase * 0.05)
    wave3 = math.sin((x + y) * 0.08 + time_phase * 0.06)
    plasma_value = (wave1 + wave2 + wave3) / 3
    
    if plasma_value > 0.5:
        return "\033[38;5;226m"  # Yellow
    elif plasma_value > 0.2:
        return "\033[38;5;208m"  # Orange
    elif plasma_value > -0.2:
        return "\033[38;5;196m"  # Red
    elif plasma_value > -0.5:
        return "\033[38;5;129m"  # Purple
    else:
        return "\033[38;5;21m"   # Blue

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
            char = '█' if wave_val > 0.3 else '▓' if wave_val > 0 else '▒' if wave_val > -0.3 else '░'
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
    radius, thickness, steps = 2.2, 0.3, 20
    
    vertices_front = []
    vertices_back = []
    for i in range(steps):
        theta = 2 * math.pi * i / steps
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        vertices_front.append([x, y, thickness])
        vertices_back.append([x, y, -thickness])
    
    all_vertices = vertices_front + vertices_back
    angle_x = angle_y = time_phase = 0
    
    try:
        while True:
            buffer = [[' '] * width for _ in range(height)]
            
            # Plasma background
            for y in range(0, height, 3):
                for x in range(0, width, 4):
                    if buffer[y][x] == ' ':
                        color = get_plasma_color(x, y, time_phase)
                        intensity = abs(math.sin(x * 0.05 + y * 0.03 + time_phase * 0.02))
                        if intensity > 0.6:
                            buffer[y][x] = f"{color}·\033[0m"
            
            projected_points = []
            for v in all_vertices:
                x, y, z = v
                y, z = rotate_x(y, z, angle_x)
                x, z = rotate_y(x, z, angle_y)
                z_dist = z + 4
                if z_dist <= 0: z_dist = 0.1
                xp = int(x * 16 / z_dist) + width // 2
                yp = int(y * 8 / z_dist) + height // 2
                projected_points.append((xp, yp))
            
            proj_front = projected_points[:steps]
            proj_back = projected_points[steps:]
            
            for i in range(steps):
                next_i = (i + 1) % steps
                p1, p2 = proj_front[i], proj_front[next_i]
                draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height, time_phase)
                
                p3, p4 = proj_back[i], proj_back[next_i]
                draw_line(buffer, p3[0], p3[1], p4[0], p4[1], width, height, time_phase + 20)
                
                draw_line(buffer, p1[0], p1[1], p3[0], p3[1], width, height, time_phase + 10)

            # Plasma center
            center_x, center_y = width // 2, height // 2
            if 0 <= center_x < width and 0 <= center_y < height:
                center_color = get_plasma_color(center_x, center_y, time_phase)
                buffer[center_y][center_x] = f"{center_color}$\033[0m"

            output = ["\033[H\033[2J"]
            
            # Plasma title
            title_colors = []
            title_text = "PLASMA COIN FIELD"
            for i, char in enumerate(title_text):
                color = get_plasma_color(i * 5, 0, time_phase)
                title_colors.append(f"{color}{char}")
            
            title = "".join(title_colors) + "\033[0m"
            subtitle_color = get_plasma_color(50, 0, time_phase + 20)
            subtitle = f"{subtitle_color}~ Energy Currency ~\033[0m"
            
            output.append(title.center(width + 30))
            output.append(subtitle.center(width + 30))
            output.append("")
            output.extend("".join(row) for row in buffer)
            
            energy_level = abs(math.sin(time_phase * 0.05)) * 100
            status_color = get_plasma_color(time_phase, 0, time_phase)
            status = f"{status_color}⚡ PLASMA ENERGY: {energy_level:.1f}% ⚡\033[0m"
            output.append("")
            output.append(status.center(width + 30))
            
            sys.stdout.write("\n".join(output))
            sys.stdout.flush()
            
            angle_x += 3.5
            angle_y += 1.8
            time_phase += 1
            time.sleep(0.04)
            
    except KeyboardInterrupt:
        plasma_color = get_plasma_color(50, 25, time_phase)
        print(f"\n{plasma_color}>>> PLASMA COIN DISSIPATED <<<\033[0m")

if __name__ == "__main__":
    os.system('clear')
    main()

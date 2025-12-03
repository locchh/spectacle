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

def draw_line(buffer, x0, y0, x1, y1, width, height, char='█'):
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
    width, height = 90, 35
    
    radius = 2.0
    thickness = 0.3
    steps = 20
    
    vertices_front = []
    vertices_back = []
    
    for i in range(steps):
        theta = 2 * math.pi * i / steps
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        vertices_front.append([x, y, thickness])
        vertices_back.append([x, y, -thickness])
    
    all_vertices = vertices_front + vertices_back
    
    # Neon color palette
    neon_colors = [
        "\033[38;5;196m",  # Hot pink
        "\033[38;5;51m",   # Cyan
        "\033[38;5;46m",   # Lime green
        "\033[38;5;226m",  # Yellow
        "\033[38;5;201m",  # Magenta
    ]
    
    angle_x = angle_y = 0
    pulse_phase = 0
    
    try:
        while True:
            buffer = [[' '] * width for _ in range(height)]
            
            projected_points = []
            for v in all_vertices:
                x, y, z = v
                y, z = rotate_x(y, z, angle_x)
                x, z = rotate_y(x, z, angle_y)
                
                z_dist = z + 4
                if z_dist <= 0: z_dist = 0.1
                
                xp = int(x * 18 / z_dist) + width // 2
                yp = int(y * 9 / z_dist) + height // 2
                
                projected_points.append((xp, yp))
            
            proj_front = projected_points[:steps]
            proj_back = projected_points[steps:]
            
            for i in range(steps):
                next_i = (i + 1) % steps
                
                # Pulsing neon effect
                pulse = abs(math.sin(pulse_phase * 0.1 + i * 0.3))
                color_idx = int((pulse_phase + i * 5) / 10) % len(neon_colors)
                color = neon_colors[color_idx]
                
                # Front face - bright neon
                p1, p2 = proj_front[i], proj_front[next_i]
                if pulse > 0.7:
                    char = color + '◆\033[0m'
                else:
                    char = color + '♦\033[0m'
                draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height, char)
                
                # Back face - dimmer
                p3, p4 = proj_back[i], proj_back[next_i]
                back_color = neon_colors[(color_idx + 2) % len(neon_colors)]
                char = back_color + '○\033[0m'
                draw_line(buffer, p3[0], p3[1], p4[0], p4[1], width, height, char)
                
                # Connecting edges
                edge_color = neon_colors[(color_idx + 1) % len(neon_colors)]
                char = edge_color + '│\033[0m'
                draw_line(buffer, p1[0], p1[1], p3[0], p3[1], width, height, char)

            # Neon center symbol
            center_x, center_y = width // 2, height // 2
            center_color = neon_colors[int(pulse_phase / 8) % len(neon_colors)]
            if 0 <= center_x < width and 0 <= center_y < height:
                buffer[center_y][center_x] = f"{center_color}$\033[0m"

            # Neon UI
            output = []
            output.append("\033[H\033[2J")
            
            # Animated neon title
            title_color = neon_colors[int(pulse_phase / 12) % len(neon_colors)]
            glow = "▓▒░" if int(pulse_phase / 5) % 2 else "░▒▓"
            
            title = f"{title_color}{glow} NEON COIN SYNTHWAVE {glow}\033[0m"
            output.append(title.center(width + 20))
            
            for row in buffer:
                output.append("".join(row))
            
            # Neon sparkles
            sparkle_line = ""
            for _ in range(width // 4):
                if random.random() < 0.4:
                    sparkle_color = random.choice(neon_colors)
                    sparkle_line += f"{sparkle_color}✦\033[0m "
                else:
                    sparkle_line += "  "
            output.append(sparkle_line)
            
            sys.stdout.write("\n".join(output))
            sys.stdout.flush()
            
            angle_x += 4
            angle_y += 2
            pulse_phase += 1
            
            time.sleep(0.04)
            
    except KeyboardInterrupt:
        print(f"\n{neon_colors[0]}>>> NEON COIN SHUTDOWN <<<\033[0m")

if __name__ == "__main__":
    os.system('clear')
    main()

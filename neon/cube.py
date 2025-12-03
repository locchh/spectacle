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
    width, height = 100, 40
    
    vertices = [
        [-1.5, -1.5, -1.5], [1.5, -1.5, -1.5], [1.5, 1.5, -1.5], [-1.5, 1.5, -1.5],
        [-1.5, -1.5, 1.5], [1.5, -1.5, 1.5], [1.5, 1.5, 1.5], [-1.5, 1.5, 1.5]
    ]
    
    edges = [
        (0,1), (1,2), (2,3), (3,0),
        (4,5), (5,6), (6,7), (7,4),
        (0,4), (1,5), (2,6), (3,7)
    ]
    
    # Neon color palette
    neon_colors = [
        "\033[38;5;196m",  # Hot pink
        "\033[38;5;51m",   # Cyan
        "\033[38;5;46m",   # Lime green
        "\033[38;5;226m",  # Yellow
        "\033[38;5;201m",  # Magenta
        "\033[38;5;39m",   # Blue
    ]
    
    angle_x = angle_y = angle_z = 0
    pulse_phase = 0
    
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
                
                xp = int(x * 25 / z_dist) + width // 2
                yp = int(y * 12 / z_dist) + height // 2
                
                projected_points.append((xp, yp))
            
            # Draw edges with pulsing neon colors
            for i, edge in enumerate(edges):
                p1, p2 = projected_points[edge[0]], projected_points[edge[1]]
                
                # Pulsing effect
                pulse = abs(math.sin(pulse_phase * 0.1 + i))
                color_idx = int((pulse_phase + i * 10) / 20) % len(neon_colors)
                color = neon_colors[color_idx]
                
                # Different chars for intensity
                if pulse > 0.8:
                    char = color + '█\033[0m'
                elif pulse > 0.5:
                    char = color + '▓\033[0m'
                else:
                    char = color + '▒\033[0m'
                
                draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height, char)
                
            # Glowing vertices
            for i, p in enumerate(projected_points):
                if 0 <= p[0] < width and 0 <= p[1] < height:
                    vertex_color = neon_colors[i % len(neon_colors)]
                    buffer[p[1]][p[0]] = f"{vertex_color}◉\033[0m"

            # Neon UI
            output = []
            output.append("\033[H\033[2J")
            
            # Animated neon title
            title_color = neon_colors[int(pulse_phase / 15) % len(neon_colors)]
            glow = "▓▒░" if int(pulse_phase / 5) % 2 else "░▒▓"
            
            title = f"{title_color}{glow} NEON CUBE SYNTHWAVE {glow}\033[0m"
            output.append(title.center(width + 20))
            
            for row in buffer:
                output.append("".join(row))
            
            # Add some random neon sparkles
            sparkle_line = ""
            for _ in range(width // 4):
                if random.random() < 0.3:
                    sparkle_color = random.choice(neon_colors)
                    sparkle_line += f"{sparkle_color}✦\033[0m "
                else:
                    sparkle_line += "  "
            output.append(sparkle_line)
            
            sys.stdout.write("\n".join(output))
            sys.stdout.flush()
            
            angle_x += 2
            angle_y += 3
            angle_z += 1
            pulse_phase += 1
            
            time.sleep(0.04)
            
    except KeyboardInterrupt:
        print(f"\n{neon_colors[0]}>>> NEON SHUTDOWN <<<\033[0m")

if __name__ == "__main__":
    os.system('clear')
    main()

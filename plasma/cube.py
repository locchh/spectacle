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

def get_plasma_color(x, y, time_phase):
    """Generate plasma-like color based on position and time"""
    # Plasma wave equations
    wave1 = math.sin(x * 0.1 + time_phase * 0.05)
    wave2 = math.sin(y * 0.08 + time_phase * 0.03)
    wave3 = math.sin((x + y) * 0.06 + time_phase * 0.04)
    wave4 = math.sin(math.sqrt(x*x + y*y) * 0.05 + time_phase * 0.02)
    
    plasma_value = (wave1 + wave2 + wave3 + wave4) / 4
    
    # Map to color spectrum
    if plasma_value > 0.6:
        return "\033[38;5;226m"  # Bright yellow
    elif plasma_value > 0.3:
        return "\033[38;5;208m"  # Orange
    elif plasma_value > 0:
        return "\033[38;5;196m"  # Red
    elif plasma_value > -0.3:
        return "\033[38;5;129m"  # Purple
    elif plasma_value > -0.6:
        return "\033[38;5;21m"   # Blue
    else:
        return "\033[38;5;51m"   # Cyan

def draw_line(buffer, x0, y0, x1, y1, width, height, time_phase):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        if 0 <= x0 < width and 0 <= y0 < height:
            color = get_plasma_color(x0, y0, time_phase)
            # Different characters for different plasma intensities
            wave_val = math.sin(x0 * 0.1 + y0 * 0.08 + time_phase * 0.05)
            if wave_val > 0.5:
                char = '█'
            elif wave_val > 0:
                char = '▓'
            elif wave_val > -0.5:
                char = '▒'
            else:
                char = '░'
            
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

def draw_plasma_background(buffer, width, height, time_phase):
    """Draw plasma background effect"""
    for y in range(0, height, 2):  # Skip every other line for performance
        for x in range(0, width, 3):  # Skip every 3rd column
            if buffer[y][x] == ' ':  # Don't overwrite cube
                color = get_plasma_color(x, y, time_phase)
                intensity = abs(math.sin(x * 0.05 + y * 0.03 + time_phase * 0.02))
                if intensity > 0.7:
                    buffer[y][x] = f"{color}·\033[0m"

def main():
    width, height = 100, 40
    
    vertices = [
        [-1.3, -1.3, -1.3], [1.3, -1.3, -1.3], [1.3, 1.3, -1.3], [-1.3, 1.3, -1.3],
        [-1.3, -1.3, 1.3], [1.3, -1.3, 1.3], [1.3, 1.3, 1.3], [-1.3, 1.3, 1.3]
    ]
    
    edges = [
        (0,1), (1,2), (2,3), (3,0),
        (4,5), (5,6), (6,7), (7,4),
        (0,4), (1,5), (2,6), (3,7)
    ]
    
    angle_x = angle_y = angle_z = 0
    time_phase = 0
    
    try:
        while True:
            buffer = [[' '] * width for _ in range(height)]
            
            # Draw plasma background
            draw_plasma_background(buffer, width, height, time_phase)
            
            projected_points = []
            for v in vertices:
                x, y, z = v
                y, z = rotate_x(y, z, angle_x)
                x, z = rotate_y(x, z, angle_y)
                x, y = rotate_z(x, y, angle_z)
                
                z_dist = z + 4
                if z_dist <= 0: z_dist = 0.1
                
                xp = int(x * 22 / z_dist) + width // 2
                yp = int(y * 11 / z_dist) + height // 2
                
                projected_points.append((xp, yp))
            
            # Draw cube with plasma coloring
            for edge in edges:
                p1, p2 = projected_points[edge[0]], projected_points[edge[1]]
                draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height, time_phase)
                
            # Plasma vertices with pulsing effect
            for i, p in enumerate(projected_points):
                if 0 <= p[0] < width and 0 <= p[1] < height:
                    vertex_color = get_plasma_color(p[0], p[1], time_phase + i * 10)
                    pulse = abs(math.sin(time_phase * 0.1 + i))
                    if pulse > 0.7:
                        char = '◉'
                    elif pulse > 0.3:
                        char = '●'
                    else:
                        char = '○'
                    buffer[p[1]][p[0]] = f"{vertex_color}{char}\033[0m"

            # Plasma UI
            output = []
            output.append("\033[H\033[2J")
            
            # Animated plasma title
            title_colors = []
            title_text = "PLASMA FIELD CUBE"
            for i, char in enumerate(title_text):
                color = get_plasma_color(i * 5, 0, time_phase)
                title_colors.append(f"{color}{char}")
            
            title = "".join(title_colors) + "\033[0m"
            subtitle_color = get_plasma_color(50, 0, time_phase + 20)
            subtitle = f"{subtitle_color}~ Flowing Energy Visualization ~\033[0m"
            
            output.append(title.center(width + 30))
            output.append(subtitle.center(width + 30))
            output.append("")
            
            for row in buffer:
                output.append("".join(row))
            
            # Plasma status bar
            status_color = get_plasma_color(time_phase, 0, time_phase)
            energy_level = abs(math.sin(time_phase * 0.05)) * 100
            status = f"{status_color}⚡ PLASMA ENERGY: {energy_level:.1f}% | PHASE: {time_phase} ⚡\033[0m"
            output.append("")
            output.append(status.center(width + 30))
            
            sys.stdout.write("\n".join(output))
            sys.stdout.flush()
            
            angle_x += 1.8
            angle_y += 2.5
            angle_z += 1.2
            time_phase += 1
            
            time.sleep(0.04)
            
    except KeyboardInterrupt:
        plasma_color = get_plasma_color(50, 25, time_phase)
        print(f"\n{plasma_color}>>> PLASMA FIELD DISSIPATED <<<\033[0m")

if __name__ == "__main__":
    os.system('clear')
    main()

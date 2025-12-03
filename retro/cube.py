import math
import time
import os
import sys

def rotate_x(y, z, angle):
    rad = angle * math.pi / 180
    cosa = math.cos(rad)
    sina = math.sin(rad)
    new_y = y * cosa - z * sina
    new_z = y * sina + z * cosa
    return new_y, new_z

def rotate_y(x, z, angle):
    rad = angle * math.pi / 180
    cosa = math.cos(rad)
    sina = math.sin(rad)
    new_x = x * cosa - z * sina
    new_z = x * sina + z * cosa
    return new_x, new_z

def rotate_z(x, y, angle):
    rad = angle * math.pi / 180
    cosa = math.cos(rad)
    sina = math.sin(rad)
    new_x = x * cosa - y * sina
    new_y = x * sina + y * cosa
    return new_x, new_y

def draw_line(buffer, x0, y0, x1, y1, width, height, char='#'):
    """Bresenham's Line Algorithm"""
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
    # Screen dimensions - retro 80x25 terminal
    width = 80
    height = 25
    
    # Cube vertices
    vertices = [
        [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
        [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
    ]
    
    edges = [
        (0,1), (1,2), (2,3), (3,0), # Back face
        (4,5), (5,6), (6,7), (7,4), # Front face
        (0,4), (1,5), (2,6), (3,7)  # Connecting lines
    ]
    
    # Retro colors - amber on black
    amber = "\033[33m"
    green = "\033[32m" 
    reset = "\033[0m"
    
    # Retro ASCII chars
    retro_chars = ['█', '▓', '▒', '░', '■', '□', '▪', '▫']
    
    angle_x = 0
    angle_y = 0
    angle_z = 0
    frame = 0
    
    try:
        while True:
            buffer = [[' ' for _ in range(width)] for _ in range(height)]
            
            projected_points = []
            for v in vertices:
                x, y, z = v[0], v[1], v[2]
                
                y, z = rotate_x(y, z, angle_x)
                x, z = rotate_y(x, z, angle_y)
                x, y = rotate_z(x, y, angle_z)
                
                fov = 40
                distance = 4
                z_dist = z + distance
                
                if z_dist == 0: z_dist = 0.1
                
                xp = int((x * fov) / z_dist) + width // 2
                yp = int((y * fov * 0.5) / z_dist) + height // 2
                
                projected_points.append((xp, yp))
            
            # Draw edges with retro styling
            for i, edge in enumerate(edges):
                p1 = projected_points[edge[0]]
                p2 = projected_points[edge[1]]
                
                # Alternate between amber and green
                color = amber if i % 2 == 0 else green
                char = retro_chars[i % len(retro_chars)]
                
                draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height, color + char + reset)
                
            # Draw vertices
            for p in projected_points:
                if 0 <= p[0] < width and 0 <= p[1] < height:
                    buffer[p[1]][p[0]] = amber + '●' + reset

            # Retro UI
            output = []
            output.append("\033[H\033[2J")
            
            # Retro title with ASCII art border
            title = f"{green}╔══════════════════════════════════════════════════════════════════════════════╗{reset}"
            subtitle = f"{green}║{amber}                            >>> RETRO CUBE v1.0 <<<                            {green}║{reset}"
            status = f"{green}║{amber}                          FRAME: {frame:06d} | ROTATING...                          {green}║{reset}"
            bottom = f"{green}╚══════════════════════════════════════════════════════════════════════════════╝{reset}"
            
            output.append(title)
            output.append(subtitle)
            output.append(status)
            output.append(bottom)
            
            for row in buffer:
                output.append("".join(row))
            
            sys.stdout.write("\n".join(output))
            sys.stdout.flush()
            
            angle_x += 1.5
            angle_y += 2
            angle_z += 0.5
            frame += 1
            
            time.sleep(0.08)  # Slower for retro feel
            
    except KeyboardInterrupt:
        print(f"\n{amber}>>> SYSTEM HALT <<<{reset}")

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    main()

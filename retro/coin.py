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

def draw_line(buffer, x0, y0, x1, y1, width, height, char='#'):
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
    
    radius = 1.5
    thickness = 0.2
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
            for v in all_vertices:
                x, y, z = v
                y, z = rotate_x(y, z, angle_x)
                x, z = rotate_y(x, z, angle_y)
                x, y = rotate_z(x, y, angle_z)
                
                z_dist = z + 4
                if z_dist <= 0: z_dist = 0.1
                
                xp = int(x * 15 / z_dist) + width // 2
                yp = int(y * 8 / z_dist) + height // 2
                
                projected_points.append((xp, yp))
            
            proj_front = projected_points[:steps]
            proj_back = projected_points[steps:]
            
            for i in range(steps):
                next_i = (i + 1) % steps
                
                # Front face - amber
                p1, p2 = proj_front[i], proj_front[next_i]
                draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height, amber + '$' + reset)
                
                # Back face - green
                p3, p4 = proj_back[i], proj_back[next_i]
                draw_line(buffer, p3[0], p3[1], p4[0], p4[1], width, height, green + '.' + reset)
                
                # Connecting edges
                draw_line(buffer, p1[0], p1[1], p3[0], p3[1], width, height, amber + '|' + reset)

            # Retro UI
            output = []
            output.append("\033[H\033[2J")
            
            title = f"{green}╔══════════════════════════════════════════════════════════════════════════════╗{reset}"
            subtitle = f"{green}║{amber}                            >>> RETRO COIN v1.0 <<<                            {green}║{reset}"
            status = f"{green}║{amber}                          FRAME: {frame:06d} | SPINNING...                         {green}║{reset}"
            bottom = f"{green}╚══════════════════════════════════════════════════════════════════════════════╝{reset}"
            
            output.append(title)
            output.append(subtitle)
            output.append(status)
            output.append(bottom)
            
            for row in buffer:
                output.append("".join(row))
            
            sys.stdout.write("\n".join(output))
            sys.stdout.flush()
            
            angle_x += 5
            angle_y += 2
            frame += 1
            
            time.sleep(0.08)
            
    except KeyboardInterrupt:
        print(f"\n{amber}>>> COIN TOSS COMPLETE <<<{reset}")

if __name__ == "__main__":
    os.system('clear')
    main()

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

def main():
    width, height = 70, 28
    
    radius = 2.0
    lat_steps = 10
    lon_steps = 14
    
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

    # ASCII line characters
    line_chars = ['─', '│', '╱', '╲', '┼', '┌', '┐', '└', '┘']
    
    angle_x = angle_y = angle_z = 0
    
    try:
        while True:
            buffer = [[' '] * width for _ in range(height)]
            
            projected_points = []
            for v in vertices:
                x, y, z = v
                y, z = rotate_x(y, z, angle_x)
                x, z = rotate_y(x, z, angle_y)
                
                z_dist = z + 4
                if z_dist <= 0: z_dist = 0.1
                
                xp = int(x * 12 / z_dist) + width // 2
                yp = int(y * 6 / z_dist) + height // 2
                
                projected_points.append((xp, yp))
            
            # Draw edges with ASCII line art
            for i, edge in enumerate(edges):
                p1, p2 = projected_points[edge[0]], projected_points[edge[1]]
                
                if (0 <= p1[0] < width or 0 <= p2[0] < width) and \
                   (0 <= p1[1] < height or 0 <= p2[1] < height):
                    
                    # Choose character based on line direction and type
                    dx = p2[0] - p1[0]
                    dy = p2[1] - p1[1]
                    
                    if abs(dx) > abs(dy):
                        char = '─'
                    elif abs(dy) > abs(dx):
                        char = '│'
                    elif dx * dy > 0:
                        char = '╲'
                    else:
                        char = '╱'
                    
                    draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height, char)
            
            # ASCII art vertices
            vertex_chars = ['◊', '◈', '◇', '◆', '○', '●', '□', '■']
            for i, p in enumerate(projected_points):
                if 0 <= p[0] < width and 0 <= p[1] < height:
                    buffer[p[1]][p[0]] = vertex_chars[i % len(vertex_chars)]

            # ASCII art border and title
            output = []
            output.append("\033[H")
            
            border_top = "╔" + "═" * (width - 2) + "╗"
            title_line = f"║{'ASCII ART SPHERE'.center(width - 2)}║"
            border_mid = "╠" + "─" * (width - 2) + "╣"
            
            output.append(border_top)
            output.append(title_line)
            output.append(border_mid)
            
            for row in buffer:
                output.append("║" + "".join(row)[1:-1] + "║")
            
            border_bottom = "╚" + "═" * (width - 2) + "╝"
            output.append(border_bottom)
            
            sys.stdout.write("\n".join(output))
            sys.stdout.flush()
            
            angle_x += 1.0
            angle_y += 1.5
            
            time.sleep(0.08)
            
    except KeyboardInterrupt:
        print("\n╔═══════════════════╗")
        print("║  SPHERE STOPPED   ║")
        print("╚═══════════════════╝")

if __name__ == "__main__":
    os.system('clear')
    main()

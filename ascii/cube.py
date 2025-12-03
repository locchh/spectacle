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
    width, height = 80, 30
    
    vertices = [
        [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
        [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
    ]
    
    edges = [
        (0,1), (1,2), (2,3), (3,0),
        (4,5), (5,6), (6,7), (7,4),
        (0,4), (1,5), (2,6), (3,7)
    ]
    
    # ASCII art characters for different line types
    ascii_chars = {
        'horizontal': '─',
        'vertical': '│',
        'diagonal1': '╱',
        'diagonal2': '╲',
        'cross': '┼',
        'corner': '┌┐└┘',
        'heavy': '━',
        'double': '═'
    }
    
    angle_x = angle_y = angle_z = 0
    
    try:
        while True:
            buffer = [[' '] * width for _ in range(height)]
            
            projected_points = []
            for v in vertices:
                x, y, z = v
                y, z = rotate_x(y, z, angle_x)
                x, z = rotate_y(x, z, angle_y)
                x, y = rotate_z(x, y, angle_z)
                
                z_dist = z + 3.5
                if z_dist <= 0: z_dist = 0.1
                
                xp = int(x * 22 / z_dist) + width // 2
                yp = int(y * 11 / z_dist) + height // 2
                
                projected_points.append((xp, yp))
            
            # Draw edges with ASCII line art
            for i, edge in enumerate(edges):
                p1, p2 = projected_points[edge[0]], projected_points[edge[1]]
                
                # Choose character based on line direction
                dx = p2[0] - p1[0]
                dy = p2[1] - p1[1]
                
                if abs(dx) > abs(dy):
                    char = ascii_chars['horizontal']
                elif abs(dy) > abs(dx):
                    char = ascii_chars['vertical']
                elif dx * dy > 0:
                    char = ascii_chars['diagonal2']
                else:
                    char = ascii_chars['diagonal1']
                
                # Different styles for different edge types
                if i < 4:  # Back face
                    char = '·'
                elif i < 8:  # Front face
                    char = ascii_chars['heavy']
                else:  # Connecting edges
                    char = ascii_chars['vertical']
                
                draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height, char)
                
            # ASCII art vertices
            vertex_chars = ['◊', '◈', '◇', '◆', '○', '●', '□', '■']
            for i, p in enumerate(projected_points):
                if 0 <= p[0] < width and 0 <= p[1] < height:
                    buffer[p[1]][p[0]] = vertex_chars[i]

            # ASCII art border and title
            output = []
            output.append("\033[H")
            
            border_top = "╔" + "═" * (width - 2) + "╗"
            title_line = f"║{'ASCII ART CUBE'.center(width - 2)}║"
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
            
            angle_x += 1.2
            angle_y += 1.8
            angle_z += 0.6
            
            time.sleep(0.08)
            
    except KeyboardInterrupt:
        print("\n╔═══════════════════╗")
        print("║   PROGRAM ENDED   ║")
        print("╚═══════════════════╝")

if __name__ == "__main__":
    os.system('clear')
    main()

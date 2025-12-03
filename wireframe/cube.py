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

def draw_line(buffer, x0, y0, x1, y1, width, height, char='│'):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        if 0 <= x0 < width and 0 <= y0 < height:
            # Choose line character based on direction
            if abs(dx) > abs(dy) * 2:
                buffer[y0][x0] = '─'
            elif abs(dy) > abs(dx) * 2:
                buffer[y0][x0] = '│'
            elif (x1 - x0) * (y1 - y0) > 0:
                buffer[y0][x0] = '╲'
            else:
                buffer[y0][x0] = '╱'
        
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

def draw_grid(buffer, width, height, spacing=10):
    """Draw a technical grid background"""
    grid_char = '·'
    
    # Vertical grid lines
    for x in range(0, width, spacing):
        for y in range(0, height):
            if buffer[y][x] == ' ':
                buffer[y][x] = grid_char
    
    # Horizontal grid lines
    for y in range(0, height, spacing):
        for x in range(0, width):
            if buffer[y][x] == ' ':
                buffer[y][x] = grid_char

def main():
    width, height = 80, 35
    
    vertices = [
        [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
        [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
    ]
    
    edges = [
        (0,1), (1,2), (2,3), (3,0),
        (4,5), (5,6), (6,7), (7,4),
        (0,4), (1,5), (2,6), (3,7)
    ]
    
    angle_x = angle_y = angle_z = 0
    
    try:
        while True:
            buffer = [[' '] * width for _ in range(height)]
            
            # Draw technical grid
            draw_grid(buffer, width, height, 8)
            
            projected_points = []
            for v in vertices:
                x, y, z = v
                y, z = rotate_x(y, z, angle_x)
                x, z = rotate_y(x, z, angle_y)
                x, y = rotate_z(x, y, angle_z)
                
                z_dist = z + 3.5
                if z_dist <= 0: z_dist = 0.1
                
                xp = int(x * 18 / z_dist) + width // 2
                yp = int(y * 9 / z_dist) + height // 2
                
                projected_points.append((xp, yp))
            
            # Draw wireframe edges
            for i, edge in enumerate(edges):
                p1, p2 = projected_points[edge[0]], projected_points[edge[1]]
                draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height)
                
            # Draw vertices with technical symbols
            vertex_symbols = ['┌', '┐', '┘', '└', '┬', '┤', '┴', '├']
            for i, p in enumerate(projected_points):
                if 0 <= p[0] < width and 0 <= p[1] < height:
                    buffer[p[1]][p[0]] = vertex_symbols[i]

            # Technical wireframe UI
            output = []
            output.append("\033[H")
            
            # Technical header
            header = "┌" + "─" * (width - 2) + "┐"
            title = f"│{'WIREFRAME TECHNICAL VIEW'.center(width - 2)}│"
            coords = f"│{'X: {:.1f}° Y: {:.1f}° Z: {:.1f}°'.format(angle_x % 360, angle_y % 360, angle_z % 360).center(width - 2)}│"
            separator = "├" + "─" * (width - 2) + "┤"
            
            output.append(header)
            output.append(title)
            output.append(coords)
            output.append(separator)
            
            for row in buffer:
                output.append("│" + "".join(row)[1:-1] + "│")
            
            # Technical footer
            footer = "└" + "─" * (width - 2) + "┘"
            status = f"STATUS: RENDERING | VERTICES: 8 | EDGES: 12"
            
            output.append(footer)
            output.append(status.center(width))
            
            sys.stdout.write("\n".join(output))
            sys.stdout.flush()
            
            angle_x += 1
            angle_y += 1.3
            angle_z += 0.7
            
            time.sleep(0.06)
            
    except KeyboardInterrupt:
        print("\n┌─────────────────────┐")
        print("│  WIREFRAME HALTED   │")
        print("└─────────────────────┘")

if __name__ == "__main__":
    os.system('clear')
    main()

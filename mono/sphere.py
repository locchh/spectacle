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

def draw_line(buffer, x0, y0, x1, y1, width, height, char='.'):
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
    # Screen dimensions
    width = 80
    height = 40
    
    radius = 1.8
    lat_steps = 10
    lon_steps = 16
    
    vertices = []
    edges = []
    
    # Generate Sphere Vertices
    for i in range(lat_steps + 1):
        phi = math.pi * i / lat_steps # From 0 to Pi
        for j in range(lon_steps):
            theta = 2 * math.pi * j / lon_steps # From 0 to 2Pi
            
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.sin(phi) * math.sin(theta)
            z = radius * math.cos(phi)
            
            vertices.append([x, y, z])
            
            # Current vertex index
            p_idx = i * lon_steps + j
            
            # Add Horizontal Edge (Longitude ring)
            # Connect to next point in the same latitude ring
            next_j = (j + 1) % lon_steps
            edges.append((p_idx, i * lon_steps + next_j))
            
            # Add Vertical Edge (Latitude line)
            # Connect to point in the next latitude ring
            if i < lat_steps:
                edges.append((p_idx, (i + 1) * lon_steps + j))

    angle_x = 0
    angle_y = 0
    angle_z = 0
    
    try:
        while True:
            buffer = [[' ' for _ in range(width)] for _ in range(height)]
            
            projected_points = []
            
            # Rotate and Project
            for v in vertices:
                x, y, z = v[0], v[1], v[2]
                
                y, z = rotate_x(y, z, angle_x)
                x, z = rotate_y(x, z, angle_y)
                x, y = rotate_z(x, y, angle_z)
                
                fov = 40
                distance = 4
                z_dist = z + distance
                
                if z_dist <= 0: z_dist = 0.1
                
                xp = int((x * fov) / z_dist) + width // 2
                yp = int((y * fov * 0.5) / z_dist) + height // 2
                
                projected_points.append((xp, yp))
            
            # Draw Edges
            for edge in edges:
                p1 = projected_points[edge[0]]
                p2 = projected_points[edge[1]]
                
                # Optimization: Don't draw if both points are off screen
                if (0 <= p1[0] < width or 0 <= p2[0] < width) and \
                   (0 <= p1[1] < height or 0 <= p2[1] < height):
                    
                    # Use different chars for vertical vs horizontal lines to make it look cooler?
                    # Nah, simple is better.
                    draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height, '.')
            
            # Draw Vertices (optional, adds "knots" to the net)
            for p in projected_points:
                if 0 <= p[0] < width and 0 <= p[1] < height:
                    buffer[p[1]][p[0]] = 'o'

            output = []
            output.append("\033[H")
            
            for row in buffer:
                output.append("".join(row))
            
            sys.stdout.write("\n".join(output))
            sys.stdout.flush()
            
            angle_x += 1
            angle_y += 2
            angle_z += 1
            
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    main()

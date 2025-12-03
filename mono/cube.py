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
    # Screen dimensions
    width = 80
    height = 40
    
    # Cube vertices (x, y, z) centered at 0
    # Cube size is 2 units (-1 to 1)
    vertices = [
        [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
        [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
    ]
    
    # Edges connecting vertices indices
    edges = [
        (0,1), (1,2), (2,3), (3,0), # Back face
        (4,5), (5,6), (6,7), (7,4), # Front face
        (0,4), (1,5), (2,6), (3,7)  # Connecting lines
    ]
    
    angle_x = 0
    angle_y = 0
    angle_z = 0
    
    try:
        while True:
            # Create empty buffer
            buffer = [[' ' for _ in range(width)] for _ in range(height)]
            
            # Rotate and project vertices
            projected_points = []
            for v in vertices:
                x, y, z = v[0], v[1], v[2]
                
                # Rotate
                y, z = rotate_x(y, z, angle_x)
                x, z = rotate_y(x, z, angle_y)
                x, y = rotate_z(x, y, angle_z)
                
                # Projection parameters
                fov = 40
                distance = 4
                z_dist = z + distance
                
                # Avoid division by zero
                if z_dist == 0: z_dist = 0.1
                
                # Project to 2D
                xp = int((x * fov) / z_dist) + width // 2
                # Multiply y by 0.5 because terminal characters are usually taller than wide
                yp = int((y * fov * 0.5) / z_dist) + height // 2
                
                projected_points.append((xp, yp))
            
            # Draw edges
            for edge in edges:
                p1 = projected_points[edge[0]]
                p2 = projected_points[edge[1]]
                draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height)
                
            # Draw vertices (corners)
            for p in projected_points:
                if 0 <= p[0] < width and 0 <= p[1] < height:
                    buffer[p[1]][p[0]] = '@'

            # Build the frame string
            output = []
            # Move cursor to top-left
            output.append("\033[H") 
            
            for row in buffer:
                output.append("".join(row))
            
            # Print everything at once to reduce flicker
            sys.stdout.write("\n".join(output))
            sys.stdout.flush()
            
            # Update angles
            angle_x += 2
            angle_y += 3
            angle_z += 1
            
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    # Clear screen once at start
    os.system('cls' if os.name == 'nt' else 'clear')
    main()

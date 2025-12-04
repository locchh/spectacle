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
    
    # Coin properties
    radius = 1.5
    thickness = 0.2
    steps = 24  # Number of segments for the circle
    
    # Generate vertices
    vertices_front = []
    vertices_back = []
    
    for i in range(steps):
        theta = 2 * math.pi * i / steps
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        vertices_front.append([x, y, thickness])
        vertices_back.append([x, y, -thickness])
    
    all_vertices = vertices_front + vertices_back
    
    angle_x = 0
    angle_y = 0
    angle_z = 0
    
    try:
        while True:
            # Create empty buffer
            buffer = [[' ' for _ in range(width)] for _ in range(height)]
            
            # Rotate and project all vertices
            projected_points = []
            for v in all_vertices:
                x, y, z = v[0], v[1], v[2]
                
                # Rotate
                # Make it spin mostly on Y (like a coin flip) or Z (spinning top)
                # Let's do a coin toss rotation (X axis) + some spin (Z axis)
                y, z = rotate_x(y, z, angle_x)
                x, z = rotate_y(x, z, angle_y)
                x, y = rotate_z(x, y, angle_z)
                
                # Projection parameters
                fov = 40
                distance = 4
                z_dist = z + distance
                
                # Avoid division by zero
                if z_dist <= 0: z_dist = 0.1
                
                # Project to 2D
                xp = int((x * fov) / z_dist) + width // 2
                yp = int((y * fov * 0.5) / z_dist) + height // 2
                
                projected_points.append((xp, yp))
            
            # Split projected points back into front and back
            proj_front = projected_points[:steps]
            proj_back = projected_points[steps:]
            
            # Draw edges
            for i in range(steps):
                next_i = (i + 1) % steps
                
                # Draw circumference of front face
                p1 = proj_front[i]
                p2 = proj_front[next_i]
                draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height, '.')
                
                # Draw circumference of back face
                p3 = proj_back[i]
                p4 = proj_back[next_i]
                draw_line(buffer, p3[0], p3[1], p4[0], p4[1], width, height, '.')
                
                # Draw connecting ridges (thickness)
                draw_line(buffer, p1[0], p1[1], p3[0], p3[1], width, height, '#')

            # Draw specific currency symbol in the middle? 
            # That's hard in wireframe. Let's just put a center point.
            # (Calculated as average of front face points)
            
            # Build the frame string
            output = []
            output.append("\033[H") # Home cursor
            
            for row in buffer:
                output.append("".join(row))
            
            sys.stdout.write("\n".join(output))
            sys.stdout.flush()
            
            # Update angles
            # A typical coin toss spin
            angle_x += 5  # Flip speed
            angle_y += 2  # Spin speed
            # angle_z += 0
            
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    main()

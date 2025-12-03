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

def draw_line(buffer, x0, y0, x1, y1, width, height):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        if 0 <= x0 < width and 0 <= y0 < height:
            buffer[y0][x0] = '·'
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
    width, height = 50, 25
    
    radius = 1.5
    lat_steps = 6
    lon_steps = 10
    
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

    angle_x = angle_y = angle_z = 0
    
    try:
        while True:
            buffer = [[' '] * width for _ in range(height)]
            
            projected_points = []
            for v in vertices:
                x, y, z = v
                y, z = rotate_x(y, z, angle_x)
                x, z = rotate_y(x, z, angle_y)
                
                z_dist = z + 3
                if z_dist <= 0: z_dist = 0.1
                
                xp = int(x * 10 / z_dist) + width // 2
                yp = int(y * 5 / z_dist) + height // 2
                
                projected_points.append((xp, yp))
            
            for edge in edges:
                p1, p2 = projected_points[edge[0]], projected_points[edge[1]]
                
                if (0 <= p1[0] < width or 0 <= p2[0] < width) and \
                   (0 <= p1[1] < height or 0 <= p2[1] < height):
                    draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height)
            
            for p in projected_points:
                if 0 <= p[0] < width and 0 <= p[1] < height:
                    buffer[p[1]][p[0]] = '○'

            print("\033[H", end="")
            for row in buffer:
                print("".join(row))
            
            angle_x += 0.8
            angle_y += 1.2
            
            time.sleep(0.06)
            
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    os.system('clear')
    main()

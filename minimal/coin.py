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
    
    radius = 1.2
    thickness = 0.15
    steps = 12
    
    vertices_front = []
    vertices_back = []
    
    for i in range(steps):
        theta = 2 * math.pi * i / steps
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        vertices_front.append([x, y, thickness])
        vertices_back.append([x, y, -thickness])
    
    all_vertices = vertices_front + vertices_back
    
    angle_x = angle_y = 0
    
    try:
        while True:
            buffer = [[' '] * width for _ in range(height)]
            
            projected_points = []
            for v in all_vertices:
                x, y, z = v
                y, z = rotate_x(y, z, angle_x)
                x, z = rotate_y(x, z, angle_y)
                
                z_dist = z + 3
                if z_dist <= 0: z_dist = 0.1
                
                xp = int(x * 12 / z_dist) + width // 2
                yp = int(y * 6 / z_dist) + height // 2
                
                projected_points.append((xp, yp))
            
            proj_front = projected_points[:steps]
            proj_back = projected_points[steps:]
            
            for i in range(steps):
                next_i = (i + 1) % steps
                
                p1, p2 = proj_front[i], proj_front[next_i]
                draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height)
                
                p3, p4 = proj_back[i], proj_back[next_i]
                draw_line(buffer, p3[0], p3[1], p4[0], p4[1], width, height)
                
                draw_line(buffer, p1[0], p1[1], p3[0], p3[1], width, height)

            for p in proj_front:
                if 0 <= p[0] < width and 0 <= p[1] < height:
                    buffer[p[1]][p[0]] = '○'

            print("\033[H", end="")
            for row in buffer:
                print("".join(row))
            
            angle_x += 4
            angle_y += 1.5
            
            time.sleep(0.06)
            
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    os.system('clear')
    main()

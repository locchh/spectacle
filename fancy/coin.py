import math
import time
import os
import sys
import random

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

def draw_sparkle(buffer, x, y, width, height):
    """Add sparkle effects around a point"""
    sparkle_chars = ['✦', '✧', '★', '☆', '✪', '✫', '⭐']
    for dx in range(-2, 3):
        for dy in range(-1, 2):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and random.random() < 0.3:
                sparkle = random.choice(sparkle_chars)
                color = random.choice(["\033[93m", "\033[33m", "\033[1;33m", "\033[1;93m"])
                buffer[ny][nx] = f"{color}{sparkle}\033[0m"

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
    width = 100
    height = 50
    
    # Coin properties
    radius = 2.0
    thickness = 0.3
    steps = 32  # Number of segments for the circle (more detail)
    
    # Animation state
    spin_speed = 1.0
    glow_phase = 0
    bounce_phase = 0
    
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
            
            # Enhanced color palette with gradients and effects
            colors = {
                'gold': "\033[38;5;220m",
                'bright_gold': "\033[38;5;226m", 
                'deep_gold': "\033[38;5;178m",
                'bronze': "\033[38;5;130m",
                'copper': "\033[38;5;166m",
                'shine': "\033[1;38;5;230m",
                'shadow': "\033[2;38;5;94m"
            }
            reset = "\033[0m"
            
            # Add glow effect
            glow_intensity = abs(math.sin(glow_phase * 0.1))
            current_shine = f"\033[1;38;5;{int(226 + 4 * glow_intensity)}m"
            
            # Calculate bounce effect
            bounce_offset = math.sin(bounce_phase * 0.15) * 3
            
            for i in range(steps):
                next_i = (i + 1) % steps
                
                # Calculate lighting based on angle (simulate directional light)
                light_angle = (angle_y + i * 360 / steps) % 360
                light_factor = (math.cos(math.radians(light_angle)) + 1) / 2
                
                # Choose colors based on lighting
                if light_factor > 0.8:
                    edge_color = current_shine
                    char = '◆'
                elif light_factor > 0.5:
                    edge_color = colors['bright_gold']
                    char = '♦'
                elif light_factor > 0.3:
                    edge_color = colors['gold']
                    char = '●'
                else:
                    edge_color = colors['deep_gold']
                    char = '•'
                
                # Draw circumference of front face with enhanced effects
                p1 = proj_front[i]
                p2 = proj_front[next_i]
                draw_line(buffer, p1[0], int(p1[1] + bounce_offset), p2[0], int(p2[1] + bounce_offset), 
                         width, height, edge_color + char + reset)
                
                # Add sparkles on bright edges
                if light_factor > 0.7 and random.random() < 0.4:
                    draw_sparkle(buffer, p1[0], int(p1[1] + bounce_offset), width, height)
                
                # Draw circumference of back face
                p3 = proj_back[i]
                p4 = proj_back[next_i]
                back_color = colors['bronze'] if light_factor < 0.5 else colors['copper']
                draw_line(buffer, p3[0], int(p3[1] + bounce_offset), p4[0], int(p4[1] + bounce_offset), 
                         width, height, back_color + '○' + reset)
                
                # Draw connecting ridges with gradient effect
                ridge_color = colors['shadow'] if light_factor < 0.4 else colors['bronze']
                draw_line(buffer, p1[0], int(p1[1] + bounce_offset), p3[0], int(p3[1] + bounce_offset), 
                         width, height, ridge_color + '│' + reset)

            # Draw center emblem with pulsing effect
            center_x, center_y = width // 2, height // 2 + int(bounce_offset)
            pulse = int(2 + math.sin(glow_phase * 0.2) * 2)
            emblem_color = f"\033[1;38;5;{220 + pulse}m"
            
            # Draw $ symbol in center
            if 0 <= center_x < width and 0 <= center_y < height:
                buffer[center_y][center_x] = emblem_color + '💰' + reset
            
            # Add orbital sparkles
            for orbit in range(3):
                orbit_radius = 15 + orbit * 8
                orbit_angle = (glow_phase * (2 + orbit)) % 360
                orbit_x = center_x + int(orbit_radius * math.cos(math.radians(orbit_angle)))
                orbit_y = center_y + int(orbit_radius * math.sin(math.radians(orbit_angle)) * 0.5)
                if 0 <= orbit_x < width and 0 <= orbit_y < height and random.random() < 0.6:
                    sparkle_color = random.choice([colors['shine'], colors['bright_gold']])
                    buffer[orbit_y][orbit_x] = sparkle_color + '✨' + reset
            
            # Enhanced UI with animated border
            output = []
            output.append("\033[H\033[2J")  # Clear screen
            
            # Animated title with gradient effect
            title_colors = ["\033[38;5;220m", "\033[38;5;226m", "\033[38;5;228m", "\033[38;5;230m"]
            title_phase = int(glow_phase / 5) % len(title_colors)
            title_color = title_colors[title_phase]
            
            border_char = '═' if int(glow_phase / 3) % 2 else '━'
            top_border = f"{title_color}{border_char * width}{reset}"
            title_text = f"{current_shine}✦ ◆ ENCHANTED GOLDEN COIN ◆ ✦{reset}"
            
            output.append(top_border)
            output.append(title_text.center(width + 20))  # Account for ANSI codes
            output.append(f"{title_color}{''.join(['⬥'] * (width // 2))}{reset}")
            
            for row in buffer:
                output.append("".join(row))
            
            sys.stdout.write("\n".join(output))
            sys.stdout.flush()
            
            # Enhanced animation with variable speeds and effects
            # Dynamic coin toss with physics-like motion
            angle_x += 3 + math.sin(bounce_phase * 0.1) * 2  # Variable flip speed
            angle_y += 1.5 + glow_intensity * 0.5  # Glow-influenced spin
            angle_z += 0.5 * math.cos(bounce_phase * 0.05)  # Subtle wobble
            
            # Update animation phases
            glow_phase += 1
            bounce_phase += 1
            
            # Occasional speed bursts
            if random.random() < 0.02:
                spin_speed *= 1.5
            elif random.random() < 0.01:
                spin_speed *= 0.7
            spin_speed = max(0.5, min(2.0, spin_speed))
            
            # Add status info
            status_line = f"{colors['gold']}Spin: {angle_y:.1f}° | Glow: {glow_intensity:.2f} | Bounce: {bounce_offset:.1f}{reset}"
            output.append("")
            output.append(status_line.center(width + 20))
            
            time.sleep(0.04)  # Slightly faster for smoother animation
            
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    main()

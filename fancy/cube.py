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

def draw_particle(buffer, width, height, particles):
    """Draw floating particles around the cube"""
    for particle in particles:
        x, y, life, char, color = particle
        if 0 <= x < width and 0 <= y < height and life > 0:
            alpha = min(1.0, life / 30)
            buffer[int(y)][int(x)] = f"{color}{char}\033[0m"

def create_particles(center_x, center_y, count=15):
    """Create particle effects around a point"""
    particles = []
    particle_chars = ['•', '●', '✧', '✦', '⋆', '⭐']
    colors = ["\033[91m", "\033[93m", "\033[94m", "\033[95m", "\033[96m", "\033[1;91m"]
    
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.5, 2.0)
        distance = random.uniform(10, 25)
        x = center_x + math.cos(angle) * distance
        y = center_y + math.sin(angle) * distance * 0.5
        life = random.randint(20, 40)
        char = random.choice(particle_chars)
        color = random.choice(colors)
        particles.append([x, y, life, char, color])
    
    return particles

def update_particles(particles, dt=0.1):
    """Update particle positions and life"""
    for particle in particles:
        particle[0] += random.uniform(-0.5, 0.5)  # x drift
        particle[1] += random.uniform(-0.3, 0.1)  # y drift
        particle[2] -= 1  # decrease life
    return [p for p in particles if p[2] > 0]  # Remove dead particles

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
    width = 120
    height = 50
    
    # Enhanced cube vertices with larger size
    size = 1.8
    vertices = [
        [-size, -size, -size], [size, -size, -size], [size, size, -size], [-size, size, -size],
        [-size, -size, size], [size, -size, size], [size, size, size], [-size, size, size]
    ]
    
    # Edges connecting vertices indices
    edges = [
        (0,1), (1,2), (2,3), (3,0), # Back face
        (4,5), (5,6), (6,7), (7,4), # Front face
        (0,4), (1,5), (2,6), (3,7)  # Connecting lines
    ]
    
    # Faces for coloring (indices of vertices)
    faces = [
        [0, 1, 2, 3], # Back
        [4, 5, 6, 7], # Front
        [0, 4, 7, 3], # Left
        [1, 5, 6, 2], # Right
        [3, 2, 6, 7], # Top
        [0, 1, 5, 4]  # Bottom
    ]
    
    # Enhanced color palette with RGB and effects
    colors = {
        'neon_red': "\033[38;5;196m",
        'neon_green': "\033[38;5;46m", 
        'neon_blue': "\033[38;5;21m",
        'neon_purple': "\033[38;5;165m",
        'neon_cyan': "\033[38;5;51m",
        'neon_yellow': "\033[38;5;226m",
        'neon_pink': "\033[38;5;207m",
        'electric_blue': "\033[38;5;33m",
        'hot_pink': "\033[38;5;200m",
        'lime': "\033[38;5;118m",
        'bright_white': "\033[1;37m",
        'glow': "\033[1;38;5;255m"
    }
    color_list = list(colors.values())
    reset = "\033[0m"
    
    # Animation and effect variables
    pulse_phase = 0
    wave_phase = 0
    particles = []

    
    angle_x = 0
    angle_y = 0
    angle_z = 0
    
    # Enhanced rotation speeds
    speed_x = 2.5
    speed_y = 3.2
    speed_z = 1.8
    
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
            
            # Enhanced edge rendering with depth-based effects
            for i, edge in enumerate(edges):
                p1 = projected_points[edge[0]]
                p2 = projected_points[edge[1]]
                
                # Calculate 3D positions after rotation for depth
                v1 = vertices[edge[0]][:]
                v2 = vertices[edge[1]][:]
                
                # Apply all rotations to get final 3D position
                v1[1], v1[2] = rotate_x(v1[1], v1[2], angle_x)
                v1[0], v1[2] = rotate_y(v1[0], v1[2], angle_y)
                v1[0], v1[1] = rotate_z(v1[0], v1[1], angle_z)
                
                v2[1], v2[2] = rotate_x(v2[1], v2[2], angle_x)
                v2[0], v2[2] = rotate_y(v2[0], v2[2], angle_y)
                v2[0], v2[1] = rotate_z(v2[0], v2[1], angle_z)
                
                # Average Z depth for this edge
                avg_z = (v1[2] + v2[2]) / 2
                
                # Determine edge type and styling
                if i < 4:  # Back face edges
                    base_color = colors['neon_blue']
                    char = '□'  # Hollow square
                elif i < 8:  # Front face edges  
                    base_color = colors['neon_red']
                    char = '■'  # Filled square
                else:  # Connecting edges
                    base_color = colors['neon_purple']
                    char = '─'  # Horizontal line
                
                # Add depth-based intensity
                if avg_z > 0:  # Closer to viewer
                    color = colors['glow']
                    char = '█'  # Full block
                elif avg_z > -1:
                    color = base_color
                else:  # Further away
                    color = f"\033[2m{base_color.replace('[38', '[38')}"  # Dimmed
                    char = '░'  # Light shade
                
                # Add wave effect
                wave_intensity = abs(math.sin(wave_phase * 0.1 + i * 0.5))
                if wave_intensity > 0.8:
                    color = colors['neon_cyan']
                    char = '▉'  # Dense block
                
                draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height, color + char + reset)
                
                # Add occasional sparkle effects on edges
                if random.random() < 0.05:
                    mid_x, mid_y = (p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2
                    if 0 <= mid_x < width and 0 <= mid_y < height:
                        sparkle_color = random.choice([colors['neon_yellow'], colors['bright_white']])
                        buffer[mid_y][mid_x] = f"{sparkle_color}✨{reset}"
                
            # Enhanced vertex rendering with pulsing effect
            pulse_intensity = (math.sin(pulse_phase * 0.15) + 1) / 2
            vertex_color = f"\033[38;5;{int(196 + pulse_intensity * 30)}m"
            
            for i, p in enumerate(projected_points):
                if 0 <= p[0] < width and 0 <= p[1] < height:
                    # Different symbols for different vertices
                    vertex_chars = ['❖', '✶', '✿', '❀', '❁', '❂', '❃', '❅']
                    char = vertex_chars[i] if i < len(vertex_chars) else '❖'
                    buffer[p[1]][p[0]] = f"{vertex_color}{char}{reset}"
                    
                    # Generate particles around vertices occasionally
                    if random.random() < 0.08:
                        particles.extend(create_particles(p[0], p[1], count=3))
            
            # Update and draw particles
            particles = update_particles(particles)
            draw_particle(buffer, width, height, particles)

            # Enhanced UI with dynamic effects
            output = []
            output.append("\033[H\033[2J")  # Clear screen and home cursor
            
            # Animated title with cycling colors
            title_color = color_list[int(pulse_phase / 8) % len(color_list)]
            glow_char = '★' if int(pulse_phase / 4) % 2 else '⭐'
            
            # Create fancy border
            border_chars = ['═', '━', '╌', '╍']
            current_border = border_chars[int(wave_phase / 10) % len(border_chars)]
            top_border = f"{colors['electric_blue']}{current_border * width}{reset}"
            
            title_text = f"{title_color}{glow_char} ◆◇ QUANTUM HYPERCUBE ◇◆ {glow_char}{reset}"
            subtitle = f"{colors['neon_cyan']}∴ Dimensional Matrix Visualizer ∴{reset}"
            
            output.append(top_border)
            output.append(title_text.center(width + 30))
            output.append(subtitle.center(width + 20))
            output.append(f"{colors['hot_pink']}{''.join(['⋅'] * (width // 2))}{reset}")
            
            for row in buffer:
                # Since we have ANSI codes in the buffer, just joining them is fine
                # but we need to handle the length carefully if we were centering strings.
                output.append("".join(row))
            
            # Print everything at once to reduce flicker
            sys.stdout.write("\n".join(output))
            sys.stdout.flush()
            
            # Dynamic rotation with variable speeds and effects
            # Sine wave modulation for organic movement
            speed_mod_x = 1 + 0.5 * math.sin(wave_phase * 0.05)
            speed_mod_y = 1 + 0.3 * math.cos(wave_phase * 0.07)
            speed_mod_z = 1 + 0.4 * math.sin(wave_phase * 0.03)
            
            angle_x += speed_x * speed_mod_x
            angle_y += speed_y * speed_mod_y
            angle_z += speed_z * speed_mod_z
            
            # Update animation phases
            pulse_phase += 1
            wave_phase += 1
            
            # Random speed variations
            if random.random() < 0.01:
                speed_x += random.uniform(-0.5, 0.5)
                speed_y += random.uniform(-0.5, 0.5)
                speed_z += random.uniform(-0.5, 0.5)
                
                # Keep speeds in reasonable range
                speed_x = max(1, min(5, speed_x))
                speed_y = max(1, min(5, speed_y))
                speed_z = max(1, min(5, speed_z))
            
            # Enhanced status display
            stats_color = colors['lime']
            status_line = f"{stats_color}Angles: X:{angle_x:.1f}° Y:{angle_y:.1f}° Z:{angle_z:.1f}° | Particles: {len(particles)} | Wave: {wave_phase}{reset}"
            output.append("")
            output.append(status_line.center(width + 40))
            
            # Performance indicator
            perf_color = colors['neon_green'] if len(particles) < 50 else colors['neon_yellow']
            perf_line = f"{perf_color}⚡ Performance: {'OPTIMAL' if len(particles) < 50 else 'HIGH LOAD'} ⚡{reset}"
            output.append(perf_line.center(width + 20))
            
            time.sleep(0.035)  # Faster animation
            
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    # Clear screen once at start
    os.system('cls' if os.name == 'nt' else 'clear')
    main()

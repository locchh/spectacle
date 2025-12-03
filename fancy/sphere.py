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

def calculate_lighting(x, y, z, light_pos, light_intensity=1.0):
    """Calculate lighting intensity based on position relative to light source"""
    # Vector from surface point to light
    lx, ly, lz = light_pos
    dx, dy, dz = lx - x, ly - y, lz - z
    distance = math.sqrt(dx*dx + dy*dy + dz*dz)
    
    # Surface normal (for sphere, it's the normalized position vector)
    normal_length = math.sqrt(x*x + y*y + z*z)
    if normal_length == 0:
        return 0
    
    nx, ny, nz = x/normal_length, y/normal_length, z/normal_length
    
    # Light direction (normalized)
    if distance == 0:
        return light_intensity
    light_dx, light_dy, light_dz = dx/distance, dy/distance, dz/distance
    
    # Dot product for diffuse lighting (Lambert's law)
    dot_product = max(0, nx*light_dx + ny*light_dy + nz*light_dz)
    
    # Distance falloff
    falloff = 1.0 / (1.0 + distance * 0.1)
    
    return dot_product * light_intensity * falloff

def create_stars(width, height, count=50):
    """Create background stars"""
    stars = []
    star_chars = ['•', '·', '✧', '⋅', '*', '✱']
    star_colors = ["\033[37m", "\033[1;37m", "\033[36m", "\033[1;36m", "\033[35m"]
    
    for _ in range(count):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        char = random.choice(star_chars)
        color = random.choice(star_colors)
        brightness = random.uniform(0.3, 1.0)
        stars.append((x, y, char, color, brightness))
    
    return stars

def draw_stars(buffer, stars, phase):
    """Draw twinkling background stars"""
    for x, y, char, color, base_brightness in stars:
        # Twinkling effect
        twinkle = abs(math.sin(phase * 0.1 + x * 0.1 + y * 0.05))
        brightness = base_brightness * (0.5 + 0.5 * twinkle)
        
        if random.random() < brightness:
            if 0 <= x < len(buffer[0]) and 0 <= y < len(buffer):
                buffer[y][x] = f"{color}{char}\033[0m"

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
    width = 110
    height = 55
    
    # Enhanced sphere properties
    radius = 2.5
    lat_steps = 16  # More detail
    lon_steps = 24  # More detail
    
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

    # Animation variables
    angle_x = 0
    angle_y = 0
    angle_z = 0
    
    # Lighting setup
    light_phase = 0
    aurora_phase = 0
    
    # Create background elements
    stars = create_stars(width, height, 80)
    
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
            
            # Enhanced lighting and color system
            # Dynamic light source that orbits around the sphere
            light_x = 3 * math.cos(light_phase * 0.02)
            light_y = 2 * math.sin(light_phase * 0.03)
            light_z = 4 + math.sin(light_phase * 0.01)
            light_pos = (light_x, light_y, light_z)
            
            # Advanced color palette
            colors = {
                'plasma_purple': "\033[38;5;135m",
                'plasma_pink': "\033[38;5;201m", 
                'plasma_blue': "\033[38;5;39m",
                'plasma_cyan': "\033[38;5;87m",
                'electric_blue': "\033[38;5;33m",
                'neon_green': "\033[38;5;46m",
                'aurora_pink': "\033[38;5;205m",
                'aurora_green': "\033[38;5;83m",
                'deep_purple': "\033[38;5;55m",
                'bright_white': "\033[1;37m",
                'dim_blue': "\033[2;38;5;25m"
            }
            reset = "\033[0m"
            
            # Draw background stars first
            draw_stars(buffer, stars, light_phase)
            
            # Enhanced sphere rendering with lighting
            for i, edge in enumerate(edges):
                p1 = projected_points[edge[0]]
                p2 = projected_points[edge[1]]
                
                # Get 3D coordinates after rotation for lighting calculation
                v1_idx, v2_idx = edge[0], edge[1]
                
                # Calculate lighting for both vertices
                v1_3d = vertices[v1_idx][:]
                v2_3d = vertices[v2_idx][:]
                
                # Apply rotations to get world coordinates
                v1_3d[1], v1_3d[2] = rotate_x(v1_3d[1], v1_3d[2], angle_x)
                v1_3d[0], v1_3d[2] = rotate_y(v1_3d[0], v1_3d[2], angle_y)
                v1_3d[0], v1_3d[1] = rotate_z(v1_3d[0], v1_3d[1], angle_z)
                
                v2_3d[1], v2_3d[2] = rotate_x(v2_3d[1], v2_3d[2], angle_x)
                v2_3d[0], v2_3d[2] = rotate_y(v2_3d[0], v2_3d[2], angle_y)
                v2_3d[0], v2_3d[1] = rotate_z(v2_3d[0], v2_3d[1], angle_z)
                
                # Calculate average lighting
                light1 = calculate_lighting(v1_3d[0], v1_3d[1], v1_3d[2], light_pos)
                light2 = calculate_lighting(v2_3d[0], v2_3d[1], v2_3d[2], light_pos)
                avg_light = (light1 + light2) / 2
                
                # Determine color and character based on lighting
                if avg_light > 0.8:
                    color = colors['bright_white']
                    char = '█'  # Full block
                elif avg_light > 0.6:
                    color = colors['plasma_cyan']
                    char = '▓'  # Dark shade
                elif avg_light > 0.4:
                    color = colors['plasma_blue']
                    char = '▒'  # Medium shade
                elif avg_light > 0.2:
                    color = colors['plasma_purple']
                    char = '░'  # Light shade
                else:
                    color = colors['deep_purple']
                    char = '·'  # Middle dot
                
                # Add aurora effect on certain edges
                aurora_intensity = abs(math.sin(aurora_phase * 0.05 + i * 0.3))
                if aurora_intensity > 0.7:
                    aurora_color = colors['aurora_pink'] if i % 2 else colors['aurora_green']
                    color = aurora_color
                    char = '✧'  # Sparkle
                
                # Optimization: Don't draw if both points are off screen
                if (0 <= p1[0] < width or 0 <= p2[0] < width) and \
                   (0 <= p1[1] < height or 0 <= p2[1] < height):
                    draw_line(buffer, p1[0], p1[1], p2[0], p2[1], width, height, color + char + reset)
            
            # Enhanced vertex rendering with dynamic effects
            for i, p in enumerate(projected_points):
                if 0 <= p[0] < width and 0 <= p[1] < height:
                    # Calculate lighting for vertex
                    v_3d = vertices[i][:]
                    v_3d[1], v_3d[2] = rotate_x(v_3d[1], v_3d[2], angle_x)
                    v_3d[0], v_3d[2] = rotate_y(v_3d[0], v_3d[2], angle_y)
                    v_3d[0], v_3d[1] = rotate_z(v_3d[0], v_3d[1], angle_z)
                    
                    vertex_light = calculate_lighting(v_3d[0], v_3d[1], v_3d[2], light_pos)
                    
                    # Different vertex symbols based on lighting
                    if vertex_light > 0.7:
                        vertex_char = '⭐'  # Star
                        vertex_color = colors['bright_white']
                    elif vertex_light > 0.4:
                        vertex_char = '●'  # Filled circle
                        vertex_color = colors['plasma_cyan']
                    else:
                        vertex_char = '○'  # Empty circle
                        vertex_color = colors['plasma_purple']
                    
                    # Pulsing effect on bright vertices
                    pulse = abs(math.sin(light_phase * 0.1 + i * 0.5))
                    if vertex_light > 0.6 and pulse > 0.8:
                        vertex_char = '✨'  # Sparkles
                        vertex_color = colors['aurora_pink']
                    
                    buffer[p[1]][p[0]] = vertex_color + vertex_char + reset
                    
                    # Add energy rings around bright vertices
                    if vertex_light > 0.8 and random.random() < 0.1:
                        for ring_r in range(1, 4):
                            for angle in range(0, 360, 45):
                                ring_x = p[0] + int(ring_r * math.cos(math.radians(angle)))
                                ring_y = p[1] + int(ring_r * math.sin(math.radians(angle)) * 0.5)
                                if 0 <= ring_x < width and 0 <= ring_y < height:
                                    ring_intensity = 1.0 / ring_r
                                    if random.random() < ring_intensity * 0.3:
                                        ring_color = colors['neon_green']
                                        buffer[ring_y][ring_x] = f"{ring_color}⋅{reset}"

            # Spectacular UI with dynamic elements
            output = []
            output.append("\033[H\033[2J")  # Clear screen
            
            # Dynamic title with aurora colors
            title_colors = [colors['aurora_pink'], colors['aurora_green'], colors['plasma_cyan'], colors['plasma_purple']]
            title_color = title_colors[int(aurora_phase / 15) % len(title_colors)]
            
            # Animated border with constellation theme
            constellation_chars = ['★', '☆', '⭐', '✪', '✨', '✴']
            border_char = constellation_chars[int(light_phase / 10) % len(constellation_chars)]
            
            cosmic_border = f"{colors['electric_blue']}{''.join([border_char if i % 3 == 0 else '─' for i in range(width)])}{reset}"
            
            title_main = f"{title_color}✦ ◆◇ PLASMA SPHERE NEBULA ◇◆ ✦{reset}"
            subtitle = f"{colors['plasma_cyan']}∴ Quantum Field Visualization ∴{reset}"
            light_info = f"{colors['neon_green']}⚡ Light Source: ({light_x:.1f}, {light_y:.1f}, {light_z:.1f}) ⚡{reset}"
            
            output.append(cosmic_border)
            output.append(title_main.center(width + 30))
            output.append(subtitle.center(width + 20))
            output.append(light_info.center(width + 30))
            output.append(f"{colors['aurora_pink']}{''.join(['·'] * (width // 2))}{reset}")
            
            for row in buffer:
                output.append("".join(row))
            
            sys.stdout.write("\n".join(output))
            sys.stdout.flush()
            
            # Sophisticated animation with orbital mechanics
            # Primary rotation (sphere spinning)
            angle_x += 0.8 + 0.3 * math.sin(light_phase * 0.01)
            angle_y += 1.2 + 0.2 * math.cos(light_phase * 0.015)
            angle_z += 0.5 + 0.1 * math.sin(light_phase * 0.02)
            
            # Update animation phases
            light_phase += 1
            aurora_phase += 1
            
            # Occasional gravitational perturbations
            if random.random() < 0.005:
                angle_x += random.uniform(-5, 5)
                angle_y += random.uniform(-5, 5)
            
            # Regenerate some stars occasionally for twinkling effect
            if light_phase % 200 == 0:
                new_stars = create_stars(width, height, 10)
                stars = stars[:-10] + new_stars
            
            # Enhanced status and performance display
            stats_color = colors['plasma_cyan']
            aurora_level = "HIGH" if abs(math.sin(aurora_phase * 0.05)) > 0.7 else "MEDIUM" if abs(math.sin(aurora_phase * 0.05)) > 0.3 else "LOW"
            
            status_line = f"{stats_color}Rotation: X:{angle_x:.1f}° Y:{angle_y:.1f}° Z:{angle_z:.1f}°{reset}"
            aurora_line = f"{colors['aurora_pink']}Aurora Activity: {aurora_level} | Phase: {aurora_phase}{reset}"
            perf_line = f"{colors['neon_green']}⚡ Vertices: {len(vertices)} | Edges: {len(edges)} | Stars: {len(stars)} ⚡{reset}"
            
            output.append("")
            output.append(status_line.center(width + 20))
            output.append(aurora_line.center(width + 20))
            output.append(perf_line.center(width + 30))
            
            time.sleep(0.04)  # Smooth animation
            
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    main()

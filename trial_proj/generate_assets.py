from PIL import Image, ImageDraw

def create_bird():
    # Create a 32x32 image with transparency
    img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Bird body (yellow)
    draw.ellipse([4, 4, 28, 28], fill=(255, 223, 0))
    
    # Wing (darker yellow)
    draw.ellipse([8, 12, 20, 24], fill=(218, 165, 32))
    
    # Eye (white with black pupil)
    draw.ellipse([20, 8, 26, 14], fill=(255, 255, 255))
    draw.ellipse([22, 10, 24, 12], fill=(0, 0, 0))
    
    # Beak (orange)
    draw.polygon([(26, 14), (32, 16), (26, 18)], fill=(255, 140, 0))
    
    img.save('assets/bird.png')

def create_background():
    # Create a 400x600 image
    img = Image.new('RGB', (400, 600), (135, 206, 235))  # Sky blue
    draw = ImageDraw.Draw(img)
    
    # Draw sun
    draw.ellipse([320, 50, 380, 110], fill=(255, 255, 0))
    
    # Draw clouds
    cloud_color = (255, 255, 255)
    for y in [80, 150, 200]:
        for x in range(0, 400, 200):
            draw.ellipse([x, y, x+60, y+30], fill=cloud_color)
            draw.ellipse([x+20, y-10, x+80, y+20], fill=cloud_color)
            draw.ellipse([x+40, y, x+100, y+30], fill=cloud_color)
    
    # Draw mountains
    mountain_color = (101, 67, 33)  # Brown
    draw.polygon([(0, 600), (0, 400), (100, 300), (200, 400), (300, 350), (400, 420), (400, 600)], 
                fill=mountain_color)
    
    # Draw grass
    grass_color = (34, 139, 34)  # Forest green
    draw.rectangle([0, 500, 400, 600], fill=grass_color)
    
    img.save('assets/background.png')

def create_pipe():
    # Create a 52x600 image with transparency
    img = Image.new('RGBA', (52, 600), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Main pipe body (green)
    pipe_color = (40, 180, 40)
    draw.rectangle([0, 0, 50, 600], fill=pipe_color)
    
    # Pipe highlight
    highlight_color = (60, 200, 60)
    draw.rectangle([2, 0, 10, 600], fill=highlight_color)
    
    # Pipe edge
    edge_color = (35, 155, 35)
    draw.rectangle([0, 0, 50, 20], fill=edge_color)
    draw.rectangle([0, 580, 50, 600], fill=edge_color)
    
    img.save('assets/pipe.png')

if __name__ == '__main__':
    create_bird()
    create_background()
    create_pipe()

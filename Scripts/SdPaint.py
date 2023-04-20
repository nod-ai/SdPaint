import pygame
import requests
import threading
import numpy as np
import base64
import io
import json
import time
from PIL import Image, ImageOps
import tkinter as tk
from tkinter import filedialog

# Initialize Pygame
pygame.init()

# setup sd inputs
url = "http://localhost:8080"
prompt = "A painting by Monet"
seed = 3456456767

# Set up the display
screen = pygame.display.set_mode((1024, 512))
pygame.display.set_caption("Sd Paint with SHARK")
# Setup text
font = pygame.font.SysFont(None, 24)
# Set up the drawing surface
canvas = pygame.Surface((1024, 562))
pygame.draw.rect(canvas, (255, 255, 255), (0, 50, 1024, 512))


colour_active = pygame.Color('lightskyblue3')
colour_passive = pygame.Color('gray15')
colour_wrong = pygame.Color('red')
colour_default_text = pygame.Color('cornsilk3')

# PROMPT BOX
prompt = ""
prompt_rect = pygame.Rect(0, 0, 924, 50)
prompt_rec_color = colour_passive
prompt_rect_active = False
default_prompt = "Enter your prompt here and then go back to scribbling in the canvas on left (default is 'shark')"
prompt_box_text = default_prompt

# STEPS BOX
steps = "20"
steps_rect = pygame.Rect(924, 0, 100, 50)
steps_rec_color = colour_passive
steps_rect_active = False
invalid_step = False

# VERTICAL LINE
line_color = (0, 0, 0)

# Set up the brush
brush_size = {1: 2, 2: 10}
brush_colors = {
    1: (0, 0, 0),  # Left mouse button color
    2: (255, 255, 255),  # Middle mouse button color
}
brush_pos = {1: None, 2: None}

# Define the cursor size and color
cursor_size = 1
cursor_color = (0, 0, 0)

# Set up flag to check if server is busy or not
server_busy = False

def save_file_dialog():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(defaultextension=".png")
    saveimg = canvas.subsurface(pygame.Rect(0, 0, 512, 512)).copy()
    if file_path:
        pygame.image.save(saveimg, file_path)
        time.sleep(1)  # add a 1-second delay
    return file_path

def update_image(image_data):
    # Decode base64 image data
    img_bytes = io.BytesIO(base64.b64decode(image_data))
    img_surface = pygame.image.load(img_bytes)
    canvas.blit(img_surface, (512, 50))

def update_payload():
    with open("payload.json", "r") as f:
        payload = json.load(f)
    if prompt != "":
        payload["prompt"] = prompt
    else:
        payload["prompt"] = "shark"
    payload["steps"] = int(steps)
    with open("payload.json", "w") as f:
        json.dump(payload, f, indent=4)

def is_invalid_step():
    if not steps.isnumeric():
        return True
    if steps == "":
        return True
    int_steps = int(steps)
    if int_steps not in range(1,150):
        return True

# Set up the main loop
running = True
while running:

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if prompt_rect_active:
                if event.key == pygame.K_BACKSPACE:
                    prompt = prompt[:-1]
                else:
                    prompt += event.unicode
            elif steps_rect_active:
                if event.key == pygame.K_BACKSPACE:
                    steps = steps[:-1]
                elif len(steps) < 3:
                    steps += event.unicode
                invalid_step = is_invalid_step()
            elif event.key == pygame.K_BACKSPACE:
                pygame.draw.rect(canvas, (255, 255, 255), (0, 50, 512, 512))
            elif event.key == pygame.K_s:
                save_file_dialog()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if prompt_rect.collidepoint(event.pos):
                prompt_rect_active = True
                steps_rect_active = False
            elif steps_rect.collidepoint(event.pos):
                steps_rect_active = True
                prompt_rect_active = False
            elif event.button in brush_colors:
                brush_pos[event.button] = event.pos
                prompt_rect_active = False
                steps_rect_active = False
            elif event.button == 4:  # scroll up
                brush_size[1] = max(1, brush_size[1] + 1)
                prompt_rect_active = False
                steps_rect_active = False
            elif event.button == 5:  # scroll down
                brush_size[1] = max(1, brush_size[1] - 1)
                prompt_rect_active = False
                steps_rect_active = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if prompt_rect.collidepoint(event.pos):
                prompt_rect_active = True
                steps_rect_active = False
            elif steps_rect.collidepoint(event.pos):
                steps_rect_active = True
                prompt_rect_active = False
            elif event.button in brush_colors:
                prompt_rect_active = False
                steps_rect_active = False
                update_payload()
                brush_pos[event.button] = None
                brush_color = brush_colors[event.button]
                # Check if server is busy before sending request
                if not server_busy:
                    server_busy = True
                    img = canvas.subsurface(pygame.Rect(0, 50, 512, 512)).copy()

                    # Convert the Pygame surface to a PIL image
                    pil_img = Image.frombytes('RGB', img.get_size(), pygame.image.tostring(img, 'RGB'))

                    # Invert the colors of the PIL image
                    pil_img = ImageOps.invert(pil_img)

                    # Convert the PIL image back to a Pygame surface
                    img = pygame.image.fromstring(pil_img.tobytes(), pil_img.size, pil_img.mode).convert_alpha()

                    # Save the inverted image as base64-encoded data
                    data = io.BytesIO()
                    pygame.image.save(img, data)
                    data = base64.b64encode(data.getvalue()).decode('utf-8')
                    with open("payload.json", "r") as f:
                        payload = json.load(f)
                    payload['init_images'][0] = data
                    
                    def send_request():
                        global server_busy
                        response = requests.post(url=f'{url}/sdapi/v1/img2img', json=payload)
                        r = response.json()
                        return_img = r['images'][0]
                        update_image(return_img)
                        server_busy = False
                    
                    t = threading.Thread(target=send_request)
                    t.start()
        elif event.type == pygame.MOUSEMOTION:
            for button, pos in brush_pos.items():
                if pos is not None and button in brush_colors:
                    pygame.draw.circle(canvas, brush_colors[button], event.pos, brush_size[button])
    
    # Draw the canvas and brushes on the screen
    if prompt_rect_active:
        prompt_rec_color = colour_active
    else:
        prompt_rec_color = colour_passive
    if steps_rect_active:
        steps_rec_color = colour_active
        if invalid_step:
            steps_rec_color = colour_wrong
    else:
        steps_rec_color = colour_passive
    pygame.draw.rect(canvas, prompt_rec_color, prompt_rect, 5)
    prompt_text_surface = ""
    if prompt == "" and not prompt_rect_active:
        prompt_text_surface = font.render(default_prompt, True, colour_default_text)
    else:
        prompt_text_surface = font.render(prompt, True, (255, 255, 255))
    pygame.draw.rect(canvas, steps_rec_color, steps_rect, 5)
    steps_text_surface = font.render(steps, True, (255, 255, 255))
    screen.blit(canvas, (0, 0))
    
    # Create a new surface with a circle
    cursor_size = brush_size[1]*2
    cursor_surface = pygame.Surface((cursor_size, cursor_size), pygame.SRCALPHA)
    pygame.draw.circle(cursor_surface, cursor_color, (cursor_size // 2, cursor_size // 2), cursor_size // 2)

    # Blit the cursor surface onto the screen surface at the position of the mouse
    mouse_pos = pygame.mouse.get_pos()
    screen.blit(cursor_surface, (mouse_pos[0] - cursor_size // 2, mouse_pos[1] - cursor_size // 2))
        
    pygame.draw.line(canvas, line_color, (512, 50), (512, 562))
    screen.blit(prompt_text_surface, (prompt_rect.x + 10, prompt_rect.y + 20))
    screen.blit(steps_text_surface, (steps_rect.center[0] - 7, steps_rect.center[1] - 5))
    for button, pos in brush_pos.items():
        if pos is not None and button in brush_colors:
            pygame.draw.circle(screen, brush_colors[button], pos, brush_size[button])

    # Update the display
    pygame.display.update()

# Clean up Pygame
pygame.quit()
mouse_x = pyautogui.position()[0]
mouse_y = pyautogui.position()[1]

if not os.path.isfile(path):
   raise SystemExit("No screenshot found")
image = Image.open(path)

prompt = f"""The cursor\'s current position is ({mouse_x}, {mouse_y}). The screen size is 1920 x 1080. Please indicate the 
             new x and y position for the cursor (where you want to move it to). 
             Expected format: 
                {{
                  X: *new x position*,
                  Y: *new y position* 
                }}
             """
response = model.generate_content([prompt, image])

print(response.text)

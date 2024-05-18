"""
test gemini vision (sending images)
get consistent output from it (mouse movements and keyboard inputs)
use pyautogui to automate the loop of:
    - screenshot
    - send screenshot and ask for mouse and keyboard input
    - use pyautogui to execute the inputs

after the above is working, try to implement NLP and make more user friendly
""" 
import json
import google.generativeai as genai
from dotenv import load_dotenv
import os, shutil
import pyautogui
from PIL import Image

CURRENT_DIR = os.getcwd()
screenshots_dir = os.path.join(CURRENT_DIR, 'screenshots')
current_screenshot = 1
path = os.path.join(screenshots_dir, f"screenshot{current_screenshot}.png")

def delete_screenshots():
    for filename in os.listdir(screenshots_dir):
        file_path = os.path.join(screenshots_dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def parse_response(response):
    response = response.strip()
    print(response)
    data = json.loads(response)
    X = data["X"]
    Y = data["Y"]
    drag = float(data["Drag"])
    inputs = data["Inputs"]
    left_click = float(data["Left Click"])
    right_click = float(data["Right Click"])
    thoughts = data["Thoughts"]

    return float(X), float(Y), bool(drag), bool(left_click), bool(right_click), str(inputs), str(thoughts)

def perform_actions(x, y, drag, left_click, right_click, inputs):
    if drag: pyautogui.dragTo(x, y, button='left')
    else: 
        if left_click: pyautogui.click(x, y)
        if right_click: pyautogui.click(x, y, button='right')
    
    print(f'moving cursor to ({x},{y})')

    pyautogui.write(inputs, interval=0.1) # interval subject to change

load_dotenv()
API_KEY = os.getenv('API_KEY')

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro-vision')

# loop start
for i in range(30):
    delete_screenshots()
    screenshot = pyautogui.screenshot(path)
    current_screenshot += 1

    mouse_x = pyautogui.position()[0]
    mouse_y = pyautogui.position()[1]

    if not os.path.isfile(path):
        raise SystemExit("No screenshot found")
    image = Image.open(path)

    prompt = f"""The cursor\'s current position is ({mouse_x}, {mouse_y}). The screen size is 1920 x 1080. Please indicate the 
                new x and y position for the cursor (where you want to move it to). To left click and drag, indicate it by writing 'True' in the 'Drag' field.
                The Left Click and Right Click fields are for if you would like to perform a click at the new cursor position.
                If you would like to type anything please enter your inputs in the 'Inputs' field. Keep in mind however that combinations 
                will not work and each character will be typed consecutively. In the 'Thoughts' field you should include your current thoughts and
                what you are trying to do. 
                NOTES: Always include the double quotes around the keys, this is essential for it to be valid JSON. Fields enclosed with asterisks are placeholders.
                ***IMPORTANT*** Your goal is to navigate to chess.com and attempt to play a game!
                Expected format: 
                    {{
                    "X": *new x position*,
                    "Y": *new y position*,
                    "Drag": *1 or 0*,
                    "Left Click": *1 or 0*,
                    "Right Click": *1 or 0*,
                    "Inputs": *abc*,
                    "Thoughts": *I am trying to do...*
                    }}
                """

    # should add error handling for this response and error handling in general
    # maybe make it async too
    response = model.generate_content([prompt, image])
    response_text = response.text
    # print(response.text) # would be good to know what this response looks like when it fails

    # after a response is recieved
    x, y, drag, left_click, right_click, inputs, thoughts = parse_response(response.text)
    print(f'GEMINI: {thoughts}') 
    perform_actions(x, y, drag, left_click, right_click, inputs) 


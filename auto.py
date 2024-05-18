"""
test gemini vision (sending images)
get consistent output from it (mouse movements and keyboard inputs)
use pyautogui to automate the loop of:
    - screenshot
    - send screenshot and ask for mouse and keyboard input
    - use pyautogui to execute the inputs

after the above is working, try to implement NLP and make more user friendly
""" 
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

load_dotenv()
API_KEY = os.getenv('API_KEY')

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro-vision')

screenshot = pyautogui.screenshot(path)
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


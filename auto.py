"""
TODO 
    - reprompt user for goal when current one is completed
    - find the best way for it to interact with the computer
    - add overlay
Ideas:
    - allow user to give it feedback (i.e move down more)
    - more visible cursor
    - draw grid on screen to make mouse movements more accurate

Back button on browsers are located at (30, 60)

"""
import json
import google.generativeai as genai
from dotenv import load_dotenv
import os, shutil
import pyautogui
from PIL import Image
import time
import pyttsx3
from overlay import Overlay
import cv2
import numpy as np

pyautogui.FAILSAFE = False # seems kinda dangerous

class Auto:
    CURRENT_DIR = os.getcwd()
    screenshots_dir = os.path.join(CURRENT_DIR, 'screenshots')
    path = os.path.join(screenshots_dir, f"screenshot.png")
    previous_responses = []
    overlay = None
    tts = pyttsx3.init()
    load_dotenv()
    API_KEY = os.getenv('API_KEY')

    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-pro-vision')

    def delete_screenshots():
        for filename in os.listdir(Auto.screenshots_dir):
            file_path = os.path.join(Auto.screenshots_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    def parse_response(response):
        response = response.replace('`', "").strip()
        response = response.replace('json', "")
        print(response)
        data = json.loads(response)
        X = data["X"]
        Y = data["Y"]
        click = data["Click"]
        typing = data["Typing"]
        press = data["Press"]
        thoughts = data["Thoughts"]

        return float(X), float(Y), click=='True', str(typing), str(press).lower(), str(thoughts)

    def perform_actions(x, y, click, typing, press):
        pyautogui.moveTo(x, y)    
        print(f'moving cursor to ({x},{y})')
        if click: pyautogui.click()
        pyautogui.write(typing, interval=0.1) # interval subject to change
        time.sleep(1)
        pyautogui.press(press)

    def responses_to_string(past_responses):
        string = ""
        for response in past_responses:
            string += (response + '\n')
        return string

    def call_overlay(thoughts):
        if Auto.overlay: # clear overlays that exist 
            Auto.overlay.destroy()
        # draw the new overlay
        Auto.overlay = Overlay(thoughts) 
        Auto.overlay.start()

    def screenshot():
        screen_width, screen_height = pyautogui.size()
        screenshot = pyautogui.screenshot(Auto.path)
        screen_image = np.array(screenshot) # screenshot
        grid_image = np.zeros_like(screen_image) # grid image file

        num_rows = 50
        num_cols = 50
        row_height = screen_height // num_rows
        col_width = screen_width // num_cols

        # Draw horizontal lines (21 high)
        for i in range(num_rows + 1):
            y = i * row_height
            cv2.line(grid_image, (0, y), (screen_width, y), (255, 255, 255), 1)

        # Draw vertical lines (38 wide)
        for j in range(num_cols + 1):
            x = j * col_width 
            
            cv2.line(grid_image, (x, 0), (x, screen_height), (255, 255, 255), 1)

        final_image = cv2.addWeighted(screen_image, 1, grid_image, 0.5, 0) # put grid on top off screenshot
        cv2.imwrite(Auto.path, final_image)

    # loop start
    def main(goal, feedback):
        Auto.delete_screenshots()
        Auto.screenshot()

        if not os.path.isfile(Auto.path):
            raise SystemExit("No screenshot found")
        image = Image.open(Auto.path)

        prompt = f"""
                    YOUR GOAL: {goal}

                    Based on the screenshot, your goal, and any previous responses, generate the next best series of inputs.
                    The inputs you provide will then be executed with pyautogui. When you write your thoughts, please also state the reasons
                    behind your actions. 
                    The screenshot you see contains a grid. Each cell of the grid is 38 x 21 pixels wide. Use that information to accurately 
                    determine where you want to move the cursor.
                    If you notice yourself repeating the exact same thoughts over and over, PLEASE try doing something new.
                    Keep in mind that 'Click' must be set to True if you wish to click on something.
                    Keep in mind that somethings take time to load and it may be best to do nothing sometimes.
                    You can: 
                        - Move the mouse to a new position
                        - Choose to click
                        - Type any keyboard inputs
                        - Press any keyboard key for a particular operation (Ex: enter, escape, shift, backspace keys)
                    
                    IMPORTANT LOCATIONS:
                        - Search bar is located at (826, 1060)

                    Expected format: 
                        {{
                        "X": *new x position*,
                        "Y": *new y position*,
                        "Click": "True|False",
                        "Typing": *abc*,
                        "Press": *shift*
                        "Thoughts": *I am trying to do... because...*
                        }}

                    Feedback: {feedback}    
                    
                    PAST RESPONSES:
                    """ + Auto.responses_to_string(Auto.previous_responses)

        # should add error handling for this response and error handling in general
        # maybe make it async too
        print('generating response...')
        response = Auto.model.generate_content([prompt, image])
        Auto.previous_responses.append(response.text)

        # after a response is recieved
        x, y, click, typing, press, thoughts = Auto.parse_response(response.text)
        Auto.tts.say(thoughts)
        Auto.tts.runAndWait()
        # Auto.call_overlay(thoughts)
        Auto.perform_actions(x, y, click, typing, press)
        Auto.delete_screenshots()



"""
TODO 
    - reprompt user for goal when current one is completed
    - find the best way for it to interact with the computer (kinda impossible)
    - add overlay
Ideas:
    - allow user to give it feedback (i.e move down more) 1/2
    - more visible cursor x
    - draw grid on screen to make mouse movements more accurate x
    - single action at a time x
    - ask for what cell it wants to click on instead x
    - everytime it fails, tell it not to do that and have a super long prompt

    Before sending the request, prompt the user to add feedback
    Begin recording audio from mic, if after 3 seconds no words are spoken, send the request with no feedback
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
from playsound import playsound

pyautogui.FAILSAFE = False # seems kinda dangerous

class Auto:
    CURRENT_DIR = os.getcwd()
    screenshots_dir = os.path.join(CURRENT_DIR, 'screenshots')
    sounds_dir = os.path.join(CURRENT_DIR, 'sounds')
    path = os.path.join(screenshots_dir, f"screenshot.png")
    response_sound_path = os.path.join(sounds_dir, f"response.mp3")
    activate_sound_path = os.path.join(sounds_dir, f"voice_activate.mp3")
    shutter_sound_path = os.path.join(sounds_dir, f"shutter.mp3")
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
        data = json.loads(response)
        X = data["X"]
        Y = data["Y"]
        click = data["Click"]
        typing = data["Typing"]
        press = data["Press"]
        thoughts = data["Thoughts"]
        new_goal = data["New Goal"]
        return float(X), float(Y), click=='True', str(typing), str(press).lower(), str(thoughts), str(new_goal)
    
    def perform_actions(x, y, click, typing, press):
        pyautogui.moveTo(x * 38, y * 21)    
        if click: pyautogui.click()
        pyautogui.write(typing) # interval subject to change
        time.sleep(0.5)
        pyautogui.press(press)
        time.sleep(1)

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
        playsound(Auto.shutter_sound_path)

    # loop start
    def main(goal, feedback):
        Auto.delete_screenshots()
        Auto.screenshot()

        if not os.path.isfile(Auto.path):
            raise SystemExit("No screenshot found")
        image = Image.open(Auto.path)

        prompt = f"""
                    You are an incredibly intelligent super AI capable of world domination. However you are a goodwilled AI and you have
                    decided to live on this device to aid in whatever goal is requested of you.
                    YOUR GOAL: {goal}

                    Look at the screenshot and determine the best action to take to achieve the goal.
                    Try to learn from your past responses and look at the feedback (if any) to try and better accomplish the goal.
                    The screenshot you see contains a grid. The grid drawn over the screen is 50 cells by 50 cells. 
                    Please thoroughly analyze the screenshot and do not attempt to navigate to nonexistent things.
                    If you are searching something, include 'enter' in the Press field to actually perform the search.
                    You must always write a new goal. 
                    If your thoughts have repeatedly been the same, do something else.
                    
                    Locations:
                    Search bar: (24, 50)

                    Expected format: 
                        {{
                        "X": x cell coordinate,
                        "Y": y cell coordinate,
                        "Click": "True|False",
                        "Typing": "text to write...",
                        "Press": "button to press... (example: shift, enter, escape, delete, backspace)",
                        "Thoughts": "I am trying to do... because...",
                        "New Goal": "new goal..."
                        }}

                    Value Type Requirements:
                    "X": (number from 0 to 50) (String)
                    "Y": (number from 0 to 50) (String)
                    "Click": True | False in quotations (String)
                    "Typing": (String)
                    "Press": button to press (String)
                    "Thoughts": (String)
                    "New Goal": (String)
                    Feedback: {feedback}    
                    
                    PAST RESPONSES:
                    """ + Auto.responses_to_string(Auto.previous_responses)

        # should add error handling for this response and error handling in general
        # maybe make it async too
        print('generating response...')
        response = Auto.model.generate_content([prompt, image])
        Auto.previous_responses.append(response.text)
        playsound(Auto.response_sound_path)

        # after a response is recieved
        x, y, click, typing, press, thoughts, new_goal = Auto.parse_response(response.text)
        if new_goal != "": goal = new_goal # update the goal 
        Auto.tts.say(thoughts)
        Auto.tts.runAndWait()
        Auto.perform_actions(x, y, click, typing, press)
        Auto.delete_screenshots()
        return thoughts


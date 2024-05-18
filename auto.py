"""
TODO 
    - reprompt user for goal when current one is completed
    - find the best way for it to interact with the computer
    - add overlay
    - add NLP and text to speech
"""
import json
import google.generativeai as genai
from dotenv import load_dotenv
import os, shutil
import pyautogui
from PIL import Image
import time

class Auto:
    CURRENT_DIR = os.getcwd()
    screenshots_dir = os.path.join(CURRENT_DIR, 'screenshots')
    path = os.path.join(screenshots_dir, f"screenshot.png")
    previous_responses = []

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
        typing = data["Typing"]
        press = data["Press"]
        thoughts = data["Thoughts"]

        return float(X), float(Y), str(typing), str(press).lower(), str(thoughts)

    def perform_actions(x, y, press, typing):
        pyautogui.click(x, y)    
        print(f'moving cursor to ({x},{y})')
        pyautogui.write(typing, interval=0.1) # interval subject to change
        time.sleep(2)
        pyautogui.press(press)

    def responses_to_string(past_responses):
        string = ""
        for response in past_responses:
            string += (response + '\n')
        return string

    load_dotenv()
    API_KEY = os.getenv('API_KEY')

    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-pro-vision')

    # loop start
    def main(goal):
        Auto.delete_screenshots()
        pyautogui.screenshot(Auto.path)

        if not os.path.isfile(Auto.path):
            raise SystemExit("No screenshot found")
        image = Image.open(Auto.path)

        prompt = f"""
                    YOUR GOAL: {goal}

                    Based on the screenshot, your goal, and any previous responses, generate the next best series of inputs.
                    The inputs you provide will then be executed with pyautogui. Try to do different things than your past responses.
                    You can: 
                        - Move the mouse to a new position
                        - Type any keyboard inputs
                        - Press any keyboard key for a particular operation (Ex: enter, escape, shift, backspace keys)
                    
                    IMPORTANT LOCATIONS:
                        - Search bar is located at (826, 1060)

                    Expected format: 
                        {{
                        "X": *new x position*,
                        "Y": *new y position*,
                        "Typing": *abc*,
                        "Press": *shift*
                        "Thoughts": *I am trying to do...*
                        }}

                    PAST RESPONSES:
                    """ + Auto.responses_to_string(Auto.previous_responses)

        # should add error handling for this response and error handling in general
        # maybe make it async too
        print('generating response...')
        response = Auto.model.generate_content([prompt, image])
        Auto.previous_responses.append(response.text)
        # print(response.text) # would be good to know what this response looks like when it fails

        # after a response is recieved
        x, y, typing, press, thoughts = Auto.parse_response(response.text)
        print(f'GEMINI: {thoughts}') 
        Auto.perform_actions(x, y, press, typing) 
        Auto.delete_screenshots()



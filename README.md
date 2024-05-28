# Attempt to utilize Google's AI vision API to control a computer

## About
The idea would be to have a core loop consisting of:
1. Get goal from user (Ex: go to chess.com and play against the computer)
2. Take screenshot
3. Send screenshot + prompt asking it to reply with inputs it would like to do based on the screenshot and goal
4. Use **pyautogui** to perform the inputs
5. Go back to step 2
### Example Screenshot
![image](https://github.com/aiden10/gemini/assets/51337166/c92cca9a-d895-498b-b778-2268f25d884b)
I added a grid over the screenshot since I thought it might be more accurate if asked to respond with an (x,y) position between 0-50 for the mouse movement as opposed to 0-1920 or 0-1080. 

## Issues
Unfortunately, the AI tends to hallucinate and get caught in loops. Often it is unable to do even the most basic tasks unless explicit information about it is given.
I do not believe that this is something which can be fixed by better prompts or better image processing. 

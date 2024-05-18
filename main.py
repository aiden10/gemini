from auto import Auto
        
if __name__ == '__main__':
    objective = input("What would you like the AI to do?\n")
    feedback = ""
    while True:
        Auto.main(objective, feedback)
        # feedback = input("Do you have any feedback to give the AI? (leave blank if you have no feedback)\n")

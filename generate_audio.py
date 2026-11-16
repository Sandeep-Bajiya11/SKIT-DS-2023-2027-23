import pyttsx3

engine = pyttsx3.init()

# 1. Positive emotion test
engine.save_to_file("I am very happy and excited about this amazing project!", 'test_positive.wav')

# 2. Negative emotion test
engine.save_to_file("I am completely frustrated and upset with how poorly this is working.", 'test_negative.wav')

# 3. Neutral speech test
engine.save_to_file("The current temperature is twenty two degrees celsius.", 'test_neutral.wav')

engine.runAndWait()
print("WAV files generated successfully.")
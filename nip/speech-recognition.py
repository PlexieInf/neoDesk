import speech_recognition as sr
import traceback

print("starting system")

r = sr.Recognizer()

try:
    mics = sr.Microphone.list_microphone_names()
    print("\nmics detected:", len(mics))

    if len(mics) == 0:
        print("no microphones found at all")
        exit()

    print("\navailable mics\n")
    for i, name in enumerate(mics):
        print(str(i) + " - " + str(name))

    print("\nwaiting for your input now")
    choice_raw = input("type mic index and press enter: ")

    print("you typed:", choice_raw)

    choice = int(choice_raw)

    if choice < 0 or choice >= len(mics):
        print("invalid index out of range")
        exit()

    print("selected mic:", mics[choice])

except Exception:
    print("setup crash")
    traceback.print_exc()
    exit()

mic = sr.Microphone(device_index=choice)

def calibrate():
    print("calibrating")
    try:
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=2)
        print("done calibrating")
    except:
        print("calibration failed")
        traceback.print_exc()

def listen():
    with mic as source:
        print("listening...")
        audio = r.listen(source, timeout=5, phrase_time_limit=10)
    return audio

def recognize(audio):
    try:
        text = r.recognize_google(audio)
        print("you said:", text)
    except Exception:
        traceback.print_exc()

def main():
    calibrate()
    print("ready")

    while True:
        try:
            audio = listen()
            recognize(audio)
        except Exception:
            print("loop error")
            traceback.print_exc()

main()

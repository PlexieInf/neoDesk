import speech_recognition as sr
import traceback
import time

r = sr.Recognizer()

print("booting")

mics = sr.Microphone.list_microphone_names()

if len(mics) == 0:
    print("no mic found")
    exit()

for i, name in enumerate(mics):
    print(i, name)

choice = int(input("mic index: "))

mic = sr.Microphone(device_index=choice)

print("selected:", mics[choice])

def calibrate():
    print("calibrating")
    with mic as source:
        r.adjust_for_ambient_noise(source, duration=2)
    print("done")

def listen_once():
    try:
        with mic as source:
            print("listening")
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            return audio
    except Exception:
        print("listen crash")
        traceback.print_exc()
        return None

def recognize(audio):
    try:
        text = r.recognize_google(audio)
        print("you said:", text)
    except Exception:
        traceback.print_exc()

def main():
    calibrate()

    i = 0

    while True:
        i += 1
        print("\nloop", i)

        audio = listen_once()

        if audio is None:
            continue

        recognize(audio)

        time.sleep(0.1)

main()

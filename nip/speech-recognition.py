import speech_recognition as sr
import traceback
import time

r = sr.Recognizer()

print("booting voice system")

mics = sr.Microphone.list_microphone_names()

if not mics:
    print("no mics detected system is silent")
    exit()

print("\navailable microphones\n")

for i, name in enumerate(mics):
    print(i, name)

try:
    choice = int(input("\npick mic index "))
except:
    print("invalid input bro typed air")
    exit()

if choice < 0 or choice >= len(mics):
    print("that mic index does not exist in this reality")
    exit()

mic = sr.Microphone(device_index=choice)

print("\nselected mic")
print(mics[choice])

def calibrate():
    print("calibrating noise profile")
    try:
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=2)
        print("calibration done")
    except Exception:
        print("calibration failed")
        traceback.print_exc()

def listen():
    try:
        with mic as source:
            print("listening")
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        return audio
    except Exception:
        print("listen failed")
        traceback.print_exc()
        return None

def recognize(audio):
    try:
        text = r.recognize_google(audio)
        print("you said", text)
    except sr.UnknownValueError:
        print("could not understand audio")
    except sr.RequestError:
        print("api request failed internet or google being weird")
    except Exception:
        print("recognition crash")
        traceback.print_exc()

def main():
    print("assistant online")
    calibrate()

    count = 0

    while True:
        count += 1
        print("\ncycle", count, time.time())

        audio = listen()

        if audio is None:
            continue

        recognize(audio)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("stopped manually")
    except Exception:
        print("fatal error")
        traceback.print_exc()

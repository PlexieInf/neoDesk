import speech_recognition as sr
import time
import traceback

print("boot sequence start")

try:
    r = sr.Recognizer()
    print("recognizer loaded ok")

    mic_list = sr.Microphone.list_microphone_names()
    print("mic devices found")
    for i, m in enumerate(mic_list):
        print(i, m)

    mic_index = None

    if len(mic_list) == 0:
        print("no microphones detected bro system is cooked")
        exit()

    mic_index = 0
    print("using mic index", mic_index)

    mic = sr.Microphone(device_index=mic_index)

except Exception as e:
    print("setup failed")
    print(e)
    traceback.print_exc()
    exit()

def calibrate():
    print("calibrating ambient noise start")
    try:
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=2)
        print("calibration done")
    except Exception as e:
        print("calibration failed")
        traceback.print_exc()

def listen_once():
    print("waiting for audio chunk")
    try:
        with mic as source:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        print("audio captured size", len(audio.frame_data))
        return audio
    except sr.WaitTimeoutError:
        print("timeout no speech detected")
    except Exception as e:
        print("listen error")
        traceback.print_exc()
    return None

def recognize(audio):
    print("sending to speech api")
    try:
        text = r.recognize_google(audio)
        print("decoded text", text)
        return text
    except sr.UnknownValueError:
        print("could not understand speech")
    except sr.RequestError as e:
        print("api request failed", e)
    except Exception as e:
        print("recognition crash")
        traceback.print_exc()
    return None

def main():
    print("assistant online")
    calibrate()

    counter = 0

    while True:
        counter += 1
        print("\nloop tick", counter, "time", time.time())

        audio = listen_once()
        if audio is None:
            continue

        text = recognize(audio)
        if text:
            print("FINAL OUTPUT >>>", text)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("stopped manually")
    except Exception as e:
        print("fatal crash")
        traceback.print_exc()

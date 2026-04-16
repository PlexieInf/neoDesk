import speech_recognition as sr
import traceback
import time

r = sr.Recognizer()

print("booting")

# List available microphones
mics = sr.Microphone.list_microphone_names()

if len(mics) == 0:
    print("no mics found")
    exit()

for i, name in enumerate(mics):
    print(i, name)

choice = int(input("mic index: "))
mic = sr.Microphone(device_index=choice)
print("selected:", mics[choice])

def calibrate():
    print("calibrating...")
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            with mic as source:
                r.adjust_for_ambient_noise(source, duration=2)
            print("calibration done")
            return True
        except Exception as e:
            print(f"calibration attempt {attempt + 1} failed: {e}")
            time.sleep(1)
    print("calibration failed after multiple attempts")
    return False

def listen_once(source):
    try:
        print("listening...")
        audio = r.listen(source, timeout=5, phrase_time_limit=10)
        return audio
    except sr.WaitTimeoutError:
        print("listening timed out - no speech detected")
        return None
    except Exception as e:
        print(f"listen error: {e}")
        return None

def recognize(audio):
    try:
        text = r.recognize_google(audio)
        print(f"you said: {text}")
        return text
    except sr.UnknownValueError:
        print("could not understand the audio")
        return None
    except sr.RequestError as e:
        print(f"API error: {e}")
        return None
    except Exception as e:
        print(f"recognition error: {e}")
        return None

def main():
    if not calibrate():
        print("Failed to calibrate. Continuing anyway...")
    
    print("starting loop...")
    print("Speak into the microphone (Ctrl+C to stop)\n")

    consecutive_errors = 0
    
    while True:
        try:
            # Keep the microphone context open for the entire operation
            with mic as source:
                # Small pause to let the microphone stabilize
                time.sleep(0.3)
                
                audio = listen_once(source)
                
                if audio is None:
                    consecutive_errors += 1
                    if consecutive_errors > 10:
                        print("Too many consecutive errors, restarting loop...")
                        consecutive_errors = 0
                        time.sleep(2)
                    continue
                
                # Reset error counter on successful listen
                consecutive_errors = 0
                
                # Recognize speech
                result = recognize(audio)
                if result:
                    # Optional: Do something with the recognized text here
                    pass
                
        except KeyboardInterrupt:
            print("\n\nProgram stopped by user")
            break
        except Exception as e:
            print(f"unexpected error: {e}")
            traceback.print_exc()
            time.sleep(1)

if __name__ == "__main__":
    main()

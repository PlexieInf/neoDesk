import speech_recognition as sr

r = sr.Recognizer()
mic = sr.Microphone()

def listen_loop():
    with mic as source:
        r.adjust_for_ambient_noise(source)

    print("listening started... speak anytime")

    while True:
        try:
            with mic as source:
                audio = r.listen(source)

            text = r.recognize_google(audio)
            print("you said:", text)

        except sr.UnknownValueError:
            print("could not understand audio")
        except sr.RequestError:
            print("api error bro internet issue probably")

listen_loop()

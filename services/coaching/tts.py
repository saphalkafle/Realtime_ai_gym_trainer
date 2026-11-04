from io import BytesIO  #create virtual blank memory
from gtts import gTTS  #google text to speech

class TextToSpeech:
    def speak(self,text,lang="en"):
        cleaned = (text or "").strip()

        if not cleaned:
            return


        buffer = BytesIO()
        gTTS(text = cleaned,lang=lang).write_to_fp(buffer)
        buffer.seek(0)  #change pointer to first location

        return buffer.read()



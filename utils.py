import os
import hashlib
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
from extension import database
import shutil

load_dotenv()

speech_config = speechsdk.SpeechConfig(
    subscription=os.environ.get("SPEECH_KEY"), region=os.environ.get("SPEECH_REGION")
)

# The language of the voice that speaks.
speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"


TTS_FILE = os.path.expanduser("~") + os.sep + ".ttsfile"


def init():
    if not os.path.exists(TTS_FILE):
        os.makedirs(TTS_FILE)
    conn = database.get_db()
    c = conn.cursor()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS audio (
        id TEXT PRIMARY KEY,
        message TEXT NOT NULL,
        time TEXT NOT NULL
    );"""
    )
    conn.commit()
    c.close()


def full_path(name):
    return os.path.join(TTS_FILE, name)


def speak_and_save(message):
    file_name = hashlib.md5(message.encode()).hexdigest() + ".wav"
    # check if file exists
    conn = database.get_db()
    c = conn.cursor()
    audio = c.execute("SELECT * FROM audio WHERE id = ?", (file_name,)).fetchone()
    c.close()
    if audio:
        return {
            "isSuccess": True,
            "file": file_name,
            "message": message,
        }
    audio_config = speechsdk.audio.AudioOutputConfig(
        filename=os.path.join(TTS_FILE, file_name)
    )
    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config
    )
    speech_synthesis_result = speech_synthesizer.speak_text_async(message).get()
    is_success = (
        speech_synthesis_result.reason
        == speechsdk.ResultReason.SynthesizingAudioCompleted
    )
    if is_success:
        c = conn.cursor()
        c.execute(
            "INSERT INTO audio (id, message, time) VALUES (?, ?, datetime())",
            (file_name, message),
        )
        conn.commit()
        c.close()
    return {
        "isSuccess": is_success,
        "file": file_name,
        "message": message,
    }


def get_history():
    conn = database.get_db()
    c = conn.cursor()
    history = c.execute("SELECT * FROM audio ORDER BY time DESC").fetchall()
    c.close()
    return history


def del_history():
    conn = database.get_db()
    c = conn.cursor()
    c.execute("DELETE FROM audio")
    conn.commit()
    c.close()
    # remote files
    shutil.rmtree(TTS_FILE)
    os.mkdir(TTS_FILE)

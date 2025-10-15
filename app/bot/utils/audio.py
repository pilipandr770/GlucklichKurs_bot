# file: app/bot/utils/audio.py
from pydub import AudioSegment
from io import BytesIO

def ogg_bytes_to_wav_bytes(ogg: bytes) -> bytes:
    audio = AudioSegment.from_file(BytesIO(ogg), format="ogg")
    out = BytesIO()
    audio.export(out, format="wav")
    return out.getvalue()

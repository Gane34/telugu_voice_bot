from app.telephony.base import TelephonyProvider


class CurrentTelephonyProvider(TelephonyProvider):
    def dial(self, number: str):
        return {"status": "dialed", "number": number}

    def answer(self):
        return {"status": "answered"}

    def hangup(self):
        return {"status": "hung_up"}

    def send_audio(self, chunks):
        return {"status": "audio_sent", "chunks": len(chunks) if chunks else 0}

    def receive_audio(self):
        return b""

    def get_call_status(self):
        return "idle"

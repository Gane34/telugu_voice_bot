# Phone Mode

The existing Twilio/Telnyx telephony code remains the transport layer and may be used for outbound calls. The AI stack is kept separate so local or cloud telephony can be plugged in without changing the business logic.

## Flow

- Application receives a phone call.
- The existing WebSocket/telephony path connects to the transport.
- Audio is routed through STT.
- The local LLM interprets the Telugu conversation.
- TTS generates a response.
- The audio is sent back to the call.

## Run phone mode

```powershell
python -m app.main --mode=phone
```

Phone mode still depends on valid Twilio/Telnyx credentials and an exposed server URL when using the live transport.

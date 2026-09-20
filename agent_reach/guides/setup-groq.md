# Groq Whisper Setup

Groq can be used as an optional transcription provider when a YouTube video has
no usable subtitles.

## Get an API key

Create a key at https://console.groq.com and provide it explicitly to the Agent
Reach configuration flow.

```bash
agent-reach configure groq-key
```

The key must never be printed in logs or command output.

After configuration:

```bash
agent-reach doctor --json
```

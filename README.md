# TuneTrainer 

TuneTrainer is a simple Streamlit app that listens to a note played or sung through your microphone, detects its pitch, and tells you whether you are sharp, flat, or in tune.

## Features
- Records audio directly from your default microphone
- Detects fundamental frequency using `librosa`
- Maps frequency to the nearest musical note
- Calculates cent deviation and gives clear visual feedback
- Adjustable recording duration and sample rate

## Installation

```bash
git clone <https://github.com/sedegah/TuneTrainer>
cd tunetrainer
pip install -r requirements.txt
```

### On Windows
You may need to install Microsoft C++ Build Tools and ensure you have an appropriate audio backend.

## Running the App

```bash
streamlit run tunetrainer_app.py
```

Press **“🎙️ Record”** in the web interface, play or sing a sustained note, and view your tuning results in real time.

## Dependencies
See `requirements.txt`.

## License
MIT License

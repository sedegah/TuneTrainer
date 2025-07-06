
import math
import time
from pathlib import Path

import numpy as np
import sounddevice as sd
import streamlit as st
import librosa


# ---------------------------
# Utility functions
# ---------------------------

def record_audio(duration: float = 2.0, samplerate: int = 44100) -> tuple[np.ndarray, int]:
    """Record mono audio from the default microphone for the given duration."""
    st.info(f"Recording for {duration} seconds...", icon="🎙️")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="float32")
    sd.wait()
    st.success("Recording complete!", icon="✅")
    return audio.flatten(), samplerate


def detect_pitch(audio: np.ndarray, sr: int) -> float | None:
    """Estimate fundamental frequency using librosa.yin.

    Returns median f0 in Hz or None if no pitch detected."""
    y = audio.astype(np.float32)
    f0_series = librosa.yin(y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"), sr=sr)
    f0_series = f0_series[~np.isnan(f0_series)]
    if len(f0_series) == 0:
        return None
    return float(np.median(f0_series))


def hz_to_note(freq: float):
    """Map frequency in Hz to nearest note & cent deviation.

    Returns (note_name, cents_off, target_freq)."""
    if freq <= 0:
        return None, None, None

    midi_num = 69 + 12 * math.log2(freq / 440.0)
    nearest_midi = int(round(midi_num))
    cents_off = (midi_num - nearest_midi) * 100

    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    note_name = note_names[nearest_midi % 12] + str((nearest_midi // 12) - 1)
    target_freq = 440.0 * (2 ** ((nearest_midi - 69) / 12))

    return note_name, cents_off, target_freq


def show_feedback(note_name: str, cents_off: float):
    """Display tuning feedback to Streamlit UI."""
    st.subheader(f"Detected Note: {note_name}")
    cents_abs = abs(cents_off)
    if cents_abs < 5:
        st.success("🎉 In tune (±5 cents)!")
    elif cents_off > 0:
        st.warning(f"🔊 {cents_abs:.1f} cents sharp")
    else:
        st.warning(f"🔊 {cents_abs:.1f} cents flat")

    progress_val = int(np.clip((cents_off + 50), 0, 100))
    st.progress(progress_val, text="← flat | sharp →")


# ---------------------------
# Streamlit UI
# ---------------------------

st.set_page_config(page_title="TuneTrainer", page_icon="🎺", layout="centered")
st.title("🎺 TuneTrainer – Real‑Time Pitch Feedback")

st.markdown(
    """
Press **Record** and play or sing a single note for ~2 seconds. TuneTrainer will tell you the pitch, the nearest note, and whether you're sharp or flat.

**Tip:** Minimize background noise and use headphones to reduce feedback.
"""
)

with st.sidebar:
    st.header("Settings")
    duration = st.slider("Recording Duration (seconds)", 1.0, 5.0, 2.0, 0.5)
    sr = st.selectbox("Sample Rate", [44100, 48000])

if st.button("🎙️ Record", type="primary"):
    audio, sr_actual = record_audio(duration, sr)
    with st.spinner("Analyzing pitch..."):
        freq = detect_pitch(audio, sr_actual)

    if freq is None:
        st.error("No pitch detected. Try playing a clearer, sustained note.")
    else:
        note_name, cents_off, target_freq = hz_to_note(freq)
        show_feedback(note_name, cents_off)

        with st.expander("Details"):
            st.write(f"**Fundamental frequency:** {freq:.2f} Hz")
            st.write(f"**Nearest note frequency:** {target_freq:.2f} Hz")
            st.write(f"**Cent deviation:** {cents_off:+.1f} cents")

            import matplotlib.pyplot as plt

            fig, ax = plt.subplots()
            ax.plot(audio)
            ax.set_title("Waveform")
            ax.set_ylabel("Amplitude")
            ax.set_xlabel("Samples")
            st.pyplot(fig)

st.markdown("---")
st.caption("© 2025 TuneTrainer – Built with Streamlit, SoundDevice, and Librosa")

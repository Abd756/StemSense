import librosa
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
import os

class AudioAnalyzer:
    def __init__(self):
        """
        Initializes the AudioAnalyzer using librosa for musical features 
        and pyloudnorm for industrial loudness standards.
        """
        # Mapping for librosa's numerical key output to human-readable strings
        self.key_map = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    def analyze(self, audio_path):
        """
        Extracts BPM, Musical Key, and Loudness (LUFS) from an audio file.
        
        Args:
            audio_path (str): Path to the audio file.
            
        Returns:
            dict: A dictionary containing bpm, key, and loudness.
        """
        if not os.path.exists(audio_path):
            print(f"Error: File not found {audio_path}")
            return None

        print(f"Analyzing audio: {os.path.basename(audio_path)}")

        try:
            # 1. Load the audio file
            # sr=None preserves the original sampling rate
            y, sr = librosa.load(audio_path, sr=None)

            # 2. Extract BPM (Tempo)
            # onset_envelope helps find the rhythmic pulses
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
            # tempo is usually a 1D array, we take the first value
            final_bpm = float(tempo[0]) if isinstance(tempo, (np.ndarray, list)) else float(tempo)

            # 3. Extract Key
            # We use a Chromagram to see the intensity of each note
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            chroma_mean = np.mean(chroma, axis=1)
            
            # Simple major/minor detection based on the strongest Chroma
            key_index = int(np.argmax(chroma_mean))
            detected_key = self.key_map[key_index]
            
            # 4. Extract Loudness (LUFS)
            # pyloudnorm requires data in (samples, channels) format
            # If mono, we reshape it
            data, rate = sf.read(audio_path)
            meter = pyln.Meter(rate) # create BS.1770 meter
            loudness = meter.integrated_loudness(data)

            results = {
                "bpm": round(final_bpm, 2),
                "key": detected_key,
                "loudness_lufs": round(float(loudness), 2)
            }
            
            print(f"Analysis Complete: {results}")
            return results

        except Exception as e:
            print(f"Error during analysis: {e}")
            return None

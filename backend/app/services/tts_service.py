from gtts import gTTS
import os
import uuid


class TTSService:

    def __init__(self, output_dir="generated_audio"):
        self.output_dir = output_dir

        # Create folder if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_audio(self, text: str, language: str = "en") -> str:
        """
        Convert text into speech.

        Args:
            text: Text that should be converted to speech.
            language: Language code, e.g. en, hi, mr.

        Returns:
            Path of generated MP3 file.
        """

        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        # Generate unique filename
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(self.output_dir, filename)

        # Convert text to speech
        tts = gTTS(
            text=text,
            lang=language,
            slow=False
        )

        # Save audio
        tts.save(filepath)

        return filepath
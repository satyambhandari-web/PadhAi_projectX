from pathlib import Path
from uuid import uuid4

from gtts import gTTS


class TTSService:
    """
    Text-to-Speech service for PadhAI.

    Uses Google Text-to-Speech (gTTS) to convert text
    into an MP3 audio file.
    """

    # Languages currently supported by PadhAI
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "hi": "Hindi",
        "mr": "Marathi",
    }

    def __init__(self, output_dir: str | None = None):
        """
        Initialize the TTS service.

        Args:
            output_dir:
                Directory where generated MP3 files will be stored.
                If not provided, 'generated_audio' is created
                relative to the backend directory.
        """

        if output_dir is None:
            # backend/
            # ├── app/
            # └── generated_audio/
            backend_dir = Path(__file__).resolve().parents[2]
            self.output_dir = backend_dir / "generated_audio"
        else:
            self.output_dir = Path(output_dir).resolve()

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_audio(
        self,
        text: str,
        language: str = "en",
    ) -> str:
        """
        Convert text into speech and save it as an MP3 file.

        Args:
            text:
                Text that should be converted into speech.

            language:
                Language code:
                - en = English
                - hi = Hindi
                - mr = Marathi

        Returns:
            Absolute path of the generated MP3 file.

        Raises:
            ValueError:
                If text is empty or language is unsupported.

            RuntimeError:
                If gTTS fails to generate the audio.
        """

        # Validate text
        if not isinstance(text, str) or not text.strip():
            raise ValueError(
                "Text cannot be empty."
            )

        # Normalize language
        language = language.lower().strip()

        # Validate language
        if language not in self.SUPPORTED_LANGUAGES:
            supported = ", ".join(
                f"{code} ({name})"
                for code, name in self.SUPPORTED_LANGUAGES.items()
            )

            raise ValueError(
                f"Unsupported language '{language}'. "
                f"Supported languages: {supported}"
            )

        # Generate unique filename
        filename = f"{uuid4().hex}.mp3"
        filepath = self.output_dir / filename

        try:
            # Create TTS object
            tts = gTTS(
                text=text.strip(),
                lang=language,
                slow=False,
            )

            # Save MP3
            tts.save(str(filepath))

        except Exception as exc:
            # Remove partially created file if generation failed
            if filepath.exists():
                filepath.unlink()

            raise RuntimeError(
                f"Failed to generate audio: {exc}"
            ) from exc

        return str(filepath)

    def get_supported_languages(self) -> dict[str, str]:
        """
        Return all languages supported by PadhAI.
        """
        return self.SUPPORTED_LANGUAGES.copy()
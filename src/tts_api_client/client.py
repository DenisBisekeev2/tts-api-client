"""HTTP-клиент для TTS API (https://github.com/<ты>/tts-api)."""
from __future__ import annotations

import os
from typing import Optional

import requests

__all__ = ["TTS_API", "TTSError"]

DEFAULT_API_URL = "http://84.21.173.179:3000/tts"


class TTSError(Exception):
    """Ошибка при обращении к TTS API.

    Атрибуты:
        kind: короткий код ошибки — ``tts_down``, ``tts_invalid``, ``tts_limit``.
        message: человекочитаемое описание.
    """

    def __init__(self, kind: str, message: str) -> None:
        self.kind = kind
        self.message = message
        super().__init__(message)


def _json_err(resp: requests.Response) -> str:
    try:
        return resp.json().get("error", resp.text)
    except ValueError:
        return resp.text


class TTS_API:
    """Клиент TTS API.

    Пример:
        >>> from tts_api_client import TTS_API
        >>> api = TTS_API("tts_xxx")
        >>> api.get_voice("Привет", voice="male")
        'C:/path/voice_message.mp3'
    """

    def __init__(
        self,
        token: str,
        api_url: str = DEFAULT_API_URL,
        user_agent: str = "tts_api_client/1.0",
        timeout: int = 30,
    ) -> None:
        if not token:
            raise ValueError("token не должен быть пустым")

        self.token = token
        self.api_url = api_url
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": user_agent})

    def get_voice(
        self,
        text: str,
        lang: str = "ru",
        out_path: Optional[str] = None,
        save_dir: Optional[str] = None,
        filename: str = "voice_message.mp3",
        voice: str = "female",
        timeout: Optional[int] = None,
    ) -> str:
        """Синтезирует текст в MP3 и сохраняет файл.

        Приоритет путей:
            1. ``out_path``  — полный путь к файлу (папка создаётся).
            2. ``save_dir``  — папка + ``filename``.
            3. ничего        — текущая рабочая папка + ``filename``.

        Args:
            text: Текст для озвучки (до 200 символов).
            lang: Язык, по умолчанию ``ru``.
            out_path: Полный путь к итоговому MP3.
            save_dir: Папка для сохранения.
            filename: Имя файла, если задан ``save_dir``.
            voice: ``female`` (по умолчанию) или ``male``.
            timeout: Таймаут запроса в секундах (переопределяет значение из конструктора).

        Returns:
            Абсолютный путь к сохранённому файлу.

        Raises:
            TTSError: при ошибке сети или ответа API.
        """
        # 1. Определяем итоговый путь
        if out_path:
            final_path = os.path.abspath(out_path)
        elif save_dir:
            final_path = os.path.abspath(os.path.join(save_dir, filename))
        else:
            final_path = os.path.abspath(os.path.join(os.getcwd(), filename))

        os.makedirs(os.path.dirname(final_path) or ".", exist_ok=True)

        # 2. Запрос
        params = {
            "text": text,
            "lang": lang,
            "token": self.token,
            "voice": voice,
        }

        try:
            resp = self._session.get(
                self.api_url,
                params=params,
                timeout=timeout or self.timeout,
            )
        except requests.RequestException as exc:
            raise TTSError("tts_down", f"сеть: {exc}") from exc

        # 3. Обработка статусов
        if resp.status_code in (401, 403):
            raise TTSError("tts_invalid", _json_err(resp))
        if resp.status_code == 429:
            raise TTSError("tts_limit", _json_err(resp))
        if resp.status_code >= 500:
            raise TTSError("tts_down", _json_err(resp))
        if resp.status_code != 200:
            raise TTSError("tts_invalid", f"{resp.status_code}: {_json_err(resp)}")

        if "audio" not in resp.headers.get("Content-Type", ""):
            raise TTSError("tts_invalid", "ожидался audio/*")

        # 4. Сохранение
        with open(final_path, "wb") as f:
            f.write(resp.content)

        return final_path
# tts-api-client

Python-клиент для [TTS API](https://github.com/<ты>/tts-api) — синтез речи в MP3,
выбор мужского/женского голоса, сохранение в любую папку.

## Установка

```bash
pip install tts-api-client
```

## Быстрый старт

```python
from tts_api_client import TTS_API

api = TTS_API("tts_xxxxxxxxxxxxxxxxxxxxxxxx")

# Сохранит в текущую папку → ./voice_message.mp3
path = api.get_voice("Привет, мир!")
print(path)

# Мужской голос + своя папка
api.get_voice("Привет", voice="male", save_dir="cache", filename="hi.mp3")

# Полный путь
api.get_voice("Привет", out_path="/tmp/hello.mp3")
```

## API

### `TTS_API(token, api_url=DEFAULT_API_URL, user_agent="tts_api_client/1.0", timeout=30)`

Создаёт клиент. Токен получается на лендинге твоего TTS API (`POST /api/register`).

### `TTS_API.get_voice(...)`

| Параметр   | Тип            | По умолчанию           | Описание                          |
|------------|----------------|------------------------|-----------------------------------|
| `text`     | `str`          | —                      | Текст, до 200 символов            |
| `lang`     | `str`          | `"ru"`                 | Язык                              |
| `out_path` | `Optional[str]`| `None`                 | Полный путь к файлу               |
| `save_dir` | `Optional[str]`| `None`                 | Папка (с `filename`)              |
| `filename` | `str`          | `"voice_message.mp3"`  | Имя файла                         |
| `voice`    | `str`          | `"female"`             | `female` или `male`               |
| `timeout`  | `Optional[int]`| `None`                 | Таймаут (переопределяет дефолт)   |

Возвращает **абсолютный путь** к сохранённому MP3.

### `TTSError`

Ловится отдельно. Поле `kind` — `tts_down`, `tts_invalid` или `tts_limit`.

```python
from tts_api_client import TTS_API, TTSError

try:
    TTS_API("tts_xxx").get_voice("Привет")
except TTSError as e:
    print(e.kind, e.message)
```

## Лицензия

MIT
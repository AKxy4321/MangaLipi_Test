

# API Documentation 

## 🌐 Translate API Endpoint `/v1/api/translate`

This endpoint translates text from one language to another. You need to provide the text to be translated, the source language, and the target language in the request body.

```bash
curl -X POST http://localhost:8000/v1/api/translate \
-H "Content-Type: application/json" \
-d '{
    "text": "Hello, how are you?",
    "source_lang": "en",
    "target_lang": "es"
}'
```

### Request Body Parameters

- **`text`**: The text you want to translate. 📝
- **`source_lang`**: The language code of the source text. 🌍
- **`target_lang`**: The language code of the target text. 🌐

### Example Response

```bash
"Hola, ¿cómo estás?"
```

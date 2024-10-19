

# API Documentation 

## 🌐 POST `/v1/api/translate`

This endpoint translates text from one language to another. You need to provide the text to be translated, the source language, and the target language in the request body.

<span style="color:red">**Note**: You must be connected to the `vivo Y16` network to access this endpoint.</span>


```bash
curl -X POST http://192.168.0.30:8000/v1/api/translate \
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


## 📚 `GET /v1/api/manga-list`

**Description**:  
Fetches the list of available manga chapters from the `data/images` directory.

### Request:
- **Method**: `GET`
- **URL**: `/v1/api/manga-list`
- **Headers**: None required

### Response:
- **200 OK**: Returns a JSON object containing a list of folders representing available manga chapters.

```json
{
    "chapters": [
        "chapter1",
        "chapter2",
        "chapter3"
    ]
}
```


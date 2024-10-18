import os

from groq import Groq

client = Groq(
    api_key="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"
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You must translate Text from English to Kannada",
        },
        {
            "role": "user",
            "content": "Hello, how are you?",
        }
    ],
    model="llama3-70b-8192",
)

print(chat_completion.choices[0].message.content)



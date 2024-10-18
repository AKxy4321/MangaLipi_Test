from groq import Groq

class LLM:
    def __init__(self):
        self.client = Groq(
            # I know not secure blah blah blah dotenv is not fucking working
            api_key="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"
        )

    def _preprocess_sentence(self, raw_text):
        return self.client.chat.completions.create(
            messages=[
                {
                    "role" : "system",
                    "content" : "You must take the text and correct for grammatical mistakes and optimize the text for translation. Substitute Less Frequent Words with More Freuqent words used.You must only return the text asked. Don't return any additional text."
                },
                {
                    "role" : "user",
                    "content" : f"{raw_text}"
                }
            ],
            model="llama3-70b-8192"
        ).choices[0].message.content

    def translate(self, raw_text, source_language, target_language):

        processed_text = self._preprocess_sentence(raw_text=raw_text)
        print(processed_text)
        return self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"You must translate Text from {source_language} to {target_language}. Return only the translated text. Dont be formal with your translation.",
                },
                {
                    "role": "user",
                    "content": processed_text,
                }
            ],
            model="llama3-70b-8192",
        ).choices[0].message.content


# # Usage
llm = LLM()
raw_text = """
Okay, fair point! But what if it’s different this time? Imagine if we could summon a legendary creature or gain superpowers!"""
translated_text = llm.translate(raw_text=raw_text, source_language="english", target_language="kannada")

with open("translated_text.txt", "w") as f:
    f.write(translated_text)

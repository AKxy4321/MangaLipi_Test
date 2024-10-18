from groq import Groq

class LLM:
    """
    A class to interact with the Groq API for text preprocessing and translation.

    Methods
    -------
    __init__():
        Initializes the LLM class with the Groq client.

    _preprocess_sentence(raw_text):
        Internal method. Must not be called directly.
        Preprocesses the input text by correcting grammatical mistakes and optimizing it for translation.

    translate(raw_text, source_language, target_language):
        Translates the preprocessed text from the source language to the target language.
    """

    def __init__(self):
        self.client = Groq(
            # I know not secure blah blah blah dotenv is not fucking working
            api_key="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"
        )

    def _preprocess_sentence(self, raw_text) -> str:
        """
        Preprocesses the given raw text by correcting grammatical mistakes and optimizing it for translation.

        This method sends the raw text to a language model to:
        - Correct grammatical errors.
        - Substitute less frequent words with more frequent ones.
        - Ensure the text is optimized for translation.

        Parameters:
        raw_text (str): The raw text to be preprocessed.

        Returns:
        str: The preprocessed text with corrections and optimizations applied.
        """
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

    def translate(self, raw_text, source_language, target_language) -> str:
        """
        Translates the given raw text from the source language to the target language.

        Args:
            raw_text (str): The text to be translated.
            source_language (str): The language of the input text.
            target_language (str): The language to translate the text into.

        Returns:
            str: The translated text.

        """

        processed_text = self._preprocess_sentence(raw_text=raw_text)
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
    
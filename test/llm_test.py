import asyncio
import unittest
<<<<<<< HEAD:test/llm_test.py
from speaking_script import ask_openai_async, load_config, create_aysnc_client
=======
from script1 import ask_openai_async, load_config, create_aysnc_client
>>>>>>> f918746 (1.0 speaker notes setting):llm_test.py

class TestOpenAI(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        config = load_config()
        self.queue = asyncio.Queue()
        self.client, self.gpt_model = create_aysnc_client(config=config)
        self.tokens = config.OpenAI.MaxTokens
        self.conversation = []

    async def ask_openai_with_ending(self, text, ending):
        await ask_openai_async(self.client, self.gpt_model, text, self.tokens, self.conversation, self.queue, ending)

    async def test_ask_openai_async_chinese(self):
        # Test the ask_openai_async function
        text = "你好？"

        # Create task call ask_openai_async
        ending_punctuations = ("。", "？", "！", "；", "”")
        # client, model, prompt, max_token, conversation, queue, ending
        task = asyncio.create_task(self.ask_openai_with_ending(text, ending_punctuations))

        # Wait until the task is done
        await task

    async def test_ask_openai_async_english(self):
        # Test the ask_openai_async function
        text = "hello~"

        # Create task call ask_openai_async
        ending_punctuations = (".", "?", "!", ";")
        # client, model, prompt, max_token, conversation, queue, ending
        task = asyncio.create_task(self.ask_openai_with_ending(text, ending_punctuations))

        # Wait until the task is done
        await task

if __name__ == '__main__':
    unittest.main()
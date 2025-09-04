import asyncio
from openai import AsyncOpenAI

async def main():
    client = AsyncOpenAI(api_key="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")
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "hello"}
        ],
        max_tokens=100
    )
    print(response.choices[0].message.content)

asyncio.run(main())
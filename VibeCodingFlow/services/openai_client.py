import os
from openai import AsyncOpenAI, OpenAIError

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'), max_retries=3, timeout=60)

async def chat(prompt: str, system: str=None, model: str='gpt-4o', temperature: float=0.2) -> str:
    messages = []
    if system:
        messages.append({'role':'system','content':system})
    messages.append({'role':'user','content':prompt})
    resp = await client.chat.completions.create(model=model, messages=messages, temperature=temperature)
    return resp.choices[0].message.content

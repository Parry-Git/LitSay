import os
from google import genai
from openai import OpenAI

client = genai.Client(api_key=os.environ.get('GEMINI_KEY'))

response = client.models.generate_content(
    # model="gemini-2.0-flash",
    model="gemini-2.5-flash-preview-05-20",
    contents="Explain how AI works for short",
)

print(response.text)


# client = OpenAI(api_key="sk-37fa9dd4d3bc4b268eeabd61ec348fc4", base_url="https://api.deepseek.com")

# response = client.chat.completions.create(
#     model="deepseek-chat",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant"},
#         {"role": "user", "content": "Hello"},
#     ],
#     stream=False
# )

# print(response.choices[0].message.content)
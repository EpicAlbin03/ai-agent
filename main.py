import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import sys

def main():
    args = sys.argv[1:]
    if not args:
        print('no prompt provided')
        sys.exit(1)

    prompt = args[0]
    verbose = '--verbose' in args

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    messages = [
        types.Content(role="user", parts=[types.Part(text=prompt)]),
    ]
    res = client.models.generate_content(model='gemini-2.0-flash-001', contents=messages)
    prompt_tokens = res.usage_metadata.prompt_token_count
    resp_tokens = res.usage_metadata.candidates_token_count

    if verbose:
        print('User prompt:', prompt)
        print('Prompt tokens:', prompt_tokens)
        print('Response tokens:', resp_tokens, '\n')
    print(res.text)

if __name__ == "__main__":
    main()

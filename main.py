import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import sys
from functions.schemas import available_functions, functions
from config import WORKING_DIR


def main():
    verbose = "--verbose" in sys.argv
    args = []
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            args.append(arg)

    if not args:
        print("no prompt provided")
        sys.exit(1)

    prompt = " ".join(args)

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    messages = [
        types.Content(role="user", parts=[types.Part(text=prompt)]),
    ]
    system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""
    res = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
    )
    prompt_tokens = res.usage_metadata.prompt_token_count
    resp_tokens = res.usage_metadata.candidates_token_count

    if verbose:
        print("User prompt:", prompt)
        print("Prompt tokens:", prompt_tokens)
        print("Response tokens:", resp_tokens, "\n")
    for function_call_part in res.function_calls:
        call_res = call_function(function_call_part, verbose)
        resp = call_res.parts[0].function_response.response
        if not resp:
            raise Exception("Error: No response from function call")
        else:
            print(f"-> {resp}")


def call_function(function_call_part: types.FunctionCall, verbose=False):
    function_name = function_call_part.name
    function_args = {**function_call_part.args, "working_directory": WORKING_DIR}

    if verbose:
        print(f"Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")

    if function_name not in functions:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    res = functions[function_name](**function_args)
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": res},
            )
        ],
    )


if __name__ == "__main__":
    main()

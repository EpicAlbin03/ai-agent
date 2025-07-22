import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import sys
from functions.schemas import available_functions, functions
from config import WORKING_DIR, MAX_ITERATIONS, SYSTEM_PROMPT


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

    call_model(client, messages, SYSTEM_PROMPT, prompt, verbose)


def call_model(
    client: genai.Client,
    messages: list[types.Content],
    system_prompt: str,
    prompt: str,
    verbose=False,
):
    try:
        for i in range(MAX_ITERATIONS):
            res = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions], system_instruction=system_prompt
                ),
            )

            if not res.function_calls:
                print(res.text)
                break

            prompt_tokens = res.usage_metadata.prompt_token_count
            resp_tokens = res.usage_metadata.candidates_token_count
            for candidate in res.candidates:
                messages.append(candidate.content)

            if verbose:
                print("User prompt:", prompt)
                print("Prompt tokens:", prompt_tokens)
                print("Response tokens:", resp_tokens, "\n")

            for function_call_part in res.function_calls:
                call_res = call_function(function_call_part, verbose)
                resp = call_res.parts[0].function_response.response

                if not resp:
                    raise Exception("Error: No response from function call")

                messages.append(
                    types.Content(
                        role="tool",
                        parts=[
                            types.Part.from_function_response(
                                name=call_res.parts[0].function_response.name,
                                response=resp,
                            )
                        ],
                    )
                )

        if i == MAX_ITERATIONS - 1:
            print(f"Maximum iterations ({MAX_ITERATIONS}) reached.")
            sys.exit(1)
    except Exception as e:
        raise Exception(f"Error: {e}")


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

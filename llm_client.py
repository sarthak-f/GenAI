from __future__ import annotations # This import allows for postponed evaluation of type annotations, which can help with forward references and circular imports.

import os
from typing import Optional

from env_loader import load_environment
from prompt_builder import SYSTEM_PROMPT, build_few_shot_prompt, build_user_prompt

load_environment()


class MissingApiKeyError(RuntimeError): # This is a custom exception class that inherits from RuntimeError. It is used to indicate that the required API key for accessing the Groq service is missing from the environment variables. When this exception is raised, it typically means that the application cannot proceed with generating SQL queries because it does not have the necessary credentials to interact with the Groq API.
    pass


class SqlGenerationError(RuntimeError): #
    pass # This is another custom exception class that inherits from RuntimeError. It is used to indicate that there was an error during the SQL generation process. This could be due to various reasons, such as issues with the Groq API response, problems with the input data, or other unexpected conditions that prevent successful SQL generation. When this exception is raised, it signals that something went wrong in the process of converting a natural language request into a SQL query.


def generate_sql_from_request(
    natural_language_request: str, # This parameter is the natural language request that the user wants to convert into SQL. It is expected to be a string.
    model: Optional[str] = None, # This optional parameter allows the caller to specify which language model to use for generating the SQL. If not provided, it will default to the value of the GROQ_MODEL environment variable or "mixtral-8x7b-32768" if that variable is not set.
    temperature: float = 0.2,
    system_prompt: Optional[str] = None, # This optional parameter allows the caller to provide a custom system prompt for the language model. If not provided, it will default to a predefined SYSTEM_PROMPT.
    examples_text: str = '',
) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise MissingApiKeyError("GROQ_API_KEY is not set.")

    try:
        from groq import Groq # This import statement attempts to import the Groq class from the groq package. The Groq class is typically used to interact with the Groq API, allowing the application to send requests and receive responses for tasks such as generating SQL queries based on natural language input. If the groq package is not installed, this import will fail, and the code will raise a SqlGenerationError indicating that the required package is not available.
    except ImportError as exc: # If the import of the Groq class fails due to the groq package not being installed, this except block will catch the ImportError and raise a SqlGenerationError instead, with a message indicating that the groq package is not installed. This provides a clearer error message to the user about what went wrong in the context of SQL generation.
        raise SqlGenerationError("The groq package is not installed.") from exc 

    client = Groq(api_key=api_key)
    selected_model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    system_input = system_prompt or SYSTEM_PROMPT
    system_text = system_input
    if examples_text:
        system_text = f"{system_input}\n\nExamples:\n{examples_text}"

    response = client.chat.completions.create( # This line sends a request to the Groq API to create a response based on the provided input. The request includes the selected model, temperature, and messages array that consists of a system message (which may include the system prompt and examples) and a user message (which contains the natural language request). The API will process this input and generate an output, which is expected to be the SQL query corresponding to the user's natural language request.
        model=selected_model,
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": system_text,
            },
            {
                "role": "user",
                "content": build_user_prompt(natural_language_request),
            },
        ],
    )

    output_text = response.choices[0].message.content.strip() # This line retrieves the content from the first choice in the response. The Groq API returns the response with choices containing the generated message, and we extract the content and strip whitespace.
    if not output_text:
        raise SqlGenerationError("The model returned an empty response.")
    return output_text
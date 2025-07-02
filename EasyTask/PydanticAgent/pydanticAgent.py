import os
import json
import base64
import asyncio
from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

from EasyTask.PydanticAgent.system_prompt import SYSTEM_PROMPT

load_dotenv()


# Pydantic models for structured output
class VerificationResult(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


class TaskVerification(BaseModel):
    verification: VerificationResult = Field(
        description="Whether the task passes verification or not"
    )
    reason: str = Field(
        description="A brief explanation of why the task passed or failed verification. Also describe the image the user attached."
    )


class Provider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class TaskVerificationEngine:
    def __init__(self, provider: Provider = Provider.OPENAI):
        self.provider = provider
        if provider == Provider.OPENAI:
            self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif provider == Provider.ANTHROPIC:
            self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def image_to_base64(self, image_path: str) -> str:
        """Convert an image file to a base64 encoded string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def get_system_instructions(self) -> str:
        """Get the system instructions for task verification."""
        return SYSTEM_PROMPT

    async def verify_task_with_openai(
            self,
            image_paths: List[str],
            task_name: str,
            description: str,
            location: str
    ) -> TaskVerification:
        """Verify task using OpenAI with structured output."""

        # Define the function for structured output
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "task_verification",
                    "description": "Verify if a user has completed their task based on evidence",
                    "parameters": TaskVerification.model_json_schema()
                }
            }
        ]

        messages = [
            {
                "role": "system",
                "content": self.get_system_instructions()
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""Given a user's task related info, determine whether they passed or not:
* Task name: "{task_name}"
* Description: "{description}"
* User location: "{location}"

Please verify if the evidence in the attached image shows successful completion of the task."""
                    },
                ]
            }
        ]

        # Add each image to the content array
        for image_path in image_paths:
            base64_image = self.image_to_base64(image_path)
            messages[1]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "task_verification"}}
        )

        # Parse the response
        message = response.choices[0].message
        if message.tool_calls:
            arguments = message.tool_calls[0].function.arguments
            result_dict = json.loads(arguments)
        else:
            result_dict = json.loads(message.content)

        return TaskVerification(**result_dict)

    async def verify_task_with_anthropic(
            self,
            image_paths: List[str],
            task_name: str,
            description: str,
            location: str
    ) -> TaskVerification:
        """Verify task using Anthropic Claude."""

        # Prepare the content with images
        content = [
            {
                "type": "text",
                "text": f"""Given a user's task related info, determine whether they passed or not:
* Task name: "{task_name}"
* Description: "{description}"
* User location: "{location}"

Please verify if the evidence in the attached image shows successful completion of the task.

Respond with a JSON object in exactly this format:
{{
    "verification": "PASS" or "FAIL",
    "reason": "brief explanation"
}}"""
            }
        ]

        # Add images to content
        for image_path in image_paths:
            base64_image = self.image_to_base64(image_path)
            # Determine image type from file extension
            image_type = "image/jpeg"  # Default
            if image_path.lower().endswith('.png'):
                image_type = "image/png"
            elif image_path.lower().endswith('.webp'):
                image_type = "image/webp"
            elif image_path.lower().endswith('.gif'):
                image_type = "image/gif"

            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": image_type,
                    "data": base64_image
                }
            })

        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",  # or claude-3-opus-20240229
            max_tokens=1000,
            system=self.get_system_instructions(),
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ]
        )

        # Parse the JSON response
        response_text = response.content[0].text

        # Extract JSON from the response (Claude might wrap it in markdown or other text)
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                result_dict = json.loads(json_str)
            else:
                # Fallback: try to parse the entire response as JSON
                result_dict = json.loads(response_text)
        except json.JSONDecodeError as e:
            # If JSON parsing fails, create a failure response
            result_dict = {
                "verification": "FAIL",
                "reason": f"Could not parse model response: {response_text[:100]}..."
            }

        return TaskVerification(**result_dict)

    async def verify_task_with_image(
            self,
            image_paths: List[str],
            task_name: str,
            description: str,
            location: str
    ) -> TaskVerification:
        """Verify task using the configured provider."""
        if self.provider == Provider.OPENAI:
            return await self.verify_task_with_openai(image_paths, task_name, description, location)
        elif self.provider == Provider.ANTHROPIC:
            return await self.verify_task_with_anthropic(image_paths, task_name, description, location)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")


async def main():
    # You can switch between providers here
    provider = Provider.ANTHROPIC  # or Provider.OPENAI

    # Initialize the verification engine
    engine = TaskVerificationEngine(provider=provider)

    print(f"Using provider: {provider.value}")
    print("=" * 50)

    task = {
        "taskTitle": "Go to the gym",
        "taskDescription": "Go to the gym and snap a picture to suggest that I am at the gym",
        "userLocation": "Singapore",
        "evidenceImage": ["test_images/singapore_gym.jpg"],
        "expected": "PASS"
    }
    image_path = task.get("evidenceImage")
    task_name = task.get("taskTitle")
    description = task.get("taskDescription")
    location = task.get("userLocation")

    try:
        result = await engine.verify_task_with_image(
            image_path, task_name, description, location
        )

        # Print the verification result and reason
        print(f"@@@ {task_name}")
        print(f"Verification: {result.verification.value}")
        print(f"Expected: {task.get('expected')}")
        print(f"Reason: {result.reason}\n\n")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
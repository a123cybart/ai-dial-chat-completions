import json

import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):
    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._endpoint = (
            DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"
        )

    def get_completion(self, messages: list[Message]) -> Message:
        # TODO:
        # Take a look at README.md of how the request and regular response are looks like!
        # 1. Create headers dict with api-key and Content-Type
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json",
        }
        # 2. Create request_data dictionary with:
        #   - "messages": convert messages list to dict format using msg.to_dict() for each message
        request_data = {"messages": [msg.to_dict() for msg in messages]}
        # 3. Make POST request using requests.post() with:
        #   - URL: self._endpoint
        #   - headers: headers from step 1
        #   - json: request_data from step 2
        response = requests.post(
            url=self._endpoint,
            headers=headers,
            json=request_data,
        )
        print(
            f"{response.request.method} {response.request.url} {response.request.headers}\n{response.request.body}"
        )
        # 4. Get content from response, print it and return message with assistant role and content
        if response.status_code == 200:
            response_data = response.json()
            print(
                json.dumps(response_data, indent=2)
            )  # Print whole response for debugging
            if "choices" in response_data and response_data["choices"]:
                content = response_data["choices"][0]["message"]["content"]
                print(content)
                return Message(role=Role.AI, content=content)
            else:
                raise Exception("No choices in response found")
        # 5. If status code != 200 then raise Exception with format: f"HTTP {response.status_code}: {response.text}"
        raise Exception(f"HTTP {response.status_code}: {response.text}")

    async def stream_completion(self, messages: list[Message]) -> Message:
        # TODO:
        # Take a look at README.md of how the request and streamed response chunks are looks like!
        # 1. Create headers dict with api-key and Content-Type
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json",
        }
        # 2. Create request_data dictionary with:
        #    - "stream": True  (enable streaming)
        #    - "messages": convert messages list to dict format using msg.to_dict() for each message
        request_data = {"stream": True, "messages": [msg.to_dict() for msg in messages]}
        # 3. Create empty list called 'contents' to store content snippets
        contents = []
        # 4. Create aiohttp.ClientSession() using 'async with' context manager
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self._endpoint,
                json=request_data,
                headers=headers,
            ) as response:
                # 5. Inside session, make POST request using session.post() with:
                #    - URL: self._endpoint
                #    - json: request_data from step 2
                #    - headers: headers from step 1
                #    - Use 'async with' context manager for response
                print(
                    f"{response.request_info.method} {response.request_info.url} {response.request_info.headers}\n{json.dumps(request_data, indent=2)}"
                )
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"HTTP {response.status}: {text}")
                # 6. Get content from chunks (don't forget that chunk start with `data: `, final chunk is `data: [DONE]`), print
                #    chunks, collect them and return as assistant message
                async for line in response.content:
                    decoded_line = line.decode("utf-8").strip()
                    if decoded_line.startswith("data: "):
                        data = decoded_line[len("data: ") :]
                        if data == "[DONE]":
                            break
                        chunk = json.loads(data)
                        print(
                            json.dumps(chunk, indent=2)
                        )  # Print whole chunk for debugging
                        if "choices" in chunk and chunk["choices"]:
                            delta = chunk["choices"][0].get("delta", {})
                            content_part = delta.get("content", "")
                            if content_part:
                                contents.append(content_part)
                                print(content_part, end="", flush=True)
        print()
        return Message(role=Role.AI, content="".join(contents))

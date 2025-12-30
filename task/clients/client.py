from aidial_client import AsyncDial, Dial

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):
    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        # TODO:
        # Documentation: https://pypi.org/project/aidial-client/ (here you can find how to create and use these clients)
        # 1. Create Dial client
        self._client = Dial(base_url=DIAL_ENDPOINT, api_key=self._api_key)
        # 2. Create AsyncDial client
        self._async_client = AsyncDial(base_url=DIAL_ENDPOINT, api_key=self._api_key)

    def get_completion(self, messages: list[Message]) -> Message:
        # TODO:
        # 1. Create chat completions with client
        #    Hint: to unpack messages you can use the `to_dict()` method from Message object
        completion = self._client.chat.completions.create(
            deployment_name=self._deployment_name,
            stream=False,
            messages=[msg.to_dict() for msg in messages],
        )
        # 2. Get content from response, print it and return message with assistant role and content
        if completion.choices:
            if completion.choices[0].message:
                print(completion.choices[0].message.content)
            return Message(role=Role.AI, content=completion.choices[0].message.content)
        # 3. If choices are not present then raise Exception("No choices in response found")
        raise Exception("No choices in response found")

    async def stream_completion(self, messages: list[Message]) -> Message:
        # TODO:
        # 1. Create chat completions with async client
        #    Hint: don't forget to add `stream=True` in call.
        completion = await self._async_client.chat.completions.create(
            deployment_name=self._deployment_name,
            stream=True,
            messages=[msg.to_dict() for msg in messages],
        )
        # 2. Create array with `contents` name (here we will collect all content chunks)
        contents = []
        # 3. Make async loop from `chunks` (from 1st step)
        async for chunk in completion:
            if (
                chunk.choices
                and chunk.choices[0].delta
                and chunk.choices[0].delta.content
            ):
                # 4. Print content chunk and collect it contents array
                contents.append(chunk.choices[0].delta.content)
                print(chunk.choices[0].delta.content, end="", flush=True)
        # 5. Print empty row `print()` (it will represent the end of streaming and in console we will print input from a new line)
        print()
        # 6. Return Message with assistant role and message collected content
        return Message(role=Role.AI, content="".join(contents))

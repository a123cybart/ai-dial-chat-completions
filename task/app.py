import asyncio

from task.clients.client import DialClient
from task.clients.custom_client import DialClient as CustomDialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


async def start(stream: bool, custom: bool = False) -> None:
    # TODO:
    # 1.1. Create DialClient
    # (you can get available deployment_name via https://ai-proxy.lab.epam.com/openai/models
    #  you can import Postman collection to make a request, file in the project root `dial-basics.postman_collection.json`
    #  don't forget to add your API_KEY)
    if custom:
        client = CustomDialClient(deployment_name="gpt-4o")
    else:
        client = DialClient(deployment_name="gpt-4o")
    # 2. Create Conversation object
    conversation = Conversation()
    # 3. Get System prompt from console or use default -> constants.DEFAULT_SYSTEM_PROMPT and add to conversation
    #    messages.
    system_message = input("Enter system prompt (or press Enter to use default): ")
    if not system_message.strip():
        system_message = DEFAULT_SYSTEM_PROMPT
    conversation.add_message(Message(role=Role.SYSTEM, content=system_message))
    # 4. Use infinite cycle (while True) and get yser message from console
    print("Start chatting with the assistant (type 'exit' to quit):")
    while True:
        user_input = input("You: ")
        # 5. If user message is `exit` then stop the loop
        if user_input.strip().lower() == "exit":
            print("Exiting the conversation.")
            break
        # 6. Add user message to conversation history (role 'user')
        conversation.add_message(Message(role=Role.USER, content=user_input))
        print("Assistant: ")
        # 7. If `stream` param is true -> call DialClient#stream_completion()
        #    else -> call DialClient#get_completion()
        if stream:
            response_message = await client.stream_completion(
                conversation.get_messages()
            )
        else:
            response_message = client.get_completion(conversation.get_messages())
        # 8. Add generated message to history
        conversation.add_message(response_message)
    # 9. Test it with DialClient and CustomDialClient
    # 10. In CustomDialClient add print of whole request and response to see what you send and what you get in response


asyncio.run(start(True, custom=True))

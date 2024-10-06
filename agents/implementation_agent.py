from .base_agent import Agent

class ImplementationAgent(Agent):
    """
    Agent responsible for implementing milestones in the project.
    """

    def __init__(self, client, prompt="", gen_kwargs=None):
        super().__init__(name="Implementation Agent", client=client, prompt=prompt, gen_kwargs=gen_kwargs)

    async def execute(self, message_history):
        """
        Executes the implementation agent's functionality.
        """
        print("DEBUG: IMPLEMENTATION AGENT execute")
        # Call the base agent's execute method
        #response = await super().execute(message_history)

        # Additional implementation-specific logic can be added here if needed
        copied_message_history = message_history.copy()

        # Check if the first message is a system prompt
        if copied_message_history and copied_message_history[0]["role"] == "system":
            # Replace the system prompt with the agent's prompt
            copied_message_history[0] = {"role": "system", "content": self.prompt}
        else:
            # Insert the agent's prompt at the beginning
            copied_message_history.insert(0, {"role": "system", "content": self.prompt})

        response_message = cl.Message(content="")
        await response_message.send()

        stream = await self.client.chat.completions.create(messages=copied_message_history, stream=True, tools=self.tools, tool_choice="auto", **self.gen_kwargs)
        function_name = ""
        arguments = ""
        async for part in stream:
            if part.choices[0].delta.tool_calls:
                tool_call = part.choices[0].delta.tool_calls[0]
                function_name_delta = tool_call.function.name or ""
                arguments_delta = tool_call.function.arguments or ""

                function_name += function_name_delta
                arguments += arguments_delta

            if token := part.choices[0].delta.content or "":
                await response_message.stream_token(token)

        if function_name:
            print("DEBUG: IMPLEMENTATION AGENT function_name:")
            print("type:", type(function_name))
            print("IMPLEMENTATION AGENT value:", function_name)
            print("DEBUG: IMPLEMENTATION AGENT arguments:")
            print("type:", type(arguments))
            print("IMPLEMENTATION AGENT value:", arguments)

        await response_message.update()

        return response_message.content

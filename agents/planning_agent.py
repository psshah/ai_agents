from .base_agent import Agent
import chainlit as cl
import os

class PlanningAgent(Agent):
    """
    Agent responsible for planning the project and creating milestones.
    """

    def __init__(self, client, prompt="", gen_kwargs=None):
        super().__init__(name="Planning Agent", client=client, prompt=prompt, gen_kwargs=gen_kwargs)

    async def execute(self, message_history):
        """
        Executes the planning agent's functionality.
        """
        print("DEBUG: PLANNING AGENT execute")

        copied_message_history = message_history.copy()

        # Check if the first message is a system prompt
        if copied_message_history and copied_message_history[0]["role"] == "system":
            # Replace the system prompt with the agent's prompt
            copied_message_history[0] = {"role": "system", "content": self._build_system_prompt()}
        else:
            # Insert the agent's prompt at the beginning
            copied_message_history.insert(0, {"role": "system", "content": self._build_system_prompt()})

        # Call the base agent's execute method
        await super().execute(message_history)
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
            print("DEBUG: function_name:")
            print("type:", type(function_name))
            print("value:", function_name)
            print("DEBUG: arguments:")
            print("type:", type(arguments))
            print("value:", arguments)

            if function_name == "updateArtifact":
                import json

                arguments_dict = json.loads(arguments)
                filename = arguments_dict.get("filename")
                contents = arguments_dict.get("contents")

                if filename and contents:
                    os.makedirs("artifacts", exist_ok=True)
                    with open(os.path.join("artifacts", filename), "w") as file:
                        file.write(contents)

                    # Add a message to the message history
                    message_history.append({
                        "role": "system",
                        "content": f"The artifact '{filename}' was updated."
                    })

                    stream = await self.client.chat.completions.create(messages=message_history, stream=True, **self.gen_kwargs)
                    async for part in stream:
                        if token := part.choices[0].delta.content or "":
                            await response_message.stream_token(token)
            elif function_name == "implement":
                print("DEBUG: implementing")
                import json

                arguments_dict = json.loads(arguments)
                milestone = arguments_dict.get("milestone")
                filename = arguments_dict.get("filename")
                contents = arguments_dict.get("contents")
                print("DEBUG: milestone:", milestone)
                print("DEBUG: filename:", filename)
                print("DEBUG: contents:", contents)

                implementation_agent = Agent(name="Implementation Agent", client=self.client, prompt=self.IMPLEMENTATION_PROMPT)
                print("DEBUG: calling implementation_agent:execute")
                response_message = await implementation_agent.execute(message_history)
                message_history.append({"role": "assistant", "content": response_message})
                cl.user_session.set("message_history", message_history)
        else:
            print("No tool call")

        await response_message.update()

        return response_message.content

    def _build_system_prompt(self):
        """
        Builds the system prompt for the planning agent.
        """
        # You can customize this method if needed
        return super()._build_system_prompt()

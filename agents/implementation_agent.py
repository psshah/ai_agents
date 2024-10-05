from agents.base_agent import Agent

class ImplementationAgent(Agent):
    def __init__(self, name, client, prompt="", gen_kwargs=None):
        super().__init__(name, client, prompt or Agent.IMPLEMENTATION_PROMPT, gen_kwargs)

    async def execute(self, message_history):
        print("ImplementationAgent: execute:")
        response_message = await super().execute(message_history)

        return response_message

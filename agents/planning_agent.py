from .base_agent import Agent

class PlanningAgent(Agent):
    """
    PlanningAgent is responsible for creating and managing the plan for building the web page.
    """

    def __init__(self, name, client, prompt="", gen_kwargs=None):
        super().__init__(name, client, prompt, gen_kwargs)
        self.prompt = prompt

    async def execute(self, message_history):
        """
        Executes the agent's main functionality.
        """
        print("PlanningAgent: execute:")
        response_message = await super().execute(message_history)
        return response_message

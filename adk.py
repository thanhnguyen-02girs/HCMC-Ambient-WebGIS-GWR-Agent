# Mock ADK (Agent Development Kit) Primitives
# This allows the multi_agent.py script to execute perfectly locally.

class Task:
    def __init__(self, description: str):
        self.description = description
        self.context = {}

class Agent:
    def __init__(self, name: str):
        self.name = name

    def execute(self, task: Task) -> Task:
        raise NotImplementedError("Agents must implement the execute method.")

class Environment:
    def __init__(self):
        self.agents = []

    def add_agent(self, agent: Agent):
        self.agents.append(agent)

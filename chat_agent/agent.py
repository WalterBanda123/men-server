# Mock implementation to replace Google ADK (which doesn't exist in PyPI)
# This is a simplified version for Docker build compatibility

class MockLiteLlm:
    def __init__(self, model: str):
        self.model = model

class MockLlmAgent:
    def __init__(self, model, name: str, description: str, instruction: str):
        self.model = model
        self.name = name
        self.description = description
        self.instruction = instruction

root_agent = MockLlmAgent(
    model=MockLiteLlm(model="openai/gpt-4"),
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)
base_agent = root_agent

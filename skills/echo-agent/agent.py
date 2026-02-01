from tools import TOOLS
from memory import SimpleMemory

class EchoAgent:
    def __init__(self):
        self.memory = SimpleMemory()

    def run(self, text: str):
        result = TOOLS["echo_tool"](text)
        self.memory.store(result)
        return result


if __name__ == "__main__":
    agent = EchoAgent()
    output = agent.run("Hello OpenClaw")
    print(output)


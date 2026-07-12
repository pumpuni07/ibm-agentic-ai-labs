"""Step 3 — A custom tool on the real BeeAI Tool pipeline."""
import asyncio
from core import CalculatorInput, SimpleCalculatorTool

async def main():
    tool = SimpleCalculatorTool()
    output = await tool.run(CalculatorInput(expression="(2 + 3) * 4")).middleware()
    print(output.get_text_content())

if __name__ == "__main__":
    asyncio.run(main())

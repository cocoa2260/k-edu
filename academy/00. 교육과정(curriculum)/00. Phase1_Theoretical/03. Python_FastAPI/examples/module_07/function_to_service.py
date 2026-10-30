class PromptBuilder:
    def __init__(self, system_message: str):
        self.system_message = system_message

    def build(self, question: str) -> str:
        return f"{self.system_message}\n질문: {question.strip()}"

builder = PromptBuilder("간결하게 답하세요.")
print(builder.build("Class가 필요한 이유는?"))

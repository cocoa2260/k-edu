from pydantic import BaseModel

class ChatResponse(BaseModel):
    answer: str
    model: str

response = ChatResponse(answer="완료", model="fake-model")
print(response.model_dump())
print(response.model_dump_json())

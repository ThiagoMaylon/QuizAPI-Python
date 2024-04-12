from fastapi import FastAPI, Path, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

class Questions:
    def __init__(self):
        self.question = ""
        self.answers = []
        self.right_answer = 0
        self.tip = ""

class Topics:
    def __init__(self):
        self.id = 0
        self.title = ""
        self.content = ""
        self.questions = []

class Quiz:
    def __init__(self):
        self.topics = []

def get_quiz(filename):
    quiz = Quiz()
    current_topic = None
    id = 1

    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith("Topico: "):
                if current_topic is not None:
                    quiz.topics.append(current_topic)
                current_topic = Topics()
                current_topic.title = line[len("Topico: "):]
                current_topic.id = id
                id += 1
            elif line.startswith("Conteudo: "):
                if current_topic is not None:
                    current_topic.content += line[len("Conteudo: "):]
            elif line.startswith("Pergunta: "):
                if current_topic is not None:
                    ques = Questions()
                    ques.question = line[len("Pergunta: "):]
                    for _ in range(3):
                        resp = next(file).strip()
                        ques.answers.append(resp)
                    resp_correta = int(next(file).strip())
                    ques.right_answer = resp_correta - 1
                    current_topic.questions.append(ques)
            elif line.startswith("Dica: "):
                if current_topic is not None and len(current_topic.questions) > 0:
                    tip = line[len("Dica: "):]
                    current_topic.questions[-1].tip = tip

    if current_topic is not None:
        quiz.topics.append(current_topic)

    return quiz


class QuizQuestion(BaseModel):
    question: str
    answers: List[str]
    right_answer: int
    tip: str

class QuizTopic(BaseModel):
    id: int
    title: str
    content: str
    questions: List[QuizQuestion]

class QuizResponse(BaseModel):
    topics: List[QuizTopic]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/", response_model=QuizResponse)
async def get_quiz_data():
    filename = "quiz.txt"
    quiz = get_quiz(filename)
    return quiz

@app.get("/{topic_id}", response_model=QuizTopic)
async def get_topic(topic_id: int = Path(..., title="Topic ID")):
    filename = "quiz.txt"
    quiz = get_quiz(filename)
    
    if topic_id <= 0 or topic_id > len(quiz.topics):
        raise HTTPException(status_code=404, detail="Tópico não encontrado")
    
    topic = quiz.topics[topic_id - 1]
    return topic

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

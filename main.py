from faker import Faker
from fastapi import FastAPI

app = FastAPI()
fake = Faker()

@app.get("/")
def get_root():
    return fake.name()

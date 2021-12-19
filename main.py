from fastapi import FastAPI

app = FastAPI()



@app.get("/")
async def root():
    return {"message": "Hello World!"}

@app.get("/")
def get_posts():
    return {"data": "This is your post"}
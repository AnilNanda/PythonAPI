from fastapi import FastAPI, status, HTTPException, Response, Depends
from fastapi.params import Body
from pydantic import BaseModel #Used for schema validation in API POST Body
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND
import time
from . import models, schemas
from .database import engine, get_db
from sqlalchemy.orm import Session



models.Base.metadata.create_all(bind=engine)

app = FastAPI()

#This class defines the Body schema for the API in POST method

while True:
    try:
        conn = psycopg2.connect(host='localhost',database='fastapi',user='postgres',password='postgres', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("DB connection success")
        break
    except Exception as error:
        print("Error making connection")
        print(error)
        time.sleep(5)


my_posts = [{"title": "title of post 1 ", "content": "content of post 1", "id": 1},{"title": "title of post 2", "content": "content of post 2", "id": 2}]

def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p

def find_index(id):
    print(id)
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i


@app.get("/")
async def root():
    return {"message": "Hello World!"}


@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    
    #Get using SQL query
    #cursor.execute(""" SELECT * FROM posts""")
    #posts = cursor.fetchall()
    #print(posts)

    # Get using SQLAlchemy
    posts = db.query(models.Post).all()
    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(payload: schemas.PostCreate, db: Session = Depends(get_db)):
    
    # Updating DB with the payload Body
    #cursor.execute("""INSERT INTO posts(title,content,published) VALUES(%s, %s, %s) RETURNING *""",(payload.title,payload.content,payload.published))
    #new_post = cursor.fetchone()
    #conn.commit()

    # Using SQLAlchemy
    #new_post = models.Post(title=payload.title,content=payload.content,published=payload.published)
    new_post = models.Post(**payload.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)


    # For reading the payload from body and updating the my_posts dict
    #post_dict = payload.dict()
    #post_dict['id'] = randrange(5,1000000)
    #my_posts.append(post_dict)


    #print(payload.rating)
    #print(payload)
    #print(payload.dict())
    #return {"message": f"title: {payload.title} and content: {payload.content}"}
    #return {"message": post_dict}
    return {"message": new_post}

@app.get("/posts/{id}")
def get_posts(id: int, db: Session = Depends(get_db)): #, response: Response):
    #cursor.execute("""SELECT * FROM posts where id = %s""",(str(id)))
    #test_post = cursor.fetchone()
    #post = find_post(id)
    test_post = db.query(models.Post).filter(models.Post.id==id).first()
    if not test_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id {id} is not found")
        #response.status_code = 404
        #response.status_code = status.HTTP_404_NOT_FOUND
        #return {"message": f"post with id {id} is not found"}
    return {"post_detail" : test_post}

@app.delete("/posts/{id}", status_code=HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    #cursor.execute("""DELETE FROM posts where id = %s RETURNING *""",(str(id),))
    #delete_post = cursor.fetchone()
    #conn.commit()
    #index = find_index(id)
    #print(index)
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
    #if delete_post == None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,detail=f"Id {id} not found in DB")
    #my_posts.pop(index)
    post.delete(synchronize_session=False)
    db.commit()
    return {"message": "post was successfully deleted"}

@app.put("/posts/{id}")
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    #cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",(post.title,post.content,post.published, str(id)))
    #updated_post = cursor.fetchone()
    #conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = post_query.first()


    #index = find_index(id)
    #print(index)
    if updated_post == None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,detail=f"Id {id} not found in DB")
    post_query.update(post.dict(),synchronize_session=False)
    db.commit()
    #post_dict = post.dict()
    #post_dict['id'] = id
    #my_posts[index] = post_dict
    return {"data": updated_post}

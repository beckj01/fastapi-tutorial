from typing import List, Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, oauth2, schemas

# for path operations you simply add another parameter to your path function (e.g. ", limit: int = 10")
# note: to include a space in a path parameter value %20 is used to represent a space. (e.g. "best beaches" could be searched by "...?search=best%20beaches")

router = APIRouter(
    prefix="/posts", # add the /posts route the beginning of all router functions below
    tags=["Posts"] # this tag is to group the routes in this file in the fastAPI documentation
)

@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    #cursor.execute("""SELECT * FROM posts""")
    #posts = cursor.fetchall()

    posts = db.query(models.Post).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()

    # default join is a LEFT INNER join, hence use isouter keyword to set to a LEFT OUTER join
    # .label() allows you to assign an alias to a field name
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()

    return results


@router.get("/me", response_model=List[schemas.PostOut])
def get_myposts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    my_posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
        models.Post.owner_id == current_user.id).all()
    return my_posts


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, response: Response, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    #cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id)))
    #post = cursor.fetchone()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
        models.Post.id==id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id {id} was not found.")
    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(new_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    #cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (new_post.title, new_post.content, new_post.published))
    #return_post = cursor.fetchone()
    #conn.commit()
    
    #return_post = models.Post(title=new_post.title, content=new_post.content, published=new_post.published) # this is one way of defining each field, or you can use the unpacking method below
    #print(f"UserID: {current_user.id}, email: {current_user.email}")

    return_post = models.Post(**new_post.model_dump(), owner_id=current_user.id)
    db.add(return_post)
    db.commit()
    db.refresh(return_post) # requeries the database to return the record that was just created, & store it back in the return_post object

    return return_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    #cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id)))
    #deleted_post = cursor.fetchone()
    #conn.commit()
    delete_query = db.query(models.Post).filter(models.Post.id==id) # a query for the deletion
    deleted_post = delete_query.first() #the first record found in the delete query

    if deleted_post == None: # if no item is found for deletion do not try to delete anything
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")

    if deleted_post.owner_id != current_user.id: # prevents the logged in user from deleting another users post
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot delete another users post")

    delete_query.delete(synchronize_session=False) # execute the delete query
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    #cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, 
    #               (post.title, post.content, post.published, str(id)))
    #updated_post = cursor.fetchone()
    #conn.commit()

    update_query = db.query(models.Post).filter(models.Post.id==id)
    updated_post = update_query.first()

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} does not exist.")

    if updated_post.owner_id != current_user.id: # prevents the logged in user from editing another users post
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You cannot update another users post")

    update_query.update(post.model_dump(), synchronize_session=False)
    db.commit()

    return update_query.first()
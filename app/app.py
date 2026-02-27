from fastapi import FastAPI, HTTPException, File, UploadFile, Depends, HTTPException, Form
from fastapi.params import Path

from app.schema import PostCreate
from app.db import Post,create_db_and_tables,get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
import  shutil
#shutil is a built in python module used for highlevel file and directory operations
import os
import uuid
import tempfile
#tempfile is built in python module used to create temporary file and directories that are automatically cleaned up when you are done with them




@asynccontextmanager
async def lifespan(app:FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
#in life span where the connect to the db and lod ml model ,initilize the cache,open file handles
#close db connection ,save logs,release resources

@app.post("/upload")
async def upload_file(file: UploadFile = File(...),
                      caption: str = Form(""),
                      session: AsyncSession = Depends(get_async_session)
                      ):
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False,suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file,temp_file)

        upload_result = imagekit.files.upload(
            file = open(temp_file_path,'rb'),
            file_name =file.filename,
            folder = "/images",
            tags = ["backend-upload"]
        )

        post = Post(
            caption = caption,
            url = upload_result.url,
            file_type = "video" if file.content_type.startswith("video/")else "image",
            file_name = upload_result.name,
        )
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()






@app.get("/feed")
async def get_feed(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]
    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat()
            }
        )
    return {"posts": posts_data}


@app.delete("/post/{post_id}")
async def delete_post(post_id:str,session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(select(Post).where(Post.id == post_id))
        post = result.scalars().first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        await session.delete(post)
        await session.commit()
        return {"success": True,"message": "Post deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




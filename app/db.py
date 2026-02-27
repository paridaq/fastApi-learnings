# from datetime import datetime, timezone
# from _collections_abc import AsyncGenerator
# import uuid
# from sqlalchemy import Column, String,Text,DateTime,ForeignKey
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_session, async_sessionmaker
# from sqlalchemy.orm import declarative_base, relationship, DeclarativeBase
#
# DATABASE_URL = "sqlite+aiosqlite:///./test.db"
# class Base(DeclarativeBase):
#    pass
#
#
# class Post(DeclarativeBase):
#     __tablename__ = "posts"
#     id= Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     caption = Column(String)
#     url = Column(String,nullable=False)
#     file_type=Column(String,nullable=False)
#     date_posted = Column(DateTime,nullable=False)
#     file_name = Column(String,nullable=False)
#     created_at = Column(DateTime,nullable=False,default=datetime.utcnow())
#
# engine = create_async_engine(DATABASE_URL)
#
# async_session_maker  = async_sessionmaker(engine, expire_on_commit=False)
# async def create_db_and_tables():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#
# async def get_async_session()->AsyncGenerator[AsyncSession,None]:
#     async with async_session_maker() as session:
#         yield session
#


from collections.abc import AsyncGenerator
import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime, timezone
from fastapi import Depends

DATABASE_URL = "sqlite+aiosqlite:///./test.db"


class Base(DeclarativeBase):
    pass


def generate_uuid():
    return str(uuid.uuid4())


class Post(Base):
    __tablename__ = "posts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    caption = Column(Text)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))




engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
#this create  database session



#yield remembers where it stopped ,can resume latter



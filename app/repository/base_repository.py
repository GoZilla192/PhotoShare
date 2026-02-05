from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


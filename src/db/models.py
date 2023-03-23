from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.db import Base


class Url(Base):
    __tablename__ = 'urls'

    id = Column(Integer, primary_key=True)
    original = Column(String(1024), unique=True, nullable=False)
    short = Column(String(128), unique=True, index=True, nullable=False)
    description = Column(String(1024), nullable=False)
    is_deleted = Column(Boolean, default=False)
    is_private = Column(Boolean, default=False)

    user = relationship('User', back_populates='urls')
    transitions = relationship('Transition', back_populates='url')

    user_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=True
    )


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(16), unique=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)

    urls = relationship('Url', back_populates='user')
    transitions = relationship('Transition', back_populates='user')


class Transition(Base):
    __tablename__ = 'transitions'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, index=True, default=datetime.utcnow)

    url = relationship('Url', back_populates='transitions')
    user = relationship('User', back_populates='transitions')

    url_id = Column(Integer, ForeignKey('urls.id', ondelete='CASCADE'))
    user_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=True
    )

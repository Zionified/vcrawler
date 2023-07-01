from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

__DEFAULT_ENGINE__ = create_engine(
    "mysql+pymysql://root:123456@127.0.0.1:3306/vcrawler", echo=False
)

__DEFAULT_SESSION_MAKER = sessionmaker(__DEFAULT_ENGINE__)


def get_engine():
    return __DEFAULT_ENGINE__


def get_session():
    return __DEFAULT_SESSION_MAKER()


__all__ = ["get_engine", "get_session"]

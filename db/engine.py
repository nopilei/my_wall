from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine('sqlite+aiosqlite://///Users/alexey/PycharmProjects/my_wall/db/storage/user_info.sqlite3',
                             echo=True)
Session = async_sessionmaker(engine, expire_on_commit=False)

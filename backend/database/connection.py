
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, Session


# SQL Server connection details
SERVER = r"DESKTOP-HBFF74V\SQLEXPRESS"
DATABASE = "HomeDecoratorDB"
DRIVER = "ODBC Driver 18 for SQL Server"


# Create the connection string
connection_string = (
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)


# Create SQLAlchemy database URL
connection_url = URL.create(
    "mssql+pyodbc",
    query={"odbc_connect": connection_string}
)


# Create database engine
engine = create_engine(
    connection_url,
    pool_pre_ping=True,
)


# Create a reusable session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# FastAPI database dependency
def get_db():
    db: Session = SessionLocal()

    try:
        yield db
    finally:
        db.close()

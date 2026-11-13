# TODO 1: Import Python's built-in `json` module (for parsing/serializing JSON messages)
# and `datetime` / `timezone` from `datetime` (for message timestamps)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# ==========================================
# DATABASE SETUP (SQLAlchemy + SQLite)
# ========================================
# TODO 2: Define `DATABASE_URL = "sqlite:///./chat.db"`, create the SQLAlchemy `engine`
# (remember `connect_args={"check_same_thread": False}` for SQLite), create `SessionLocal`
# using `sessionmaker(...)`, and initialize `Base = declarative_base()`.

SQLALCHEMY_DATABASE_URL = "sqlite:///./chat.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
class ChatMessage(Base):
    __tablename__ = "USERSofAPP" #use "messages"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, default="Anonymous")
    message = Column(String nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
# TODO 3: Define a `ChatMessage(Base)` model class with `__tablename__ = "messages"` and columns:
# - `id`: Integer, primary_key=True, index=True
# - `username`: String, default="Anonymous"
# - `message`: String, nullable=False
# - `timestamp`: DateTime, default=lambda: datetime.now(timezone.utc)


# TODO 4: Call `Base.metadata.create_all(bind=engine)` so SQLAlchemy automatically creates the `chat.db` file and table on startup.

Base.metadata.create_all(bind=engine)

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def get():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# TODO 5 (Optional): Create a `@app.get("/history")` endpoint (or send history inside `/ws` right after `await manager.connect(websocket)`)
# that opens a `SessionLocal()` session, queries past `ChatMessage` rows ordered by `id`,
# and returns/sends them as JSON objects `{"username": ..., "message": ...}` so refreshing the page keeps old messages
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()

            # TODO 6: Parse `data` with `json.loads(data)` to extract `username` (default to "Anonymous" if blank) and `message`.
            json.loads(data)

            # TODO 7: Open a database session (`db = SessionLocal()`), create a new `ChatMessage(username=..., message=...)` instance,
            # `db.add(...)`, `db.commit()`, and close the session (`db.close()` or use a `with SessionLocal() as db:` block).

            # TODO 8: Serialize the cleaned payload `{"username": username, "message": message}` back into a string using `json.dumps(...)`
            # and pass that JSON string into `await manager.broadcast(...)`.
            await manager.broadcast(data)

    except WebSocketDisconnect:
        manager.disconnect(websocket)

        # TODO 9: Format this disconnect message as a JSON string using `json.dumps({"username": "System", "message": "A user left the chat."})`
        # so the frontend `JSON.parse()` does not throw an error when someone disconnects.
        await manager.broadcast("A user left the chat.")
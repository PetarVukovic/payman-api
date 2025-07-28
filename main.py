from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from payman_sdk.client import PaymanClient
from payman_sdk.types import PaymanConfig
import requests

load_dotenv()
app = FastAPI()

# ✅ CORS konfiguracija
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ možeš zameniti sa specifičnim domenima za veću sigurnost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ Pydantic model za unos
class QueryRequest(BaseModel):
    query: str
    session_id: str | None = None


# ✅ Inicijalizacija Payman klijenta
def get_client(session_id: str = None) -> PaymanClient:
    config: PaymanConfig = {
        "client_id": os.getenv("PAYMAN_CLIENT_ID"),
        "client_secret": os.getenv("PAYMAN_CLIENT_SECRET"),
    }
    if session_id:
        config["session_id"] = session_id
    return PaymanClient.with_credentials(config)


# ✅ FastAPI endpoint
@app.post("/payman/ask")
def ask_payman(data: QueryRequest):
    try:
        client = get_client(data.session_id)
        response = client.ask(data.query)
        return {"response": response, "session_id": response.get("sessionId")}
    except requests.exceptions.RequestException as e:
        if hasattr(e, "response") and e.response is not None:
            raise HTTPException(
                status_code=e.response.status_code, detail=e.response.json()
            )
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Pokretanje aplikacije s dinamičkim portom (npr. za Render)
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from agent.admin_fee_agent import admin_agent
import traceback
import os


app = FastAPI()


# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================= Request model =================
class ChatRequest(BaseModel):
    message: str
    


# ================= HELPER: detect report type =================
def detect_report_type(message: str) -> str:
    """
    Decide report type based on user query text.
    """
    msg = message.lower()

    if "mess" in msg:
        return "mess"
    elif "hostel" in msg:
        return "hostel"
    else:
        # default → academic
        return "academic"


# ================= Chat endpoint =================
@app.post("/chat")
def chat(req: ChatRequest):
    try:
        #  detect report type from user message
        report_type = detect_report_type(req.message)

        #  get AI response text and DataFrame
        text, df = admin_agent(req.message)

        #  prepare table safely
        columns = []
        rows = []

        if df is not None and not df.empty:
            columns = df.columns.tolist()
            rows = df.fillna("").to_dict(orient="records")

        #  FINAL RESPONSE (frontend-friendly + type included)
        return {
            "type": report_type,   #  VERY IMPORTANT FIX
            "text": text,
            "columns": columns,
            "rows": rows
        }

    except Exception as e:
        print("ERROR in /chat endpoint:", e)
        traceback.print_exc()

        return {
            "type": "error",
            "text": "Internal server error occurred. Please try again.",
            "columns": [],
            "rows": []
        }


# ================= Mount frontend =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

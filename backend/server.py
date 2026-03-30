from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import random
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="INWO Game - Suplementos Mais Baratos")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# =============================================================================
# MODELS
# =============================================================================

class ParticipantCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    whatsapp: str = Field(..., min_length=10, max_length=20)

class Participant(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    whatsapp: str
    total_points: int = 0
    games_played: int = 0
    prizes_won: List[dict] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GameResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    participant_id: str
    score: int
    correct_answers: int
    total_questions: int
    prize_won: Optional[dict] = None
    played_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AnswerSubmission(BaseModel):
    participant_id: str
    question_id: str
    answer: str

class GameSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    participant_id: str
    questions: List[dict]
    current_question: int = 0
    score: int = 0
    correct_answers: int = 0
    status: str = "active"  # active, completed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Prize(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    code: str
    discount_percent: int
    image_url: str
    active: bool = True
    quantity: int = 100

# =============================================================================
# INWO CARDS DATA - Quiz Questions based on the game
# =============================================================================

INWO_CARDS = [
    {
        "id": "illuminati_1",
        "name": "Bavarian Illuminati",
        "type": "Illuminati",
        "description": "Uma das sociedades secretas mais famosas da história",
        "power": 10,
        "image": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=400"
    },
    {
        "id": "illuminati_2",
        "name": "The Network",
        "type": "Illuminati",
        "description": "Controla a informação digital em todo o mundo",
        "power": 9,
        "image": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400"
    },
    {
        "id": "illuminati_3",
        "name": "Gnomes of Zürich",
        "type": "Illuminati",
        "description": "Os banqueiros que controlam as finanças mundiais",
        "power": 9,
        "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400"
    },
    {
        "id": "illuminati_4",
        "name": "Servants of Cthulhu",
        "type": "Illuminati",
        "description": "Adoradores de entidades cósmicas antigas",
        "power": 8,
        "image": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=400"
    },
    {
        "id": "illuminati_5",
        "name": "UFOs",
        "type": "Illuminati",
        "description": "Alienígenas que monitoram a humanidade",
        "power": 8,
        "image": "https://images.unsplash.com/photo-1516339901601-2e1b62dc0c45?w=400"
    },
    {
        "id": "group_1",
        "name": "Hackers",
        "type": "Group",
        "description": "Especialistas em invasão de sistemas",
        "power": 6,
        "image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=400"
    },
    {
        "id": "group_2",
        "name": "I.R.S.",
        "type": "Group",
        "description": "A temida agência de impostos americana",
        "power": 5,
        "image": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=400"
    },
    {
        "id": "group_3",
        "name": "CIA",
        "type": "Group",
        "description": "Agência Central de Inteligência",
        "power": 7,
        "image": "https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=400"
    },
    {
        "id": "group_4",
        "name": "Pentagon",
        "type": "Group",
        "description": "O centro do poder militar americano",
        "power": 8,
        "image": "https://images.unsplash.com/photo-1569982175971-d92b01cf8694?w=400"
    },
    {
        "id": "group_5",
        "name": "Big Media",
        "type": "Group",
        "description": "Controla o que você vê e ouve",
        "power": 6,
        "image": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400"
    },
    {
        "id": "plot_1",
        "name": "Market Manipulation",
        "type": "Plot",
        "description": "Manipula os mercados financeiros",
        "power": 4,
        "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400"
    },
    {
        "id": "plot_2",
        "name": "Media Blitz",
        "type": "Plot",
        "description": "Lança uma campanha massiva na mídia",
        "power": 5,
        "image": "https://images.unsplash.com/photo-1586339949216-35c2747cc36d?w=400"
    },
    {
        "id": "plot_3",
        "name": "Power Grab",
        "type": "Plot",
        "description": "Uma jogada ousada para tomar o controle",
        "power": 6,
        "image": "https://images.unsplash.com/photo-1521791136064-7986c2920216?w=400"
    },
    {
        "id": "resource_1",
        "name": "Orbital Mind Control Lasers",
        "type": "Resource",
        "description": "Tecnologia de controle mental por satélite",
        "power": 7,
        "image": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=400"
    },
    {
        "id": "resource_2",
        "name": "Necronomicon",
        "type": "Resource",
        "description": "O livro dos mortos com poderes ocultos",
        "power": 8,
        "image": "https://images.unsplash.com/photo-1476275466078-4007374efbbe?w=400"
    }
]

QUIZ_QUESTIONS = [
    {
        "id": "q1",
        "question": "Qual Illuminati é conhecida por controlar as finanças mundiais?",
        "options": ["Bavarian Illuminati", "Gnomes of Zürich", "The Network", "UFOs"],
        "correct": "Gnomes of Zürich",
        "difficulty": "easy",
        "card_ref": "illuminati_3"
    },
    {
        "id": "q2",
        "question": "Qual grupo no INWO representa hackers e especialistas em tecnologia?",
        "options": ["CIA", "Hackers", "Pentagon", "I.R.S."],
        "correct": "Hackers",
        "difficulty": "easy",
        "card_ref": "group_1"
    },
    {
        "id": "q3",
        "question": "O que significa a sigla INWO?",
        "options": ["International New World Order", "Illuminati: New World Order", "Internet Network World Organization", "Inner Nova World Orbit"],
        "correct": "Illuminati: New World Order",
        "difficulty": "easy",
        "card_ref": None
    },
    {
        "id": "q4",
        "question": "Qual recurso permite controle mental via satélite?",
        "options": ["Necronomicon", "Market Manipulation", "Orbital Mind Control Lasers", "Media Blitz"],
        "correct": "Orbital Mind Control Lasers",
        "difficulty": "medium",
        "card_ref": "resource_1"
    },
    {
        "id": "q5",
        "question": "Quem criou o jogo Illuminati: New World Order?",
        "options": ["Richard Garfield", "Steve Jackson", "Gary Gygax", "Klaus Teuber"],
        "correct": "Steve Jackson",
        "difficulty": "easy",
        "card_ref": None
    },
    {
        "id": "q6",
        "question": "Qual Illuminati está associada a entidades cósmicas lovecraftianas?",
        "options": ["UFOs", "Bavarian Illuminati", "Servants of Cthulhu", "The Network"],
        "correct": "Servants of Cthulhu",
        "difficulty": "medium",
        "card_ref": "illuminati_4"
    },
    {
        "id": "q7",
        "question": "Em que ano foi lançado o INWO?",
        "options": ["1990", "1994", "1998", "2001"],
        "correct": "1994",
        "difficulty": "hard",
        "card_ref": None
    },
    {
        "id": "q8",
        "question": "Qual é o tipo de carta que representa organizações como CIA e Pentagon?",
        "options": ["Illuminati", "Group", "Plot", "Resource"],
        "correct": "Group",
        "difficulty": "easy",
        "card_ref": "group_3"
    },
    {
        "id": "q9",
        "question": "O Necronomicon no jogo é considerado que tipo de carta?",
        "options": ["Illuminati", "Group", "Plot", "Resource"],
        "correct": "Resource",
        "difficulty": "medium",
        "card_ref": "resource_2"
    },
    {
        "id": "q10",
        "question": "Quantos jogadores podem participar de uma partida em grupo de INWO?",
        "options": ["2 a 4", "3 a 6", "4 a 8", "2 a 6"],
        "correct": "3 a 6",
        "difficulty": "hard",
        "card_ref": None
    },
    {
        "id": "q11",
        "question": "Qual carta representa 'uma jogada ousada para tomar o controle'?",
        "options": ["Media Blitz", "Power Grab", "Market Manipulation", "I Lied"],
        "correct": "Power Grab",
        "difficulty": "medium",
        "card_ref": "plot_3"
    },
    {
        "id": "q12",
        "question": "Qual Illuminati controla a informação digital?",
        "options": ["Bavarian Illuminati", "UFOs", "The Network", "Discordian Society"],
        "correct": "The Network",
        "difficulty": "easy",
        "card_ref": "illuminati_2"
    }
]

DEFAULT_PRIZES = [
    {
        "id": "prize_1",
        "name": "10% OFF em Whey Protein",
        "description": "Desconto de 10% em qualquer Whey Protein da loja",
        "code": "INWO10WHEY",
        "discount_percent": 10,
        "image_url": "https://images.unsplash.com/photo-1693996045300-521e9d08cabc?w=400",
        "active": True,
        "quantity": 100
    },
    {
        "id": "prize_2",
        "name": "15% OFF em Creatina",
        "description": "Desconto de 15% em Creatina",
        "code": "INWO15CREAT",
        "discount_percent": 15,
        "image_url": "https://images.unsplash.com/photo-1693996045899-7cf0ac0229c7?w=400",
        "active": True,
        "quantity": 50
    },
    {
        "id": "prize_3",
        "name": "20% OFF Compra Acima de R$200",
        "description": "Desconto de 20% em compras acima de R$200",
        "code": "INWO20SUPER",
        "discount_percent": 20,
        "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400",
        "active": True,
        "quantity": 30
    },
    {
        "id": "prize_4",
        "name": "Frete Grátis",
        "description": "Frete grátis em qualquer pedido",
        "code": "INWOFRETEGRATIS",
        "discount_percent": 0,
        "image_url": "https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?w=400",
        "active": True,
        "quantity": 80
    },
    {
        "id": "prize_5",
        "name": "5% OFF em Todo o Site",
        "description": "Desconto de 5% em qualquer produto",
        "code": "INWO5ALL",
        "discount_percent": 5,
        "image_url": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=400",
        "active": True,
        "quantity": 200
    }
]

# =============================================================================
# ROUTES - Participants
# =============================================================================

@api_router.post("/participants", response_model=dict)
async def register_participant(data: ParticipantCreate):
    """Register a new participant"""
    # Check if email or whatsapp already exists
    existing = await db.participants.find_one({
        "$or": [
            {"email": data.email},
            {"whatsapp": data.whatsapp}
        ]
    }, {"_id": 0})
    
    if existing:
        # Return existing participant
        return {"participant": existing, "is_new": False}
    
    # Create new participant
    participant = Participant(
        name=data.name,
        email=data.email,
        whatsapp=data.whatsapp
    )
    
    doc = participant.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.participants.insert_one(doc)
    doc.pop('_id', None)
    
    return {"participant": doc, "is_new": True}

@api_router.get("/participants/{participant_id}")
async def get_participant(participant_id: str):
    """Get participant by ID"""
    participant = await db.participants.find_one({"id": participant_id}, {"_id": 0})
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    return participant

@api_router.get("/participants")
async def list_participants(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List all participants (admin)"""
    participants = await db.participants.find({}, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
    total = await db.participants.count_documents({})
    return {"participants": participants, "total": total}

# =============================================================================
# ROUTES - Cards
# =============================================================================

@api_router.get("/cards")
async def get_all_cards():
    """Get all INWO cards"""
    return {"cards": INWO_CARDS}

@api_router.get("/cards/{card_id}")
async def get_card(card_id: str):
    """Get a specific card"""
    card = next((c for c in INWO_CARDS if c["id"] == card_id), None)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

# =============================================================================
# ROUTES - Game/Quiz
# =============================================================================

@api_router.post("/game/start")
async def start_game(participant_id: str):
    """Start a new game session"""
    # Verify participant exists
    participant = await db.participants.find_one({"id": participant_id}, {"_id": 0})
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    # Select 5 random questions
    questions = random.sample(QUIZ_QUESTIONS, min(5, len(QUIZ_QUESTIONS)))
    
    session = GameSession(
        participant_id=participant_id,
        questions=questions
    )
    
    doc = session.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.game_sessions.insert_one(doc)
    doc.pop('_id', None)
    
    # Return session with first question (hide correct answers)
    return {
        "session_id": session.id,
        "total_questions": len(questions),
        "current_question": 0,
        "question": {
            "id": questions[0]["id"],
            "question": questions[0]["question"],
            "options": questions[0]["options"],
            "difficulty": questions[0]["difficulty"]
        }
    }

@api_router.post("/game/answer")
async def submit_answer(session_id: str, question_id: str, answer: str):
    """Submit an answer for the current question"""
    session = await db.game_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session["status"] != "active":
        raise HTTPException(status_code=400, detail="Game session is not active")
    
    current_idx = session["current_question"]
    questions = session["questions"]
    
    if current_idx >= len(questions):
        raise HTTPException(status_code=400, detail="No more questions")
    
    current_q = questions[current_idx]
    is_correct = answer == current_q["correct"]
    
    # Calculate points based on difficulty
    points = 0
    if is_correct:
        difficulty_points = {"easy": 10, "medium": 20, "hard": 30}
        points = difficulty_points.get(current_q["difficulty"], 10)
    
    # Update session
    new_score = session["score"] + points
    new_correct = session["correct_answers"] + (1 if is_correct else 0)
    new_current = current_idx + 1
    
    # Check if game is complete
    is_complete = new_current >= len(questions)
    new_status = "completed" if is_complete else "active"
    
    await db.game_sessions.update_one(
        {"id": session_id},
        {"$set": {
            "score": new_score,
            "correct_answers": new_correct,
            "current_question": new_current,
            "status": new_status
        }}
    )
    
    response = {
        "is_correct": is_correct,
        "correct_answer": current_q["correct"],
        "points_earned": points,
        "total_score": new_score,
        "correct_answers": new_correct,
        "is_complete": is_complete
    }
    
    # If game is complete, process prize
    if is_complete:
        prize = await award_prize(session["participant_id"], new_score, new_correct, len(questions))
        response["prize"] = prize
        response["final_score"] = new_score
        
        # Update participant stats
        await db.participants.update_one(
            {"id": session["participant_id"]},
            {
                "$inc": {"total_points": new_score, "games_played": 1},
                "$push": {"prizes_won": prize} if prize else {}
            }
        )
    else:
        # Return next question
        next_q = questions[new_current]
        response["next_question"] = {
            "id": next_q["id"],
            "question": next_q["question"],
            "options": next_q["options"],
            "difficulty": next_q["difficulty"]
        }
        response["question_number"] = new_current + 1
    
    return response

async def award_prize(participant_id: str, score: int, correct: int, total: int):
    """Award a random prize based on performance"""
    # Everyone wins something! Better performance = better prizes
    percentage = (correct / total) * 100
    
    # Get available prizes
    prizes = await db.prizes.find({"active": True, "quantity": {"$gt": 0}}, {"_id": 0}).to_list(100)
    
    if not prizes:
        # Use default prizes if none in DB
        prizes = [p for p in DEFAULT_PRIZES if p["active"] and p["quantity"] > 0]
    
    if not prizes:
        return None
    
    # Sort by discount (better performance = better prize chance)
    prizes_sorted = sorted(prizes, key=lambda x: x["discount_percent"], reverse=True)
    
    # Select prize based on performance
    if percentage >= 80:
        selected = random.choice(prizes_sorted[:2]) if len(prizes_sorted) >= 2 else prizes_sorted[0]
    elif percentage >= 60:
        mid_range = prizes_sorted[1:4] if len(prizes_sorted) > 3 else prizes_sorted
        selected = random.choice(mid_range)
    else:
        selected = random.choice(prizes_sorted[-2:]) if len(prizes_sorted) >= 2 else prizes_sorted[-1]
    
    # Decrease quantity
    await db.prizes.update_one(
        {"id": selected["id"]},
        {"$inc": {"quantity": -1}}
    )
    
    return {
        "id": selected["id"],
        "name": selected["name"],
        "description": selected["description"],
        "code": selected["code"],
        "discount_percent": selected["discount_percent"],
        "image_url": selected["image_url"]
    }

@api_router.get("/game/session/{session_id}")
async def get_session(session_id: str):
    """Get game session details"""
    session = await db.game_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

# =============================================================================
# ROUTES - Prizes
# =============================================================================

@api_router.get("/prizes")
async def get_prizes():
    """Get all available prizes"""
    prizes = await db.prizes.find({"active": True}, {"_id": 0}).to_list(100)
    if not prizes:
        return {"prizes": DEFAULT_PRIZES}
    return {"prizes": prizes}

@api_router.post("/prizes")
async def create_prize(prize: Prize):
    """Create a new prize (admin)"""
    doc = prize.model_dump()
    await db.prizes.insert_one(doc)
    doc.pop('_id', None)
    return doc

@api_router.put("/prizes/{prize_id}")
async def update_prize(prize_id: str, prize: Prize):
    """Update a prize (admin)"""
    doc = prize.model_dump()
    doc.pop('id', None)
    result = await db.prizes.update_one({"id": prize_id}, {"$set": doc})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Prize not found")
    return {"message": "Prize updated"}

# =============================================================================
# ROUTES - Stats/Admin
# =============================================================================

@api_router.get("/stats")
async def get_stats():
    """Get overall game statistics"""
    total_participants = await db.participants.count_documents({})
    total_games = await db.game_sessions.count_documents({})
    completed_games = await db.game_sessions.count_documents({"status": "completed"})
    
    # Get top players
    top_players = await db.participants.find(
        {}, {"_id": 0, "id": 1, "name": 1, "total_points": 1, "games_played": 1}
    ).sort("total_points", -1).limit(10).to_list(10)
    
    return {
        "total_participants": total_participants,
        "total_games": total_games,
        "completed_games": completed_games,
        "top_players": top_players
    }

@api_router.get("/leaderboard")
async def get_leaderboard(limit: int = Query(10, ge=1, le=50)):
    """Get top players leaderboard"""
    players = await db.participants.find(
        {"games_played": {"$gt": 0}},
        {"_id": 0, "id": 1, "name": 1, "total_points": 1, "games_played": 1}
    ).sort("total_points", -1).limit(limit).to_list(limit)
    
    return {"leaderboard": players}

# =============================================================================
# ROUTES - Initialize
# =============================================================================

@api_router.post("/init-prizes")
async def init_prizes():
    """Initialize default prizes in the database"""
    for prize in DEFAULT_PRIZES:
        existing = await db.prizes.find_one({"id": prize["id"]})
        if not existing:
            await db.prizes.insert_one(prize)
    return {"message": "Prizes initialized", "count": len(DEFAULT_PRIZES)}

# Root endpoint
@api_router.get("/")
async def root():
    return {"message": "INWO Game API - Suplementos Mais Baratos", "version": "1.0.0"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    # Initialize prizes on startup
    for prize in DEFAULT_PRIZES:
        existing = await db.prizes.find_one({"id": prize["id"]})
        if not existing:
            await db.prizes.insert_one(prize)
    logger.info("Prizes initialized")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

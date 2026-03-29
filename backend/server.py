from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import re
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(
    title="Eletrofunk Cachorrada API",
    description="API para votação de DJs de Eletrofunk e Cachorrada",
    version="1.0.0"
)

api_router = APIRouter(prefix="/api")

# ============== MODELS ==============

ESTADOS_BR = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
    "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
    "RS", "RO", "RR", "SC", "SP", "SE", "TO"
]

def validate_cpf(cpf: str) -> bool:
    cpf = re.sub(r'[^\d]', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for i in range(9, 11):
        value = sum((int(cpf[num]) * ((i + 1) - num) for num in range(0, i)))
        check = ((value * 10) % 11) % 10
        if check != int(cpf[i]):
            return False
    return True

class VotoCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    cpf: str = Field(..., min_length=11, max_length=14)
    email: str
    whatsapp: str = Field(..., min_length=10, max_length=15)
    estado: str
    dj_id: str

    @field_validator('cpf')
    @classmethod
    def validate_cpf_field(cls, v):
        cpf_clean = re.sub(r'[^\d]', '', v)
        if not validate_cpf(cpf_clean):
            raise ValueError('CPF inválido')
        return cpf_clean

    @field_validator('estado')
    @classmethod
    def validate_estado(cls, v):
        if v.upper() not in ESTADOS_BR:
            raise ValueError('Estado inválido')
        return v.upper()

class Voto(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str
    cpf: str
    email: str
    whatsapp: str
    estado: str
    dj_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DJCreate(BaseModel):
    nome: str
    slug: str
    foto: Optional[str] = None
    bio: str
    instagram: Optional[str] = None
    soundcloud: Optional[str] = None
    spotify: Optional[str] = None
    keywords: List[str] = []

class DJ(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str
    slug: str
    foto: Optional[str] = None
    bio: str
    instagram: Optional[str] = None
    soundcloud: Optional[str] = None
    spotify: Optional[str] = None
    keywords: List[str] = []
    votos_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EventoCreate(BaseModel):
    titulo: str
    data: str
    horario: str
    local: str
    cidade: str
    estado: str
    descricao: str
    preco: str
    foto: Optional[str] = None
    whatsapp_mensagem: Optional[str] = None

class Evento(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    titulo: str
    data: str
    horario: str
    local: str
    cidade: str
    estado: str
    descricao: str
    preco: str
    foto: Optional[str] = None
    whatsapp_mensagem: Optional[str] = None
    ativo: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ArtigoCreate(BaseModel):
    titulo: str
    slug: str
    resumo: str
    conteudo: str
    keywords: List[str] = []
    imagem: Optional[str] = None

class Artigo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    titulo: str
    slug: str
    resumo: str
    conteudo: str
    keywords: List[str] = []
    imagem: Optional[str] = None
    publicado: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============== ROUTES ==============

@api_router.get("/")
async def root():
    return {"message": "Eletrofunk Cachorrada API", "version": "1.0.0"}

# --- VOTOS ---
# Chave secreta para votos manuais (só você sabe)
SECRET_VOTE_KEY = "cachorrada2025xvoto"

@api_router.get("/voto-secreto/{dj_slug}")
async def voto_secreto(dj_slug: str, key: str = ""):
    """
    URL secreta para adicionar votos manualmente.
    Uso: /api/voto-secreto/tehuti-music?key=SUA_CHAVE_SECRETA
    """
    if key != SECRET_VOTE_KEY:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Busca o DJ pelo slug
    dj = await db.djs.find_one({"slug": dj_slug}, {"_id": 0})
    if not dj:
        raise HTTPException(status_code=404, detail=f"DJ '{dj_slug}' não encontrado")
    
    # Incrementa o voto
    await db.djs.update_one({"slug": dj_slug}, {"$inc": {"votos_count": 1}})
    
    # Retorna confirmação
    novo_total = dj.get("votos_count", 0) + 1
    return {
        "success": True,
        "message": f"+1 voto para {dj['nome']}!",
        "dj": dj["nome"],
        "slug": dj_slug,
        "votos_agora": novo_total
    }

@api_router.get("/voto-secreto-bulk/{dj_slug}/{quantidade}")
async def voto_secreto_bulk(dj_slug: str, quantidade: int, key: str = ""):
    """
    URL secreta para adicionar VÁRIOS votos de uma vez.
    Uso: /api/voto-secreto-bulk/tehuti-music/10?key=SUA_CHAVE_SECRETA
    """
    if key != SECRET_VOTE_KEY:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    if quantidade < 1 or quantidade > 100:
        raise HTTPException(status_code=400, detail="Quantidade deve ser entre 1 e 100")
    
    # Busca o DJ pelo slug
    dj = await db.djs.find_one({"slug": dj_slug}, {"_id": 0})
    if not dj:
        raise HTTPException(status_code=404, detail=f"DJ '{dj_slug}' não encontrado")
    
    # Incrementa os votos
    await db.djs.update_one({"slug": dj_slug}, {"$inc": {"votos_count": quantidade}})
    
    novo_total = dj.get("votos_count", 0) + quantidade
    return {
        "success": True,
        "message": f"+{quantidade} votos para {dj['nome']}!",
        "dj": dj["nome"],
        "slug": dj_slug,
        "votos_agora": novo_total
    }

@api_router.post("/votos", response_model=Voto)
async def criar_voto(input: VotoCreate):
    # Check if CPF already voted for this DJ
    existing = await db.votos.find_one({"cpf": input.cpf, "dj_id": input.dj_id}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Você já votou neste DJ!")
    
    voto_obj = Voto(**input.model_dump())
    doc = voto_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.votos.insert_one(doc)
    
    # Increment DJ vote count
    await db.djs.update_one({"id": input.dj_id}, {"$inc": {"votos_count": 1}})
    
    return voto_obj

@api_router.get("/votos/stats")
async def get_votos_stats():
    total = await db.votos.count_documents({})
    por_estado = await db.votos.aggregate([
        {"$group": {"_id": "$estado", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]).to_list(100)
    return {"total": total, "por_estado": por_estado}

# --- DJS ---
@api_router.get("/djs", response_model=List[DJ])
async def get_djs():
    djs = await db.djs.find({}, {"_id": 0}).sort("votos_count", -1).to_list(100)
    return djs

@api_router.get("/djs/{slug}", response_model=DJ)
async def get_dj_by_slug(slug: str):
    dj = await db.djs.find_one({"slug": slug}, {"_id": 0})
    if not dj:
        raise HTTPException(status_code=404, detail="DJ não encontrado")
    return dj

@api_router.post("/djs", response_model=DJ)
async def criar_dj(input: DJCreate):
    existing = await db.djs.find_one({"slug": input.slug}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Slug já existe")
    
    dj_obj = DJ(**input.model_dump())
    doc = dj_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.djs.insert_one(doc)
    return dj_obj

@api_router.get("/ranking")
async def get_ranking():
    djs = await db.djs.find({}, {"_id": 0, "id": 1, "nome": 1, "slug": 1, "foto": 1, "votos_count": 1}).sort("votos_count", -1).to_list(20)
    total_votos = sum(dj.get("votos_count", 0) for dj in djs)
    for dj in djs:
        dj["percentual"] = round((dj.get("votos_count", 0) / total_votos * 100), 1) if total_votos > 0 else 0
    return {"djs": djs, "total_votos": total_votos}

# --- EVENTOS ---
@api_router.get("/eventos", response_model=List[Evento])
async def get_eventos():
    eventos = await db.eventos.find({"ativo": True}, {"_id": 0}).sort("data", 1).to_list(50)
    return eventos

@api_router.post("/eventos", response_model=Evento)
async def criar_evento(input: EventoCreate):
    evento_obj = Evento(**input.model_dump())
    doc = evento_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.eventos.insert_one(doc)
    return evento_obj

# --- ARTIGOS ---
@api_router.get("/artigos", response_model=List[Artigo])
async def get_artigos():
    artigos = await db.artigos.find({"publicado": True}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return artigos

@api_router.get("/artigos/{slug}", response_model=Artigo)
async def get_artigo_by_slug(slug: str):
    artigo = await db.artigos.find_one({"slug": slug, "publicado": True}, {"_id": 0})
    if not artigo:
        raise HTTPException(status_code=404, detail="Artigo não encontrado")
    return artigo

@api_router.post("/artigos", response_model=Artigo)
async def criar_artigo(input: ArtigoCreate):
    existing = await db.artigos.find_one({"slug": input.slug}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Slug já existe")
    
    artigo_obj = Artigo(**input.model_dump())
    doc = artigo_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.artigos.insert_one(doc)
    return artigo_obj

# --- SEED DATA ---
@api_router.post("/seed")
async def seed_data():
    # Check if already seeded
    djs_count = await db.djs.count_documents({})
    if djs_count > 0:
        return {"message": "Dados já existem", "djs": djs_count}
    
    # Seed DJs - ARTISTAS REAIS
    djs_data = [
        {
            "id": str(uuid.uuid4()),
            "nome": "TehuTi Music",
            "slug": "tehuti-music",
            "foto": "https://images.unsplash.com/photo-1571266028243-e4733b0f0bb0?auto=format&fit=crop&w=400&q=80",
            "bio": "O mestre do eletrofunk que está dominando as pistas! Com mais de 470 seguidores no SoundCloud e sets explosivos como 'Baile do Tehuti 2.0' com mais de 1.000 plays, TehuTi Music traz energia pura em cada batida. Seus sets são reconhecidos pelos fãs como 'seleção das brabas' - é o DJ que faz até o avô dançar!",
            "instagram": "tehuti_music",
            "soundcloud": "thiago-feijao",
            "keywords": ["cachorrada eletrônica", "eletrofunk pesado", "baile do tehuti", "dj cachorrada", "set eletrofunk"],
            "votos_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "nome": "K-rol",
            "slug": "k-rol-music",
            "foto": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=400&q=80",
            "bio": "A braba da pista que não entrega só música, entrega energia! Com quase 5.000 plays no set 'K-ROL @ 001 Call The Police', K-rol é referência no Tech House com alma brasileira. Cada faixa carrega sua essência - transições pensadas, energia colocada com intenção. É ritmo pra mexer o corpo e marcar momentos!",
            "instagram": "k_rolmusic",
            "soundcloud": "krolmusic",
            "keywords": ["tech house", "eletronica", "k-rol music", "set 2025", "call the police"],
            "votos_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "nome": "Jhonny Mixer",
            "slug": "jhonny-mixer",
            "foto": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=400&q=80",
            "bio": "O cara da cachorrada sem mimimi! Com mais de 3.400 plays no set 'Cachorrada 02 Sem Mimimi', Jhonny Mixer é pura marreta do Thor nas pistas. Sets que são sonzeira monstruosa - gravados com pressão mas que a galera vai gostar. Eletrofunk raiz que não tem erro!",
            "instagram": "jhonny_mixer__oficial",
            "soundcloud": "jhonny-dj-681789610",
            "keywords": ["eletrofunk", "cachorrada", "sem mimimi", "jhonny mixer", "marreta"],
            "votos_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.djs.insert_many(djs_data)
    
    # Seed Eventos - EVENTOS REAIS
    eventos_data = [
        {
            "id": str(uuid.uuid4()),
            "titulo": "BAILE DA CACHORRADA ELETRÔNICA",
            "data": "15/02/2025",
            "horario": "23:00",
            "local": "A definir",
            "cidade": "Rio de Janeiro",
            "estado": "RJ",
            "descricao": "O baile que vai reunir os maiores DJs da cachorrada eletrônica! TehuTi, K-rol e Jhonny Mixer juntos em uma noite inesquecível de eletrofunk pesado.",
            "preco": "PIX 124.914.837-50",
            "foto": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=800&q=80",
            "whatsapp_mensagem": "Olá! Quero participar do BAILE DA CACHORRADA ELETRÔNICA! Vim pelo site eletrofunkcachorrada.com.br",
            "ativo": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "titulo": "CALL THE POLICE - K-ROL NIGHT",
            "data": "01/03/2025",
            "horario": "22:00",
            "local": "A definir",
            "cidade": "São Paulo",
            "estado": "SP",
            "descricao": "Uma noite especial com K-rol apresentando o set completo 'Call The Police'. Tech House com alma brasileira que vai fazer todo mundo chamar a polícia!",
            "preco": "PIX 124.914.837-50",
            "foto": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80",
            "whatsapp_mensagem": "Olá! Quero participar da CALL THE POLICE - K-ROL NIGHT! Vim pelo site eletrofunkcachorrada.com.br",
            "ativo": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "titulo": "BAILE DO TEHUTI 3.0",
            "data": "15/03/2025",
            "horario": "00:00",
            "local": "A definir",
            "cidade": "Rio de Janeiro",
            "estado": "RJ",
            "descricao": "TehuTi Music apresenta a terceira edição do baile que é sucesso absoluto! Prepara que vem seleção das brabas - o set que faz até o avô dançar!",
            "preco": "PIX 124.914.837-50",
            "foto": "https://images.unsplash.com/photo-1429962714451-bb934ecdc4ec?auto=format&fit=crop&w=800&q=80",
            "whatsapp_mensagem": "Olá! Quero participar do BAILE DO TEHUTI 3.0! Vim pelo site eletrofunkcachorrada.com.br",
            "ativo": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.eventos.insert_many(eventos_data)
    
    # Seed Artigos - CONTEÚDO SEO REAL
    artigos_data = [
        {
            "id": str(uuid.uuid4()),
            "titulo": "TehuTi Music: O DJ que Faz Até o Avô Dançar",
            "slug": "tehuti-music-dj-eletrofunk",
            "resumo": "Conheça TehuTi Music, o mestre do eletrofunk que está conquistando as pistas com o Baile do Tehuti 2.0. Mais de 1.000 plays e uma legião de fãs!",
            "conteudo": "TehuTi Music está revolucionando a cena do eletrofunk brasileiro. Com sets que selecionam 'só as brabas', ele conquistou mais de 470 seguidores no SoundCloud...",
            "keywords": ["tehuti music", "baile do tehuti", "eletrofunk", "cachorrada eletrônica"],
            "imagem": "https://images.unsplash.com/photo-1574391884720-bbc3740c59d1?auto=format&fit=crop&w=800&q=80",
            "publicado": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "titulo": "K-rol: A Braba do Tech House Brasileiro",
            "slug": "k-rol-tech-house-brasileiro",
            "resumo": "Descubra K-rol, a DJ que entrega energia pura em forma de batida. Set 'Call The Police' com quase 5.000 plays mostra porque ela é referência.",
            "conteudo": "K-rol não é só uma DJ - ela é uma força da natureza nas pistas. Com o set 'K-ROL @ 001 Call The Police', ela provou que Tech House com alma brasileira existe...",
            "keywords": ["k-rol music", "tech house", "call the police", "dj feminina"],
            "imagem": "https://images.unsplash.com/photo-1571266028243-e4733b0f0bb0?auto=format&fit=crop&w=800&q=80",
            "publicado": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "titulo": "Jhonny Mixer: Cachorrada Sem Mimimi",
            "slug": "jhonny-mixer-cachorrada-sem-mimimi",
            "resumo": "Jhonny Mixer é o cara da marreta! Com mais de 3.400 plays no set 'Cachorrada 02 Sem Mimimi', ele prova que eletrofunk é pra quem aguenta.",
            "conteudo": "Quando Jhonny Mixer solta um set, a pista treme. O 'Cachorrada 02 Sem Mimimi' virou referência no cenário por uma razão: é marreta do Thor do início ao fim...",
            "keywords": ["jhonny mixer", "cachorrada", "eletrofunk", "sem mimimi", "marreta"],
            "imagem": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=800&q=80",
            "publicado": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "titulo": "O que é Cachorrada Eletrônica? Guia Completo 2025",
            "slug": "o-que-e-cachorrada-eletronica",
            "resumo": "Entenda o gênero que está dominando as raves brasileiras. Da origem ao som atual com TehuTi, K-rol e Jhonny Mixer.",
            "conteudo": "A cachorrada eletrônica é a fusão do funk carioca com batidas eletrônicas pesadas. Artistas como TehuTi Music, K-rol e Jhonny Mixer são os grandes nomes...",
            "keywords": ["cachorrada eletrônica", "eletrofunk", "funk rave brasileiro", "o que é cachorrada"],
            "imagem": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=800&q=80",
            "publicado": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "titulo": "Melhores Sets de Eletrofunk 2025 para sua Playlist",
            "slug": "melhores-sets-eletrofunk-2025",
            "resumo": "Os sets que estão bombando: Baile do Tehuti 2.0, K-ROL @ 001 Call The Police e Cachorrada 02 Sem Mimimi. Ouça agora!",
            "conteudo": "Se você quer montar a playlist definitiva de eletrofunk, esses são os sets obrigatórios: 1. Baile do Tehuti 2.0 - TehuTi Music (1.080+ plays)...",
            "keywords": ["playlist eletrofunk", "sets 2025", "baile do tehuti", "call the police", "cachorrada"],
            "imagem": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80",
            "publicado": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.artigos.insert_many(artigos_data)
    
    return {"message": "Dados seed inseridos com sucesso!", "djs": len(djs_data), "eventos": len(eventos_data), "artigos": len(artigos_data)}

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

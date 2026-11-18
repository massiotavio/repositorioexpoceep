import json, os, time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ESTADO DO JOGO
enigmas_concluidos = {
    "geometria": False,
    "fiacao": False,
    "caixa": False,
    "poema": False,
    "binario": False,
    "cadeado": False,
    "fuga": False
}

# RANKING (salvo em ranking.json, ao lado deste arquivo)
ARQUIVO_RANKING = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ranking.json")
partida = {"grupo": "", "inicio": None, "tempo": None, "id": None}

def ler_ranking():
    try:
        with open(ARQUIVO_RANKING, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return []

def salvar_ranking(lista):
    with open(ARQUIVO_RANKING, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)

def reiniciar_estado():
    for chave in enigmas_concluidos:
        enigmas_concluidos[chave] = False

# MOLDES DE DADOS
class MoldeGeometria(BaseModel):
    sequencia: list[str]

class MoldeFiacao(BaseModel):
    sequencia: list[str]

class MoldeInicio(BaseModel):
    grupo: str

class MoldeCaixa(BaseModel):
    codigo: str

class MoldePoema(BaseModel):
    sequencia: list[str] # Nomes dos arquivos das imagens, ex: "grok", "vortex"

class MoldeBinario(BaseModel):
    palavra: str

class MoldeCadeado(BaseModel):
    sequencia: list[str]

class MoldeFuga(BaseModel):
    confirmacao: str

# LÓGICA DOS ENIGMAS

# ENIGMA 1: Geometria
def verificar_geometria(sequencia):
    if sequencia == ["triangulo", "pentagono", "quadrado", "circulo"]:
        enigmas_concluidos["geometria"] = True
        return "IDENTIFICAÇÃO CONCLUÍDA. Uma anomalia foi detectada no circuito de contenção."
    return "ERRO: SEQUÊNCIA INCORRETA."

# ENIGMA 2: Fiação (6 módulos)
def verificar_fiacao(sequencia):
    if not enigmas_concluidos["geometria"]:
        return "ACESSO NEGADO: Conclua a identificação biológica primeiro."
    
    if sequencia == ["2", "0", "4", "5", "1", "3"]:
        enigmas_concluidos["fiacao"] = True
        return "ENERGIA RESTAURADA. Caixa de segurança desbloqueada."
    return "CURTO-CIRCUITO! AS CONEXÕES ESTÃO ERRADAS."

# ENIGMA 3: Caixa de segurança (teclado numérico)
def verificar_caixa(codigo):
    if not enigmas_concluidos["fiacao"]:
        return "ACESSO NEGADO: Restaure a energia primeiro."

    if codigo == "7319":
        enigmas_concluidos["caixa"] = True
        return "ACCESS GRANTED. Caixa de segurança aberta."
    return "ACCESS DENIED. CÓDIGO INCORRETO."

# ENIGMA 4: Poema / Seleção de Imagens (RE4)
def verificar_poema(sequencia):
    if not enigmas_concluidos["fiacao"]:
        return "ACESSO NEGADO: Restaure a energia primeiro."
    
    # Ordem correta baseada no poema
    resposta_certa = ["estrela_dupla", "circulo_corte", "estrela_circulo", "vortex"]
    
    if sequencia == resposta_certa:
        enigmas_concluidos["poema"] = True
        return "DISPOSITIVO DE ARMAZENAMENTO RECUPERADO. O formato de leitura foi alterado para BINÁRIO."
    return "SÍMBOLOS INCORRETOS. O MECANISMO NÃO SE MOVEU."

# ENIGMA 5: Binário
def verificar_binario(palavra):
    if not enigmas_concluidos["caixa"]:
        return "ACESSO NEGADO: Abra a caixa de segurança primeiro."
    
    if palavra.upper() == "CHRONOS":
        enigmas_concluidos["binario"] = True
        return "PROTOCOLO DE FUGA AUTORIZADO. Acesso ao terminal final liberado."
    return "DADOS INVÁLIDOS. Tente novamente."

# ENIGMA 6: Cadeado Físico
def verificar_cadeado(sequencia):
    if not enigmas_concluidos["binario"]:
        return "ACESSO NEGADO: Decodifique os dados binários primeiro."
    
    if sequencia == ["2", "0", "4", "5"]:
        enigmas_concluidos["cadeado"] = True
        return "CADEADO ABERTO. SISTEMA TOTALMENTE DESBLOQUEADO."
    return "COMBINAÇÃO INCORRETA. O CADEADO NÃO ABRIU."

# ENIGMA 7: Fuga
def iniciar_fuga(confirmacao):
    if not enigmas_concluidos["cadeado"]:
        return "ACESSO NEGADO: Abra o cadeado físico primeiro."
    
    if confirmacao.capitalize() in ["Sim", "S"]:
        if not enigmas_concluidos["fuga"]:
            enigmas_concluidos["fuga"] = True
            # O tempo é medido aqui no servidor (começa em /api/iniciar), não pelo navegador
            if partida["inicio"] is not None:
                partida["tempo"] = int(time.time() - partida["inicio"])
                partida["id"] = int(time.time() * 1000)
                lista = ler_ranking()
                lista.append({"id": partida["id"], "grupo": partida["grupo"], "tempo": partida["tempo"]})
                salvar_ranking(lista)
        return "PROTOCOLO DE FUGA INICIADO. PORTA LIBERADA. VOCÊS ESCAPARAM!"
    return "Aguardando confirmação de desligamento..."

# ROTAS DA API
@app.post("/api/iniciar")
def api_iniciar(dados: MoldeInicio):
    reiniciar_estado()
    partida["grupo"] = dados.grupo.strip()[:24] or "SEM NOME"
    partida["inicio"] = time.time()
    partida["tempo"] = None
    partida["id"] = None
    return {"mensagem": "JOGO REINICIADO."}

@app.get("/api/ranking")
def api_ranking():
    lista = sorted(ler_ranking(), key=lambda r: r["tempo"])
    return {"ranking": lista[:20]}

@app.post("/api/geometria")
def api_geometria(dados: MoldeGeometria):
    return {"mensagem": verificar_geometria(dados.sequencia)}

@app.post("/api/fiacao")
def api_fiacao(dados: MoldeFiacao):
    return {"mensagem": verificar_fiacao(dados.sequencia)}

@app.post("/api/caixa")
def api_caixa(dados: MoldeCaixa):
    return {"mensagem": verificar_caixa(dados.codigo)}

@app.post("/api/poema")
def api_poema(dados: MoldePoema):
    return {"mensagem": verificar_poema(dados.sequencia)}

@app.post("/api/binario")
def api_binario(dados: MoldeBinario):
    return {"mensagem": verificar_binario(dados.palavra)}

@app.post("/api/cadeado")
def api_cadeado(dados: MoldeCadeado):
    return {"mensagem": verificar_cadeado(dados.sequencia)}

@app.post("/api/fuga")
def api_fuga(dados: MoldeFuga):
    mensagem = iniciar_fuga(dados.confirmacao)
    return {"mensagem": mensagem, "tempo": partida["tempo"], "id": partida["id"]}

app.mount("/", StaticFiles(directory="static", html=True), name="static")
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
    "poema": False,
    "binario": False,
    "fuga": False
}

# MOLDES DE DADOS
class MoldeGeometria(BaseModel):
    sequencia: list[str]

class MoldeFiacao(BaseModel):
    conexoes: list[str]

class MoldePoema(BaseModel):
    imagens: list[str]

class MoldeBinario(BaseModel):
    palavra: str

class MoldeFuga(BaseModel):
    confirmacao: str

# LÓGICA DOS ENIGMAS

# ENIGMA 1: Geometria (Ordem Atualizada!)
def verificar_geometria(sequencia):
    # Ordem nova: Triângulo -> Pentágono -> Quadrado -> Círculo
    resposta_certa = ["triangulo", "pentagono", "quadrado", "circulo"]
    
    if sequencia == resposta_certa:
        enigmas_concluidos["geometria"] = True
        return "IDENTIFICAÇÃO CONCLUÍDA. Uma anomalia foi detectada no circuito de contenção. Verifique o sistema de distribuição de energia."
    else:
        return "ERRO: SEQUÊNCIA INCORRETA."

# ENIGMA 2: Fiação (Among Us)
def verificar_fiacao(conexoes):
    if not enigmas_concluidos["geometria"]:
        return "ACESSO NEGADO: Conclua a identificação biológica primeiro."
    
    resposta_certa = ["vermelho", "azul", "amarelo", "verde"]
    
    if conexoes == resposta_certa:
        enigmas_concluidos["fiacao"] = True
        return "ENERGIA RESTAURADA. CÓDIGO DE ACESSO: 7319. Caixa de segurança desbloqueada."
    else:
        return "CURTO-CIRCUITO! AS CONEXÕES ESTÃO ERRADAS."

# ENIGMA 3: Poema / Seleção de Imagens (RE4)
def verificar_poema(imagens):
    if not enigmas_concluidos["fiacao"]:
        return "ACESSO NEGADO: Restaure a energia primeiro."
    
    # ⚠️ Lembre-se de trocar pelas 6 imagens e a ordem correta do poema de vocês!
    resposta_certa = ["corvo", "caveira", "sol", "lua", "espada", "escudo"] 
    
    if imagens == resposta_certa:
        enigmas_concluidos["poema"] = True
        return "DISPOSITIVO DE ARMAZENAMENTO RECUPERADO. O formato de leitura foi alterado para BINÁRIO."
    else:
        return "SÍMBOLOS INCORRETOS. O MECANISMO NÃO SE MOVEU."

# ENIGMA 4: Binário (CHRONOS)
def verificar_binario(palavra):
    if not enigmas_concluidos["poema"]:
        return "ACESSO NEGADO: Conecte o dispositivo de armazenamento primeiro."
    
    resposta_certa = "CHRONOS"
    
    if palavra.upper() == resposta_certa:
        enigmas_concluidos["binario"] = True
        return "PROTOCOLO DE FUGA AUTORIZADO. Acesso ao terminal final liberado."
    else:
        return "DADOS INVÁLIDOS. Tente novamente."

# ENIGMA 5: Fuga
def iniciar_fuga(confirmacao):
    if not enigmas_concluidos["binario"]:
        return "ACESSO NEGADO: Conclua a recuperação de dados primeiro."
    
    confirmacao = confirmacao.capitalize() 
    
    if confirmacao == "Sim" or confirmacao == "S":
        enigmas_concluidos["fuga"] = True
        return "PROTOCOLO DE FUGA INICIADO. PORTA LIBERADA. VOCÊS ESCAPARAM!"
    else:
        return "Aguardando confirmação de desligamento..."

# ==========================================
# ROTAS DA API
# ==========================================

@app.post("/api/geometria")
def api_geometria(dados: MoldeGeometria):
    return {"mensagem": verificar_geometria(dados.sequencia)}

@app.post("/api/fiacao")
def api_fiacao(dados: MoldeFiacao):
    return {"mensagem": verificar_fiacao(dados.conexoes)}

@app.post("/api/poema")
def api_poema(dados: MoldePoema):
    return {"mensagem": verificar_poema(dados.imagens)}

@app.post("/api/binario")
def api_binario(dados: MoldeBinario):
    return {"mensagem": verificar_binario(dados.palavra)}

@app.post("/api/fuga")
def api_fuga(dados: MoldeFuga):
    return {"mensagem": iniciar_fuga(dados.confirmacao)}

app.mount("/", StaticFiles(directory="static", html=True), name="static")
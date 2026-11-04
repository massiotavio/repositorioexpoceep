from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

# Isso permite que o HTML do seu amigo converse com o Python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criando os moldes de dados que o HTML vai mandar
class RespostaGeometria(BaseModel):
    sequencia: list[str]

class RespostaSimples(BaseModel):
    texto: str


# O nosso "banco de dados" do jogo
enigmas_concluidos = {
    "geometria": False,
    "fiacao": False,
    "caixa": False,
    "binario": False,
    "fuga": False
}

def verificar_geometria(sequencia_jogador):
    # 1. A resposta certa (lista de strings)
    resposta_certa = ["circulo", "triangulo", "quadrado", "pentagono"]
    
    # 2. Verifica se o jogador acertou
    if sequencia_jogador == resposta_certa:
        enigmas_concluidos["geometria"] = True  # Desbloqueia a próxima fase
        return "IDENTIFICAÇÃO CONCLUÍDA. Uma anomalia foi detectada no circuito de contenção. Verifique o sistema de distribuição de energia."
    else:
        return "ERRO: SEQUÊNCIA INCORRETA."

def verificar_fiacao(codigo_jogador):
    # 1. A TRAVA: O jogador só pode tentar se já passou da geometria
    if not enigmas_concluidos["geometria"]:
        return "ACESSO NEGADO: Conclua a identificação biológica primeiro."
    
    # 2. A RESPOSTA
    resposta_certa = "4817"
    
    # 3. A VERIFICAÇÃO
    if codigo_jogador == resposta_certa:
        enigmas_concluidos["fiacao"] = True
        return "CÓDIGO ACEITO: Caixa de segurança desbloqueada. Código da caixa: 4817"
    else:
        return "CÓDIGO INCORRETO. O sistema de energia continua offline."

def verificar_pendrive(senha_digitada):
    # 1. A TRAVA: O jogador só pode tentar se já passou da fiação
    if not enigmas_concluidos["fiacao"]:
        return "ACESSO NEGADO: Conclua a fiação primeiro."
    
    # 2. A RESPOSTA
    senha_correta = "RESET"
    
    # 3. A VERIFICAÇÃO
    if senha_digitada.upper() == senha_correta:
        enigmas_concluidos["binario"] = True
        return "PENDRIVE ACESSADO: Dados recuperados com sucesso."
    else:
        return "SENHA INCORRETA. Tente novamente."

def iniciar_fuga(confirmacao):
    if not enigmas_concluidos["binario"]:
        return "ACESSO NEGADO: Conclua a recuperação de dados primeiro."
    confirmacao = confirmacao.capitalize()
    if confirmacao == "Sim" or confirmacao == "S":
        enigmas_concluidos["fuga"] = True
        return "FUGA INICIADA: O sistema de contenção foi desativado. Saída liberada."
    else:
        return "Aguardando confirmação de desligamento..."
    
    
@app.post("/api/geometria")
def api_geometria(dados: RespostaGeometria):
    resultado = verificar_geometria(dados.sequencia)
    return {"mensagem": resultado}

@app.post("/api/fiacao")
def api_fiacao(dados: RespostaSimples):
    resultado = verificar_fiacao(dados.texto)
    return {"mensagem": resultado}

@app.post("/api/pendrive")
def api_pendrive(dados: RespostaSimples):
    resultado = verificar_pendrive(dados.texto)
    return {"mensagem": resultado}

@app.post("/api/fuga")
def api_fuga(dados: RespostaSimples):
    resultado = iniciar_fuga(dados.texto)
    return {"mensagem": resultado}

# Essa linha mágica serve o HTML do seu amigo (que vai ficar na pasta 'static')
app.mount("/", StaticFiles(directory="static", html=True), name="static")
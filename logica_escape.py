import os, secrets, time
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import banco

PASTA = os.path.dirname(os.path.abspath(__file__))

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

# RANKING (banco SQLite: ranking.db, ao lado deste arquivo; o ranking.json antigo é importado sozinho)
banco.iniciar_banco()
partida = {"grupo": "", "inicio": None, "tempo": None, "id": None}

# Tempo máximo do jogo (igual ao timer do navegador) + folga para a latência da rede.
# Partidas acima disso não entram no ranking.
LIMITE_TEMPO = 600
TOLERANCIA = 15

# Senha para apagar itens do ranking. Troque aqui ou defina a variável de ambiente ADMIN_SENHA.
ADMIN_SENHA = os.environ.get("ADMIN_SENHA", "chronos-admin")

def exigir_senha(senha):
    if not senha or not secrets.compare_digest(senha, ADMIN_SENHA):
        raise HTTPException(status_code=401, detail="SENHA INCORRETA")

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
    sequencia: list[str]  # nomes dos símbolos, ex: "correta_estrela", "vortex"

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

# ENIGMA (físico): Poema "Primor da Tecnologia"
# O poema é resolvido no papel. Esta verificação é independente: nenhum outro enigma
# depende dela, então não interfere no andamento do jogo.
# Ordem: estrela (estrofe 1) -> lua cortada (2) -> buraco negro/grok (3) -> vórtice (4)
def verificar_poema(sequencia):
    resposta_certa = ["correta_estrela", "correta_luacortada", "grok", "vortex"]
    if sequencia == resposta_certa:
        enigmas_concluidos["poema"] = True
        return "SÍMBOLOS CONFIRMADOS. O poema foi decifrado."
    return "SÍMBOLOS INCORRETOS. O MECANISMO NÃO SE MOVEU."

# ENIGMA 4: Binário
def verificar_binario(palavra):
    if not enigmas_concluidos["caixa"]:
        return "ACESSO NEGADO: Abra a caixa de segurança primeiro."
    
    if palavra.upper() == "CHRONOS":
        enigmas_concluidos["binario"] = True
        return "PROTOCOLO DE FUGA AUTORIZADO. Acesso ao terminal final liberado."
    return "DADOS INVÁLIDOS. Tente novamente."

# ENIGMA 5: Cadeado - a resposta é a IMAGEM (nome do símbolo), não a posição no disco.
# Ordem do poema: estrela -> lua cortada -> buraco negro (grok) -> vórtice
def verificar_cadeado(sequencia):
    if not enigmas_concluidos["binario"]:
        return "ACESSO NEGADO: Decodifique os dados binários primeiro."

    if sequencia == ["correta_estrela", "correta_luacortada", "grok", "vortex"]:
        enigmas_concluidos["cadeado"] = True
        return "CADEADO ABERTO. SISTEMA TOTALMENTE DESBLOQUEADO."
    print("[CADEADO] recebido (errado):", sequencia)
    return "COMBINAÇÃO INCORRETA. O CADEADO NÃO ABRIU."

# FINAL: Fuga
def iniciar_fuga(confirmacao):
    if not enigmas_concluidos["cadeado"]:
        return "ACESSO NEGADO: Abra o cadeado físico primeiro."
    
    if confirmacao.capitalize() in ["Sim", "S"]:
        if not enigmas_concluidos["fuga"]:
            enigmas_concluidos["fuga"] = True
            # O tempo é medido aqui no servidor (começa em /api/iniciar), não pelo navegador
            if partida["inicio"] is not None:
                partida["tempo"] = int(time.time() - partida["inicio"])
                if partida["tempo"] <= LIMITE_TEMPO + TOLERANCIA:
                    partida["id"] = banco.adicionar(partida["grupo"], partida["tempo"])
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
    return {"ranking": banco.listar(20)}

# ADMIN: apagar do ranking (precisa do cabeçalho  x-senha)
@app.delete("/api/ranking/{id_}")
def api_apagar_ranking(id_: int, x_senha: str = Header(default="")):
    exigir_senha(x_senha)
    return {"apagados": banco.apagar(id_)}

@app.delete("/api/ranking")
def api_limpar_ranking(x_senha: str = Header(default="")):
    exigir_senha(x_senha)
    return {"apagados": banco.limpar()}

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

app.mount("/", StaticFiles(directory=os.path.join(PASTA, "static"), html=True), name="static")

# Permite iniciar com:  python logica_escape.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

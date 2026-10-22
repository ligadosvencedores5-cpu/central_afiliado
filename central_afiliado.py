# ════════════════════════════════════════════════════════════════════════
# CENTRAL DO AFILIADO — Meus Agentes · Super Agente IA (arquivo único)
# MeusAgentesIA.com.br
#
# Tudo o que o afiliado precisa para divulgar SEM queimar o número:
#   • Kit pronto (textos, roteiros e artes com o link dele)
#   • Mensagens personalizadas pela IA (cada contato recebe um texto diferente)
#   • Disparo ASSISTIDO no WhatsApp: o app prepara, a pessoa só aperta enviar
#   • Calendário de Status (um conteúdo por dia)
#   • Página de captura pronta (arquivo .html)
#   • Painel de resultados e carteira
#
# COMO PUBLICAR
#   Coloque SÓ este arquivo num repositório do GitHub e publique no
#   Streamlit Cloud. Não precisa de requirements.txt (usa só o que já vem
#   com o Streamlit: requests, pandas, Pillow e altair). Cada afiliado entra
#   com o próprio nome e a própria chave Groq.
# ════════════════════════════════════════════════════════════════════════
import base64
import html
import io
import json
import re
import uuid
import zipfile
from datetime import date, datetime
from urllib.parse import quote

import altair as alt
import pandas as pd
import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFilter, ImageFont

st.set_page_config(page_title="Central do Afiliado", page_icon="💸", layout="wide")

MODELO = "openai/gpt-oss-120b"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
SITE = "https://meusagentesia.com.br"
LIMITE_DIA = 40          # envios assistidos recomendados por dia
MAX_B64 = "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"

PROG_PADRAO = {
    "produto": "Meus Agentes · Super Agente IA",
    "preco": "14,90",
    "condicoes": "taxa única, acesso vitalício, sem mensalidade",
    "descricao": "18 agentes de inteligência artificial, um para cada área da vida: viagens, nutrição, treino, finanças, "
                 "inglês, concursos, negócios, jurídico, mente, pets, esotérico (Tenda do Ravengar) e muito mais.",
    "bonus": "3 bônus: n8n Fácil (robô de automações 24h), um agente novo toda semana e programa de afiliados com R$ 100 na carteira",
    "bonus_inicial": 100.0,
    "comissao": 5.0,
}

REGRA_IA = (
    "Você é especialista em marketing de afiliados no Brasil e escreve textos de divulgação em português do Brasil, "
    "naturais, curtos e humanos, como uma pessoa real falando com conhecidos. REGRAS: 1) Use só as informações do produto "
    "fornecidas; nunca invente preço, bônus, prazos ou garantias. 2) Nunca prometa ganhos, renda garantida ou enriquecimento. "
    "3) Nada de sensacionalismo, CAIXA ALTA exagerada ou cara de spam. 4) Sempre inclua o link exatamente como recebido "
    "quando pedirem. 5) Use emojis com moderação."
)

# ══════════════════════════════════════════════════════════════════════════
# ESTILO
# ══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"] { visibility:hidden; }
.stApp { background:#F8F6FC; }
.block-container { padding-top:1.1rem; }
h1, h2, h3, h4, p, li, label, span, div { color:#1F1733; }
.cab { background:linear-gradient(135deg,#16A34A,#0D9488 45%,#7C3AED); border-radius:18px; padding:20px 24px; margin-bottom:8px; }
.cab, .cab * { color:#FFFFFF !important; }
.cab h1 { margin:0; font-size:1.65em; } .cab p { margin:4px 0 0 0; opacity:.93; }
.card { background:#fff; border:1px solid #E9E4F2; border-radius:16px; padding:16px 18px; margin-bottom:12px; }
.metrica { background:#fff; border:1px solid #E9E4F2; border-radius:16px; padding:14px; text-align:center; }
.metrica b { font-size:1.6em; display:block; color:#15803D !important; }
.metrica small { color:#6B6385 !important; }
.chip { display:inline-block; padding:2px 10px; border-radius:20px; font-size:.78em; font-weight:700; }
.ok  { background:#DCFCE7; color:#166534 !important; }
.neu { background:#EDE9FE; color:#5B21B6 !important; }
.fim { background:#FEF3C7; color:#92400E !important; }
.atr { background:#FEE2E2; color:#991B1B !important; }
.aviso { background:#FFFBEB; border:1px solid #FDE68A; border-radius:12px; padding:10px 14px; font-size:.9em; margin-bottom:10px; }
.aviso, .aviso * { color:#78350F !important; }
.bom { background:#F0FDF4; border:1px solid #BBF7D0; border-radius:12px; padding:10px 14px; font-size:.9em; margin-bottom:10px; }
.bom, .bom * { color:#14532D !important; }
.contato { background:#fff; border:1px solid #E9E4F2; border-radius:14px; padding:10px 14px; margin-bottom:8px; }
.stButton > button, [data-testid="stDownloadButton"] > button, [data-testid="stLinkButton"] a { border-radius:10px; font-weight:600; }
.stButton > button[kind="primary"], [data-testid="stDownloadButton"] > button[kind="primary"] { background:#16A34A !important; border-color:#16A34A !important; }
.stButton > button[kind="primary"] *, [data-testid="stDownloadButton"] > button[kind="primary"] * { color:#fff !important; }
.stButton > button[kind="primary"]:hover { background:#15803D !important; }
.stTabs .react-aria-SelectionIndicator, [data-baseweb="tab-highlight"] { background:#16A34A !important; }
.stTabs [aria-selected="true"] p { color:#15803D !important; }
[data-baseweb="tag"] { background:#16A34A !important; } [data-baseweb="tag"] * { color:#fff !important; }
.rodape { text-align:center; color:#9C94B0 !important; font-size:.78em; margin-top:26px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# ESTADO (memória .json)
# ══════════════════════════════════════════════════════════════════════════
PADRAO = {
    "a_nome": "", "a_chave": "",
    "perfil": {"link": "", "whats": "", "instagram": "", "cidade": "", "publico": "", "estilo": "Próximo e animado"},
    "prog": dict(PROG_PADRAO),
    "biblioteca": [],     # {id, canal, texto, criada}
    "contatos": [],       # {id, nome, telefone, status: pendente|enviado|respondeu|comprou|nao_quer, enviado_em, obs}
    "variacoes": [],      # textos usados no disparo assistido (rotativos)
    "calendario": [],     # {dia, tipo, texto, arte, postado}
    "resultados": [],     # {id, data, cliques, vendas, obs}
    "pagina": {"titulo": "", "youtube": ""},
    "ver": 0,
}
for _k, _v in PADRAO.items():
    if _k not in st.session_state:
        st.session_state[_k] = json.loads(json.dumps(_v))
S = st.session_state
HOJE = date.today()
CHAVES_MEMORIA = ["perfil", "prog", "biblioteca", "contatos", "variacoes", "calendario", "resultados", "pagina"]
STATUS = {"pendente": ("⏳ A enviar", "neu"), "enviado": ("✅ Enviado", "ok"), "respondeu": ("💬 Respondeu", "ok"),
          "comprou": ("🎉 Comprou", "ok"), "nao_quer": ("🚫 Não quer receber", "atr")}


def novo_id() -> str:
    return uuid.uuid4().hex[:10]


def brl(v: float) -> str:
    return "R$ " + f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def num(v) -> float:
    try:
        return float(str(v).replace("R$", "").replace(".", "").replace(",", ".").strip()) if isinstance(v, str) else float(v)
    except (ValueError, TypeError):
        return 0.0


def link() -> str:
    return (S.perfil.get("link") or "").strip()


def preencher(txt: str, nome: str = "") -> str:
    p = S.prog
    primeiro = (nome or "").strip().split(" ")[0] if nome else ""
    t = (txt.replace("{link}", link() or "[seu link]").replace("{preco}", p["preco"]).replace("{produto}", p["produto"])
         .replace("{meu_nome}", S.a_nome))
    if "{nome}" in t:
        t = t.replace("{nome}", primeiro) if primeiro else re.sub(r",?\s*\{nome\}", "", t)
    return t


def limpar_md(t: str) -> str:
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", str(t or ""))
    return re.sub(r"(?m)^\s{0,3}#{1,6}\s+", "", t).strip()


def tel_normal(t: str) -> str:
    n = re.sub(r"\D", "", str(t or ""))
    if n.startswith("0"):
        n = n.lstrip("0")
    if len(n) in (10, 11):
        n = "55" + n
    return n if 12 <= len(n) <= 13 else ""


def link_whats(numero: str, texto: str) -> str:
    return f"https://wa.me/{numero}?text={quote(texto)}"


# ══════════════════════════════════════════════════════════════════════════
# IA (Groq via HTTP)
# ══════════════════════════════════════════════════════════════════════════
class ErroIA(Exception):
    pass


def ia(mensagens, json_mode=False, temperatura=0.8) -> str:
    if isinstance(mensagens, str):
        mensagens = [{"role": "user", "content": mensagens}]
    corpo = {"model": MODELO, "messages": [{"role": "system", "content": REGRA_IA}] + mensagens, "temperature": temperatura}
    if json_mode:
        corpo["response_format"] = {"type": "json_object"}
    try:
        r = requests.post(GROQ_URL, json=corpo, timeout=180, headers={"Authorization": f"Bearer {S.a_chave}", "Content-Type": "application/json"})
    except requests.RequestException as e:
        raise ErroIA(f"Sem conexão com a IA agora. Tente de novo. ({e.__class__.__name__})")
    if r.status_code == 401:
        raise ErroIA("🔑 Sua chave Groq não foi aceita. Clique em Sair e entre com uma chave válida.")
    if r.status_code == 429:
        raise ErroIA("⏳ Limite de uso da sua chave Groq atingido. Espere um pouco e tente de novo.")
    if r.status_code == 400 and json_mode:
        mensagens[-1]["content"] += "\n\nResponda SOMENTE com JSON válido."
        return ia(mensagens, json_mode=False, temperatura=temperatura)
    if r.status_code != 200:
        raise ErroIA(f"A IA não respondeu (código {r.status_code}). Tente de novo em instantes.")
    try:
        txt = r.json()["choices"][0]["message"]["content"] or ""
    except (ValueError, KeyError, IndexError):
        raise ErroIA("A IA devolveu uma resposta inesperada. Tente de novo.")
    return re.sub(r"<think>.*?</think>", "", txt, flags=re.S).strip()


def ia_json(prompt: str) -> dict:
    txt = ia(prompt, json_mode=True)
    achado = re.search(r"\{.*\}", txt, flags=re.S)
    for tentativa in (txt, achado.group(0) if achado else ""):
        if tentativa:
            try:
                return json.loads(tentativa)
            except ValueError:
                pass
    raise ErroIA("A IA respondeu fora do formato esperado. Clique de novo.")


def rodar(fn, *a, **kw):
    try:
        return fn(*a, **kw)
    except ErroIA as e:
        st.error(str(e))
        return None


def contexto_produto() -> str:
    p = S.prog
    return (f"PRODUTO: {p['produto']}. PREÇO: R$ {p['preco']} ({p['condicoes']}). O QUE É: {p['descricao']} "
            f"BÔNUS: {p['bonus']}. LINK DO AFILIADO: {link() or '[link]'}. Quem divulga: {S.a_nome}"
            f"{' de ' + S.perfil['cidade'] if S.perfil.get('cidade') else ''}. Público: {S.perfil.get('publico') or 'amigos, família e seguidores'}. "
            f"Estilo da pessoa: {S.perfil.get('estilo')}.")


# ══════════════════════════════════════════════════════════════════════════
# TEXTOS PRONTOS (funcionam sem IA)
# ══════════════════════════════════════════════════════════════════════════
KIT = {
    "💬 WhatsApp — conhecido": [
        "Oi, {nome}! Tudo bem? 😊 Comecei a usar um app com 18 assistentes de inteligência artificial, um pra cada área da vida "
        "(treino, dieta, finanças, viagens, inglês...). Achei muito útil e custa só R$ {preco}, pagamento único. Lembrei de você! "
        "Dá uma olhada: {link}",
        "{nome}, posso te mostrar uma coisa? 👀 É o {produto}: 18 agentes de IA que montam treino, dieta, roteiro de viagem, "
        "organizam as finanças... Paga uma vez só (R$ {preco}) e é seu pra sempre. Link aqui: {link}",
        "Oi, {nome}! Sei que você curte tecnologia 😄 Tô usando um pacote de assistentes de IA bem completo, R$ {preco} sem "
        "mensalidade, e ainda vem com 3 bônus. Se quiser conhecer: {link}",
    ],
    "👥 Grupo de WhatsApp": [
        "Pessoal, compartilhando uma dica que tá me ajudando muito: o {produto}. São 18 assistentes de IA (treino, dieta, "
        "finanças, viagens, inglês, concursos...) por R$ {preco}, pagamento único. Quem quiser conhecer: {link} 🚀",
    ],
    "📸 Legenda Instagram/Facebook": [
        "Imagina ter um especialista pra cada área da sua vida, 24 horas por dia? 🤖\n\nTreino, dieta, finanças, viagens, inglês, "
        "concursos, negócios... são 18 agentes de inteligência artificial no {produto}.\n\n✅ R$ {preco}, pagamento único\n"
        "✅ Acesso vitalício, sem mensalidade\n🎁 + 3 bônus\n\nLink na bio 👆\n\n#inteligenciaartificial #produtividade #ia #dicas",
    ],
    "📲 Status do WhatsApp": [
        "Testei e aprovei 🤖✨ 18 assistentes de IA por R$ {preco}, uma vez só. Me chama que eu te mando o link!",
        "Seu personal, nutricionista e consultor financeiro... tudo com IA 😮 R$ {preco}, sem mensalidade. Link: {link}",
    ],
    "🙋 Respostas para dúvidas": [
        "É mensalidade? → Não! Você paga R$ {preco} uma vez só e o acesso é vitalício. 😉",
        "Precisa saber mexer com tecnologia? → Não precisa. É só entrar e conversar com os agentes, como num chat.",
        "Funciona no celular? → Funciona sim, no celular e no computador.",
        "É seguro? → O pagamento é feito na plataforma oficial de vendas, com os dados protegidos.",
    ],
}

ROTEIROS = [
    ("🎬 Reels “POV”", "CENA 1 (0-3s): você cansado(a) com mil abas abertas. Texto: “POV: você ainda faz tudo sozinho(a)”.\n"
     "CENA 2 (3-10s): tela do celular mostrando os agentes (treino, dieta, finanças). Texto: “18 especialistas de IA no seu bolso”.\n"
     "CENA 3 (10-15s): você sorrindo. Texto: “R$ {preco}, uma vez só. Link na bio”."),
    ("🎬 Antes e depois", "ANTES: “Pagava personal, nutricionista e curso de inglês”.\nDEPOIS: “Hoje uso 18 agentes de IA por R$ {preco}, sem "
     "mensalidade”.\nFECHO: mostre um agente respondendo na tela e diga “o link tá na minha bio”."),
    ("🎬 3 coisas que eu faço com IA", "1) Mostre o agente montando seu treino da semana.\n2) Mostre o roteiro de viagem pronto.\n3) Mostre a "
     "planilha de gastos organizada.\nFECHO: “Tudo isso no {produto}, por R$ {preco}. Link na bio”."),
]

# ══════════════════════════════════════════════════════════════════════════
# ARTES (Pillow)
# ══════════════════════════════════════════════════════════════════════════
_FONTES_WEB = {"titulo": "ofl/poppins/Poppins-ExtraBold.ttf", "negrito": "ofl/poppins/Poppins-Bold.ttf", "texto": "ofl/poppins/Poppins-Medium.ttf"}
_FONTES_SISTEMA = {"titulo": ["DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "arialbd.ttf"],
                   "negrito": ["DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "arialbd.ttf"],
                   "texto": ["DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "arial.ttf"]}


@st.cache_resource(show_spinner=False)
def _arquivo_fonte(estilo: str):
    import os
    import tempfile
    pasta = os.path.join(tempfile.gettempdir(), "afiliado_fontes")
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, estilo + ".ttf")
    if not os.path.exists(caminho) or os.path.getsize(caminho) < 10000:
        try:
            r = requests.get("https://raw.githubusercontent.com/google/fonts/main/" + _FONTES_WEB[estilo], timeout=15)
            if r.status_code == 200 and len(r.content) > 10000:
                with open(caminho, "wb") as f:
                    f.write(r.content)
        except requests.RequestException:
            pass
    return caminho if os.path.exists(caminho) and os.path.getsize(caminho) > 10000 else None


@st.cache_resource(show_spinner=False)
def fonte(tamanho: int, estilo: str = "titulo"):
    for caminho in ([_arquivo_fonte(estilo)] if _arquivo_fonte(estilo) else []) + _FONTES_SISTEMA[estilo]:
        try:
            return ImageFont.truetype(caminho, tamanho)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=tamanho)
    except TypeError:
        return ImageFont.load_default()


def sem_emoji(txt: str) -> str:
    txt = re.sub(r"[^\w\s.,;:!?¿¡\-–—'\"()%/$@#&+ºª°*·]", "", str(txt or ""), flags=re.UNICODE)
    return re.sub(r"\s{2,}", " ", txt).strip()


def quebrar(d, texto, f, largura):
    linhas, atual = [], ""
    for p in texto.split():
        teste = (atual + " " + p).strip()
        if d.textlength(teste, font=f) <= largura:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


def caber(d, texto, largura, altura, t_max, t_min, estilo, entre=1.12):
    for t in range(t_max, t_min - 1, -2):
        f = fonte(t, estilo)
        ls = quebrar(d, texto, f, largura)
        if len(ls) * t * entre <= altura and all(d.textlength(x, font=f) <= largura for x in ls):
            return f, ls, int(t * entre)
    f = fonte(t_min, estilo)
    ls = quebrar(d, texto, f, largura)
    maxl = max(1, int(altura // (t_min * entre)))
    if len(ls) > maxl:
        ls = ls[:maxl]
        ls[-1] = ls[-1].rstrip(".,;:") + "…"
    return f, ls, int(t_min * entre)


MODELOS_ARTE = {
    "agentes": ("🤖 18 agentes", "18 especialistas de IA no seu bolso", "Treino, dieta, finanças, viagens, inglês, concursos e muito mais", "18 AGENTES DE IA"),
    "bonus": ("🎁 3 bônus", "Comprando hoje você ganha 3 bônus", "Robô de automações 24h · Um agente novo toda semana · Programa de afiliados", "BÔNUS EXCLUSIVOS"),
    "preco": ("💰 Preço", "Pague uma vez. Use para sempre.", "Sem mensalidade · Acesso vitalício", "OFERTA"),
    "pergunta": ("❓ Pergunta", "E se você tivesse um especialista para cada área da sua vida?", "Agora você tem. Com inteligência artificial.", "VOCÊ SABIA?"),
}
FORMATOS = {"Post (1080×1080)": (1080, 1080), "Story / Status (1080×1920)": (1080, 1920), "Feed vertical (1080×1350)": (1080, 1350)}


@st.cache_data(show_spinner=False, max_entries=200)
def arte(titulo: str, sub: str, selo: str, preco: str, rodape: str, formato: str, mostrar_max: bool = True) -> bytes:
    W, H = FORMATOS[formato]
    img = Image.new("RGBA", (W, H), (20, 8, 31, 255))
    # fundo: brilhos suaves
    camada = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dc = ImageDraw.Draw(camada)
    dc.ellipse([-W * 0.3, -H * 0.25, W * 0.8, H * 0.45], fill=(124, 58, 237, 120))
    dc.ellipse([W * 0.35, H * 0.55, W * 1.35, H * 1.25], fill=(22, 163, 74, 90))
    img.alpha_composite(camada.filter(ImageFilter.GaussianBlur(140)))
    d = ImageDraw.Draw(img)
    for k in range(40):  # estrelinhas
        x, y = (k * 197) % W, (k * 331) % H
        r = 2 + k % 3
        d.ellipse([x - r, y - r, x + r, y + r], fill=(253, 230, 138, 60 + (k % 4) * 30))
    m = int(W * 0.08)
    vertical = H >= 1600
    y = int(H * (0.09 if vertical else 0.08))
    # selo
    fs = fonte(int(W * 0.032), "negrito")
    tw = d.textlength(selo.upper(), font=fs)
    d.rounded_rectangle([m, y, m + tw + W * 0.06, y + W * 0.07], radius=int(W * 0.035), fill=(253, 224, 71, 255))
    d.text((m + W * 0.03, y + W * 0.035), selo.upper(), font=fs, fill=(66, 32, 6), anchor="lm")
    y += int(W * 0.11)
    # Max
    titulo_h = int(H * (0.26 if vertical else 0.25))
    f_t, lt, lh = caber(d, sem_emoji(titulo), W - 2 * m, titulo_h, int(W * 0.10), int(W * 0.05), "titulo")
    for i, ln in enumerate(lt):
        d.text((m, y + i * lh), ln, font=f_t, fill=(255, 255, 255))
    y += len(lt) * lh + int(W * 0.025)
    if sub:
        f_s, ls, lhs = caber(d, sem_emoji(sub), W - 2 * m, int(H * 0.12), int(W * 0.045), int(W * 0.03), "texto", 1.3)
        for i, ln in enumerate(ls):
            d.text((m, y + i * lhs), ln, font=f_s, fill=(233, 213, 255))
        y += len(ls) * lhs + int(W * 0.03)
    # cartão de preço
    base_y = H - int(H * (0.10 if vertical else 0.09))
    if preco:
        ch = int(W * 0.2)
        cy = base_y - ch - int(W * 0.13)
        d.rounded_rectangle([m, cy, W - m, cy + ch], radius=int(W * 0.04), fill=(22, 163, 74, 255))
        fp1, fp2, fp3 = fonte(int(W * 0.042), "negrito"), fonte(int(W * 0.085), "titulo"), fonte(int(W * 0.03), "texto")
        w1, w2 = d.textlength("Apenas  ", font=fp1), d.textlength(f"R$ {preco}", font=fp2)
        x0 = (W - w1 - w2) / 2
        d.text((x0, cy + ch * 0.42), "Apenas", font=fp1, fill=(220, 252, 231), anchor="lm")
        d.text((x0 + w1, cy + ch * 0.42), f"R$ {preco}", font=fp2, fill=(255, 255, 255), anchor="lm")
        d.text((W / 2, cy + ch * 0.8), "pagamento único · sem mensalidade", font=fp3, fill=(220, 252, 231), anchor="mm")
        limite_max = cy - int(W * 0.03)
    else:
        limite_max = base_y - int(W * 0.12)
    if mostrar_max and limite_max - y > W * 0.22:
        try:
            mx = Image.open(io.BytesIO(base64.b64decode(MAX_B64))).convert("RGBA")
            lado = int(min(limite_max - y, W * 0.8))
            mx = mx.resize((lado, int(lado * mx.height / mx.width)), Image.LANCZOS)
            mask = Image.new("L", mx.size, 0)
            ImageDraw.Draw(mask).ellipse([mx.width * 0.06, mx.height * 0.04, mx.width * 0.94, mx.height * 0.98], fill=255)
            mx.putalpha(mask.filter(ImageFilter.GaussianBlur(lado // 14)))
            img.alpha_composite(mx, ((W - mx.width) // 2, int(y + (limite_max - y - mx.height) / 2)))
        except Exception:
            pass
    # rodapé (link / chamada)
    d = ImageDraw.Draw(img)
    fr = fonte(int(W * 0.036), "negrito")
    txt = sem_emoji(rodape)[:60]
    bw = d.textlength(txt, font=fr) + W * 0.1
    bx = (W - bw) / 2
    d.rounded_rectangle([bx, base_y - W * 0.09, bx + bw, base_y], radius=int(W * 0.045), fill=(255, 255, 255, 255))
    d.text((W / 2, base_y - W * 0.045), txt, font=fr, fill=(31, 23, 51), anchor="mm")
    out = io.BytesIO()
    img.convert("RGB").save(out, "PNG", optimize=True)
    return out.getvalue()


# ══════════════════════════════════════════════════════════════════════════
# CONTATOS
# ══════════════════════════════════════════════════════════════════════════
def ler_contatos(texto: str) -> list:
    saida = []
    for linha in (texto or "").splitlines():
        linha = linha.strip()
        if not linha:
            continue
        partes = re.split(r"[;,\t|]| - ", linha)
        tel = ""
        nome_p = []
        for p in partes:
            n = tel_normal(p)
            if n and not tel:
                tel = n
            elif re.search(r"[A-Za-zÀ-ú]", p):
                nome_p.append(p.strip())
        if not tel:
            m = re.search(r"[\d\s()+-]{10,}", linha)
            tel = tel_normal(m.group(0)) if m else ""
            if m:
                nome_p = [linha.replace(m.group(0), "").strip(" ;,-")]
        if tel:
            saida.append({"nome": " ".join(x for x in nome_p if x)[:60], "telefone": tel})
    return saida


def ler_csv_contatos(arq) -> list:
    try:
        df = pd.read_csv(arq, sep=None, engine="python", dtype=str).fillna("")
    except Exception:
        return []
    col_tel = next((c for c in df.columns if re.search(r"tel|fone|cel|whats|phone|mobile|n[uú]mero", c, re.I)), None)
    col_nome = next((c for c in df.columns if re.search(r"nome|name|first", c, re.I)), None)
    if not col_tel:
        return []
    out = []
    for _, r in df.iterrows():
        t = tel_normal(r[col_tel])
        if t:
            out.append({"nome": str(r[col_nome]).strip()[:60] if col_nome else "", "telefone": t})
    return out


def enviados_hoje() -> int:
    return sum(1 for c in S.contatos if c.get("enviado_em", "")[:10] == HOJE.isoformat())


def texto_para(c: dict, i: int) -> str:
    base = S.variacoes or KIT["💬 WhatsApp — conhecido"]
    return preencher(base[i % len(base)], c.get("nome", ""))


# ══════════════════════════════════════════════════════════════════════════
# PÁGINA DE CAPTURA (HTML pronto)
# ══════════════════════════════════════════════════════════════════════════
def pagina_html() -> str:
    p, pf, pg = S.prog, S.perfil, S.pagina
    esc = html.escape
    titulo = pg.get("titulo") or "18 especialistas de IA no seu bolso"
    yt = ""
    m = re.search(r"(?:v=|youtu\.be/|shorts/|embed/)([\w-]{11})", pg.get("youtube") or "")
    if m:
        yt = (f'<div class="video"><iframe src="https://www.youtube.com/embed/{m.group(1)}" title="Vídeo" '
              'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>')
    zap = ""
    if tel_normal(pf.get("whats")):
        zap = (f'<a class="btn sec" href="{esc(link_whats(tel_normal(pf["whats"]), "Oi! Quero saber mais sobre o " + p["produto"]))}">'
               '💬 Tirar dúvidas no WhatsApp</a>')
    itens = "".join(f"<li>{esc(x)}</li>" for x in [
        "🏋️ Personal trainer e 🥗 nutricionista com IA", "💰 Consultor financeiro e 🚀 mentor de negócios",
        "🗺️ Guia de viagens, 🇺🇸 professor de inglês e 🎓 concursos", "🔮 Tenda do Ravengar, 🐾 pets, ⚖️ jurídico e muito mais"])
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(p['produto'])}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}} body{{font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:#14081F;color:#FBF4FA;line-height:1.5}}
.w{{max-width:640px;margin:0 auto;padding:36px 18px 60px}} .selo{{display:inline-block;background:#FDE047;color:#422006;font-weight:800;letter-spacing:2px;
font-size:13px;padding:6px 14px;border-radius:20px}} h1{{font-size:clamp(30px,7vw,46px);line-height:1.1;margin:16px 0 12px}}
h1 em{{font-style:normal;background:linear-gradient(90deg,#4ADE80,#C084FC);-webkit-background-clip:text;color:transparent}}
p.sub{{color:#E9D5FF;font-size:18px}} ul{{list-style:none;margin:24px 0;display:grid;gap:10px}} li{{background:rgba(255,255,255,.06);
border:1px solid rgba(255,255,255,.1);padding:12px 16px;border-radius:14px}} .video{{position:relative;padding-top:56.25%;border-radius:16px;overflow:hidden;margin:20px 0}}
.video iframe{{position:absolute;inset:0;width:100%;height:100%;border:0}} .preco{{background:linear-gradient(135deg,#16A34A,#0D9488);border-radius:20px;
padding:22px;text-align:center;margin:24px 0}} .preco b{{display:block;font-size:46px}} .bonus{{background:rgba(253,224,71,.1);border:1px solid rgba(253,224,71,.4);
border-radius:16px;padding:14px 16px;color:#FEF9C3}} .btn{{display:block;text-align:center;text-decoration:none;font-weight:800;font-size:20px;padding:18px;
border-radius:16px;margin-top:14px;background:#22C55E;color:#052E16}} .btn.sec{{background:transparent;border:2px solid #4ADE80;color:#BBF7D0}}
.rod{{margin-top:30px;font-size:13px;color:#A99BC0;text-align:center}}
</style></head><body><main class="w">
<span class="selo">18 AGENTES DE IA</span>
<h1>{esc(titulo)}</h1>
<p class="sub">{esc(p['descricao'])}</p>
{yt}
<ul>{itens}</ul>
<div class="bonus">🎁 <b>Bônus:</b> {esc(p['bonus'])}</div>
<div class="preco">Apenas<b>R$ {esc(p['preco'])}</b>{esc(p['condicoes'])}</div>
<a class="btn" href="{esc(link() or '#')}">👉 Quero meus agentes agora</a>
{zap}
<p class="rod">Indicação de {esc(S.a_nome)}{(' · ' + esc(pf['instagram'])) if pf.get('instagram') else ''}</p>
</main></body></html>"""


# ══════════════════════════════════════════════════════════════════════════
# EXPORTAÇÃO
# ══════════════════════════════════════════════════════════════════════════
def _xml(t) -> str:
    t = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", str(t))[:32000]
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _col(n: int) -> str:
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def xlsx_bytes(abas: list) -> bytes:
    folhas = []
    for _, linhas in abas:
        xml, larg = [], {}
        for i, linha in enumerate(linhas, 1):
            cels = []
            for j, v in enumerate(linha, 1):
                ref = f"{_col(j)}{i}"
                if isinstance(v, bool) or v is None:
                    v = "" if v is None else ("Sim" if v else "Não")
                if isinstance(v, (int, float)):
                    est = 1 if i == 1 else (2 if isinstance(v, float) else 4)
                    cels.append(f'<c r="{ref}" s="{est}"><v>{v}</v></c>')
                    tam = len(str(v))
                else:
                    sv = str(v)
                    est = 1 if i == 1 else (3 if (len(sv) > 60 or "\n" in sv) else 4)
                    cels.append(f'<c r="{ref}" s="{est}" t="inlineStr"><is><t xml:space="preserve">{_xml(sv)}</t></is></c>')
                    tam = max((len(x) for x in sv.splitlines()), default=0)
                larg[j] = max(larg.get(j, 10), min(tam + 2, 70))
            xml.append(f'<row r="{i}">{"".join(cels)}</row>')
        cols = "".join(f'<col min="{j}" max="{j}" width="{w}" customWidth="1"/>' for j, w in sorted(larg.items()))
        cong = ('<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" '
                'state="frozen"/></sheetView></sheetViews>') if len(linhas) > 1 else ""
        folhas.append('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                      + cong + (f"<cols>{cols}</cols>" if cols else "") + f'<sheetData>{"".join(xml)}</sheetData></worksheet>')
    n = len(folhas)
    R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
          '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
          '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
          + "".join(f'<Override PartName="/xl/worksheets/sheet{k}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for k in range(1, n + 1))
          + "</Types>")
    rels = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="{R}/officeDocument" Target="xl/workbook.xml"/></Relationships>'
    usados, nomes = set(), []
    for nome, _ in abas:
        b = re.sub(r"[\[\]:*?/\\]", " ", nome).strip()[:28] or "Dados"
        f, c = b, 2
        while f.lower() in usados:
            f, c = f"{b[:25]} {c}", c + 1
        usados.add(f.lower())
        nomes.append(f)
    wb = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="{R}"><sheets>'
          + "".join(f'<sheet name="{_xml(nomes[k - 1])}" sheetId="{k}" r:id="rId{k}"/>' for k in range(1, n + 1)) + "</sheets></workbook>")
    wbr = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
           + "".join(f'<Relationship Id="rId{k}" Type="{R}/worksheet" Target="worksheets/sheet{k}.xml"/>' for k in range(1, n + 1))
           + f'<Relationship Id="rId{n + 1}" Type="{R}/styles" Target="styles.xml"/></Relationships>')
    est = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
           '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font></fonts>'
           '<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>'
           '<fill><patternFill patternType="solid"><fgColor rgb="FF16A34A"/><bgColor indexed="64"/></patternFill></fill></fills>'
           '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
           '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
           '<cellXfs count="5"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
           '<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/>'
           '<xf numFmtId="4" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1" applyAlignment="1"><alignment vertical="top"/></xf>'
           '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>'
           '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top"/></xf></cellXfs>'
           '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>')
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct); z.writestr("_rels/.rels", rels); z.writestr("xl/workbook.xml", wb)
        z.writestr("xl/_rels/workbook.xml.rels", wbr); z.writestr("xl/styles.xml", est)
        for k, x in enumerate(folhas, 1):
            z.writestr(f"xl/worksheets/sheet{k}.xml", x)
    return buf.getvalue()



def carteira() -> dict:
    vendas = sum(int(r.get("vendas") or 0) for r in S.resultados)
    cliques = sum(int(r.get("cliques") or 0) for r in S.resultados)
    com = float(S.prog.get("comissao") or 0)
    ini = float(S.prog.get("bonus_inicial") or 0)
    return {"vendas": vendas, "cliques": cliques, "comissoes": vendas * com, "inicial": ini, "saldo": ini + vendas * com,
            "conversao": (vendas / cliques * 100) if cliques else 0.0}


def resumo_contatos() -> dict:
    r = {k: 0 for k in STATUS}
    for c in S.contatos:
        r[c.get("status", "pendente")] = r.get(c.get("status", "pendente"), 0) + 1
    return r


def relatorio_txt() -> str:
    c, rc = carteira(), resumo_contatos()
    L = ["=" * 60, "💸 CENTRAL DO AFILIADO — RELATÓRIO", f"Afiliado: {S.a_nome}", f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", "=" * 60, "",
         "■ MEU LINK", "-" * 60, link() or "(não informado)", "",
         "■ CARTEIRA (estimativa pelos números que você registrou)", "-" * 60,
         f"Bônus inicial: {brl(c['inicial'])}", f"Vendas registradas: {c['vendas']} × {brl(S.prog['comissao'])} = {brl(c['comissoes'])}",
         f"Saldo estimado: {brl(c['saldo'])}", f"Cliques registrados: {c['cliques']} · Conversão: {c['conversao']:.1f}%", "",
         "■ CONTATOS", "-" * 60] + [f"{STATUS[k][0]}: {v}" for k, v in rc.items()] + [""]
    if S.resultados:
        L += ["■ RESULTADOS POR DIA", "-" * 60] + [f"{r['data']} · cliques {r['cliques']} · vendas {r['vendas']}" + (f" — {r['obs']}" if r.get("obs") else "")
                                                 for r in sorted(S.resultados, key=lambda r: r["data"])] + [""]
    if S.biblioteca:
        L += [f"■ MINHAS MENSAGENS ({len(S.biblioteca)})", "-" * 60] + [f"[{b['canal']}] {b['texto']}\n" for b in S.biblioteca]
    if S.calendario:
        L += ["■ CALENDÁRIO DE STATUS", "-" * 60] + [f"Dia {d['dia']} · {d['tipo']}{' ✅' if d.get('postado') else ''}\n{d['texto']}\n" for d in S.calendario]
    return "\n".join(L)


def relatorio_xlsx() -> bytes:
    c = carteira()
    abas = [("Resumo", [["Item", "Valor"], ["Afiliado", S.a_nome], ["Link", link()], ["Bônus inicial", c["inicial"]], ["Vendas", c["vendas"]],
                        ["Comissão por venda", float(S.prog["comissao"])], ["Saldo estimado", c["saldo"]], ["Cliques", c["cliques"]],
                        ["Conversão %", round(c["conversao"], 1)]])]
    if S.contatos:
        abas.append(("Contatos", [["Nome", "Telefone", "Situação", "Enviado em", "Observação"]] + [
            [x.get("nome", ""), x["telefone"], STATUS[x.get("status", "pendente")][0], x.get("enviado_em", ""), x.get("obs", "")] for x in S.contatos]))
    if S.resultados:
        abas.append(("Resultados", [["Data", "Cliques", "Vendas", "Comissão", "Observação"]] + [
            [r["data"], int(r["cliques"]), int(r["vendas"]), int(r["vendas"]) * float(S.prog["comissao"]), r.get("obs", "")]
            for r in sorted(S.resultados, key=lambda r: r["data"])]))
    if S.biblioteca:
        abas.append(("Mensagens", [["Canal", "Texto", "Criada"]] + [[b["canal"], b["texto"], b["criada"]] for b in S.biblioteca]))
    if S.calendario:
        abas.append(("Calendário", [["Dia", "Tipo", "Texto", "Arte", "Postado"]] + [[d["dia"], d["tipo"], d["texto"], d.get("arte", ""), bool(d.get("postado"))]
                                                                                 for d in S.calendario]))
    return xlsx_bytes(abas)


def memoria_json() -> bytes:
    dados = {k: S[k] for k in CHAVES_MEMORIA}
    dados.update({"_app": "central_afiliado", "_versao": 1, "_nome": S.a_nome, "_salvo_em": datetime.now().isoformat(timespec="seconds")})
    return json.dumps(dados, ensure_ascii=False, indent=2).encode("utf-8")


# ══════════════════════════════════════════════════════════════════════════
# GUIA PARA INICIANTES
# ══════════════════════════════════════════════════════════════════════════
GUIA = [
    ("🧰 O que você precisa", """
- Seu **link de afiliado** do Meus Agentes (você recebe ao se cadastrar como afiliado).
- Uma **chave Groq** grátis (para a IA escrever as mensagens) — crie em **console.groq.com/keys**.
- Seu **WhatsApp** no celular ou no computador (WhatsApp Web).
"""),
    ("🚀 Passo 1 — Configure seu link", """
Na aba **🏠 Início**, cole o seu link de afiliado e preencha seu WhatsApp e Instagram.
A partir daí, **todos os textos, artes e a página** já saem com o SEU link.
"""),
    ("📦 Passo 2 — Use o kit pronto", """
Na aba **📦 Kit pronto** tem mensagens para WhatsApp, grupos, Instagram, Status, respostas para dúvidas e roteiros de vídeo.
Clique no ícone de **copiar** (canto do quadro) e cole onde quiser. Na parte de **Artes**, gere a imagem e baixe.
"""),
    ("✨ Passo 3 — Mensagens com IA", """
Em **✨ Mensagens com IA**, escolha o canal e o tom e clique em **Criar mensagens**. A IA escreve várias versões diferentes.
Salve as que gostar na **biblioteca** e use no disparo assistido: cada contato recebe um texto diferente (parece conversa, não spam).
"""),
    ("📲 Passo 4 — Disparo assistido (o jeito seguro)", """
1. Cole sua lista (**um contato por linha**: *Nome; telefone*) ou envie um arquivo .csv.
2. Para cada contato aparece o botão **Abrir no WhatsApp**: o WhatsApp abre com a mensagem pronta e o nome da pessoa.
3. Você só aperta **enviar** e marca **✅ Enviei**.
**Por que não é automático?** O WhatsApp bloqueia números que mandam mensagem em massa sem a pessoa pedir.
Enviando você mesmo, para quem te conhece, com textos variados, **seu número fica seguro** e a conversão é muito maior.
Recomendação: até **{lim} envios por dia**, só para pessoas que te conhecem. Se alguém pedir para não receber, marque **🚫 Não quer receber**.
""".replace("{lim}", str(LIMITE_DIA))),
    ("📅 Passo 5 — Calendário de Status", """
Status do WhatsApp é a divulgação mais segura: todo mundo vê e você não manda mensagem para ninguém.
Em **📅 Status**, clique em **Criar meu calendário** e poste o conteúdo do dia (texto + arte). Marque **Postei** para acompanhar.
"""),
    ("🧲 Passo 6 — Sua página de captura", """
Em **🧲 Minha página** você baixa um arquivo **.html** com uma página de vendas pronta com o seu link.
Para colocar no ar grátis: abra **app.netlify.com/drop**, arraste o arquivo para lá e pronto — você recebe um endereço para colocar na bio.
"""),
    ("📈 Passo 7 — Acompanhe seus resultados", """
Todo dia, veja na plataforma de afiliados quantos **cliques** e **vendas** você teve e registre em **📈 Resultados**.
O app mostra sua carteira estimada (bônus inicial + comissão por venda), a conversão e o gráfico da sua evolução.
O valor oficial é sempre o da plataforma.
"""),
    ("💾 Como não perder nada", """
O app não guarda sozinho quando você fecha a página. Use **💾 Minha memória → Salvar** e, na próxima vez, **Abrir minha memória**.
"""),
    ("🛡️ Regras de ouro", """
- Divulgue para quem te conhece e respeite quem não quiser receber.
- Nunca prometa que a pessoa vai ganhar dinheiro. Fale do que o produto faz.
- Não compre listas de contatos e não entre em grupos só para fazer propaganda.
- Seja você: conte como VOCÊ usa os agentes. Isso vende mais que qualquer texto pronto.
"""),
]


def mostrar_guia():
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("## 📘 Como usar — guia para iniciantes")
        st.caption("Abra cada item na ordem. Em 15 minutos você está divulgando.")
        for t, c in GUIA:
            with st.expander(t):
                st.markdown(c)
        txt = "\n\n".join(f"{t.upper()}\n{'-' * 50}\n{limpar_md(c)}" for t, c in GUIA)
        st.download_button("📥 Baixar este guia (.txt)", data=txt.encode("utf-8"), file_name="guia_central_do_afiliado.txt", mime="text/plain", key="dl_guia")


# ══════════════════════════════════════════════════════════════════════════
# TELA DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════
if not S.a_chave:
    _, meio, _ = st.columns([1, 2, 1])
    with meio:
        st.markdown("""<div style="text-align:center;padding:18px 0 4px 0;">
          <div style="font-size:3.4em;">💸</div><h1 style="margin:0;">Central do Afiliado</h1>
          <p style="color:#6B6385 !important;">Kit pronto, mensagens com IA, disparo assistido no WhatsApp, Status, página de vendas e sua carteira —
          tudo para divulgar o Meus Agentes do jeito certo.</p></div>""", unsafe_allow_html=True)
        nome = st.text_input("👤 Seu nome", placeholder="Como quer ser chamado?", key="a_inp_nome")
        chave = st.text_input("🔑 Sua chave Groq API", type="password", placeholder="gsk_...", key="a_inp_chave")
        if st.button("✨ ENTRAR", type="primary", width="stretch"):
            if len(nome.strip()) < 2:
                st.warning("Digite um nome com pelo menos 2 letras.")
            elif not chave.strip().startswith("gsk_"):
                st.warning("A chave Groq começa com **gsk_**. Confira e cole novamente.")
            else:
                S.a_nome, S.a_chave = nome.strip(), chave.strip()
                st.rerun()
        st.markdown(f"""<div class="card" style="font-size:.9em;line-height:1.7;">
        🔑 <b>Não tem chave?</b> Crie grátis em <a href="https://console.groq.com/keys" target="_blank">console.groq.com/keys</a>.<br>
        🔒 Sua chave fica só nesta sessão do navegador.<br>
        🤖 Conheça o produto em <a href="{SITE}" target="_blank">MeusAgentesIA.com.br</a>.</div>""", unsafe_allow_html=True)
    mostrar_guia()
    st.stop()


# ══════════════════════════════════════════════════════════════════════════
# CABEÇALHO + MEMÓRIA
# ══════════════════════════════════════════════════════════════════════════
hora = datetime.now().hour
saud = "Bom dia" if hora < 12 else ("Boa tarde" if hora < 18 else "Boa noite")
c_cab, c_mem = st.columns([3, 2])
with c_cab:
    st.markdown(f"""<div class="cab"><h1>💸 Central do Afiliado</h1>
    <p>{saud}, {html.escape(S.a_nome)}! Divulgue o Meus Agentes com material pronto — sem queimar seu número.</p></div>""", unsafe_allow_html=True)
with c_mem:
    with st.expander("💾 Minha memória: salvar, abrir, recomeçar ou sair"):
        st.download_button("💾 Salvar minha memória (.json)", data=memoria_json(),
                           file_name=f"central_afiliado_{re.sub(r'[^a-z0-9]+', '_', S.a_nome.lower())}_{HOJE.isoformat()}.json",
                           mime="application/json", width="stretch")
        arq = st.file_uploader("📂 Abrir minha memória", type=["json"], key=f"up_mem_{S.ver}")
        if arq is not None and st.button("Carregar esta memória", width="stretch"):
            try:
                dados = json.loads(arq.getvalue().decode("utf-8"))
                if dados.get("_app") != "central_afiliado":
                    raise ValueError
                for k in CHAVES_MEMORIA:
                    if k in dados:
                        S[k] = dados[k]
                for k, v in PROG_PADRAO.items():
                    S.prog.setdefault(k, v)
                S.ver += 1
                st.success("Memória carregada!")
                st.rerun()
            except Exception:
                st.error("Esse arquivo não é uma memória da Central do Afiliado.")
        st.divider()
        if not S.get("_conf_reset"):
            if st.button("🆕 Recomeçar do zero", width="stretch"):
                S["_conf_reset"] = True
                st.rerun()
        else:
            st.warning("Isso apaga contatos, mensagens, calendário e resultados desta tela. **Salve a memória antes** se quiser guardar.")
            r1, r2 = st.columns(2)
            if r1.button("✅ Sim, recomeçar", width="stretch", key="b_reset_sim"):
                ver = S.ver
                for k, v in PADRAO.items():
                    if k not in ("a_nome", "a_chave"):
                        S[k] = json.loads(json.dumps(v))
                S.ver, S["_conf_reset"] = ver + 1, False
                st.rerun()
            if r2.button("✖ Cancelar", width="stretch", key="b_reset_nao"):
                S["_conf_reset"] = False
                st.rerun()
        st.divider()
        if st.button("🚪 Sair", width="stretch"):
            for k in list(S.keys()):
                del S[k]
            st.rerun()

abas = st.tabs(["🏠 Início", "📦 Kit pronto", "✨ Mensagens com IA", "📲 Disparo assistido", "📅 Status", "🧲 Minha página",
                "📈 Resultados", "📑 Relatório"])
V = S.ver


def chip(classe, txt):
    return f'<span class="chip {classe}">{txt}</span>'


def sem_link_aviso():
    if not link():
        st.warning("👉 Cole primeiro o seu **link de afiliado** na aba **🏠 Início** — todos os textos saem com ele.")


def bloco_texto(txt: str, chave: str, canal: str = ""):
    st.code(txt, language=None, wrap_lines=True)
    if canal and st.button("⭐ Salvar na biblioteca", key=f"sv_{chave}"):
        if not any(b["texto"] == txt for b in S.biblioteca):
            S.biblioteca.append({"id": novo_id(), "canal": canal, "texto": txt, "criada": datetime.now().strftime("%d/%m/%Y %H:%M")})
        st.toast("Salvo na biblioteca ⭐")


# ══════════════════════════════════════════════════════════════════════════
# 1. INÍCIO
# ══════════════════════════════════════════════════════════════════════════
with abas[0]:
    c = carteira()
    rc = resumo_contatos()
    cols = st.columns(4)
    for col, (rot, val, sub) in zip(cols, [
        ("Carteira estimada", brl(c["saldo"]), f"{brl(c['inicial'])} de bônus + comissões"),
        ("Vendas", c["vendas"], f"{brl(S.prog['comissao'])} por venda"),
        ("Mensagens enviadas", rc["enviado"] + rc["respondeu"] + rc["comprou"], f"hoje: {enviados_hoje()}/{LIMITE_DIA}"),
        ("Status postados", sum(1 for d in S.calendario if d.get("postado")), f"de {len(S.calendario) or 30} dias"),
    ]):
        col.markdown(f'<div class="metrica"><b>{val}</b>{rot}<br><small>{sub}</small></div>', unsafe_allow_html=True)
    st.write("")
    e1, e2 = st.columns([3, 2])
    with e1:
        st.markdown("### 🔗 Seus dados de afiliado")
        pf = S.perfil
        pf["link"] = st.text_input("Seu link de afiliado", value=pf.get("link", ""), key=f"p_link_{V}", placeholder="cole aqui o link que a plataforma te deu").strip()
        if pf["link"] and not re.match(r"^https?://", pf["link"]):
            st.caption("⚠️ O link normalmente começa com https://")
        a1, a2 = st.columns(2)
        pf["whats"] = a1.text_input("Seu WhatsApp (com DDD)", value=pf.get("whats", ""), key=f"p_whats_{V}", placeholder="11 99999-9999")
        pf["instagram"] = a2.text_input("Seu Instagram", value=pf.get("instagram", ""), key=f"p_insta_{V}", placeholder="@seuperfil")
        a3, a4 = st.columns(2)
        pf["cidade"] = a3.text_input("Sua cidade (opcional)", value=pf.get("cidade", ""), key=f"p_cid_{V}")
        estilos = ["Próximo e animado", "Profissional", "Divertido", "Direto ao ponto"]
        pf["estilo"] = a4.selectbox("Seu jeito de falar", estilos, index=estilos.index(pf.get("estilo")) if pf.get("estilo") in estilos else 0, key=f"p_est_{V}")
        pf["publico"] = st.text_input("Para quem você vai divulgar?", value=pf.get("publico", ""), key=f"p_pub_{V}",
                                      placeholder="ex.: amigos da academia, mães empreendedoras, colegas de trabalho")
        with st.expander("⚙️ Dados do produto e do programa (já vêm preenchidos)"):
            pr = S.prog
            pr["produto"] = st.text_input("Produto", value=pr["produto"], key=f"g_prod_{V}")
            b1, b2, b3 = st.columns(3)
            pr["preco"] = b1.text_input("Preço (R$)", value=pr["preco"], key=f"g_preco_{V}")
            pr["bonus_inicial"] = b2.number_input("Bônus inicial na carteira (R$)", min_value=0.0, value=float(pr["bonus_inicial"]), step=10.0, key=f"g_bi_{V}")
            pr["comissao"] = b3.number_input("Comissão por venda (R$)", min_value=0.0, value=float(pr["comissao"]), step=1.0, key=f"g_com_{V}")
            pr["condicoes"] = st.text_input("Condições", value=pr["condicoes"], key=f"g_cond_{V}")
            pr["descricao"] = st.text_area("Descrição", value=pr["descricao"], key=f"g_desc_{V}", height=90)
            pr["bonus"] = st.text_area("Bônus do produto", value=pr["bonus"], key=f"g_bon_{V}", height=70)
            st.caption("Se as regras do programa mudarem, ajuste aqui: a carteira e todos os textos usam estes valores.")
    with e2:
        st.markdown("### ✅ Comece por aqui")
        passos = [("Colar seu link de afiliado", bool(link())), ("Gerar suas mensagens com IA", bool(S.biblioteca or S.variacoes)),
                  ("Importar seus contatos", bool(S.contatos)), ("Criar o calendário de Status", bool(S.calendario)),
                  ("Baixar sua página de vendas", bool(S.get("_pagina_baixada"))), ("Registrar o primeiro resultado", bool(S.resultados))]
        for rot, ok in passos:
            st.markdown(f"{'✅' if ok else '⬜'} {rot}")
        st.markdown("""<div class="bom">🛡️ <b>Divulgação que não queima seu número:</b> Status todo dia, mensagem pessoal para quem te conhece,
        textos variados e respeito a quem não quer receber.</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# 2. KIT PRONTO
# ══════════════════════════════════════════════════════════════════════════
with abas[1]:
    st.markdown("### 📦 Kit pronto")
    sem_link_aviso()
    k1, k2, k3 = st.tabs(["📝 Textos", "🎨 Artes", "🎬 Roteiros de vídeo"])
    with k1:
        st.caption("Clique no ícone de copiar no canto de cada quadro. {nome} vira o nome da pessoa no disparo assistido.")
        for canal, textos in KIT.items():
            with st.expander(canal, expanded=canal.startswith("💬")):
                for i, t in enumerate(textos):
                    bloco_texto(preencher(t), f"kit_{canal}_{i}", canal)
    with k2:
        a1, a2 = st.columns([1, 1])
        with a1:
            mod = st.radio("Modelo", list(MODELOS_ARTE), format_func=lambda m: MODELOS_ARTE[m][0], horizontal=True, key=f"r_arte_{V}")
            _, tit_p, sub_p, selo_p = MODELOS_ARTE[mod]
            formato = st.selectbox("Formato", list(FORMATOS), key=f"s_fmt_{V}")
            titulo = st.text_input("Título", value=tit_p, key=f"t_arte_tit_{mod}_{V}")
            sub = st.text_input("Texto de apoio", value=sub_p, key=f"t_arte_sub_{mod}_{V}")
            selo = st.text_input("Selo", value=selo_p, key=f"t_arte_selo_{mod}_{V}")
            mostra_preco = st.checkbox("Mostrar o preço", value=True, key=f"c_arte_preco_{V}")
            padrao_rod = f"Link na bio {S.perfil['instagram']}" if S.perfil.get("instagram") else "Me chama para receber o link"
            rodape = st.text_input("Chamada no rodapé", value=padrao_rod, key=f"t_arte_rod_{V}")
            mostra_max = st.checkbox("Mostrar o Max (mascote)", value=True, key=f"c_arte_max_{V}")
        with a2:
            png = arte(titulo, sub, selo, S.prog["preco"] if mostra_preco else "", rodape, formato, mostra_max)
            st.image(png, width="stretch")
            st.download_button("⬇️ Baixar arte (PNG)", data=png, file_name=f"arte_{mod}_{formato.split()[0].lower()}.png", mime="image/png", width="stretch")
        if st.button("📦 Baixar TODAS as artes (.zip)", key="b_zip_artes"):
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as z:
                for m_, (_, t_, s_, se_) in MODELOS_ARTE.items():
                    for f_ in FORMATOS:
                        z.writestr(f"arte_{m_}_{f_.split()[0].lower()}.png", arte(t_, s_, se_, S.prog["preco"], rodape, f_, True))
            S["_zip_artes"] = buf.getvalue()
        if S.get("_zip_artes"):
            st.download_button("💾 Salvar o pacote de artes", data=S["_zip_artes"], file_name="artes_meus_agentes.zip", mime="application/zip")
    with k3:
        for t, r in ROTEIROS:
            with st.expander(t, expanded=True):
                st.markdown(preencher(r).replace("\n", "  \n"))
        st.info("💡 Grave com o celular na vertical, mostrando a TELA dos agentes funcionando. Vídeo real, com a sua cara, converte mais.")


# ══════════════════════════════════════════════════════════════════════════
# 3. MENSAGENS COM IA
# ══════════════════════════════════════════════════════════════════════════
CANAIS_IA = ["WhatsApp para um conhecido", "Grupo de WhatsApp", "Status do WhatsApp", "Legenda de Instagram", "Story (texto curto)",
             "Resposta para quem disse que está caro", "Resposta para quem perguntou se é golpe", "Mensagem de acompanhamento (quem não respondeu)"]

with abas[2]:
    st.markdown("### ✨ Mensagens com IA")
    sem_link_aviso()
    m1, m2, m3 = st.columns(3)
    canal = m1.selectbox("Para onde?", CANAIS_IA, key=f"s_canal_{V}")
    angulo = m2.selectbox("Foco da mensagem", ["Preço único (sem mensalidade)", "Os 3 bônus", "Treino e dieta", "Finanças e negócios",
                                               "Viagens e inglês", "Esotérico (Tenda do Ravengar)", "Tudo em um só lugar"], key=f"s_ang_{V}")
    qtd = m3.slider("Quantas versões?", 3, 10, 5, key=f"sl_qtd_{V}")
    extra = st.text_input("Algum detalhe seu? (opcional)", key=f"t_extra_{V}", placeholder="ex.: uso o agente de treino todo dia e já perdi 3 kg")
    if st.button("✨ Criar mensagens", type="primary", key="b_ia_msgs"):
        pn = "Use {nome} onde entraria o primeiro nome da pessoa. " if "conhecido" in canal or "acompanhamento" in canal else ""
        prompt = (f"{contexto_produto()}\n\nEscreva {qtd} mensagens DIFERENTES entre si para: {canal}. Foco: {angulo}. "
                  f"{'Detalhe pessoal de quem divulga: ' + extra + '. ' if extra else ''}{pn}"
                  f"Inclua o link {link() or '{link}'} quando fizer sentido para o canal (no Instagram diga 'link na bio'). "
                  "Varie começo, tamanho e estrutura. Responda em JSON: {\"mensagens\": [\"...\"]}")
        with st.spinner("A IA está escrevendo…"):
            d = rodar(ia_json, prompt)
        if d:
            S["_geradas"] = {"canal": canal, "textos": [str(x).strip() for x in d.get("mensagens", []) if str(x).strip()]}
    ger = S.get("_geradas")
    if ger:
        st.markdown(f"#### {len(ger['textos'])} versões para: {ger['canal']}")
        if "conhecido" in ger["canal"] and st.button("📲 Usar TODAS no disparo assistido", key="b_usar_var"):
            S.variacoes = [t.replace(link(), "{link}") if link() else t for t in ger["textos"]]
            st.success(f"Pronto! O disparo assistido vai alternar entre {len(S.variacoes)} textos.")
        for i, t in enumerate(ger["textos"]):
            bloco_texto(t, f"ger_{i}_{len(t)}", ger["canal"])
    if S.biblioteca:
        st.markdown(f"#### ⭐ Minha biblioteca ({len(S.biblioteca)})")
        for b in list(reversed(S.biblioteca)):
            with st.expander(f"{b['canal']} · {b['texto'][:60]}…"):
                st.code(b["texto"], language=None, wrap_lines=True)
                if st.button("🗑️ Remover", key=f"rm_bib_{b['id']}"):
                    S.biblioteca = [x for x in S.biblioteca if x["id"] != b["id"]]
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# 4. DISPARO ASSISTIDO
# ══════════════════════════════════════════════════════════════════════════
with abas[3]:
    st.markdown("### 📲 Disparo assistido no WhatsApp")
    st.markdown("""<div class="bom">✅ <b>Como funciona:</b> o app prepara a mensagem de cada contato (com o nome e o seu link). Você clica em
    <b>Abrir no WhatsApp</b>, aperta <b>enviar</b> e marca <b>Enviei</b>. É rápido e o seu número continua seguro.</div>""", unsafe_allow_html=True)
    sem_link_aviso()
    with st.expander("➕ Adicionar contatos", expanded=not S.contatos):
        t_cont = st.text_area("Um contato por linha: Nome; telefone", key=f"t_cont_{V}", height=140,
                              placeholder="Ana Souza; 11 98888-7777\nCarlos; (21) 97777-6666\n31966665555")
        arq_c = st.file_uploader("…ou envie uma planilha .csv (colunas nome e telefone)", type=["csv"], key=f"up_cont_{V}")
        consent = st.checkbox("Confirmo que são pessoas que me conhecem e que não compraram esta lista.", key=f"c_cons_{V}")
        if st.button("Adicionar à lista", type="primary", key="b_add_cont"):
            novos = ler_contatos(t_cont) + (ler_csv_contatos(arq_c) if arq_c else [])
            if not consent:
                st.warning("Marque a confirmação acima.")
            elif not novos:
                st.warning("Não encontrei telefones válidos. Use DDD + número (ex.: 11 98888-7777).")
            else:
                existentes = {c["telefone"] for c in S.contatos}
                add = [c for c in novos if c["telefone"] not in existentes and not existentes.add(c["telefone"])]
                for c in add:
                    S.contatos.append({"id": novo_id(), "nome": c["nome"], "telefone": c["telefone"], "status": "pendente", "enviado_em": "", "obs": ""})
                S.ver += 1
                st.success(f"{len(add)} contato(s) adicionado(s)." + (f" {len(novos) - len(add)} repetido(s) ignorado(s)." if len(novos) > len(add) else ""))
                st.rerun()
    if S.contatos:
        rc = resumo_contatos()
        hoje_n = enviados_hoje()
        c1, c2 = st.columns([3, 2])
        c1.markdown(" · ".join(f"{STATUS[k][0]}: **{v}**" for k, v in rc.items()))
        c2.progress(min(1.0, hoje_n / LIMITE_DIA), text=f"Hoje: {hoje_n} de {LIMITE_DIA} envios recomendados")
        if hoje_n >= LIMITE_DIA:
            st.markdown(f"""<div class="aviso">⏸️ Você já fez {hoje_n} envios hoje. Para proteger seu número, continue amanhã
            (ou poste no Status, que não tem limite).</div>""", unsafe_allow_html=True)
        fonte_txt = f"{len(S.variacoes)} textos da IA (alternando)" if S.variacoes else "textos do kit pronto (alternando)"
        st.caption(f"Mensagens usadas: {fonte_txt}. Para trocar, crie mensagens em ✨ Mensagens com IA → “Usar TODAS no disparo assistido”.")
        filtro = st.radio("Mostrar", ["A enviar", "Enviados", "Todos"], horizontal=True, key=f"r_filtro_{V}")
        lista = [c for c in S.contatos if (filtro == "Todos") or (filtro == "A enviar" and c["status"] == "pendente")
                 or (filtro == "Enviados" and c["status"] not in ("pendente",))]
        por_pag = 15
        pags = max(1, (len(lista) + por_pag - 1) // por_pag)
        pag = st.number_input("Página", 1, pags, 1, key=f"n_pag_{filtro}_{V}") if pags > 1 else 1
        for c in lista[(pag - 1) * por_pag: pag * por_pag]:
            i = S.contatos.index(c)
            msg = texto_para(c, i)
            with st.container(border=True):
                l1, l2, l3 = st.columns([3, 2, 2])
                l1.markdown(f"**{html.escape(c['nome'] or 'Sem nome')}** · +{c['telefone']} &nbsp; {chip(STATUS[c['status']][1], STATUS[c['status']][0])}",
                            unsafe_allow_html=True)
                with l1.expander("Ver mensagem"):
                    st.write(msg)
                if c["status"] != "nao_quer":
                    l2.link_button("📲 Abrir no WhatsApp", link_whats(c["telefone"], msg), width="stretch")
                if c["status"] == "pendente":
                    if l3.button("✅ Enviei", key=f"env_{c['id']}", width="stretch"):
                        c["status"], c["enviado_em"] = "enviado", datetime.now().isoformat(timespec="minutes")
                        st.rerun()
                else:
                    opcoes = list(STATUS)
                    novo = l3.selectbox("Situação", opcoes, index=opcoes.index(c["status"]), format_func=lambda k: STATUS[k][0],
                                        key=f"st_{c['id']}_{V}", label_visibility="collapsed")
                    if novo != c["status"]:
                        c["status"] = novo
                        if novo == "comprou":
                            st.toast("🎉 Parabéns! Registre a venda em 📈 Resultados.")
                        st.rerun()
        with st.expander("🧹 Limpar lista"):
            if st.button("Apagar todos os contatos", key="b_limpa_cont"):
                S.contatos = []
                S.ver += 1
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# 5. CALENDÁRIO DE STATUS
# ══════════════════════════════════════════════════════════════════════════
CAL_PADRAO = [
    ("Curiosidade", "Sabia que dá pra ter personal, nutricionista e consultor financeiro com IA, por R$ {preco} uma vez só? 🤖", "18 especialistas de IA no seu bolso"),
    ("Bastidor", "Hoje pedi pro meu agente de treino montar minha semana. Em 1 minuto tava pronto 💪", "Seu treino pronto em 1 minuto"),
    ("Oferta", "R$ {preco}. Sem mensalidade. Acesso vitalício. 18 agentes de IA. Me chama que eu te mando o link 👇", "Pague uma vez. Use para sempre."),
    ("Pergunta", "Se você tivesse um especialista 24h pra UMA área da sua vida, qual seria? 🤔", "Qual área da sua vida precisa de ajuda?"),
    ("Bônus", "Quem garante hoje leva 3 bônus: robô de automações, agente novo toda semana e programa de afiliados 🎁", "Comprando hoje você ganha 3 bônus"),
    ("Prova", "Usei o agente de finanças pra organizar meus gastos do mês. Achei R$ 300 que eu nem via indo embora 😮", "Organize suas finanças com IA"),
    ("Chamada", "Últimos dias com os bônus! Quem quiser o link é só me chamar aqui 📲", "Me chama e eu te mando o link"),
]

with abas[4]:
    st.markdown("### 📅 Calendário de Status")
    st.caption("Status é a divulgação mais segura do WhatsApp: todos os seus contatos veem e você não manda mensagem para ninguém.")
    s1, s2, s3 = st.columns([2, 1, 1])
    dias_cal = s2.selectbox("Quantos dias?", [7, 14, 30], index=2, key=f"s_dias_{V}")
    if s1.button("✨ Criar meu calendário com IA", type="primary", key="b_cal_ia"):
        prompt = (f"{contexto_produto()}\n\nCrie um calendário de {dias_cal} dias de Status do WhatsApp para divulgar o produto, "
                  "alternando tipos (curiosidade, bastidor, oferta, pergunta, bônus, prova/uso real, chamada para ação, dica útil). "
                  "Cada texto com até 200 caracteres. 'arte' é um título curto (até 7 palavras, sem emoji) para a imagem do dia. "
                  "Não coloque o link no texto (no Status a pessoa chama no privado). Responda em JSON: "
                  "{\"dias\": [{\"tipo\": \"...\", \"texto\": \"...\", \"arte\": \"...\"}]}")
        with st.spinner("Montando seu calendário…"):
            d = rodar(ia_json, prompt)
        if d and d.get("dias"):
            S.calendario = [{"dia": i + 1, "tipo": str(x.get("tipo", "")), "texto": str(x.get("texto", "")), "arte": str(x.get("arte", "")), "postado": False}
                            for i, x in enumerate(d["dias"][:dias_cal])]
            S.ver += 1
            st.rerun()
    if s3.button("📋 Usar modelo pronto", key="b_cal_pad"):
        S.calendario = [{"dia": i + 1, "tipo": CAL_PADRAO[i % 7][0], "texto": preencher(CAL_PADRAO[i % 7][1]), "arte": CAL_PADRAO[i % 7][2], "postado": False}
                        for i in range(dias_cal)]
        S.ver += 1
        st.rerun()
    if S.calendario:
        feitos = sum(1 for d in S.calendario if d.get("postado"))
        st.progress(feitos / len(S.calendario), text=f"{feitos} de {len(S.calendario)} dias postados")
        prox = next((d for d in S.calendario if not d.get("postado")), None)
        for d in S.calendario:
            with st.expander(f"{'✅' if d.get('postado') else '📅'} Dia {d['dia']} · {d['tipo']}", expanded=(d is prox)):
                st.code(preencher(d["texto"]), language=None, wrap_lines=True)
                x1, x2 = st.columns([1, 1])
                if x1.button("🎨 Gerar a arte do dia", key=f"arte_dia_{d['dia']}"):
                    S[f"_arte_dia_{d['dia']}"] = arte(d.get("arte") or d["tipo"], "", "MEUS AGENTES", S.prog["preco"],
                                                      "Me chama para receber o link", "Story / Status (1080×1920)", True)
                if S.get(f"_arte_dia_{d['dia']}"):
                    x1.image(S[f"_arte_dia_{d['dia']}"], width=220)
                    x1.download_button("⬇️ Baixar arte", data=S[f"_arte_dia_{d['dia']}"], file_name=f"status_dia_{d['dia']}.png",
                                       mime="image/png", key=f"dl_arte_dia_{d['dia']}")
                marcado = x2.checkbox("Postei este Status", value=bool(d.get("postado")), key=f"cb_post_{d['dia']}_{V}")
                if marcado != bool(d.get("postado")):
                    d["postado"] = marcado
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# 6. MINHA PÁGINA
# ══════════════════════════════════════════════════════════════════════════
with abas[5]:
    st.markdown("### 🧲 Minha página de vendas")
    st.caption("Uma página pronta, bonita no celular, com o SEU link no botão. Coloque na bio do Instagram e nas mensagens.")
    sem_link_aviso()
    p1, p2 = st.columns(2)
    S.pagina["titulo"] = p1.text_input("Título da página", value=S.pagina.get("titulo") or "18 especialistas de IA no seu bolso", key=f"t_pg_tit_{V}")
    S.pagina["youtube"] = p2.text_input("Vídeo do YouTube (opcional)", value=S.pagina.get("youtube", ""), key=f"t_pg_yt_{V}",
                                        placeholder="https://youtube.com/watch?v=...")
    pg_html = pagina_html()
    if st.download_button("⬇️ Baixar minha página (.html)", data=pg_html.encode("utf-8"), file_name="minha_pagina_meus_agentes.html",
                          mime="text/html", type="primary"):
        S["_pagina_baixada"] = True
    st.markdown("""**Para colocar no ar (grátis, 1 minuto):** abra **[app.netlify.com/drop](https://app.netlify.com/drop)**, arraste o arquivo
    baixado para a página e copie o endereço que aparecer. Pronto: é o link para a sua bio.""")
    with st.expander("👀 Ver como ficou", expanded=True):
        if hasattr(st, "iframe"):
            st.iframe(pg_html, height=900)
        else:
            st.components.v1.html(pg_html, height=900, scrolling=True)


# ══════════════════════════════════════════════════════════════════════════
# 7. RESULTADOS
# ══════════════════════════════════════════════════════════════════════════
with abas[6]:
    st.markdown("### 📈 Resultados e carteira")
    st.caption("Copie da plataforma de afiliados os números do dia. O valor oficial é sempre o da plataforma; aqui é a sua estimativa.")
    fv = S.get("form_res_v", 0)
    r1, r2, r3, r4 = st.columns([1, 1, 1, 2])
    d_res = r1.date_input("Dia", value=HOJE, format="DD/MM/YYYY", key=f"d_res_{fv}")
    cl = r2.number_input("Cliques", min_value=0, step=1, key=f"n_cl_{fv}")
    vd = r3.number_input("Vendas", min_value=0, step=1, key=f"n_vd_{fv}")
    ob = r4.text_input("Observação (opcional)", key=f"t_ob_{fv}", placeholder="ex.: postei o vídeo no Status")
    if st.button("💾 Registrar", type="primary", key="b_res"):
        S.resultados = [r for r in S.resultados if r["data"] != d_res.isoformat()]
        S.resultados.append({"id": novo_id(), "data": d_res.isoformat(), "cliques": int(cl), "vendas": int(vd), "obs": ob})
        S["form_res_v"] = fv + 1
        st.rerun()
    c = carteira()
    m = st.columns(4)
    for col, (rot, val, sub) in zip(m, [("Carteira estimada", brl(c["saldo"]), "bônus + comissões"), ("Comissões", brl(c["comissoes"]), f"{c['vendas']} venda(s)"),
                                         ("Cliques", c["cliques"], "no seu link"), ("Conversão", f"{c['conversao']:.1f}%", "vendas ÷ cliques")]):
        col.markdown(f'<div class="metrica"><b>{val}</b>{rot}<br><small>{sub}</small></div>', unsafe_allow_html=True)
    if S.resultados:
        df = pd.DataFrame(sorted(S.resultados, key=lambda r: r["data"]))
        df["Dia"] = pd.to_datetime(df["data"])
        df["Carteira"] = float(S.prog["bonus_inicial"]) + df["vendas"].cumsum() * float(S.prog["comissao"])
        graf = alt.Chart(df).mark_area(line={"color": "#16A34A"}, color=alt.Gradient(gradient="linear", stops=[
            alt.GradientStop(color="#DCFCE7", offset=0), alt.GradientStop(color="#16A34A", offset=1)], x1=1, x2=1, y1=1, y2=0)).encode(
            x=alt.X("Dia:T", title=None, axis=alt.Axis(format="%d/%m")), y=alt.Y("Carteira:Q", title="Carteira (R$)"),
            tooltip=[alt.Tooltip("Dia:T", format="%d/%m/%Y"), "cliques", "vendas", alt.Tooltip("Carteira:Q", format=",.2f")]).properties(height=260)
        st.altair_chart(graf, width="stretch")
        tab = df[["data", "cliques", "vendas", "obs"]].copy()
        tab["data"] = pd.to_datetime(tab["data"]).dt.strftime("%d/%m/%Y")
        st.dataframe(tab.rename(columns={"data": "Dia", "cliques": "Cliques", "vendas": "Vendas", "obs": "Observação"}).iloc[::-1],
                     width="stretch", hide_index=True)
    st.markdown("#### 🎯 Minha meta")
    g1, g2 = st.columns(2)
    meta = g1.number_input("Quanto quero ter na carteira? (R$)", min_value=0.0, value=500.0, step=50.0, key=f"n_meta_{V}")
    falta = max(0.0, meta - c["saldo"])
    com = float(S.prog["comissao"]) or 1
    vendas_falta = int(-(-falta // com))
    conv = (c["conversao"] / 100) if c["conversao"] else 0.03
    g2.markdown(f"""<div class="card">Faltam <b>{brl(falta)}</b> → <b>{vendas_falta}</b> venda(s).<br>
    Com {'a sua conversão' if c['conversao'] else 'uma conversão de 3%'} ({conv * 100:.1f}%), isso dá uns <b>{int(vendas_falta / conv) if conv else 0}</b> cliques no seu link.</div>""",
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# 8. RELATÓRIO
# ══════════════════════════════════════════════════════════════════════════
with abas[7]:
    st.markdown("### 📑 Relatório e exportação")
    agora = datetime.now().strftime("%Y%m%d_%H%M")
    e1, e2, e3 = st.columns(3)
    e1.download_button("📄 Relatório (.txt)", data=relatorio_txt().encode("utf-8"), file_name=f"afiliado_relatorio_{agora}.txt", mime="text/plain", width="stretch")
    e2.download_button("📊 Relatório (Excel)", data=relatorio_xlsx(), file_name=f"afiliado_relatorio_{agora}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
    e3.download_button("💾 Minha memória (.json)", data=memoria_json(), file_name=f"afiliado_memoria_{agora}.json", mime="application/json", width="stretch")
    with st.expander("👀 Ver o relatório"):
        st.text(relatorio_txt())

mostrar_guia()
st.markdown(f'<div class="rodape">Ganhos dependem das vendas feitas pelo seu link; os valores oficiais são os da plataforma de afiliados.<br>'
            f'© 2026 <a href="{SITE}" target="_blank" style="color:#9C94B0;">MeusAgentesIA.com.br</a></div>', unsafe_allow_html=True)

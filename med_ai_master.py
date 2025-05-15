import streamlit as st
import openai
from fpdf import FPDF
from PIL import Image
from io import BytesIO

# ========== CONFIGURAÇÃO VISUAL ========== #
st.set_page_config(page_title="med.ai — Inteligência Médica", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="css"] {
        background-color: #111;
        color: #eee;
    }
    .title { font-size: 42px; font-weight: bold; color: #2ECC71; text-align: center; }
    .subtitle { font-size: 20px; color: #58D68D; text-align: center; margin-bottom: 30px; }
    .stTextArea textarea { font-size: 16px; border-radius: 12px; }
    .stButton>button {
        background-color: #2ECC71;
        color: white;
        font-size: 16px;
        padding: 8px 20px;
        border-radius: 8px;
        margin: 5px;
    }
    .stButton>button:hover {
        background-color: #28B463;
    }
    </style>
""", unsafe_allow_html=True)

# ========== LOGO E TÍTULOS ==========
if "start" not in st.session_state:
    st.session_state.start = False

if not st.session_state.start:
    st.image("logo_medai.png", width=160)
    st.markdown("<div class='title'>med.ai</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Sua inteligência médica especializada</div>", unsafe_allow_html=True)
    st.markdown("""
    ### 👋 Bem-vindo ao med.ai
    Escolha sua especialidade, descreva seus sintomas e receba orientação da IA.
    
    *Este aplicativo não substitui um médico real.*
    """)
    if st.button("Começar consulta"):
        st.session_state.start = True
    st.stop()

# ========== ESTADOS ==========
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat Principal": []}
if "chat_atual" not in st.session_state:
    st.session_state.chat_atual = "Chat Principal"
if "especialidade" not in st.session_state:
    st.session_state.especialidade = "Clínica Geral"
if "imagem_bytes" not in st.session_state:
    st.session_state.imagem_bytes = None

especialidades = [
    "Clínica Geral", "Pneumologia", "Oftalmologia", "Angiologia", "Cardiologia", "Neurologia",
    "Ortopedia", "Ginecologia", "Dermatologia", "Gastroenterologia", "Psiquiatria",
    "Endocrinologia", "Urologia", "Infectologia", "Reumatologia", "Nefrologia",
    "Otorrinolaringologia", "Pediatria", "Oncologia", "Nutrologia"
]

client = openai.OpenAI(api_key="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")

# ========== LAYOUT PRINCIPAL ==========
st.selectbox("Especialidade Médica:", especialidades, key="especialidade")
st.file_uploader("📎 Anexar imagem (exame, machucado, etc):", type=["png", "jpg", "jpeg"], key="imagem", on_change=lambda: st.session_state.update({"imagem_bytes": st.session_state.imagem.read() if st.session_state.imagem else None}))

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🧹 Limpar conversa"):
        st.session_state.chats[st.session_state.chat_atual] = []
        st.rerun()
with col2:
    if st.button("🚑 Emergência"):
        st.warning("Se estiver com falta de ar, dor no peito, desmaio, sangramento intenso ou febre alta persistente, procure um hospital imediatamente.")
with col3:
    if st.button("📄 Gerar PDF"):
        if st.session_state.chats[st.session_state.chat_atual]:
            ultima = st.session_state.chats[st.session_state.chat_atual][-1]["content"]
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, f"med.ai - Resposta da IA\n\n{ultima}")
            pdf_data = pdf.output(dest='S').encode('latin-1')
            st.download_button("Clique para baixar PDF", data=pdf_data, file_name="medai_consulta.pdf")
        else:
            st.warning("Nenhuma resposta ainda.")

# ========== CONTEXTO DA CONVERSA ==========
if not st.session_state.chats[st.session_state.chat_atual]:
    system_msg = f"Você é a med.ai, uma IA médica. Seja simpática, clara e fóque na especialidade: {st.session_state.especialidade}."
    st.session_state.chats[st.session_state.chat_atual].append({"role": "system", "content": system_msg})

for msg in st.session_state.chats[st.session_state.chat_atual][1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

pergunta = st.chat_input("Descreva seus sintomas...")

if pergunta:
    st.chat_message("user").markdown(pergunta)
    st.session_state.chats[st.session_state.chat_atual].append({"role": "user", "content": pergunta})

    mensagens = st.session_state.chats[st.session_state.chat_atual]
    if st.session_state.imagem_bytes:
        mensagens.append({"role": "user", "content": "O paciente anexou uma imagem para consideração médica."})

    with st.spinner("💬 A med.ai está analisando sua situação..."):
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=mensagens,
            temperature=0.7
        )

    conteudo = resposta.choices[0].message.content
    st.chat_message("assistant").markdown(conteudo)
    st.session_state.chats[st.session_state.chat_atual].append({"role": "assistant", "content": conteudo})



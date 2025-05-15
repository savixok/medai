import streamlit as st
import openai
from fpdf import FPDF
from io import BytesIO
from PIL import Image
from datetime import datetime

# Chave da API OpenAI
client = openai.OpenAI(api_key="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")

st.set_page_config(page_title="med.ai — Inteligência Médica", layout="wide", page_icon="🧠")

# CSS Estético Moderno
st.markdown("""
<style>
html, body, .stApp {
    background: linear-gradient(120deg, #e8f5f5, #f7f9fc);
    font-family: 'Segoe UI', sans-serif;
}
.title-container {
    text-align: center;
    padding: 30px;
}
.title {
    font-size: 50px;
    font-weight: 800;
    color: #2C3E50;
    text-shadow: 1px 1px 3px #BDC3C7;
}
.subtitle {
    font-size: 22px;
    color: #117864;
    margin-bottom: 20px;
}
.box {
    background: white;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}
.stButton > button {
    background-color: #1F618D;
    color: white;
    font-weight: 600;
    padding: 10px 30px;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# Título
st.markdown("<div class='title-container'><div class='title'>med.ai</div><div class='subtitle'>Seu assistente de saúde com inteligência artificial</div></div>", unsafe_allow_html=True)

# Menu lateral
st.sidebar.header("⚙️ Configurações")
especialidade = st.sidebar.selectbox("Área médica:", ["Clínica Geral", "Nutrição", "Pneumologia", "Oftalmologia", "Angiologia", "Cardiologia", "Dermatologia", "Ginecologia", "Psiquiatria", "Pediatria"])
modo_escuro = st.sidebar.toggle("🌙 Modo escuro")

if modo_escuro:
    st.markdown("""
        <style>
        body, .stApp {
            background-color: #111;
            color: white;
        }
        .box {
            background-color: #1e1e1e;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

# Histórico de conversas
if "historico" not in st.session_state:
    st.session_state.historico = []

# Entrada do usuário
with st.container():
    st.markdown("### 📝 Descreva seus sintomas ou dúvidas")
    sintomas = st.text_area("Exemplo: 'Estou com tosse e falta de ar'", height=120)
    imagem = st.file_uploader("📎 Anexar imagem (opcional)", type=["jpg", "jpeg", "png"])

    if st.button("💬 Consultar a med.ai"):
        with st.spinner("⏳ Gerando resposta médica..."):
            prompt = f"""
Você é med.ai, uma IA médica especialista em {especialidade}.
Responda com empatia, clareza e base científica.
Inclua hipóteses, medicamentos comuns (sem receita), cuidados em casa e quando ir ao hospital.

Sintomas: {sintomas}
"""
            try:
                resposta = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                conteudo = resposta.choices[0].message.content
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
                st.session_state.historico.append((timestamp, sintomas, conteudo))
                st.success("✅ Resposta gerada com sucesso!")
                st.markdown("#### 📋 Resposta:")
                st.write(conteudo)

                if st.button("📄 Baixar PDF"):
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.multi_cell(0, 10, f"Consulta med.ai - {timestamp}\n\nSintomas: {sintomas}\n\nResposta:\n{conteudo}")
                    buffer = BytesIO()
                    pdf.output(buffer)
                    st.download_button("📎 Download da Consulta", data=buffer.getvalue(), file_name="consulta_medai.pdf")

            except Exception as e:
                st.error(f"Erro: {e}")

# Histórico
st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 Histórico")
for i, (time, sint, resp) in enumerate(reversed(st.session_state.historico[-5:])):
    with st.sidebar.expander(f"🕓 {time}"):
        st.markdown(f"**Sintomas:** {sint}")
        st.markdown(f"**Resposta:** {resp[:100]}...")

# Emergência
if st.sidebar.button("🚨 Emergência Médica"):
    st.sidebar.warning("Vá ao hospital se tiver:")
    st.sidebar.markdown("- Falta de ar\n- Dor no peito\n- Desmaios\n- Febre acima de 39°C\n- Vômitos constantes")

# Limpar
if st.sidebar.button("🧹 Limpar Histórico"):
    st.session_state.historico.clear()
    st.experimental_rerun()



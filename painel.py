# painel.py — JMA Consultoria (versão 2.3-L final - tema claro e independente)
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

# -----------------------------
# CONFIGURAÇÃO GERAL
# -----------------------------
st.set_page_config(
    page_title="Painel JMA Consultoria",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# CORES / TEMA CLARO
# -----------------------------
COR_PRINCIPAL = "#1f4e79"
COR_SECUNDARIA = "#6c757d"
COR_FUNDO = "#FFFFFF"
COR_TEXTO = "#1a1a1a"
COR_ALERTA = "#d9534f"
COR_SUCESSO = "#28a745"

# -----------------------------
# CSS
# -----------------------------
st.markdown(f"""
<style>
body {{
    background-color: {COR_FUNDO};
    color: {COR_TEXTO};
}}
.metric-container {{
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 14px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    margin-bottom: 12px;
    text-align: center;
    font-size: 16px;
}}
.metric-title {{
    font-size:14px;
    font-weight:bold;
    color: #444;
    margin-bottom:6px;
}}
.metric-value {{
    font-size:20px;
    font-weight:600;
}}
.small-caption {{
    color: #6c757d;
    font-size:16px;
}}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOGO E TÍTULO
# -----------------------------
logo_path = "logo_jma.png"
c1, c2, c3 = st.columns([1,2,1])
with c2:
    try:
        st.image(logo_path, width=150)
    except:
        pass
    st.markdown(f"<h1 style='color:{COR_PRINCIPAL}; text-align:center;'>Painel de Medições — JMA Consultoria</h1>", unsafe_allow_html=True)
st.markdown("---")

# -----------------------------
# GERAÇÃO AUTOMÁTICA DE DADOS
# -----------------------------
def criar_dados_simulados():
    np.random.seed(42)
    meses = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
    anos = [2023, 2024, 2025]
    dados = []
    for ano in anos:
        for i, mes in enumerate(meses, start=1):
            orcado = int(np.random.randint(400000, 800000))
            # diferenças fortes: 60% a 120% do orçado
            medido = float(orcado * np.random.uniform(0.6, 1.2))
            dados.append([ano, mes, i, orcado, medido])
    return pd.DataFrame(dados, columns=["ano","mes_abrev","mes","orcado","medido"])

df = criar_dados_simulados()

# -----------------------------
# PRÉ-PROCESSAMENTO
# -----------------------------
df["desvio_abs"] = df["medido"] - df["orcado"]
df["desvio_pct"] = (df["desvio_abs"] / df["orcado"]) * 100
df["data_ym"] = df["ano"].astype(str) + "-" + df["mes_abrev"].astype(str)

# -----------------------------
# FORMATAÇÃO
# -----------------------------
def formatar_real(valor):
    try:
        v = float(valor)
    except:
        return "R$ 0,00"
    s = f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s

def formatar_pct(valor):
    try:
        v = float(valor)
    except:
        return "0,00%"
    s = f"{v:+.2f}%".replace(".", ",")
    return s

def format_desvio_total(valor_pct):
    try:
        v = float(valor_pct)
    except:
        v = 0.0
    cor = COR_SUCESSO if v >= 0 else COR_ALERTA
    texto = formatar_pct(v)
    return texto, cor

# -----------------------------
# FILTROS (SIDEBAR)
# -----------------------------
st.sidebar.header("Filtros")

opcoes_graficos = st.sidebar.multiselect(
    "📊 Gráficos adicionais",
    options=["💰 Evolução Acumulada", "🌡️ Mapa de Calor"],
    default=["💰 Evolução Acumulada", "🌡️ Mapa de Calor"]
)

anos_disponiveis = sorted(df["ano"].unique())
ano_opcoes = ["Todos"] + anos_disponiveis
ano_sel = st.sidebar.selectbox("Ano", ano_opcoes, index=len(ano_opcoes)-1)

df_filtrado_ano = df.copy() if ano_sel=="Todos" else df[df["ano"]==ano_sel]

meses_ordenados = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
mes_opcoes = ["Todos"] + meses_ordenados
mes_sel = st.sidebar.multiselect("Meses", options=mes_opcoes, default=["Todos"])

df_filtrado = df_filtrado_ano.copy() if "Todos" in mes_sel or not mes_sel else df_filtrado_ano[df_filtrado_ano["mes_abrev"].isin(mes_sel)]
df_filtrado = df_filtrado.sort_values(["ano","mes"])

# -----------------------------
# KPIs
# -----------------------------
total_orcado = df_filtrado["orcado"].sum()
total_medido = df_filtrado["medido"].sum()
desvio = total_medido - total_orcado
desvio_pct_total = (desvio / total_orcado) * 100 if total_orcado else 0
maior_desvio = df_filtrado["desvio_pct"].max() if not df_filtrado.empty else 0
media_desvio = df_filtrado["desvio_pct"].mean() if not df_filtrado.empty else 0

desvio_texto, cor_card = format_desvio_total(desvio_pct_total)
cor_maior_desvio = COR_SUCESSO if maior_desvio >= 0 else COR_ALERTA

col1, col2, col3, col4 = st.columns([1,1,1,1])
col1.markdown(f"<div class='metric-container'>💰<div class='metric-title'>Total Orçado</div><div class='metric-value'>{formatar_real(total_orcado)}</div></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='metric-container'>📈<div class='metric-title'>Total Medido</div><div class='metric-value'>{formatar_real(total_medido)}</div></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='metric-container' style='color:{cor_card};'>📊<div class='metric-title'>Desvio Total (%)</div><div class='metric-value'>{desvio_texto}</div></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='metric-container' style='color:{cor_maior_desvio};'>🚨<div class='metric-title'>Maior Desvio (%)</div><div class='metric-value'>{formatar_pct(maior_desvio)}</div></div>", unsafe_allow_html=True)

st.markdown(f"<p class='small-caption' style='text-align:center;'>Média de Desvio Mensal: {formatar_pct(media_desvio)}</p>", unsafe_allow_html=True)
st.markdown("---")

# -----------------------------
# GRÁFICO PRINCIPAL
# -----------------------------
fig = make_subplots(specs=[[{"secondary_y": True}]])
cores_desvio = px.colors.qualitative.Plotly

if not df_filtrado.empty:
    for i, ano in enumerate(sorted(df_filtrado["ano"].unique())):
        df_ano = df_filtrado[df_filtrado["ano"]==ano]
        labels = [f"{m} ({ano})" for m in df_ano["mes_abrev"]]
        fig.add_trace(go.Bar(x=labels, y=df_ano["orcado"], name=f"Orçado {ano}", marker_color=COR_SECUNDARIA, opacity=0.8), secondary_y=False)
        fig.add_trace(go.Bar(x=labels, y=df_ano["medido"], name=f"Medido {ano}", marker_color=COR_PRINCIPAL, opacity=0.9), secondary_y=False)
        fig.add_trace(go.Scatter(x=labels, y=df_ano["desvio_pct"], mode="lines+markers", name=f"Desvio (%) {ano}", line=dict(color=cores_desvio[i%len(cores_desvio)], width=3)), secondary_y=True)

    fig.add_hline(y=0, line_dash="dot", line_color=COR_SECUNDARIA, annotation_text="Meta 0%", annotation_position="bottom right", secondary_y=True)
    fig.add_hline(y=media_desvio, line_dash="dot", line_color=COR_SUCESSO, annotation_text="Média", annotation_position="bottom right", secondary_y=True)

    fig.update_layout(
        title_text="Evolução Mensal — Orçado x Medido + Desvio (%)",
        barmode="group",
        plot_bgcolor=COR_FUNDO,
        paper_bgcolor=COR_FUNDO,
        font=dict(color=COR_TEXTO),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(l=40,r=40,t=80,b=40),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# GRÁFICOS OPCIONAIS
# -----------------------------
if "💰 Evolução Acumulada" in opcoes_graficos:
    st.markdown("### 💰 Evolução Acumulada — Orçado x Medido")
    df_acum = df_filtrado.sort_values(["ano","mes"])
    df_acum["orcado_acum"] = df_acum.groupby("ano")["orcado"].cumsum()
    df_acum["medido_acum"] = df_acum.groupby("ano")["medido"].cumsum()

    fig_area = go.Figure()
    fig_area.add_trace(go.Scatter(x=df_acum["data_ym"], y=df_acum["orcado_acum"], name="Orçado Acumulado", fill='tonexty', line_color=COR_SECUNDARIA))
    fig_area.add_trace(go.Scatter(x=df_acum["data_ym"], y=df_acum["medido_acum"], name="Medido Acumulado", fill='tonexty', line_color=COR_PRINCIPAL))
    fig_area.update_layout(
        yaxis_title="R$ Acumulado",
        xaxis_title="Mês/Ano",
        plot_bgcolor=COR_FUNDO,
        paper_bgcolor=COR_FUNDO,
        font=dict(color=COR_TEXTO),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_area, use_container_width=True)

if "🌡️ Mapa de Calor" in opcoes_graficos:
    st.markdown("### 🌡️ Mapa de Calor — Desvio (%) por Ano e Mês")
    pivot = df_filtrado.pivot_table(index="ano", columns="mes_abrev", values="desvio_pct", aggfunc="mean")
    fig_heat = px.imshow(pivot, text_auto=".1f", color_continuous_scale="RdYlGn", aspect="auto")
    fig_heat.update_layout(
        title="Desvio Percentual Médio por Ano e Mês",
        plot_bgcolor=COR_FUNDO,
        paper_bgcolor=COR_FUNDO,
        font=dict(color=COR_TEXTO)
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# -----------------------------
# TABELA DETALHADA
# -----------------------------
st.markdown("### 📋 Detalhamento Mensal")

def gerar_tabela_plotly(df):
    if df.empty:
        st.warning("Nenhum dado disponível para o filtro selecionado.")
        return
    df_exibir = df[["ano","mes_abrev","orcado","medido","desvio_abs","desvio_pct"]].copy()
    df_exibir.rename(columns={
        "ano":"Ano", "mes_abrev":"Mês", "orcado":"Orçado (R$)",
        "medido":"Medido (R$)", "desvio_abs":"Diferença (R$)", "desvio_pct":"Desvio (%)"
    }, inplace=True)
    dif_cor = np.where(df_exibir["Diferença (R$)"] >= 0, COR_SUCESSO, COR_ALERTA)
    desvio_cor = np.where(df_exibir["Desvio (%)"] >= 0, COR_SUCESSO, COR_ALERTA)
    df_exibir["Orçado (R$)"] = df_exibir["Orçado (R$)"].map(formatar_real)
    df_exibir["Medido (R$)"] = df_exibir["Medido (R$)"].map(formatar_real)
    df_exibir["Diferença (R$)"] = df_exibir["Diferença (R$)"].map(formatar_real)
    df_exibir["Desvio (%)"] = df_exibir["Desvio (%)"].map(lambda x: formatar_pct(x))
    fill_colors = [['white']*len(df_exibir)]*len(df_exibir.columns)
    font_colors = [['black']*len(df_exibir)]*4 + [dif_cor, desvio_cor]
    align = ['center','center','right','right','right','right']
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df_exibir.columns), fill_color=COR_PRINCIPAL, font=dict(color='white', size=13)),
        cells=dict(values=[df_exibir[c] for c in df_exibir.columns], fill_color=fill_colors, font=dict(color=font_colors, size=14), align=align)
    )])
    st.plotly_chart(fig, use_container_width=True)
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Exportar CSV", data=csv_bytes, file_name="medicoes_filtradas.csv", mime="text/csv")

gerar_tabela_plotly(df_filtrado)

# -----------------------------
# RODAPÉ
# -----------------------------
st.markdown("---")
st.caption(f"Atualizado em {datetime.now():%d/%m/%Y %H:%M}")
st.caption("© 2025 JMA Consultoria — Painel desenvolvido em Streamlit + Plotly")

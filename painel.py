# painel.py — Versão final JMA Consultoria com logo, paleta e views SQL friendly
import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
from pathlib import Path

# ---------------- Configurável (paleta institucional) ----------------
PALETTE = {
    "background": "#f6f8fb",
    "card": "#ffffff",
    "muted": "#6b7280",
    "primary": "#0d47a1",
    "accent": "#1565c0",
    "success": "#2e7d32",
    "warn": "#ff6f00",
    "text": "#212121"
}

LOGO_FILE = "jma_logo.svg"  # deixar na mesma pasta do painel.py

# ---------------- Streamlit page config ----------------
st.set_page_config(
    page_title="JMA Consultoria — Painel Financeiro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- Estilo (usa a paleta) ----------------
st.markdown(f"""
    <style>
        :root {{
            --bg: {PALETTE['background']};
            --card: {PALETTE['card']};
            --muted: {PALETTE['muted']};
            --primary: {PALETTE['primary']};
            --accent: {PALETTE['accent']};
            --success: {PALETTE['success']};
            --warn: {PALETTE['warn']};
            --text: {PALETTE['text']};
        }}
        body {{background-color: var(--bg);}}
        .header {{
            background: linear-gradient(90deg, #08306b 0%, var(--primary) 100%);
            padding: 14px 18px;
            color: white;
            border-radius: 8px;
            margin-bottom: 14px;
            font-family: "Helvetica", Arial, sans-serif;
            box-shadow: 0 6px 18px rgba(13,71,161,0.06);
            display:flex;
            align-items:center;
            gap:14px;
        }}
        .header .title {{
            font-size:18px; font-weight:700; margin:0;
        }}
        .header .subtitle {{font-size:12px; margin:0; opacity:0.95}}
        .metric {{
            background: var(--card);
            padding: 12px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(16,24,40,0.04);
        }}
        .small {{font-size:12px; color:var(--muted);}}
        .logo-img {{height:44px;}}
        .footer {{text-align:center; font-size:12px; color:var(--muted); margin-top:18px;}}
        /* sidebar width */
        .css-1d391kg {{min-width:260px;}}
    </style>
""", unsafe_allow_html=True)

# ---------------- Header (logo se existir) ----------------
logo_path = Path(LOGO_FILE)
if logo_path.exists():
    # exibir logo + textos
    logo_html = f'''
    <div class="header">
      <img src="data:image/svg+xml;utf8,{logo_path.read_text(encoding='utf-8')}" class="logo-img" />
      <div>
        <div class="title">JMA Consultoria — Painel Financeiro de Medições</div>
        <div class="subtitle">Visão executiva • Controle de medições, custos e performance</div>
      </div>
    </div>
    '''
else:
    # fallback sem imagem
    logo_html = '''
    <div class="header">
      <div style="margin-left:8px;">
        <div class="title">JMA Consultoria — Painel Financeiro de Medições</div>
        <div class="subtitle">Visão executiva • Controle de medições, custos e performance</div>
      </div>
    </div>
    '''
st.markdown(logo_html, unsafe_allow_html=True)

# ---------------- Carregar dados ----------------
DB = "medicoes.db"
con = sqlite3.connect(DB)
df = pd.read_sql_query("SELECT * FROM medicoes", con)
con.close()

# ---------------- Normalizações ----------------
# mes abreviado
if df['mes'].dtype not in [object, 'O']:
    meses_map = {1:"Jan",2:"Fev",3:"Mar",4:"Abr",5:"Mai",6:"Jun",7:"Jul",8:"Ago",9:"Set",10:"Out",11:"Nov",12:"Dez"}
    df['mes_abrev'] = df['mes'].map(meses_map)
else:
    df['mes_abrev'] = df['mes'].astype(str)

df['mes_abrev'] = pd.Categorical(df['mes_abrev'],
                                 categories=["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"],
                                 ordered=True)

# coluna data (ano-mes)
if 'ano' in df.columns:
    df['data_ym'] = df['ano'].astype(str) + "-" + df['mes_abrev'].astype(str)
else:
    df['data_ym'] = df['mes_abrev'].astype(str)

# detectar/renomear colunas de valores se necessário
renames = {}
for c in df.columns:
    cl = c.lower()
    if cl in ['valor_orcado','orcado','valor_orc','valor_orcamento','orcamento']:
        renames[c] = 'valor_orcado'
    if cl in ['valor_medido','medido','valor_med','valor_executado']:
        renames[c] = 'valor_medido'
if renames:
    df = df.rename(columns=renames)

# garantir colunas numéricas
if 'valor_orcado' not in df.columns:
    df['valor_orcado'] = 0.0
if 'valor_medido' not in df.columns:
    df['valor_medido'] = 0.0
df['valor_orcado'] = pd.to_numeric(df['valor_orcado'], errors='coerce').fillna(0.0)
df['valor_medido'] = pd.to_numeric(df['valor_medido'], errors='coerce').fillna(0.0)

# ---------------- Sidebar filtros ----------------
st.sidebar.header("Filtros")
anos = sorted(df['ano'].dropna().unique().astype(int)) if 'ano' in df.columns else []
if anos:
    anos_sel = st.sidebar.multiselect("Ano", anos, default=anos)
else:
    anos_sel = []

meses = [m for m in df['mes_abrev'].cat.categories if m in df['mes_abrev'].unique()]
mes_sel = st.sidebar.multiselect("Mês", meses, default=meses)

proj_exists = 'projeto' in df.columns
if proj_exists:
    projetos = sorted(df['projeto'].astype(str).unique())
    proj_sel = st.sidebar.multiselect("Projeto", projetos, default=projetos)
else:
    proj_sel = []

forn_exists = 'fornecedor' in df.columns
if forn_exists:
    fornecedores = sorted(df['fornecedor'].astype(str).unique())
    forn_sel = st.sidebar.multiselect("Fornecedor", fornecedores, default=fornecedores)
else:
    forn_sel = []

cat_exists = 'categoria' in df.columns
if cat_exists:
    categorias = sorted(df['categoria'].astype(str).unique())
    cat_sel = st.sidebar.multiselect("Categoria", categorias, default=categorias)
else:
    cat_sel = []

st.sidebar.markdown("---")
group_options = ['Mês (soma)', 'Projeto (soma)', 'Registro (detalhado)']
group_by = st.sidebar.selectbox("Modo visual", group_options, index=0)
if st.sidebar.button("Resetar filtros"):
    st.experimental_rerun()

# ---------------- Aplicar filtros ----------------
df_f = df.copy()
if anos_sel:
    df_f = df_f[df_f['ano'].isin(anos_sel)]
if mes_sel:
    df_f = df_f[df_f['mes_abrev'].isin(mes_sel)]
if proj_exists and proj_sel:
    df_f = df_f[df_f['projeto'].isin(proj_sel)]
if forn_exists and forn_sel:
    df_f = df_f[df_f['fornecedor'].isin(forn_sel)]
if cat_exists and cat_sel:
    df_f = df_f[df_f['categoria'].isin(cat_sel)]

# ---------------- Preparar df_chart conforme modo ----------------
if group_by == 'Mês (soma)':
    if 'ano' in df_f.columns:
        df_chart = df_f.groupby(['ano','mes_abrev']).agg({'valor_orcado':'sum','valor_medido':'sum'}).reset_index()
        df_chart = df_chart.sort_values(['ano','mes_abrev'])
        df_chart['data_ym'] = df_chart['ano'].astype(str) + "-" + df_chart['mes_abrev']
    else:
        df_chart = df_f.groupby(['mes_abrev']).agg({'valor_orcado':'sum','valor_medido':'sum'}).reset_index()
        df_chart = df_chart.sort_values('mes_abrev')
        df_chart['data_ym'] = df_chart['mes_abrev']
elif group_by == 'Projeto (soma)' and proj_exists:
    df_chart = df_f.groupby(['projeto']).agg({'valor_orcado':'sum','valor_medido':'sum'}).reset_index()
    df_chart['data_ym'] = df_chart['projeto']
else:
    df_chart = df_f.reset_index().rename(columns={'index':'registro'})
    df_chart['data_ym'] = df_chart.apply(lambda r: f"{r.get('ano','')}-{r.get('mes_abrev','')}", axis=1)

# ---------------- util: formatação BR ----------------
def fmt_br(x):
    try:
        return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return f"R$ {x}"

# ---------------- KPIs ----------------
total_orcado = df_f['valor_orcado'].sum()
total_medido = df_f['valor_medido'].sum()
desvio = total_medido - total_orcado
perc_exec = (total_medido / total_orcado * 100) if total_orcado != 0 else 0

k1,k2,k3,k4 = st.columns([2,2,2,2])
k1.metric("Total Orçado", fmt_br(total_orcado))
k2.metric("Total Medido", fmt_br(total_medido))
k3.metric("Desvio Absoluto", fmt_br(desvio))
perc_color = PALETTE['success'] if perc_exec >= 100 else "#b00020"
k4.markdown(f'<div class="metric" style="text-align:center;"><div style="font-size:12px;color:var(--muted)">Execução</div><div style="font-size:20px;font-weight:700; color:{perc_color}">{perc_exec:.1f}%</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ---------------- Gráfico colunas Orçado x Medido ----------------
fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(
    x=df_chart['data_ym'],
    y=df_chart['valor_orcado'],
    name='Orçado',
    marker_color=PALETTE['accent'],
    hovertemplate='%{x}<br>Orçado: R$ %{y:,.2f}<extra></extra>',
))
fig_bar.add_trace(go.Bar(
    x=df_chart['data_ym'],
    y=df_chart['valor_medido'],
    name='Medido',
    marker_color=PALETTE['success'],
    hovertemplate='%{x}<br>Medido: R$ %{y:,.2f}<extra></extra>',
))
fig_bar.update_layout(barmode='group', title='Orçado x Medido', xaxis_tickangle=-35,
                      plot_bgcolor='white', paper_bgcolor='white', legend=dict(orientation='h', y=-0.15),
                      margin=dict(t=60,b=40,l=40,r=20))
fig_bar.update_yaxes(tickformat=",.2f")

# ---------------- Gráfico linha diferença + acumulados ----------------
if {'valor_orcado','valor_medido'}.issubset(df_chart.columns):
    df_chart = df_chart.copy()
    df_chart['diferenca'] = df_chart['valor_medido'] - df_chart['valor_orcado']
    try:
        if 'ano' in df_chart.columns and 'mes_abrev' in df_chart.columns:
            df_chart = df_chart.sort_values(['ano','mes_abrev'])
    except:
        pass
    df_chart['acum_orcado'] = df_chart['valor_orcado'].cumsum()
    df_chart['acum_medido'] = df_chart['valor_medido'].cumsum()
else:
    df_chart['diferenca'] = 0
    df_chart['acum_orcado'] = 0
    df_chart['acum_medido'] = 0

fig_line = go.Figure()
fig_line.add_trace(go.Scatter(
    x=df_chart['data_ym'],
    y=df_chart['diferenca'],
    mode='lines+markers',
    name='Diferença (Medido − Orçado)',
    line=dict(color=PALETTE['warn'], width=3),
    marker=dict(size=6)
))
fig_line.add_trace(go.Scatter(
    x=df_chart['data_ym'],
    y=df_chart['acum_orcado'],
    mode='lines',
    name='Acum. Orçado',
    line=dict(color=PALETTE['accent'], width=2, dash='dash')
))
fig_line.add_trace(go.Scatter(
    x=df_chart['data_ym'],
    y=df_chart['acum_medido'],
    mode='lines',
    name='Acum. Medido',
    line=dict(color=PALETTE['success'], width=2)
))
fig_line.update_layout(title='Diferença e Acumulados', xaxis_tickangle=-35, legend=dict(orientation='h', y=-0.2),
                       plot_bgcolor='white', paper_bgcolor='white', margin=dict(t=60,b=40,l=40,r=20))
fig_line.update_yaxes(tickformat=",.2f")

# ---------------- Pizza participação por projeto ----------------
fig_pie = None
if 'projeto' in df_f.columns and not df_f.empty:
    df_pj = df_f.groupby('projeto').agg({'valor_orcado':'sum','valor_medido':'sum'}).reset_index().sort_values('valor_orcado', ascending=False)
    fig_pie = go.Figure(go.Pie(labels=df_pj['projeto'], values=df_pj['valor_orcado'], hole=0.45,
                               hovertemplate='%{label}<br>Orçado: R$ %{value:,.2f}<extra></extra>'))
    fig_pie.update_traces(textinfo='percent+label')
    fig_pie.update_layout(title='Participação no Orçado por Projeto', paper_bgcolor='white')

# ---------------- Top fornecedores ----------------
top_n = 10
if 'fornecedor' in df_f.columns:
    top_for = df_f.groupby('fornecedor').agg({'valor_medido':'sum','valor_orcado':'sum'}).reset_index()
    top_for = top_for.sort_values('valor_medido', ascending=False).head(top_n)
else:
    top_for = pd.DataFrame(columns=['fornecedor','valor_medido','valor_orcado'])

# ---------------- Layout exibição ----------------
c1, c2 = st.columns((2,2))
c1.plotly_chart(fig_bar, use_container_width=True)
c2.plotly_chart(fig_line, use_container_width=True)

st.markdown("---")
r1, r2 = st.columns((1,1))
if fig_pie:
    r1.plotly_chart(fig_pie, use_container_width=True)
r2.subheader(f"Top {top_n} Fornecedores (por Medido)")
if not top_for.empty:
    top_for_display = top_for.copy()
    top_for_display['Medido'] = top_for_display['valor_medido'].apply(lambda x: fmt_br(x))
    top_for_display['Orçado'] = top_for_display['valor_orcado'].apply(lambda x: fmt_br(x))
    r2.table(top_for_display[['fornecedor','Medido','Orçado']].rename(columns={'fornecedor':'Fornecedor'}))
else:
    r2.write("Sem dados de fornecedores.")

st.markdown("---")
st.subheader("Dados Detalhados (filtrados)")
st.dataframe(df_f.reset_index(drop=True).head(1000))

# ---------------- Downloads ----------------
def to_xlsx_bytes(df_input):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_input.to_excel(writer, index=False, sheet_name='dados')
        writer.save()
    return output.getvalue()

csv = df_f.to_csv(index=False, sep=';').encode('utf-8-sig')
st.download_button("Download CSV (filtrado)", data=csv, file_name="medicoes_filtradas.csv", mime="text/csv")
st.download_button("Download XLSX (filtrado)", data=to_xlsx_bytes(df_f), file_name="medicoes_filtradas.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ---------------- Insights ----------------
st.markdown("---")
st.subheader("Insights rápidos")
insights = []
if not df_f['valor_medido'].empty:
    med_mean = df_f['valor_medido'].mean()
    med_std = df_f['valor_medido'].std()
    lim = med_mean + 3*med_std
    outliers = df_f[df_f['valor_medido'] > lim]
    insights.append(f"{len(outliers)} registros com valor medido muito acima da média (possíveis outliers).")
if 'fornecedor' in df_f.columns:
    fornecedor_exec = df_f.groupby('fornecedor').agg({'valor_orcado':'sum','valor_medido':'sum'}).reset_index()
    fornecedor_exec['exec'] = fornecedor_exec['valor_medido'] / fornecedor_exec['valor_orcado']
    altas = fornecedor_exec[fornecedor_exec['exec'] > 1.2]
    insights.append(f"{len(altas)} fornecedores com execução > 120% do orçado.")
if insights:
    for it in insights:
        st.write("- " + it)
else:
    st.write("Sem insights automáticos para os filtros selecionados.")

# ---------------- Footer ----------------
st.markdown(f'<div class="footer">Desenvolvido por <strong>JMA Consultoria</strong> — Painel interativo</div>', unsafe_allow_html=True)

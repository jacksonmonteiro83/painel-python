from flask import Flask, render_template_string
import sqlite3
import pandas as pd
import plotly.express as px

app = Flask(__name__)

@app.route('/')
def dashboard():
    conn = sqlite3.connect('medicoes.db')
    df = pd.read_sql_query("SELECT * FROM controle_financeiro", conn)
    conn.close()

    total_orcado = df['valor_orcado'].sum()
    total_medido = df['valor_medido'].sum()
    percentual_execucao = (total_medido / total_orcado) * 100

    grafico = px.bar(df, x='mes', y=['valor_orcado', 'valor_medido'],
                     barmode='group', title='Orçado x Medido por Mês')

    grafico_html = grafico.to_html(full_html=False)

    html = f"""
    <html>
    <head>
        <title>Painel de Controle Financeiro</title>
        <style>
            body {{ font-family: Arial; background-color: #f8f9fa; text-align:center; }}
            .kpi {{ display:inline-block; background:#007bff; color:white;
                   padding:20px; margin:10px; border-radius:10px; width:200px; }}
            .valor {{ font-size:24px; font-weight:bold; }}
        </style>
    </head>
    <body>
        <h2>Painel de Controle Financeiro de Medições</h2>
        <div class="kpi"><div>Total Orçado</div><div class="valor">R$ {total_orcado:,.2f}</div></div>
        <div class="kpi"><div>Total Medido</div><div class="valor">R$ {total_medido:,.2f}</div></div>
        <div class="kpi"><div>Execução</div><div class="valor">{percentual_execucao:.1f}%</div></div>
        {grafico_html}
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)

# create_views.py
import sqlite3

DB = "medicoes.db"

views_sql = [
    # resumido por ano-mes
    ("""
    CREATE VIEW IF NOT EXISTS vw_mes_agg AS
    SELECT ano, mes AS mes_num, 
           CASE mes
             WHEN 1 THEN 'Jan' WHEN 2 THEN 'Fev' WHEN 3 THEN 'Mar' WHEN 4 THEN 'Abr'
             WHEN 5 THEN 'Mai' WHEN 6 THEN 'Jun' WHEN 7 THEN 'Jul' WHEN 8 THEN 'Ago'
             WHEN 9 THEN 'Set' WHEN 10 THEN 'Out' WHEN 11 THEN 'Nov' WHEN 12 THEN 'Dez'
           END as mes_abrev,
           SUM(valor_orcado) as total_orcado,
           SUM(valor_medido) as total_medido
    FROM medicoes
    GROUP BY ano, mes
    """),
    # resumido por projeto
    ("""
    CREATE VIEW IF NOT EXISTS vw_projeto_agg AS
    SELECT projeto, SUM(valor_orcado) as total_orcado, SUM(valor_medido) as total_medido
    FROM medicoes
    GROUP BY projeto
    """),
    # resumido por fornecedor
    ("""
    CREATE VIEW IF NOT EXISTS vw_fornecedor_agg AS
    SELECT fornecedor, SUM(valor_orcado) as total_orcado, SUM(valor_medido) as total_medido
    FROM medicoes
    GROUP BY fornecedor
    """)
]

conn = sqlite3.connect(DB)
cur = conn.cursor()
for v in views_sql:
    cur.execute(v)
conn.commit()
conn.close()
print("Views criadas/atualizadas com sucesso.")

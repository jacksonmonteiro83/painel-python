import sqlite3
import random
import pandas as pd

# Conectar/criar o banco
conn = sqlite3.connect('medicoes.db')
cursor = conn.cursor()

# Apagar tabela se já existir
cursor.execute("DROP TABLE IF EXISTS medicoes")

# Criar tabela principal
cursor.execute("""
CREATE TABLE medicoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ano INTEGER,
    mes INTEGER,
    projeto TEXT,
    fornecedor TEXT,
    categoria TEXT,
    valor_orcado REAL,
    valor_medido REAL
)
""")

# Dados base
anos = [2023, 2024, 2025]
meses = list(range(1, 13))
projetos = ['Projeto A', 'Projeto B', 'Projeto C', 'Projeto D', 'Projeto E']
fornecedores = ['Fornecedor 1', 'Fornecedor 2', 'Fornecedor 3', 'Fornecedor 4', 'Fornecedor 5',
                'Fornecedor 6', 'Fornecedor 7', 'Fornecedor 8', 'Fornecedor 9', 'Fornecedor 10']
categorias = ['Mão de obra', 'Materiais', 'Serviços', 'Equipamentos']

# Gerar registros sintéticos
registros = []
for ano in anos:
    for mes in meses:
        for projeto in projetos:
            for fornecedor in fornecedores:
                categoria = random.choice(categorias)
                valor_orcado = round(random.uniform(5000, 50000), 2)
                # Valor medido varia entre 80% e 120% do orçado
                valor_medido = round(valor_orcado * random.uniform(0.8, 1.2), 2)
                registros.append((ano, mes, projeto, fornecedor, categoria, valor_orcado, valor_medido))

# Inserir no banco
cursor.executemany("""
INSERT INTO medicoes (ano, mes, projeto, fornecedor, categoria, valor_orcado, valor_medido)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", registros)

conn.commit()
conn.close()

print(f"Banco criado e populado com {len(registros)} registros com sucesso!")

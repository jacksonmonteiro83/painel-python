import sqlite3

conn = sqlite3.connect('medicoes.db')
c = conn.cursor()

c.execute('''
CREATE TABLE controle_financeiro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fornecedor TEXT,
    contrato TEXT,
    mes TEXT,
    valor_orcado REAL,
    valor_medido REAL
)
''')

c.executemany('''
INSERT INTO controle_financeiro (fornecedor, contrato, mes, valor_orcado, valor_medido)
VALUES (?, ?, ?, ?, ?)
''', [
    ('Construtora Alfa', 'CT-001', 'Jan', 500000, 420000),
    ('Construtora Alfa', 'CT-001', 'Fev', 500000, 480000),
    ('Serviços Beta', 'CT-002', 'Jan', 300000, 250000),
    ('Serviços Beta', 'CT-002', 'Fev', 300000, 310000)
])

conn.commit()
conn.close()
print("Banco criado com sucesso!")

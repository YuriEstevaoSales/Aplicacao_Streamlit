import streamlit as st
import sqlite3
import pandas as pd

def connect_db(db_path):
    conn = sqlite3.connect(db_path)
    return conn

def query_db(conn, query):
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Erro ao executar a consulta: {e}")
        return None

DB_PATH = "dados.db"

queries = {
    """Consulta 1: Municípios do estado de São Paulo com mais de 10.000 famílias em situação de pobreza, segundo a faixa do Programa
Bolsa Família, inscritas no Cadastro Único em janeiro de 2024""": """
SELECT
Municipio.nome_municipio,
FamiliasPobres.qtd_familias
FROM Municipio
JOIN FamiliasPobres
ON CAST(TRIM(Municipio.codigo_ibge) AS TEXT) = CAST(TRIM(FamiliasPobres.codigo_ibge) AS TEXT)
WHERE TRIM(Municipio.uf) = 'SP' AND FamiliasPobres.qtd_familias > 10000 AND FamiliasPobres.mes = '202401'
ORDER BY FamiliasPobres.qtd_familias DESC
""",
    """Consulta 2: Os 5 municípios do estado do Rio de Janeiro com maior indicador de famílias com renda per capita mensal acima de
meio salário-mínimo, segundo a faixa do Programa Bolsa Família, inscritas no Cadastro Único em novembro de 2024""": """
SELECT
    Municipio.nome_municipio AS municipio,
    FamiliasAcimaMeioSalario.qtd_familias AS familias_acima_meio_salario
FROM Municipio
JOIN FamiliasAcimaMeioSalario
ON CAST(TRIM(Municipio.codigo_ibge) AS TEXT) = CAST(TRIM(FamiliasAcimaMeioSalario.codigo_ibge) AS TEXT)
WHERE TRIM(Municipio.uf) = 'RJ' AND FamiliasAcimaMeioSalario.mes = '202411'
ORDER BY FamiliasAcimaMeioSalario.qtd_familias DESC
LIMIT 5;
""",
    """Consulta 3: Os 10 municípios com o maior indicador de famílias em situação de pobreza, segundo a faixa do Programa Bolsa
Família, inscritas no Cadastro Único em janeiro de 2024""": """
SELECT
Municipio.nome_municipio,
FamiliasPobres.qtd_familias AS familias_pobres
FROM Municipio
JOIN FamiliasPobres
ON Municipio.codigo_ibge = FamiliasPobres.codigo_ibge
WHERE FamiliasPobres.mes = '202401'
ORDER BY FamiliasPobres.qtd_familias DESC
LIMIT 10;
""",
    """Consulta 4: Os 10 municípios da Região Norte (UFs: AC, AP, AM, PA, RO, RR, TO) com o maior indicador de famílias em situação de
pobreza, segundo a faixa do Programa Bolsa Família, inscritas no Cadastro Único em janeiro de 2024""": """
SELECT
Municipio.nome_municipio,
Municipio.uf,
FamiliasPobres.qtd_familias
FROM Municipio
JOIN FamiliasPobres
ON Municipio.codigo_ibge = FamiliasPobres.codigo_ibge
WHERE TRIM (Municipio.uf) IN ('AC', 'AP', 'AM', 'PA', 'RO', 'RR', 'TO') AND FamiliasPobres.mes = '202401'
ORDER BY FamiliasPobres.qtd_familias DESC
LIMIT 10;
""",
    """Consulta 5: Total de famílias em situação de pobreza, segundo a faixa do Programa Bolsa Família, da região sudeste inscritas no
Cadastro Único no período de novembro de 2024""": """
SELECT
Municipio.uf,
SUM(FamiliasPobres.qtd_familias) AS total_familias_pobres
FROM Municipio
JOIN FamiliasPobres
ON Municipio.codigo_ibge = FamiliasPobres.codigo_ibge
WHERE TRIM (Municipio.uf) IN ('MG', 'SP', 'RJ', 'ES') AND FamiliasPobres.mes = '202411'
GROUP BY Municipio.uf
ORDER BY total_familias_pobres DESC;
""",
    """Consulta 6: Quantidade de famílias inscritas no Cadastro Único por indicador listadas por período no país no ano de 2024""": """
SELECT 
    FamiliasPobres.mes AS periodo,
    SUM(FamiliasPobres.qtd_familias) AS total_familias_pobres,
    SUM(FamiliasBaixaRenda.qtd_familias) AS total_familias_baixa_renda,
    SUM(FamiliasAcimaMeioSalario.qtd_familias) AS total_familias_acima_meio_salario
FROM FamiliasPobres
LEFT JOIN FamiliasBaixaRenda 
    ON FamiliasPobres.codigo_ibge = FamiliasBaixaRenda.codigo_ibge 
    AND FamiliasPobres.mes = FamiliasBaixaRenda.mes
LEFT JOIN FamiliasAcimaMeioSalario 
    ON FamiliasPobres.codigo_ibge = FamiliasAcimaMeioSalario.codigo_ibge 
    AND FamiliasPobres.mes = FamiliasAcimaMeioSalario.mes
GROUP BY FamiliasPobres.mes
ORDER BY FamiliasPobres.mes;
""",
    """Consulta 7: Município de cada estado(UF) com os maiores valores de famílias inscritas no Cadastro Único por indicador no período
de janeiro de 2024""": """
WITH RankedCities AS (
    SELECT
        Municipio.uf,
        Municipio.nome_municipio,
        FamiliasPobres.qtd_familias AS familias_pobres,
        FamiliasBaixaRenda.qtd_familias AS familias_baixa_renda,
        FamiliasAcimaMeioSalario.qtd_familias AS familias_acima_meio_salario,
        ROW_NUMBER() OVER (PARTITION BY Municipio.uf ORDER BY FamiliasPobres.qtd_familias DESC) AS rank_pobres,
        ROW_NUMBER() OVER (PARTITION BY Municipio.uf ORDER BY FamiliasBaixaRenda.qtd_familias DESC) AS rank_baixa_renda,
        ROW_NUMBER() OVER (PARTITION BY Municipio.uf ORDER BY FamiliasAcimaMeioSalario.qtd_familias DESC) AS rank_acima_meio_salario
    FROM Municipio
    LEFT JOIN FamiliasPobres
        ON Municipio.codigo_ibge = FamiliasPobres.codigo_ibge AND FamiliasPobres.mes = '202401'
    LEFT JOIN FamiliasBaixaRenda
        ON Municipio.codigo_ibge = FamiliasBaixaRenda.codigo_ibge AND FamiliasBaixaRenda.mes = '202401'
    LEFT JOIN FamiliasAcimaMeioSalario
        ON Municipio.codigo_ibge = FamiliasAcimaMeioSalario.codigo_ibge AND FamiliasAcimaMeioSalario.mes = '202401'
)
SELECT
    uf,
    nome_municipio,
    familias_pobres,
    familias_baixa_renda,
    familias_acima_meio_salario
FROM RankedCities
WHERE rank_pobres = 1 OR rank_baixa_renda = 1 OR rank_acima_meio_salario = 1
ORDER BY uf;

""",
    """Consulta 8: Municípios de Rondônia com famílias inscritas no Cadastro Único por indicador no período de janeiro de 2024""": """
SELECT
    Municipio.nome_municipio,
    SUM(FamiliasPobres.qtd_familias) AS familias_pobres,
    SUM(FamiliasBaixaRenda.qtd_familias) AS familias_baixa_renda,
    SUM(FamiliasAcimaMeioSalario.qtd_familias) AS familias_acima_meio_salario
FROM Municipio
LEFT JOIN FamiliasPobres
    ON Municipio.codigo_ibge = FamiliasPobres.codigo_ibge AND FamiliasPobres.mes = '202401'
LEFT JOIN FamiliasBaixaRenda
    ON Municipio.codigo_ibge = FamiliasBaixaRenda.codigo_ibge AND FamiliasBaixaRenda.mes = '202401'
LEFT JOIN FamiliasAcimaMeioSalario
    ON Municipio.codigo_ibge = FamiliasAcimaMeioSalario.codigo_ibge AND FamiliasAcimaMeioSalario.mes = '202401'
WHERE TRIM(Municipio.uf) = 'RO'
GROUP BY Municipio.nome_municipio
ORDER BY Municipio.nome_municipio;
""",
    """Consulta 9: Soma total de famílias inscritas no Cadastro Único por estado (UF) para cada indicador no período de janeiro de 2024""": """
        SELECT
    Municipio.uf,
    SUM(FamiliasPobres.qtd_familias) AS total_familias_pobres,
    SUM(FamiliasBaixaRenda.qtd_familias) AS total_familias_baixa_renda,
    SUM(FamiliasAcimaMeioSalario.qtd_familias) AS total_familias_acima_meio_salario
FROM Municipio
LEFT JOIN FamiliasPobres
    ON Municipio.codigo_ibge = FamiliasPobres.codigo_ibge AND FamiliasPobres.mes = '202401'
LEFT JOIN FamiliasBaixaRenda
    ON Municipio.codigo_ibge = FamiliasBaixaRenda.codigo_ibge AND FamiliasBaixaRenda.mes = '202401'
LEFT JOIN FamiliasAcimaMeioSalario
    ON Municipio.codigo_ibge = FamiliasAcimaMeioSalario.codigo_ibge AND FamiliasAcimaMeioSalario.mes = '202401'
GROUP BY Municipio.uf
ORDER BY Municipio.uf;
    """,
    """Consulta 10: Média de famílias em situação de pobreza, segundo a faixa do Programa Bolsa Família, inscritas no Cadastro Único por
estado (UF) no período de janeiro de 2024""": """
SELECT
TRIM(Municipio.uf) AS uf,
AVG(FamiliasPobres.qtd_familias) AS media_familias_pobres
FROM Municipio
JOIN FamiliasPobres
ON Municipio.codigo_ibge = FamiliasPobres.codigo_ibge
WHERE FamiliasPobres.mes = '202401'
GROUP BY TRIM(Municipio.uf)
ORDER BY TRIM(Municipio.uf);
    """,
    "Consulta 11: Personalizada": """"""
}

st.title("TP2: Aplicação Streamlit para Consultas ao Banco de Dados")
st.sidebar.header("Escolha uma consulta")

query_choice = st.sidebar.selectbox("Selecione uma consulta:", list(queries.keys()))
query = queries[query_choice]

if query_choice == "Consulta 11: Personalizada":
    query = st.sidebar.text_area("Escreva sua consulta SQL:", placeholder="Digite sua consulta aqui...")

if st.sidebar.button("Executar Consulta"):
    if not query.strip():
        st.warning("Por favor, insira uma consulta SQL válida.")
    else:
        conn = connect_db(DB_PATH)  
        df = query_db(conn, query)  
        
        if df is not None:
            st.write(f"**Resultado da {query_choice}**")
            st.dataframe(df)
            
        if len(df.columns) == 2:
            x_col, y_col = df.columns[0], df.columns[1]
            st.bar_chart(data=df.set_index(x_col), y=y_col)
        else:
            st.warning("Os dados retornados não são compatíveis com a criação de gráficos simples.") 

            st.download_button(
                label="Baixar como CSV",
                data=df.to_csv(index=False),
                file_name=f"resultado_{query_choice}.csv",
                mime="text/csv",
            )
        conn.close()  

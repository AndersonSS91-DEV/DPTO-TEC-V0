# ==========================================================
# DASHBOARD OPS - MBF EXECUTIVO (VERSÃO CORRIGIDA REAL)
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide")

st.markdown("""
<style>
.stApp { background-color: #eef2f5; }
.block-container { padding-top: 1rem; padding-left: 2rem; padding-right: 2rem; }

.card {
    background-color: white;
    border-top: 35px solid #1f2430;
    padding: 15px;
    border-radius: 8px;
    height: 120px;
}

.big-number {
    font-size: 28px;
    font-weight: bold;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("Dashboard Operações - OPS")

arquivo = st.file_uploader("Carregar base Excel (.xlsx)", type=["xlsx"])

if arquivo:

    df = pd.read_excel(arquivo, sheet_name=0)
    df.columns = df.columns.str.strip()

    # Converter datas
    df["Inicio"] = pd.to_datetime(df["Inicio"], errors="coerce")
    df["Termino"] = pd.to_datetime(df["Termino"], errors="coerce")

    hoje = datetime.now()
    mes_atual = hoje.month
    ano_atual = hoje.year

    # ======================================================
    # FILTRO OP VÁLIDAS
    # ======================================================

    df_validas = df[
        (df["Inicio"].notna()) &
        (df["Termino"].notna()) &
        (df["Termino"] >= df["Inicio"])
    ].copy()

    # ======================================================
    # DIAS ÚTEIS CORRETOS
    # ======================================================

    df_validas["Dias_Uteis"] = df_validas.apply(
        lambda row: np.busday_count(
            row["Inicio"].date(),
            row["Termino"].date()
        ),
        axis=1
    )

    tempo_medio = df_validas["Dias_Uteis"].mean()

    # ======================================================
    # CONTAGEM MÊS VIGENTE (POR INÍCIO)
    # ======================================================

    df_mes = df_validas[
        (df_validas["Inicio"].dt.month == mes_atual) &
        (df_validas["Inicio"].dt.year == ano_atual)
    ]

    # IMPORTANTE: remover duplicidade real
    # Se tiver coluna "Pedido" ou "OP", use ela aqui
    if "Pedido" in df_mes.columns:
        df_mes = df_mes.drop_duplicates(subset=["Pedido"])
    else:
        df_mes = df_mes.drop_duplicates()

    total_mes = len(df_mes)

    # ======================================================
    # CONTAGEM POR COLABORADOR
    # ======================================================

    bento_mes = df_mes[df_mes["Elaborador"].str.upper() == "BENTO"]
    rodner_mes = df_mes[df_mes["Elaborador"].str.upper() == "RODNER"]

    # ======================================================
    # CARDS
    # ======================================================

    c1, c2, c3, c4 = st.columns(4)

    c1.markdown(f"""
    <div class="card">
        <div>(Mês atual) OP's Geradas</div>
        <div class="big-number">{total_mes}</div>
    </div>
    """, unsafe_allow_html=True)

    c2.markdown(f"""
    <div class="card">
        <div>Bento - OP's (Mês atual)</div>
        <div class="big-number">{len(bento_mes)}</div>
    </div>
    """, unsafe_allow_html=True)

    c3.markdown(f"""
    <div class="card">
        <div>Rodner - OP's (Mês atual)</div>
        <div class="big-number">{len(rodner_mes)}</div>
    </div>
    """, unsafe_allow_html=True)

    c4.markdown(f"""
    <div class="card">
        <div>Tempo Médio (Dias úteis)</div>
        <div class="big-number">{round(tempo_medio,1)}</div>
    </div>
    """, unsafe_allow_html=True)

    # ======================================================
    # GRÁFICO NOV/2025 → ATUAL
    # ======================================================

    inicio_grafico = pd.Timestamp("2025-11-01")

    df_grafico = df_validas[
        df_validas["Inicio"] >= inicio_grafico
    ]

    df_grafico["AnoMes"] = df_grafico["Inicio"].dt.to_period("M")
    mensal = df_grafico.groupby("AnoMes").size()

    media = mensal.mean()

    fig = go.Figure()

    fig.add_bar(
        x=mensal.index.astype(str),
        y=mensal.values,
        marker_color="#bcbcbc"
    )

    fig.add_hline(
        y=media,
        line_color="green",
        annotation_text=f"Média ({round(media,0)})"
    )

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10,r=10,t=10,b=10)
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Carregue a base Excel.")

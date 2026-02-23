# ==========================================================
# DASHBOARD OPS - MBF EXECUTIVO V2
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide")

# ==========================================================
# CSS VISUAL MBF
# ==========================================================

st.markdown("""
<style>

.stApp {
    background-color: #eef2f5;
}

.block-container {
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* Header */
.header-mbf {
    background-color: #dce6ea;
    padding: 18px;
    border-radius: 6px;
    margin-bottom: 20px;
}

/* Cards topo */
.card-top {
    background: linear-gradient(90deg,#1f2430,#2b3140);
    padding: 15px;
    border-radius: 8px;
    color: white;
    height: 115px;
}

/* Número grande */
.big-number {
    font-size: 30px;
    font-weight: bold;
    margin-top: 5px;
}

/* Cards laterais */
.card-side {
    background-color: white;
    border-top: 35px solid #1f2430;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
}

/* Container gráfico */
.chart-container {
    background-color: white;
    border-radius: 10px;
    padding: 15px;
    border-top: 45px solid #1f2430;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# HEADER
# ==========================================================

st.markdown("""
<div class="header-mbf">
    <h2>Dashboard Operações - OPS</h2>
</div>
""", unsafe_allow_html=True)

arquivo = st.file_uploader("Carregar base Excel (.xlsx)", type=["xlsx"])

if arquivo:

    # ======================================================
    # LEITURA ABA OP
    # ======================================================

    df = pd.read_excel(arquivo, sheet_name=0)
    df.columns = df.columns.str.strip()

    # Detectar colunas automaticamente
    col_cadastro = next((c for c in df.columns if "cadastro" in c.lower()), None)
    col_entrega = next((c for c in df.columns if "entrega" in c.lower()), None)
    col_termino = next((c for c in df.columns if "termino" in c.lower() or "término" in c.lower()), None)
    col_inicio = next((c for c in df.columns if "inicio" in c.lower()), None)
    col_elaborador = next((c for c in df.columns if "elaborador" in c.lower()), None)

    # Converter datas
    for c in [col_cadastro, col_entrega, col_termino, col_inicio]:
        if c:
            df[c] = pd.to_datetime(df[c], errors="coerce")

    # ======================================================
    # DIAS ÚTEIS
    # ======================================================

    def dias_uteis(inicio, fim):
        if pd.isna(inicio) or pd.isna(fim):
            return np.nan
        return np.busday_count(inicio.date(), fim.date())

    if col_entrega and col_termino:
        df["Dias_Uteis"] = df.apply(
            lambda row: dias_uteis(row[col_entrega], row[col_termino]),
            axis=1
        )
    else:
        df["Dias_Uteis"] = np.nan

    # ======================================================
    # FILTRO OUTUBRO → NOVEMBRO
    # ======================================================

    df_filtrado = df[
        (df[col_cadastro].dt.month >= 10) &
        (df[col_cadastro].dt.month <= 11)
    ]

    # ======================================================
    # KPIs
    # ======================================================

    mes_atual = 11  # Novembro fixo
    ano_atual = datetime.now().year

    op_mes = df[
        (df[col_cadastro].dt.month == mes_atual) &
        (df[col_cadastro].dt.year == ano_atual)
    ]

    tempo_medio = df["Dias_Uteis"].mean()

    demanda = df[
        (df[col_inicio].isna()) |
        (df[col_termino].isna())
    ] if col_inicio and col_termino else pd.DataFrame()

    # Bento e Rodner
    bento = df[df[col_elaborador] == "Bento"] if col_elaborador else pd.DataFrame()
    rodner = df[df[col_elaborador] == "Rodner"] if col_elaborador else pd.DataFrame()

    # ======================================================
    # CARDS TOPO
    # ======================================================

    c1, c2, c3, c4 = st.columns(4)

    c1.markdown(f"""
    <div class="card-top">
        <div>(Mês atual) OP's Geradas</div>
        <div class="big-number">{len(op_mes)}</div>
    </div>
    """, unsafe_allow_html=True)

    c2.markdown(f"""
    <div class="card-top">
        <div>Bento - OP's (Mês atual)</div>
        <div class="big-number">{len(bento)}</div>
    </div>
    """, unsafe_allow_html=True)

    c3.markdown(f"""
    <div class="card-top">
        <div>Rodner - OP's (Mês atual)</div>
        <div class="big-number">{len(rodner)}</div>
    </div>
    """, unsafe_allow_html=True)

    c4.markdown(f"""
    <div class="card-top">
        <div>Demanda Atual</div>
        <div class="big-number">{len(demanda)}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ======================================================
    # LAYOUT PRINCIPAL
    # ======================================================

    col_left, col_right = st.columns([1,3])

    with col_left:

        st.markdown(f"""
        <div class="card-side">
            <div>Tempo médio de Liberação / OP (Dias úteis)</div>
            <div class="big-number">{round(tempo_medio,1) if not np.isnan(tempo_medio) else "-"}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card-side">
            <div>Quantidade aguardando informações</div>
            <div class="big-number">{len(demanda)}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card-side">
            <div>Recados</div>
            <br>
            - Auditoria cliente dias 24 e 25.
        </div>
        """, unsafe_allow_html=True)

    with col_right:

        df_filtrado["AnoMes"] = df_filtrado[col_cadastro].dt.to_period("M")
        mensal = df_filtrado.groupby("AnoMes").size()
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
            margin=dict(l=10,r=10,t=10,b=10),
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Carregue a base Excel (.xlsx) para visualizar o dashboard.")

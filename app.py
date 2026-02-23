# ==========================================================
# DASHBOARD OPS - MBF EXECUTIVO (LAYOUT FIEL)
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide")

# ==========================================================
# CSS EXECUTIVO
# ==========================================================

st.markdown("""
<style>

/* Fundo geral */
.stApp {
    background-color: #eef2f5;
}

/* Remove padding padrão */
.block-container {
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #1f2430;
    color: white;
}

/* Header topo */
.top-header {
    background-color: #dce6ea;
    padding: 20px;
    border-radius: 6px;
    margin-bottom: 20px;
}

/* Cards horizontais */
.card-top {
    background: linear-gradient(90deg,#1f2430,#2b3140);
    padding: 15px;
    border-radius: 8px;
    color: white;
    height: 110px;
}

/* Cards laterais */
.card-side {
    background-color: #ffffff;
    border-top: 35px solid #1f2430;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
}

/* Título card lateral */
.side-title {
    font-size: 13px;
    margin-bottom: 8px;
}

/* Valor principal */
.big-number {
    font-size: 28px;
    font-weight: bold;
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
<div class="top-header">
    <h2>Dashboard Operações - OPS</h2>
</div>
""", unsafe_allow_html=True)

# ==========================================================
# UPLOAD
# ==========================================================

arquivo = st.file_uploader("Carregar base Excel (.xlsx)", type=["xlsx"])

if arquivo:

    df = pd.read_excel(arquivo)

    df.columns = df.columns.str.strip()

    # Detecta colunas automaticamente
    col_cadastro = next((c for c in df.columns if "cadastro" in c.lower()), None)
    col_entrega = next((c for c in df.columns if "entrega" in c.lower()), None)
    col_termino = next((c for c in df.columns if "termino" in c.lower() or "término" in c.lower()), None)
    col_inicio = next((c for c in df.columns if "inicio" in c.lower()), None)

    # Converte datas
    for c in [col_cadastro, col_entrega, col_termino, col_inicio]:
        if c:
            df[c] = pd.to_datetime(df[c], errors="coerce")

    # Dias úteis
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

    # KPIs
    mes_atual = datetime.now().month
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

    # ======================================================
    # CARDS SUPERIORES
    # ======================================================

    c1, c2, c3, c4 = st.columns(4)

    c1.markdown(f"""
    <div class="card-top">
        <div>OP's Geradas (Mês atual)</div>
        <div class="big-number">{len(op_mes)}</div>
    </div>
    """, unsafe_allow_html=True)

    c2.markdown(f"""
    <div class="card-top">
        <div>Tempo Médio (d.u.)</div>
        <div class="big-number">{round(tempo_medio,1) if not np.isnan(tempo_medio) else "-"}</div>
    </div>
    """, unsafe_allow_html=True)

    c3.markdown(f"""
    <div class="card-top">
        <div>Demanda Atual</div>
        <div class="big-number">{len(demanda)}</div>
    </div>
    """, unsafe_allow_html=True)

    c4.markdown(f"""
    <div class="card-top">
        <div>Indicador Geral</div>
        <div class="big-number">OK</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ======================================================
    # LAYOUT PRINCIPAL (LATERAL + GRÁFICO)
    # ======================================================

    col_left, col_right = st.columns([1,3])

    with col_left:

        st.markdown(f"""
        <div class="card-side">
            <div class="side-title">Tempo médio de Liberação / OP</div>
            <div class="big-number">{round(tempo_medio,1) if not np.isnan(tempo_medio) else "-"}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card-side">
            <div class="side-title">Quantidade aguardando</div>
            <div class="big-number">{len(demanda)}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card-side">
            <div class="side-title">Recados</div>
            Auditoria do cliente nos dias 24 e 25.
        </div>
        """, unsafe_allow_html=True)

    with col_right:

        df["AnoMes"] = df[col_cadastro].dt.to_period("M")
        mensal = df.groupby("AnoMes").size()
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
    st.info("Carregue a base Excel para visualizar o dashboard.")

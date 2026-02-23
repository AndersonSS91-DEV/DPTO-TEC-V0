# ==========================================================
# DASHBOARD OPS - MBF EXECUTIVO FINAL
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide")

# ==========================================================
# CSS EXECUTIVO MBF
# ==========================================================

st.markdown("""
<style>
.stApp { background-color: #eef2f5; }

.block-container {
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* HEADER */
.header-mbf {
    background-color: #dce6ea;
    padding: 18px;
    border-radius: 6px;
    margin-bottom: 25px;
}

/* CARD EXECUTIVO */
.card-mbf {
    border-radius: 8px;
    overflow: hidden;
    background-color: white;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    margin-bottom: 25px;
}

.card-header {
    background-color: #1f2430;
    color: white;
    padding: 8px 12px;
    font-size: 14px;
    font-weight: 500;
}

.card-body {
    padding: 18px 15px;
}

.card-value {
    font-size: 28px;
    font-weight: bold;
    color: black;
}

/* GRÁFICO */
.chart-container {
    background-color: white;
    border-radius: 10px;
    padding: 25px;
    border-top: 45px solid #1f2430;
    margin-left: 30px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# HEADER COM LOGO
# ==========================================================

from PIL import Image

logo = Image.open("logo_mbf.png")

col_logo, col_title = st.columns([1,8])

with col_logo:
    st.image(logo, width=80)

with col_title:
    st.markdown(
        "<h2 style='margin-top:15px;'>Dashboard - OP´s - Departamento Técnico MBF</h2>",
        unsafe_allow_html=True
    ))

st.markdown(f"""
<div class="header-mbf" style="display:flex; align-items:center; gap:18px;">
    <img src="data:image/png;base64,{logo_base64}" width="70">
    <h2 style="margin:0;">Dashboard Operações - OPS</h2>
</div>
""", unsafe_allow_html=True)
    <h2>Dashboard - OP´s - Departamento Técnico MBF</h2>
</div>
""", unsafe_allow_html=True)

arquivo = st.file_uploader("Carregar base Excel (.xlsx)", type=["xlsx"])

if arquivo:

    df = pd.read_excel(arquivo, sheet_name=0)
    df.columns = df.columns.str.strip()

    col_cadastro = next((c for c in df.columns if "cadastro" in c.lower()), None)
    col_entrega = next((c for c in df.columns if "entrega" in c.lower()), None)
    col_termino = next((c for c in df.columns if "termino" in c.lower() or "término" in c.lower()), None)
    col_inicio = next((c for c in df.columns if "inicio" in c.lower()), None)
    col_elaborador = next((c for c in df.columns if "elaborador" in c.lower()), None)

    for c in [col_cadastro, col_entrega, col_termino, col_inicio]:
        if c:
            df[c] = pd.to_datetime(df[c], errors="coerce")

    hoje = datetime.now()

    # =============================
    # DIAS ÚTEIS (ENTREGA → TERMINO)
    # =============================

    def dias_uteis(entrega, termino):
        if pd.isna(entrega) or pd.isna(termino):
            return np.nan
        if termino < entrega:
            return np.nan
        dias = np.busday_count(entrega.date(), termino.date())
        if np.is_busday(termino.date()):
            dias += 1
        return dias

    if col_entrega and col_termino:
        df["Dias_Uteis"] = df.apply(
            lambda row: dias_uteis(row[col_entrega], row[col_termino]),
            axis=1
        )
    else:
        df["Dias_Uteis"] = np.nan

    df_validos = df[(df["Dias_Uteis"].notna()) & (df["Dias_Uteis"] <= 60)]

    # =============================
    # KPIs
    # =============================

    mes_atual = hoje.month
    ano_atual = hoje.year

    if col_inicio:
        op_mes = df[
            (df[col_inicio].dt.month == mes_atual) &
            (df[col_inicio].dt.year == ano_atual)
        ]
    else:
        op_mes = pd.DataFrame()

    tempo_medio = df_validos["Dias_Uteis"].mean()

    demanda = df[
        (df[col_inicio].isna()) |
        (df[col_termino].isna())
    ] if col_inicio and col_termino else pd.DataFrame()

    if col_elaborador and col_inicio:
        df_mes = df[
            (df[col_inicio].dt.month == mes_atual) &
            (df[col_inicio].dt.year == ano_atual)
        ]
        bento_mes = df_mes[df_mes[col_elaborador].str.upper().str.strip() == "BENTO"]
        rodner_mes = df_mes[df_mes[col_elaborador].str.upper().str.strip() == "RODNER"]
    else:
        bento_mes = pd.DataFrame()
        rodner_mes = pd.DataFrame()

    # =============================
    # CARDS SUPERIORES
    # =============================

    c1, c2, c3, c4 = st.columns(4)

    def card(titulo, valor):
        return f"""
        <div class="card-mbf">
            <div class="card-header">{titulo}</div>
            <div class="card-body">
                <div class="card-value">{valor}</div>
            </div>
        </div>
        """

    c1.markdown(card("(Mês atual) OP's Geradas", len(op_mes)), unsafe_allow_html=True)
    c2.markdown(card("Bento - OP's (Mês atual)", len(bento_mes)), unsafe_allow_html=True)
    c3.markdown(card("Rodner - OP's (Mês atual)", len(rodner_mes)), unsafe_allow_html=True)
    c4.markdown(card("Demanda Atual", len(demanda)), unsafe_allow_html=True)

    # =============================
    # LAYOUT PRINCIPAL
    # =============================

    col_left, col_right = st.columns([1,3])

    with col_left:

        st.markdown(card("Tempo médio de Liberação / OP (Dias)",
                         round(tempo_medio,2) if not np.isnan(tempo_medio) else "-"),
                    unsafe_allow_html=True)

        st.markdown(card("Quantidade aguardando informações", len(demanda)),
                    unsafe_allow_html=True)

        st.markdown(card("Recados",
                         "Auditoria cliente dias 24 e 25."),
                    unsafe_allow_html=True)

    with col_right:

        if col_cadastro:

            inicio_grafico = pd.Timestamp("2025-11-01")
            fim_grafico = pd.Timestamp(hoje.year, hoje.month, 1) + pd.offsets.MonthEnd(0)

            df_grafico = df[
                (df[col_cadastro] >= inicio_grafico) &
                (df[col_cadastro] <= fim_grafico)
            ].copy()

            df_grafico["Mes"] = df_grafico[col_cadastro].dt.strftime("%b/%y")
            mensal = df_grafico.groupby("Mes").size()

            ordem_meses = (
                pd.date_range(start=inicio_grafico, end=fim_grafico, freq="MS")
                .strftime("%b/%y")
                .tolist()
            )

            mensal = mensal.reindex(ordem_meses, fill_value=0)
            media = mensal.mean()

            fig = go.Figure()

            fig.add_bar(
                x=mensal.index,
                y=mensal.values,
                marker_color="#bcbcbc",
                width=0.5
            )

            fig.add_hline(
                y=media,
                line_color="green",
                annotation_text=f"Média ({round(media,0)})"
            )

            fig.update_layout(
                margin=dict(l=40, r=40, t=20, b=40),
                plot_bgcolor="white",
                paper_bgcolor="white",
                xaxis=dict(type="category"),
                height=420
            )

            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Carregue a base Excel (.xlsx) para visualizar o dashboard.")








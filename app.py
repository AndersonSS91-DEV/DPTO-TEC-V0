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
# CSS PADRÃO EXECUTIVO
# ==========================================================

st.markdown("""
<style>
.stApp { background-color: #eef2f5; }

.block-container {
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

.header-mbf {
    background-color: #dce6ea;
    padding: 18px;
    border-radius: 6px;
    margin-bottom: 20px;
}

.card-padrao {
    background-color: white;
    border-top: 35px solid #1f2430;
    padding: 15px;
    border-radius: 8px;
    height: 120px;
    margin-bottom: 20px;
}

.big-number {
    font-size: 28px;
    font-weight: bold;
    margin-top: 10px;
}

.chart-container {
    background-color: white;
    border-radius: 10px;
    padding: 20px;
    border-top: 45px solid #1f2430;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-mbf">
    <h2>Dashboard Operações - OPS</h2>
</div>
""", unsafe_allow_html=True)

arquivo = st.file_uploader("Carregar base Excel (.xlsx)", type=["xlsx"])

if arquivo:

    # =============================
    # LEITURA
    # =============================

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

        # incluir o dia final se for dia útil
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

    # Remover distorções absurdas (>60 dias úteis)
    df_validos = df[(df["Dias_Uteis"].notna()) & (df["Dias_Uteis"] <= 60)]

    # =============================
    # KPIs
    # =============================

    mes_atual = hoje.month
    ano_atual = hoje.year

    # OP mês (por INICIO)
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

    # Elaboradores
    if col_elaborador and col_inicio:

        df_mes = df[
            (df[col_inicio].dt.month == mes_atual) &
            (df[col_inicio].dt.year == ano_atual)
        ]

        bento_mes = df_mes[
            df_mes[col_elaborador].str.upper().str.strip() == "BENTO"
        ]

        rodner_mes = df_mes[
            df_mes[col_elaborador].str.upper().str.strip() == "RODNER"
        ]
    else:
        bento_mes = pd.DataFrame()
        rodner_mes = pd.DataFrame()

    # =============================
    # CARDS SUPERIORES
    # =============================

    c1, c2, c3, c4 = st.columns(4)

    c1.markdown(f"""
    <div class="card-padrao">
        <div>(Mês atual) OP's Geradas</div>
        <div class="big-number">{len(op_mes)}</div>
    </div>
    """, unsafe_allow_html=True)

    c2.markdown(f"""
    <div class="card-padrao">
        <div>Bento - OP's (Mês atual)</div>
        <div class="big-number">{len(bento_mes)}</div>
    </div>
    """, unsafe_allow_html=True)

    c3.markdown(f"""
    <div class="card-padrao">
        <div>Rodner - OP's (Mês atual)</div>
        <div class="big-number">{len(rodner_mes)}</div>
    </div>
    """, unsafe_allow_html=True)

    c4.markdown(f"""
    <div class="card-padrao">
        <div>Demanda Atual</div>
        <div class="big-number">{len(demanda)}</div>
    </div>
    """, unsafe_allow_html=True)

    # =============================
    # LAYOUT
    # =============================

    col_left, col_right = st.columns([1,3])

    with col_left:

        st.markdown(f"""
        <div class="card-padrao">
            <div>Tempo médio de Liberação / OP (Dias úteis)</div>
            <div class="big-number">{round(tempo_medio,2) if not np.isnan(tempo_medio) else "-"}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card-padrao">
            <div>Quantidade aguardando informações</div>
            <div class="big-number">{len(demanda)}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card-padrao">
            <div>Recados</div>
            <br>
            Auditoria cliente dias 24 e 25.
        </div>
        """, unsafe_allow_html=True)

    with col_right:

        # =============================
        # GRÁFICO MENSAL (NOV/25 → MÊS ATUAL)
        # =============================

        if col_cadastro:

            inicio_grafico = pd.Timestamp("2025-11-01")
            fim_grafico = pd.Timestamp(hoje.year, hoje.month, 1) + pd.offsets.MonthEnd(0)

            df_grafico = df[
                (df[col_cadastro] >= inicio_grafico) &
                (df[col_cadastro] <= fim_grafico)
            ].copy()

            # Criar coluna mês formatada
            df_grafico["Mes"] = df_grafico[col_cadastro].dt.strftime("%b/%y")

            mensal = df_grafico.groupby("Mes").size()

            # Ordenar meses corretamente
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
                marker_color="#bcbcbc"
            )

            fig.add_hline(
                y=media,
                line_color="green",
                annotation_text=f"Média ({round(media,0)})"
            )

            fig.update_layout(
                xaxis_title="",
                yaxis_title="Quantidade de OP's",
                margin=dict(l=10, r=10, t=10, b=10),
                plot_bgcolor="white",
                paper_bgcolor="white",
                xaxis=dict(type="category")
            )

            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
else:
    st.info("Carregue a base Excel (.xlsx) para visualizar o dashboard.")





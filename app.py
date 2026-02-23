# ==========================================================
# DASHBOARD OPS - PADRÃO MBF (VERSÃO ESTÁVEL DIRETORIA)
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide")

# ==========================================================
# CSS CUSTOMIZADO
# ==========================================================

st.markdown("""
<style>
body { background-color: #eef3f7; }

.card {
    background-color: #1f2430;
    padding: 20px;
    border-radius: 10px;
    color: white;
}

.metric-title {
    font-size: 14px;
    opacity: 0.7;
}

.metric-value {
    font-size: 32px;
    font-weight: bold;
}

.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# MENU
# ==========================================================

menu = st.sidebar.radio(
    "Navegação",
    ["Dashboard OP", "Dashboard OPR"]
)

st.title("Dashboard Operações - OPS")

arquivo = st.file_uploader("Carregar base Excel", type=["xlsx"])

if arquivo is not None:

    # ======================================================
    # LEITURA INTELIGENTE DAS ABAS
    # ======================================================

    xls = pd.ExcelFile(arquivo)
    abas = xls.sheet_names

    # Localiza aba OP
    aba_op = [a for a in abas if a.strip().upper() == "OP"]
    if not aba_op:
        st.error("Aba 'OP' não encontrada no Excel.")
        st.stop()

    df_op = pd.read_excel(arquivo, sheet_name=aba_op[0])
    df_op.columns = df_op.columns.str.strip()

    # Localiza aba OPR (qualquer nome contendo OPR)
    aba_opr = [a for a in abas if "OPR" in a.upper()]
    if aba_opr:
        df_opr = pd.read_excel(arquivo, sheet_name=aba_opr[0])
        df_opr.columns = df_opr.columns.str.strip()
    else:
        df_opr = pd.DataFrame()

    # ======================================================
    # IDENTIFICAÇÃO AUTOMÁTICA DE COLUNAS IMPORTANTES
    # ======================================================

    col_cadastro = None
    col_entrega = None
    col_termino = None
    col_inicio = None

    for col in df_op.columns:
        col_lower = col.lower()

        if "cadastro" in col_lower:
            col_cadastro = col

        if "entrega" in col_lower:
            col_entrega = col

        if "término" in col_lower or "termino" in col_lower:
            col_termino = col

        if "início" in col_lower or "inicio" in col_lower:
            col_inicio = col

    if not col_cadastro:
        st.error("Coluna de Data de Cadastro não encontrada.")
        st.stop()

    # Converter datas encontradas
    for col in [col_cadastro, col_entrega, col_termino, col_inicio]:
        if col:
            df_op[col] = pd.to_datetime(df_op[col], errors="coerce")

    # ======================================================
    # CÁLCULO DIAS ÚTEIS (SOMENTE SE ENTREGAR E TERMINO EXISTIREM)
    # ======================================================

    def dias_uteis(inicio, fim):
        if pd.isna(inicio) or pd.isna(fim):
            return np.nan
        return np.busday_count(inicio.date(), fim.date())

    if col_entrega and col_termino:
        df_op["Dias_Uteis"] = df_op.apply(
            lambda row: dias_uteis(row[col_entrega], row[col_termino]),
            axis=1
        )
    else:
        df_op["Dias_Uteis"] = np.nan

    # ======================================================
    # DASHBOARD OP
    # ======================================================

    if menu == "Dashboard OP":

        st.markdown('<div class="section-title">Produção</div>', unsafe_allow_html=True)

        mes_atual = datetime.now().month
        ano_atual = datetime.now().year

        op_mes = df_op[
            (df_op[col_cadastro].dt.month == mes_atual) &
            (df_op[col_cadastro].dt.year == ano_atual)
        ]

        tempo_medio = df_op["Dias_Uteis"].mean()

        if col_inicio and col_termino:
            demanda = df_op[
                (df_op[col_inicio].isna()) |
                (df_op[col_termino].isna())
            ]
        else:
            demanda = pd.DataFrame()

        col1, col2, col3 = st.columns(3)

        col1.markdown(f"""
        <div class="card">
            <div class="metric-title">OP's no Mês</div>
            <div class="metric-value">{len(op_mes)}</div>
        </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
        <div class="card">
            <div class="metric-title">Tempo Médio (d.u.)</div>
            <div class="metric-value">{round(tempo_medio,1) if not np.isnan(tempo_medio) else "-"}</div>
        </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
        <div class="card">
            <div class="metric-title">Demanda Atual</div>
            <div class="metric-value">{len(demanda)}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        df_op["AnoMes"] = df_op[col_cadastro].dt.to_period("M")
        mensal = df_op.groupby("AnoMes").size()

        media = mensal.mean()

        fig = go.Figure()
        fig.add_bar(
            x=mensal.index.astype(str),
            y=mensal.values,
            marker_color="lightgray"
        )

        fig.add_hline(
            y=media,
            line_color="green",
            annotation_text=f"Média ({round(media,0)})"
        )

        fig.update_layout(
            title="OP's Criadas por Mês",
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(fig, use_container_width=True)

    # ======================================================
    # DASHBOARD OPR
    # ======================================================

    if menu == "Dashboard OPR":

        st.markdown('<div class="section-title">Retrabalho</div>', unsafe_allow_html=True)

        if df_opr.empty:
            st.warning("Aba OPR não encontrada ou vazia.")
        else:

            # Identificar coluna data
            col_data_opr = None
            col_motivo = None

            for col in df_opr.columns:
                col_lower = col.lower()
                if "data" in col_lower:
                    col_data_opr = col
                if "motivo" in col_lower:
                    col_motivo = col

            if col_data_opr:
                df_opr[col_data_opr] = pd.to_datetime(df_opr[col_data_opr], errors="coerce")
                df_opr["AnoMes"] = df_opr[col_data_opr].dt.to_period("M")
                mensal_opr = df_opr.groupby("AnoMes").size()
            else:
                mensal_opr = pd.Series()

            col1, col2 = st.columns(2)

            if not mensal_opr.empty:
                fig1 = go.Figure()
                fig1.add_bar(
                    x=mensal_opr.index.astype(str),
                    y=mensal_opr.values,
                    marker_color="#d9534f"
                )
                fig1.update_layout(
                    title="OPR por Mês",
                    plot_bgcolor="white",
                    paper_bgcolor="white"
                )
                col1.plotly_chart(fig1, use_container_width=True)

            if col_motivo:
                motivos = df_opr[col_motivo].value_counts()

                fig2 = go.Figure()
                fig2.add_bar(
                    x=motivos.values,
                    y=motivos.index,
                    orientation="h",
                    marker_color="#c9302c"
                )
                fig2.update_layout(
                    title="Motivos de Retrabalho",
                    plot_bgcolor="white",
                    paper_bgcolor="white"
                )
                col2.plotly_chart(fig2, use_container_width=True)

else:
    st.info("Carregue a base Excel (.xlsx) para visualizar o dashboard.")

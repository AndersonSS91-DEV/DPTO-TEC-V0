# ==========================================================
# DASHBOARD OPS - PADRÃO MBF
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide")

# ==========================================================
# CSS CUSTOMIZADO (PADRÃO VISUAL MBF)
# ==========================================================

st.markdown("""
<style>

body {
    background-color: #eef3f7;
}

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
# MENU LATERAL
# ==========================================================

menu = st.sidebar.radio(
    "Navegação",
    ["Dashboard OP", "Dashboard OPR"]
)

st.title("Dashboard Operações - OPS")

arquivo = st.file_uploader("Carregar base csv", type=["csv"])

if arquivo is not None:
    df_op = pd.read_csv(arquivo, sheet_name="OP")
    df_opr = pd.read_csv(arquivo, sheet_name="OPR")

    df_op = df[df["Tipo"] == "OP"].copy()
    df_opr = df[df["Tipo"] == "OPR"].copy()

    # Converter datas
    datas_op = ["Data Cadastro", "Data Entrega", "Data Início", "Data Término"]
    for col in datas_op:
        if col in df_op.columns:
            df_op[col] = pd.to_datetime(df_op[col], errors="coerce")

    if "Data" in df_opr.columns:
        df_opr["Data"] = pd.to_datetime(df_opr["Data"], errors="coerce")

    # Função dias úteis
    def dias_uteis(inicio, fim):
        if pd.isna(inicio) or pd.isna(fim):
            return np.nan
        return np.busday_count(inicio.date(), fim.date())

    df_op["Dias_Uteis"] = df_op.apply(
        lambda row: dias_uteis(row["Data Entrega"], row["Data Término"]),
        axis=1
    )

    if menu == "Dashboard OP":

        st.markdown('<div class="section-title">Produção</div>', unsafe_allow_html=True)

        mes_atual = datetime.now().month
        ano_atual = datetime.now().year

        op_mes = df_op[
            (df_op["Data Cadastro"].dt.month == mes_atual) &
            (df_op["Data Cadastro"].dt.year == ano_atual)
        ]

        tempo_medio = df_op["Dias_Uteis"].mean()

        demanda = df_op[
            (df_op["Data Início"].isna()) |
            (df_op["Data Término"].isna())
        ]

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
            <div class="metric-value">{round(tempo_medio,1)}</div>
        </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
        <div class="card">
            <div class="metric-title">Demanda Atual</div>
            <div class="metric-value">{len(demanda)}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        df_op["AnoMes"] = df_op["Data Cadastro"].dt.to_period("M")
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
    # ABA OPR
    # ======================================================

    if menu == "Dashboard OPR":

        st.markdown('<div class="section-title">Retrabalho</div>', unsafe_allow_html=True)

        df_opr["AnoMes"] = df_opr["Data"].dt.to_period("M")
        mensal_opr = df_opr.groupby("AnoMes").size()

        motivos = df_opr["OP R Motivo"].value_counts()

        col1, col2 = st.columns(2)

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
    st.info("Carregue a base para visualizar o dashboard.")



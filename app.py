    # ======================================================
    # CRIAÇÃO DAS ABAS DO SISTEMA
    # ======================================================

    tab_dashboard, tab_pendencias, tab_opr, tab_recados = st.tabs([
        "📊 DASHBOARD",
        "⚠️ PENDÊNCIAS",
        "🔁 DADOS DE OP´s R",
        "📢 PAINEL DE RECADOS"
    ])

    # ======================================================
    # TAB DASHBOARD
    # ======================================================

    with tab_dashboard:
        st.markdown("### 📊 DASHBOARD")
        # (mantém todo o seu código do dashboard aqui dentro)

    # ======================================================
    # TAB PENDÊNCIAS
    # ======================================================

    with tab_pendencias:
        st.markdown("### ⚠️ Painel de Pendências")
        st.info("Em desenvolvimento.")

    # ======================================================
    # TAB OP R
    # ======================================================

    with tab_opr:

        st.markdown("## 🔁 Painel de OP´s R")

        if df_opr.empty:
            st.warning("Aba OP R não encontrada no arquivo.")
        else:

            st.dataframe(df_opr, use_container_width=True)

            st.markdown("---")

            col_motivo = next(
                (c for c in df_opr.columns if "motivo" in c.lower()),
                None
            )

            if col_motivo:

                resumo = (
                    df_opr[col_motivo]
                    .fillna("Não informado")
                    .value_counts()
                    .sort_values(ascending=True)
                )

                fig = go.Figure()

                fig.add_trace(go.Bar(
                    y=resumo.index,
                    x=resumo.values,
                    orientation="h",
                    marker_color="#1f2430"
                ))

                fig.update_layout(
                    height=60 * len(resumo) + 120,
                    margin=dict(l=200, r=40, t=40, b=40),
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    title="Quantidade de OP´s R por Motivo",
                    xaxis_title="Quantidade",
                    yaxis_title=""
                )

                st.plotly_chart(fig, use_container_width=True)

            else:
                st.warning("Coluna 'Motivo' não encontrada na aba OP R.")

    # ======================================================
    # TAB RECADOS
    # ======================================================

    with tab_recados:
        st.markdown("### 📢 Painel de Recados")
        st.info("Área destinada a comunicados internos.")

else:
    st.info("Carregue a base Excel (.xlsx) para visualizar o dashboard.")

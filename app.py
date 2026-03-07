st.markdown("### Histórico de Apostas")

hist = supabase.table("apostas_simuladas").select("*").execute()

df_hist = pd.DataFrame(hist.data)

if filtro_resultados and not df_hist.empty:
    df_hist = df_hist[df_hist["resultado"] != "pendente"]

if df_hist.empty:
    st.info("Sem apostas registradas")

else:

    for i,row in df_hist.iterrows():

        col1,col2,col3,col4=st.columns([3,1,1,1])

        col1.write(row.get("evento","-"))
        col2.write(f"Odd {row.get('odd',0)}")
        col3.write(f"Stake {row.get('stake',0)}")

        # valor seguro para resultado
        resultado_atual = row.get("resultado","pendente")

        if resultado_atual not in ["pendente","green","red"]:
            resultado_atual = "pendente"

        resultado = st.selectbox(
            "Resultado",
            ["pendente","green","red"],
            index=["pendente","green","red"].index(resultado_atual),
            key=f"res{i}"
        )

        if st.button("Salvar",key=f"save{i}"):

            supabase.table("apostas_simuladas").update(
                {"resultado":resultado}
            ).eq("id",row["id"]).execute()

            st.success("Resultado atualizado")

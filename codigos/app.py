#dupla: Larissa Mayumi Odani e Leonardo Moiano Lima

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np 

@st.cache_data
def load_data():
    """
    Carrega os dados tratados do arquivo CSV.
    Assume que o arquivo foi salvo com index=True, então a primeira coluna é o índice.
    Converte colunas relevantes para tipos numéricos e trata possíveis erros.
    """
    try:
        df = pd.read_csv('bases_tratadas/dados_tratados.csv', sep=';', encoding='UTF-8', index_col=0)
        #df = pd.read_csv('../bases_tratadas/dados_tratados.csv', sep=';', encoding='UTF-8', index_col=0)
    except FileNotFoundError:
        st.error("Arquivo 'bases_tratadas/dados_tratados.csv' não encontrado. "
                 "Verifique o caminho ou se a Parte 1 do script foi executada e o arquivo foi salvo corretamente.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

    if 'Volume (ML)' in df.columns:
        df['Volume (ML)'] = pd.to_numeric(df['Volume (ML)'], errors='coerce').fillna(0).astype(int)
    if 'Precos' in df.columns:
        df['Precos'] = pd.to_numeric(df['Precos'], errors='coerce').fillna(0)
    if 'Parcela' in df.columns:
        df['Parcela'] = pd.to_numeric(df['Parcela'], errors='coerce').fillna(0).astype(int)
    
    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    return df

df = load_data()

if not df.empty:
    st.title("Análise de Vinhos Best Buys Mistral")
    st.markdown("Uma aplicação interativa para explorar os dados de vinhos com melhor custo-benefício da Mistral.")

    st.subheader('Dados Brutos')
    st.dataframe(df)

    st.subheader('Análise de Valores Nulos')
    aux_nulos = df.isnull().sum().reset_index()
    aux_nulos.columns = ['Variável', 'Quantidade de Nulos']
    st.dataframe(aux_nulos)

    st.subheader('Análises Univariadas')
    st.write('Medidas Resumo')
    try:
        st.dataframe(df.describe(include='all'))
    except Exception as e:
        st.error(f"Erro ao gerar medidas resumo: {e}")

    valid_columns_for_analysis = [col for col in df.columns if df[col].isnull().sum() < len(df[col])]

    coluna_univariada = st.selectbox('Escolha uma coluna para análise univariada', valid_columns_for_analysis)

    if coluna_univariada and coluna_univariada in df.columns:
        if df[coluna_univariada].notna().sum() == 0:
            st.warning(f"A coluna '{coluna_univariada}' não possui dados válidos para análise.")
        elif pd.api.types.is_numeric_dtype(df[coluna_univariada]):
            media_univariada = round(df[coluna_univariada].mean(skipna=True), 2)
            desvio_univariada = round(df[coluna_univariada].std(skipna=True), 2)
            mediana_univariada = round(df[coluna_univariada].median(skipna=True), 2)
            maximo_univariada = round(df[coluna_univariada].max(skipna=True), 2)
            minimo_univariada = round(df[coluna_univariada].min(skipna=True), 2)

            st.write(f'A coluna escolhida foi **{coluna_univariada}**. A sua média é **{media_univariada}**. O desvio padrão é **{desvio_univariada}**. A mediana é **{mediana_univariada}**. O valor máximo é **{maximo_univariada}** e o mínimo é **{minimo_univariada}**.')

            st.subheader(f'Histograma de {coluna_univariada}')
            if df[coluna_univariada].notna().sum() > 0:
                fig_hist = px.histogram(df, x=coluna_univariada, title=f'Distribuição de {coluna_univariada}')
                st.plotly_chart(fig_hist)
            else:
                st.write("Não há dados suficientes para gerar o histograma.")

            st.subheader(f'Boxplot de {coluna_univariada}')
            if df[coluna_univariada].notna().sum() > 0:
                fig_box = px.box(df, y=coluna_univariada, title=f'Boxplot de {coluna_univariada}')
                st.plotly_chart(fig_box)
            else:
                st.write("Não há dados suficientes para gerar o boxplot.")

            st.subheader(f"Interpretação dos Gráficos para {coluna_univariada}")
            explicacao_univariada = ""

            explicacao_univariada += f"O **histograma de {coluna_univariada}** mostra a frequência (contagem) de vinhos em diferentes faixas de valores para esta variável. "
            if df[coluna_univariada].notna().sum() > 0:
                skewness = df[coluna_univariada].skew()
                if pd.notna(skewness):
                    if skewness > 0.5:
                        explicacao_univariada += f"A distribuição parece ser **assimétrica à direita** (skewness de {skewness:.2f}). Isso sugere que há uma concentração de valores mais baixos e uma cauda mais longa de valores mais altos. Nestes casos, a média ({media_univariada}) tende a ser maior que a mediana ({mediana_univariada}). "
                    elif skewness < -0.5:
                        explicacao_univariada += f"A distribuição parece ser **assimétrica à esquerda** (skewness de {skewness:.2f}). Isso sugere uma concentração de valores mais altos e uma cauda mais longa de valores mais baixos. A média ({media_univariada}) tende a ser menor que a mediana ({mediana_univariada}). "
                    else:
                        explicacao_univariada += f"A distribuição parece ser **aproximadamente simétrica** (skewness de {skewness:.2f}). A média ({media_univariada}) e a mediana ({mediana_univariada}) devem ser próximas. "
                else:
                    explicacao_univariada += "Não foi possível calcular a assimetria (skewness) para esta coluna. "

            explicacao_univariada += f"\n\nO **boxplot de {coluna_univariada}** oferece um resumo visual da distribuição. "
            if df[coluna_univariada].notna().sum() > 0:
                Q1 = df[coluna_univariada].quantile(0.25)
                Q3 = df[coluna_univariada].quantile(0.75)
                IQR = Q3 - Q1
                explicacao_univariada += f"A linha central da caixa representa a **mediana ({mediana_univariada})**. A caixa em si abrange o intervalo interquartil (IQR), de Q1 ({Q1:.2f}) a Q3 ({Q3:.2f}), contendo 50% dos dados centrais. A altura da caixa (IQR = {IQR:.2f}) indica a dispersão. "
                limite_superior_outlier = Q3 + 1.5 * IQR
                limite_inferior_outlier = Q1 - 1.5 * IQR
                outliers = df[(df[coluna_univariada] > limite_superior_outlier) | (df[coluna_univariada] < limite_inferior_outlier)]
                if not outliers.empty:
                    explicacao_univariada += f"Os pontos fora das 'hastes' (whiskers) são considerados **outliers** (valores atípicos). Foram detectados {len(outliers)} outlier(s) para {coluna_univariada}. "
                else:
                    explicacao_univariada += "Não foram detectados outliers significativos com base na regra do 1.5 * IQR. "
            
            st.markdown(explicacao_univariada)
        
        elif df[coluna_univariada].dtype == 'object':
            st.write(f"A coluna **{coluna_univariada}** é do tipo categórica (texto).")
            st.write("Medidas resumo para colunas categóricas:")
            st.dataframe(df[coluna_univariada].describe())
            
            st.subheader(f'Gráfico de Barras de {coluna_univariada}')
            if df[coluna_univariada].notna().sum() > 0:
                contagem_categorias = df[coluna_univariada].value_counts().reset_index()
                contagem_categorias.columns = [coluna_univariada, 'Contagem']
                fig_bar = px.bar(contagem_categorias, x=coluna_univariada, y='Contagem', title=f'Contagem de Categorias em {coluna_univariada}')
                st.plotly_chart(fig_bar)

                st.subheader(f"Interpretação do Gráfico para {coluna_univariada}")
                explicacao_cat = (f"O gráfico de barras para **{coluna_univariada}** mostra a frequência de cada categoria. "
                                  f"A categoria mais frequente é '{contagem_categorias.iloc[0,0]}' com {contagem_categorias.iloc[0,1]} ocorrências. "
                                  f"A menos frequente (entre as exibidas, se houver muitas) é '{contagem_categorias.iloc[-1,0]}' com {contagem_categorias.iloc[-1,1]} ocorrências. "
                                  f"Isso ajuda a entender a predominância de certos tipos de '{coluna_univariada}' no conjunto de dados.")
                st.markdown(explicacao_cat)
            else:
                st.write("Não há dados suficientes para gerar o gráfico de barras.")
        else:
            st.write(f"A coluna {coluna_univariada} não é numérica nem categórica (object) ou está vazia, análise univariada padrão não aplicável.")


    st.subheader('Análises Bivariadas')
    colunas_bivariadas = st.multiselect('Escolha duas colunas para análise bivariada', valid_columns_for_analysis)

    if len(colunas_bivariadas) == 2:
        coluna_x, coluna_y = colunas_bivariadas[0], colunas_bivariadas[1]

        st.markdown(f"### Análise entre: **{coluna_x}** e **{coluna_y}**")

        if pd.api.types.is_numeric_dtype(df[coluna_x]) and pd.api.types.is_numeric_dtype(df[coluna_y]):
            st.markdown('**Gráfico de Dispersão**')
            fig_scatter = px.scatter(df, x=coluna_x, y=coluna_y, title=f'Dispersão entre {coluna_x} e {coluna_y}')
            st.plotly_chart(fig_scatter)

            st.subheader(f"Interpretação do Gráfico de Dispersão ({coluna_x} vs {coluna_y})")
            explicacao_scatter = f"O gráfico de dispersão entre **{coluna_x}** e **{coluna_y}** mostra a relação entre estas duas variáveis numéricas. Cada ponto representa um vinho.\n"
            try:
                correlacao = df[coluna_x].corr(df[coluna_y])
                if pd.notna(correlacao):
                    explicacao_scatter += f"A correlação de Pearson entre elas é de **{correlacao:.2f}**. "
                    if abs(correlacao) > 0.7:
                        tipo_correlacao = "forte"
                    elif abs(correlacao) > 0.4:
                        tipo_correlacao = "moderada"
                    elif abs(correlacao) > 0.1:
                        tipo_correlacao = "fraca"
                    else:
                        tipo_correlacao = "muito fraca ou inexistente"
                    
                    if correlacao > 0.1 :
                        explicacao_scatter += f"Isso indica uma relação linear positiva {tipo_correlacao}: à medida que '{coluna_x}' aumenta, '{coluna_y}' tende a aumentar também (e vice-versa). "
                    elif correlacao < -0.1:
                        explicacao_scatter += f"Isso indica uma relação linear negativa {tipo_correlacao}: à medida que '{coluna_x}' aumenta, '{coluna_y}' tende a diminuir (e vice-versa). "
                    else:
                         explicacao_scatter += f"Isso indica uma relação linear {tipo_correlacao} entre as variáveis. "
                else:
                    explicacao_scatter += "Não foi possível calcular a correlação. "
            except Exception:
                explicacao_scatter += "Não foi possível calcular a correlação (verifique se as colunas têm variação suficiente). "
            explicacao_scatter += "Observe a forma da nuvem de pontos para identificar padrões (linear, curvilíneo), a força da relação (quão próximos os pontos estão de uma linha imaginária) e a presença de outliers."
            st.markdown(explicacao_scatter)
        else:
            st.info(f"Para um gráfico de dispersão significativo e cálculo de correlação, ambas as colunas ({coluna_x}, {coluna_y}) deveriam ser numéricas. Se uma é categórica, considere o boxplot abaixo.")

        if df[coluna_x].dtype == 'object' and pd.api.types.is_numeric_dtype(df[coluna_y]):
            st.markdown('**Boxplot Comparativo**')
            fig_box_cat = px.box(df, x=coluna_x, y=coluna_y, title=f'Boxplot de {coluna_y} por {coluna_x}')
            st.plotly_chart(fig_box_cat)

            st.subheader(f"Interpretação do Boxplot ({coluna_y} por {coluna_x})")
            explicacao_boxplot_bi = (
                f"O boxplot de **{coluna_y}** (numérica) por **{coluna_x}** (categórica) compara a distribuição de '{coluna_y}' para cada categoria em '{coluna_x}'.\n"
                "Analise:\n"
                f"- **Medianas (linha central da caixa):** Como a mediana de '{coluna_y}' varia entre as categorias de '{coluna_x}'. Categorias com medianas mais altas têm, em geral, valores maiores de '{coluna_y}'.\n"
                f"- **Dispersão (altura da caixa - IQR):** Se a variabilidade (quão espalhados estão os valores) de '{coluna_y}' é diferente entre as categorias. Caixas maiores indicam maior dispersão dos 50% centrais dos dados.\n"
                f"- **Outliers (pontos individuais):** Se algumas categorias de '{coluna_x}' têm mais valores extremos (muito altos ou muito baixos) de '{coluna_y}' do que outras.\n"
            )
            try:
                medianas_por_categoria = df.groupby(coluna_x)[coluna_y].median().dropna().sort_values()
                if not medianas_por_categoria.empty:
                    explicacao_boxplot_bi += (f"Por exemplo, a categoria '{medianas_por_categoria.index[0]}' em '{coluna_x}' apresenta a menor mediana para '{coluna_y}' ({medianas_por_categoria.iloc[0]:.2f}), "
                                              f"enquanto a categoria '{medianas_por_categoria.index[-1]}' tem a maior mediana ({medianas_por_categoria.iloc[-1]:.2f}). "
                                              "Isso pode indicar diferenças significativas nos valores de '{coluna_y}' dependendo da categoria de '{coluna_x}'.")
            except Exception:
                explicacao_boxplot_bi += f"Não foi possível calcular medianas por categoria para '{coluna_x}' e '{coluna_y}' para um exemplo detalhado."
            st.markdown(explicacao_boxplot_bi)

        elif df[coluna_y].dtype == 'object' and pd.api.types.is_numeric_dtype(df[coluna_x]):
            st.markdown('**Boxplot Comparativo**')
            fig_box_cat = px.box(df, x=coluna_y, y=coluna_x, title=f'Boxplot de {coluna_x} por {coluna_y}')
            st.plotly_chart(fig_box_cat)

            st.subheader(f"Interpretação do Boxplot ({coluna_x} por {coluna_y})")
            explicacao_boxplot_bi = (
                f"O boxplot de **{coluna_x}** (numérica) por **{coluna_y}** (categórica) compara a distribuição de '{coluna_x}' para cada categoria em '{coluna_y}'.\n"
                "Analise:\n"
                f"- **Medianas (linha central da caixa):** Como a mediana de '{coluna_x}' varia entre as categorias de '{coluna_y}'.\n"
                f"- **Dispersão (altura da caixa - IQR):** Se a variabilidade de '{coluna_x}' é diferente entre as categorias.\n"
                f"- **Outliers (pontos individuais):** Se algumas categorias de '{coluna_y}' têm mais valores extremos de '{coluna_x}'.\n"
            )
            try:
                medianas_por_categoria = df.groupby(coluna_y)[coluna_x].median().dropna().sort_values()
                if not medianas_por_categoria.empty:
                    explicacao_boxplot_bi += (f"Por exemplo, a categoria '{medianas_por_categoria.index[0]}' em '{coluna_y}' apresenta a menor mediana para '{coluna_x}' ({medianas_por_categoria.iloc[0]:.2f}), "
                                              f"enquanto a categoria '{medianas_por_categoria.index[-1]}' tem a maior mediana ({medianas_por_categoria.iloc[-1]:.2f}).")
            except Exception:
                explicacao_boxplot_bi += f"Não foi possível calcular medianas por categoria para '{coluna_y}' e '{coluna_x}' para um exemplo detalhado."
            st.markdown(explicacao_boxplot_bi)
        
        elif df[coluna_x].dtype == 'object' and df[coluna_y].dtype == 'object':
            st.markdown('**Tabela de Contingência (Frequência Cruzada)**')
            try:
                tabela_contingencia = pd.crosstab(df[coluna_x], df[coluna_y])
                st.dataframe(tabela_contingencia)
                fig_heatmap = px.imshow(tabela_contingencia, title=f'Mapa de Calor da Frequência entre {coluna_x} e {coluna_y}',
                                        labels=dict(color="Contagem"))
                st.plotly_chart(fig_heatmap)

                st.subheader(f"Interpretação da Tabela de Contingência e Mapa de Calor ({coluna_x} vs {coluna_y})")
                explicacao_cont = (
                    f"A tabela de contingência e o mapa de calor mostram a frequência conjunta das categorias de **{coluna_x}** e **{coluna_y}**.\n"
                    f"- Cada célula na tabela/mapa indica quantos vinhos pertencem simultaneamente a uma categoria específica de '{coluna_x}' e uma categoria de '{coluna_y}'.\n"
                    f"- Cores mais intensas no mapa de calor indicam combinações de categorias mais frequentes.\n"
                    f"Isso ajuda a identificar possíveis associações ou padrões entre as duas variáveis categóricas."
                )
                st.markdown(explicacao_cont)

            except Exception as e:
                st.error(f"Não foi possível gerar a tabela de contingência: {e}")
        
        elif not (pd.api.types.is_numeric_dtype(df[coluna_x]) and pd.api.types.is_numeric_dtype(df[coluna_y])):
             st.info('Para o boxplot bivariado, uma das colunas selecionadas deve ser do tipo objeto (categórica) e a outra numérica. Se ambas forem numéricas, o gráfico de dispersão acima é mais indicado. Se ambas forem categóricas, uma tabela de contingência é mais apropriada.')

    elif len(colunas_bivariadas) != 0 and len(colunas_bivariadas) != 2:
        st.error('Por favor, escolha exatamente duas colunas para a análise bivariada.')

    st.sidebar.header("Informações Adicionais do Dataset")

    if 'Precos' in df.columns and pd.api.types.is_numeric_dtype(df['Precos']):
        st.sidebar.subheader("Preço")
        preco_medio_filtrado = round(df['Precos'].mean(skipna=True), 2)
        st.sidebar.write(f"Preço médio geral: **R$ {preco_medio_filtrado}**")

    if 'Volume (ML)' in df.columns and pd.api.types.is_numeric_dtype(df['Volume (ML)']):
        st.sidebar.subheader("Volume (ML)")
        volume_medio_filtrado = round(df['Volume (ML)'].mean(skipna=True), 2)
        st.sidebar.write(f"Volume médio geral: **{volume_medio_filtrado} ML**")

    if 'Parcela' in df.columns and pd.api.types.is_numeric_dtype(df['Parcela']):
        st.sidebar.subheader("Parcelamento")
        if df['Parcela'].nunique(dropna=True) > 1:
            maior_parcela = df['Parcela'].max(skipna=True)
            st.sidebar.write(f"Número máximo de parcelas encontrado: **{int(maior_parcela)}**")
        elif df['Parcela'].nunique(dropna=True) == 1:
            parcela_unica = df['Parcela'].unique()[0]
            st.sidebar.write(f"Todas as opções de parcelamento são: **{int(parcela_unica)}**")
        else:
            st.sidebar.write("Informação de parcelamento não disponível ou uniforme (após tratamento de nulos).")
else:
    st.warning("Os dados não puderam ser carregados. Algumas funcionalidades da aplicação podem não estar disponíveis.")

# Para rodar executar no terminal: streamlit run app.py
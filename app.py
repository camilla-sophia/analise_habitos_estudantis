import streamlit as st
import pandas as pd
import numpy as np  # NOVO: usado na linha de tendência e no simulador
import plotly.express as px
# NOVO: bibliotecas do modelo preditivo
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_validate

st.title('Dashboard: Hábitos de Estudo e Desempenho Acadêmico')


# CORRIGIDO: cache para o CSV não ser relido a cada interação
@st.cache_data
def carregar_dados():
    return pd.read_csv('student_habits_tratado.csv')


df = carregar_dados()

nomes_legiveis = {
    'student_id': 'ID',
    'study_time_hours': 'Horas de Estudo',
    'attendance_percent': 'Frequência (%)',
    'sleep_hours': 'Horas de Sono',
    'previous_grade': 'Nota Anterior',
    'final_exam_score': 'Nota Final',
    'final_grade': 'Conceito'
}

st.sidebar.header('Filtros')

genero = st.sidebar.multiselect(
    'Gênero',
    options=['Female', 'Male'],
    default=['Female', 'Male']
)

trabalho = st.sidebar.multiselect(
    'Trabalho de meio período',
    options=[True, False],
    default=[True, False]
)

extracurricular = st.sidebar.multiselect(
    'Atividades extracurriculares',
    options=[True, False],
    default=[True, False]
)

horas_estudo = st.sidebar.slider(
    'Horas de estudo (mínimo)',
    min_value=float(df['study_time_hours'].min()),
    max_value=float(df['study_time_hours'].max()),
    value=float(df['study_time_hours'].min())
)

df_filtrado = df[df['study_time_hours'] >= horas_estudo]
if 'Male' not in genero:
    df_filtrado = df_filtrado[df_filtrado['gender_Male'] == False]
if 'Female' not in genero:
    df_filtrado = df_filtrado[df_filtrado['gender_Male'] == True]
df_filtrado = df_filtrado[df_filtrado['part_time_job_Yes'].isin(trabalho)]
# CORRIGIDO: o filtro de extracurriculares existia na barra lateral, mas nunca era aplicado
df_filtrado = df_filtrado[df_filtrado['extracurricular_activities_Yes'].isin(extracurricular)]
# CORRIGIDO: .copy() evita o SettingWithCopyWarning ao criar colunas novas mais abaixo
df_filtrado = df_filtrado.copy()

# CORRIGIDO: se nenhum aluno sobrar, mostra aviso em vez de quebrar (NaN nas métricas, erro no idxmax)
if df_filtrado.empty:
    st.warning('Nenhum aluno atende aos filtros selecionados. Ajuste os filtros na barra lateral.')
    st.stop()

#dividir tela em 4 colunas
col1, col2, col3, col4 = st.columns(4)

#cria um "card" dentro da coluna 1 com o rótulo "Alunos filtrados" e um valor em baixo (quantidade de alunos que sobrou depois do filtro)
col1.metric('Alunos filtrados', len(df_filtrado))
#:.1f formata o número para uma casa decimal
col2.metric('Nota Média', f"{df_filtrado['final_exam_score'].mean():.1f}")
col3.metric('Horas de Estudo (média)', f"{df_filtrado['study_time_hours'].mean():.1f}h")
col4.metric('Frequência Média', f"{df_filtrado['attendance_percent'].mean():.1f}%")

colunas_exibicao = ['student_id', 'study_time_hours', 'attendance_percent', 'sleep_hours', 
                    'previous_grade', 'final_exam_score', 'final_grade']

tabela_exibicao = df_filtrado[colunas_exibicao].rename(columns=nomes_legiveis)
st.dataframe(tabela_exibicao, use_container_width=True, hide_index=True)

# NOVO: botão para baixar o CSV com os filtros aplicados
st.download_button('Baixar CSV filtrado', data=tabela_exibicao.to_csv(index=False).encode('utf-8'),
                   file_name='alunos_filtrados.csv', mime='text/csv')

st.subheader('Horas de Estudo x Nota Final')
# NOVO: pontos coloridos pelo conceito (a coluna final_grade só aparecia na tabela)
fig1 = px.scatter(df_filtrado, x='study_time_hours', y='final_exam_score',
                  color='final_grade', category_orders={'final_grade': ['A', 'B', 'C', 'D', 'F']},
                  labels={'study_time_hours': 'Horas de Estudo', 'final_exam_score': 'Nota Final', 'final_grade': 'Conceito'})
# NOVO: linha de tendência linear (calculada com numpy, sem precisar do statsmodels)
if df_filtrado['study_time_hours'].nunique() > 1:
    coef = np.polyfit(df_filtrado['study_time_hours'], df_filtrado['final_exam_score'], 1)
    xs = np.array([df_filtrado['study_time_hours'].min(), df_filtrado['study_time_hours'].max()])
    fig1.add_scatter(x=xs, y=np.polyval(coef, xs), mode='lines',
                     name='Tendência linear', line=dict(color='black', dash='dash'))
st.plotly_chart(fig1)

st.subheader('Distribuição da Nota Final')
fig2 = px.histogram(df_filtrado, x='final_exam_score', nbins=20, 
                    labels={'final_exam_score': 'Nota Final'})
fig2.update_layout(yaxis_title='Quantidade de Alunos')
st.plotly_chart(fig2)

# CORRIGIDO: a lista colunas_numericas estava repetida duas vezes; agora é definida uma vez só
colunas_numericas = ['study_time_hours', 'attendance_percent', 'sleep_hours', 'previous_grade', 'final_exam_score']

#calcular correlação entre variáveis numéricas com dados já filtrados
correlacao = df_filtrado[colunas_numericas].corr()

st.subheader('Mapa de Correlação entre Variáveis')

correlacao_legivel = correlacao.rename(columns=nomes_legiveis, index=nomes_legiveis)

fig3 = px.imshow(correlacao_legivel, text_auto='.2f', color_continuous_scale='RdBu_r', zmin=-1, zmax=1, labels=dict(color='Correlação'))
st.plotly_chart(fig3)

#px.imshow: criar heatmap
#text_auto='.2f': valor exato dentro de cada célula com 2 casas decimais
#color_continuous_scale='RdBu_r': definição de escala de cores (vermelho para valores negativos e azul para positivos)
#zmin=-1, zmax=1: fixa escala de cor entre -1 e 1, já que a correlação sempre fica nesse intervalo

st.subheader('Escolaridade dos Pais x Nota Final Média')

colunas_educacao = ['parental_education_Bachelors', 'parental_education_High School', 
                    'parental_education_Masters', 'parental_education_Not specified', 
                    'parental_education_PhD']

df_filtrado['parental_education_temp'] = df_filtrado[colunas_educacao].idxmax(axis=1).str.replace('parental_education_', '')

media_por_educacao = df_filtrado.groupby('parental_education_temp')['final_exam_score'].mean().reindex(
    ['Not specified', 'High School', 'Bachelors', 'Masters', 'PhD']
).reset_index()

fig4 = px.bar(media_por_educacao, x='parental_education_temp', y='final_exam_score',
              labels={'parental_education_temp': 'Escolaridade dos Pais', 'final_exam_score': 'Nota Final Média'})
# CORRIGIDO: o eixo começava em 80, o que exagerava diferenças pequenas; agora começa em 0
fig4.update_yaxes(range=[0, 100])
st.plotly_chart(fig4)
st.caption('O eixo começa em 0 de propósito: com o eixo truncado, diferenças pequenas pareceriam grandes.')


# ============================================================================
# NOVO: MODELO PREDITIVO E SIMULADOR
# ============================================================================
st.header('Modelo Preditivo da Nota Final')
st.write('Os modelos são treinados com todos os alunos (os filtros da barra lateral não afetam esta seção) '
         'e comparados por validação cruzada de 5 folds.')

# final_grade e final_grade_num ficam de fora de propósito: são derivadas da própria
# nota final, então usá-las seria vazamento de dados (data leakage)
features_modelo = ['study_time_hours', 'attendance_percent', 'sleep_hours', 'previous_grade',
                   'gender_Male', 'part_time_job_Yes', 'extracurricular_activities_Yes',
                   'internet_access_Yes'] + colunas_educacao


# cache_resource: o treino roda uma vez só, não a cada clique
@st.cache_resource
def treinar_modelos(dados):
    X = dados[features_modelo].astype(float)
    y = dados['final_exam_score']

    candidatos = {
        'Regressão Linear': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=300, min_samples_leaf=3, random_state=42, n_jobs=-1),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=200, max_depth=2, learning_rate=0.05, random_state=42),
    }

    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    linhas = []
    for nome, modelo in candidatos.items():
        cv = cross_validate(modelo, X, y, cv=kf, scoring=['r2', 'neg_mean_absolute_error'])
        linhas.append({
            'Modelo': nome,
            'R² (média CV)': cv['test_r2'].mean(),
            'MAE (média CV)': -cv['test_neg_mean_absolute_error'].mean(),
        })
    resultados = pd.DataFrame(linhas).sort_values('R² (média CV)', ascending=False)

    # treina o melhor modelo com todos os dados
    melhor_nome = resultados.iloc[0]['Modelo']
    melhor = candidatos[melhor_nome].fit(X, y)

    # importância das variáveis, calculada com Random Forest (fácil de interpretar)
    rf = RandomForestRegressor(n_estimators=300, min_samples_leaf=3, random_state=42, n_jobs=-1).fit(X, y)
    importancia = pd.DataFrame({'Variável': features_modelo, 'Importância': rf.feature_importances_})
    importancia = importancia.sort_values('Importância')

    return melhor_nome, melhor, resultados, importancia


melhor_nome, melhor_modelo, resultados, importancia = treinar_modelos(df)

st.subheader('Comparação de modelos')
st.dataframe(resultados.style.format({'R² (média CV)': '{:.3f}', 'MAE (média CV)': '{:.2f}'}),
             use_container_width=True, hide_index=True)
st.success(f"Modelo selecionado: {melhor_nome} "
           f"(R² = {resultados.iloc[0]['R² (média CV)']:.2f}, "
           f"erro médio de {resultados.iloc[0]['MAE (média CV)']:.1f} pontos)")

st.subheader('Importância das variáveis (Random Forest)')
importancia['Variável'] = importancia['Variável'].replace({
    'study_time_hours': 'Horas de Estudo',
    'attendance_percent': 'Frequência',
    'sleep_hours': 'Horas de Sono',
    'previous_grade': 'Nota Anterior',
    'gender_Male': 'Gênero (masc.)',
    'part_time_job_Yes': 'Trabalho meio período',
    'extracurricular_activities_Yes': 'Extracurriculares',
    'internet_access_Yes': 'Acesso à internet',
}).str.replace('parental_education_', 'Pais: ', regex=False)
fig5 = px.bar(importancia, x='Importância', y='Variável', orientation='h')
st.plotly_chart(fig5)

st.subheader('Simulador de nota')
st.write('Ajuste os valores e veja a nota prevista pelo modelo.')

sim1, sim2, sim3 = st.columns(3)
with sim1:
    sim_horas = st.slider('Horas de estudo por dia', 0.0, 10.0, 3.5, 0.1)
    sim_freq = st.slider('Frequência (%)', 40.0, 100.0, 85.0, 0.5)
    sim_sono = st.slider('Horas de sono', 3.0, 10.0, 7.0, 0.1)
with sim2:
    sim_nota_ant = st.slider('Nota anterior', 0.0, 100.0, 70.0, 0.5)
    sim_edu = st.selectbox('Escolaridade dos pais', ['Not specified', 'High School', 'Bachelors', 'Masters', 'PhD'])
    sim_genero = st.selectbox('Gênero', ['Female', 'Male'])
with sim3:
    sim_trab = st.checkbox('Trabalho de meio período')
    sim_extra = st.checkbox('Atividades extracurriculares', value=True)
    sim_net = st.checkbox('Acesso à internet', value=True)

# monta uma linha com as mesmas colunas usadas no treino
entrada = {
    'study_time_hours': sim_horas,
    'attendance_percent': sim_freq,
    'sleep_hours': sim_sono,
    'previous_grade': sim_nota_ant,
    'gender_Male': sim_genero == 'Male',
    'part_time_job_Yes': sim_trab,
    'extracurricular_activities_Yes': sim_extra,
    'internet_access_Yes': sim_net,
}
for coluna in colunas_educacao:
    entrada[coluna] = coluna == f'parental_education_{sim_edu}'
entrada = pd.DataFrame([entrada])[features_modelo].astype(float)

previsao = float(np.clip(melhor_modelo.predict(entrada)[0], 0, 100))
erro_medio = float(resultados.iloc[0]['MAE (média CV)'])

sim_col1, sim_col2 = st.columns(2)
sim_col1.metric('Nota final prevista', f'{previsao:.1f}')
sim_col2.metric('Faixa provável (± erro médio)', f'{max(previsao - erro_medio, 0):.0f} a {min(previsao + erro_medio, 100):.0f}')
st.caption('O modelo foi treinado com 1000 alunos: serve para explorar padrões, não para decidir sobre pessoas reais. '
           'A relação é estatística, não causal.')
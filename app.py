import streamlit as st
import pandas as pd
import plotly.express as px

st.title('Dashboard: Hábitos de Estudo e Desempenho Acadêmico')

df = pd.read_csv('student_habits_tratado.csv')

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

#dividir tela em 4 colunas
col1, col2, col3, col4 = st.columns(4)

#cria um "card" dentro da coluna 1 com o rótulo "Alunos filtrados" e um valor em baixo (quantidade de alunos que sobrou depois do filtro)
col1.metric('Alunos filtrados', len(df_filtrado))
#:.1f formata o número para uma casa decimal
col2.metric('Nota Média', f"{df_filtrado['final_exam_score'].mean():.1f}")
col3.metric('Horas de Estudo (média)', f"{df_filtrado['study_time_hours'].mean():.1f}h")
col4.metric('Frequência Média', f"{df_filtrado['attendance_percent'].mean():.1f}%")

nomes_colunas = {
    'student_id': 'ID',
    'study_time_hours': 'Horas de Estudo',
    'attendance_percent': 'Frequência (%)',
    'sleep_hours': 'Horas de Sono',
    'previous_grade': 'Nota Anterior',
    'final_exam_score': 'Nota Final'
}

st.write(df_filtrado.rename(columns=nomes_colunas).head)

st.subheader('Horas de Estudo x Nota Final')
fig1 = px.scatter(df_filtrado, x='study_time_hours', y='final_exam_score', labels={'study_time_hours': 'Horas de Estudo', 'final_exam_score': 'Nota Final'})
st.plotly_chart(fig1)

st.subheader('Distribuição da Nota Final')
fig2 = px.histogram(df_filtrado, x='final_exam_score', nbins=20, 
                    labels={'final_exam_score': 'Nota Final'})
fig2.update_layout(yaxis_title='Quantidade de Alunos')
st.plotly_chart(fig2)

st.subheader('Mapa de Correlação entre Variáveis')

colunas_numericas = ['study_time_hours', 'attendance_percent', 'sleep_hours', 'previous_grade', 'final_exam_score']

nomes_legiveis = {
    'study_time_hours': 'Horas de Estudo',
    'attendance_percent': 'Frequência (%)',
    'sleep_hours': 'Horas de Sono',
    'previous_grade': 'Nota Anterior',
    'final_exam_score': 'Nota Final'
}
#calcular correlação entre variáveis numéricas com dados já filtrados
correlacao = df_filtrado[colunas_numericas].corr()

st.subheader('Mapa de Correlação entre Variáveis')

colunas_numericas = ['study_time_hours', 'attendance_percent', 'sleep_hours', 'previous_grade', 'final_exam_score']

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
fig4.update_yaxes(range=[80,87])
st.plotly_chart(fig4)
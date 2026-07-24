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
st.write(df_filtrado.head())

st.subheader('Horas de Estudo x Nota Final')
fig1 = px.scatter(df_filtrado, x='study_time_hours', y='final_exam_score', labels={'study_time_hours': 'Horas de Estudo', 'final_exam_score': 'Nota Final'})
st.plotly_chart(fig1)

st.subheader('Distribuição da Nota Final')
fig2 = px.histogram(df_filtrado, x='final_exam_score', nbins=20, labels={'final_exam_score': 'Nota Final'})
st.plotly_chart(fig2)
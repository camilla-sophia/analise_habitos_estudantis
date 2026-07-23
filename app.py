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

st.write(f'Mostrando {len(df_filtrado)} de {len(df)} alunos')
st.write(df_filtrado.head())

st.subheader('Horas de Estudo x Nota Final')
fig1 = px.scatter(df_filtrado, x='study_time_hours', y='final_exam_score', labels={'study_time_hours': 'Horas de Estudo', 'final_exam_score': 'Nota Final'})
st.plotly_chart(fig1)

st.subheader('Distribuição da Nota Final')
fig2 = px.histogram(df_filtrado, x='final_exam_score', nbins=20, labels={'final_exam_score': 'Nota Final'})
st.plotly_chart(fig2)
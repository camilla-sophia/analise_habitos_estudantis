import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title='Hábitos e Desempenho', layout='wide')

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

colunas_educacao = [
    'parental_education_Bachelors', 'parental_education_High School',
    'parental_education_Masters', 'parental_education_Not specified',
    'parental_education_PhD',
]
educacao_pais_pt_para_en = {
    'Não especificado': 'Not specified',
    'Ensino médio': 'High School',
    'Graduação': 'Bachelors',
    'Mestrado': 'Masters',
    'Doutorado': 'PhD',
}
educacao_pais_en_para_pt = {en: pt for pt, en in educacao_pais_pt_para_en.items()}
opcoes_educacao_pais = list(educacao_pais_pt_para_en.keys())
ordem_educacao_en = ['Not specified', 'High School', 'Bachelors', 'Masters', 'PhD']
opcoes_conceito = ['A', 'B', 'C', 'D', 'F']
ordem_conceito_grafico = ['F', 'D', 'C', 'B', 'A']
opcoes_genero = ['Feminino', 'Masculino']
opcoes_sim_nao = ['Sim', 'Não']
sim_nao_para_bool = {'Sim': True, 'Não': False}


def dispersao_nota_final(dados, col_x, label_x, titulo, mostrar_legenda=True):
    fig = px.scatter(
        dados,
        x=col_x,
        y='final_exam_score',
        color='final_grade',
        category_orders={'final_grade': opcoes_conceito},
        labels={col_x: label_x, 'final_exam_score': 'Nota Final', 'final_grade': 'Conceito'},
    )
    if dados[col_x].nunique() > 1:
        coef = np.polyfit(dados[col_x], dados['final_exam_score'], 1)
        xs = np.array([dados[col_x].min(), dados[col_x].max()])
        fig.add_scatter(
            x=xs,
            y=np.polyval(coef, xs),
            mode='lines',
            name='Tendência linear',
            line=dict(color='black', dash='dash'),
            showlegend=mostrar_legenda,
        )
    fig.update_layout(
        title=dict(text=titulo, x=0.5, xanchor='center'),
        showlegend=mostrar_legenda,
        margin=dict(t=55, r=10 if not mostrar_legenda else 60),
        legend=dict(yanchor='top', y=0.98, xanchor='left', x=1.02) if mostrar_legenda else {},
    )
    return fig


st.sidebar.header('Filtros')

genero = st.sidebar.multiselect(
    'Gênero',
    options=opcoes_genero,
    default=opcoes_genero,
)

trabalho = st.sidebar.multiselect(
    'Trabalho de meio período',
    options=opcoes_sim_nao,
    default=opcoes_sim_nao,
)

extracurricular = st.sidebar.multiselect(
    'Atividades extracurriculares',
    options=opcoes_sim_nao,
    default=opcoes_sim_nao,
)

horas_estudo = st.sidebar.slider(
    'Horas de estudo (mínimo)',
    min_value=float(df['study_time_hours'].min()),
    max_value=float(df['study_time_hours'].max()),
    value=float(df['study_time_hours'].min())
)

freq_min, freq_max = st.sidebar.slider(
    'Frequência (%)',
    min_value=float(df['attendance_percent'].min()),
    max_value=float(df['attendance_percent'].max()),
    value=(float(df['attendance_percent'].min()), float(df['attendance_percent'].max())),
)

sono_min, sono_max = st.sidebar.slider(
    'Horas de sono',
    min_value=float(df['sleep_hours'].min()),
    max_value=float(df['sleep_hours'].max()),
    value=(float(df['sleep_hours'].min()), float(df['sleep_hours'].max())),
)

educacao_pais = st.sidebar.multiselect(
    'Escolaridade dos pais',
    options=opcoes_educacao_pais,
    default=opcoes_educacao_pais,
)

conceitos = st.sidebar.multiselect(
    'Conceito',
    options=opcoes_conceito,
    default=opcoes_conceito,
)

internet = st.sidebar.multiselect(
    'Acesso à internet',
    options=opcoes_sim_nao,
    default=opcoes_sim_nao,
)

df_filtrado = df[df['study_time_hours'] >= horas_estudo]
genero_male = []
if 'Feminino' in genero:
    genero_male.append(False)
if 'Masculino' in genero:
    genero_male.append(True)
df_filtrado = df_filtrado[df_filtrado['gender_Male'].isin(genero_male)]
df_filtrado = df_filtrado[df_filtrado['part_time_job_Yes'].isin([sim_nao_para_bool[v] for v in trabalho])]
df_filtrado = df_filtrado[df_filtrado['extracurricular_activities_Yes'].isin([sim_nao_para_bool[v] for v in extracurricular])]
df_filtrado = df_filtrado[
    (df_filtrado['attendance_percent'] >= freq_min)
    & (df_filtrado['attendance_percent'] <= freq_max)
    & (df_filtrado['sleep_hours'] >= sono_min)
    & (df_filtrado['sleep_hours'] <= sono_max)
]
df_filtrado = df_filtrado[df_filtrado['final_grade'].isin(conceitos)]
df_filtrado = df_filtrado[df_filtrado['internet_access_Yes'].isin([sim_nao_para_bool[v] for v in internet])]
escolaridade = df_filtrado[colunas_educacao].idxmax(axis=1).str.replace('parental_education_', '')
educacao_pais_en = [educacao_pais_pt_para_en[opcao] for opcao in educacao_pais]
df_filtrado = df_filtrado[escolaridade.isin(educacao_pais_en)]
# CORRIGIDO: .copy() evita o SettingWithCopyWarning ao criar colunas novas mais abaixo
df_filtrado = df_filtrado.copy()

# CORRIGIDO: se nenhum aluno sobrar, mostra aviso em vez de quebrar (NaN nas métricas, erro no idxmax)
if df_filtrado.empty:
    st.warning('Nenhum aluno atende aos filtros selecionados. Ajuste os filtros na barra lateral.')
    st.stop()

col1, col2, col3, col4, col5 = st.columns(5)

media_nota = df_filtrado['final_exam_score'].mean()
media_estudo = df_filtrado['study_time_hours'].mean()
media_freq = df_filtrado['attendance_percent'].mean()
pct_ab = df_filtrado['final_grade'].isin(['A', 'B']).mean() * 100

col1.metric('Alunos filtrados', len(df_filtrado))
col2.metric('Nota Média', f'{media_nota:.1f}')
col3.metric('Horas de Estudo (média)', f'{media_estudo:.1f}h')
col4.metric('Frequência Média', f'{media_freq:.1f}%')
col5.metric('Com conceito A ou B', f'{pct_ab:.1f}%')

st.subheader('Base de dados dos alunos')
colunas_exibicao = [
    'student_id', 'study_time_hours', 'attendance_percent', 'sleep_hours',
    'previous_grade', 'final_exam_score', 'final_grade',
]
tabela_exibicao = df_filtrado[colunas_exibicao].rename(columns=nomes_legiveis)
st.dataframe(tabela_exibicao, use_container_width=True, hide_index=True)
st.download_button(
    'Exportar planilha (CSV)',
    data=tabela_exibicao.to_csv(index=False).encode('utf-8'),
    file_name='alunos_filtrados.csv',
    mime='text/csv',
)

st.subheader('Distribuição dos conceitos')
contagem_conceitos = (
    df_filtrado['final_grade']
    .value_counts()
    .reindex(ordem_conceito_grafico, fill_value=0)
    .reset_index()
)
contagem_conceitos.columns = ['Conceito', 'Quantidade']
fig_conceitos = px.bar(
    contagem_conceitos,
    x='Conceito',
    y='Quantidade',
    category_orders={'Conceito': ordem_conceito_grafico},
    labels={'Quantidade': 'Quantidade de alunos'},
    text='Quantidade',
)
fig_conceitos.update_traces(textposition='outside')
st.plotly_chart(fig_conceitos, use_container_width=True)

st.subheader('Nota final por perfil')
st.caption('Média da nota final em cada grupo (recorte dos filtros aplicados).')
df_perfil = df_filtrado.copy()
df_perfil['Gênero'] = df_perfil['gender_Male'].map({True: 'Masculino', False: 'Feminino'})
df_perfil['Trabalho'] = df_perfil['part_time_job_Yes'].map({True: 'Sim', False: 'Não'})
df_perfil['Extracurriculares'] = df_perfil['extracurricular_activities_Yes'].map({True: 'Sim', False: 'Não'})

cores_perfil = ['#5B8FF9', '#61DDAA']
dimensoes_perfil = [
    ('Gênero', 'Gênero', opcoes_genero),
    ('Trabalho', 'Trabalho', opcoes_sim_nao),
    ('Extracurriculares', 'Extracurriculares', opcoes_sim_nao),
]
fig_perfil = make_subplots(
    rows=1,
    cols=3,
    subplot_titles=[titulo for titulo, _, _ in dimensoes_perfil],
    shared_yaxes=True,
    horizontal_spacing=0.06,
)
medias_perfil = []
for indice, (_, coluna, ordem) in enumerate(dimensoes_perfil, start=1):
    medias = df_perfil.groupby(coluna)['final_exam_score'].mean().reindex(ordem)
    medias_perfil.extend(medias.dropna().tolist())
    fig_perfil.add_trace(
        go.Bar(
            x=ordem,
            y=medias,
            text=[f'{valor:.1f}' if pd.notna(valor) else '' for valor in medias],
            textposition='outside',
            marker_color=cores_perfil[: len(ordem)],
            hovertemplate='%{x}<br>Nota média: %{y:.1f}<extra></extra>',
            showlegend=False,
        ),
        row=1,
        col=indice,
    )
if medias_perfil:
    y_max = min(100, max(medias_perfil) + 4)
    y_max = max(y_max, 75)
    fig_perfil.update_yaxes(title_text='Nota média', range=[70, y_max], row=1, col=1)
    fig_perfil.update_yaxes(range=[70, y_max], row=1, col=2)
    fig_perfil.update_yaxes(range=[70, y_max], row=1, col=3)
fig_perfil.update_layout(height=380, margin=dict(t=50, b=40), bargap=0.35)
fig_perfil.update_xaxes(tickangle=0)
st.plotly_chart(fig_perfil, use_container_width=True)

st.subheader('Hábitos x nota final')
hab1, hab2, hab3 = st.columns(3)
with hab1:
    st.plotly_chart(
        dispersao_nota_final(
            df_filtrado, 'study_time_hours', 'Horas de Estudo', 'Horas de estudo', mostrar_legenda=True
        ),
        use_container_width=True,
    )
with hab2:
    st.plotly_chart(
        dispersao_nota_final(
            df_filtrado, 'attendance_percent', 'Frequência (%)', 'Frequência', mostrar_legenda=False
        ),
        use_container_width=True,
    )
with hab3:
    st.plotly_chart(
        dispersao_nota_final(
            df_filtrado, 'sleep_hours', 'Horas de Sono', 'Horas de sono', mostrar_legenda=False
        ),
        use_container_width=True,
    )

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

df_filtrado['parental_education_temp'] = df_filtrado[colunas_educacao].idxmax(axis=1).str.replace('parental_education_', '')

media_por_educacao = df_filtrado.groupby('parental_education_temp')['final_exam_score'].mean().reindex(
    ordem_educacao_en
).reset_index()
media_por_educacao['parental_education_temp'] = media_por_educacao['parental_education_temp'].map(
    educacao_pais_en_para_pt
)

fig4 = px.bar(media_por_educacao, x='parental_education_temp', y='final_exam_score',
              category_orders={'parental_education_temp': opcoes_educacao_pais},
              labels={'parental_education_temp': 'Escolaridade dos Pais', 'final_exam_score': 'Nota Final Média'},
              text='final_exam_score', text_auto='.1f')
notas_educacao = media_por_educacao['final_exam_score'].dropna()
if not notas_educacao.empty:
    y_min = max(60, float(notas_educacao.min()) - 3)
    y_max = min(100, float(notas_educacao.max()) + 2)
    y_max = max(y_max, y_min + 5)
    fig4.update_yaxes(range=[y_min, y_max])
fig4.update_traces(textposition='outside')
st.plotly_chart(fig4)
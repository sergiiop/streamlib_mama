import streamlit as st
import pandas as pd
from io import StringIO
import seaborn as sns
import cufflinks as cf
import plotly as pl
import json
from textblob.classifiers import DecisionTreeClassifier
from textblob.classifiers import MaxEntClassifier
from textblob.classifiers import NaiveBayesClassifier
from pandasql import sqldf
import plotly.express as px
import plotly.figure_factory as ff
sql = lambda q: sqldf(q, globals())


with st.sidebar:
  datos = pd.read_excel('data_g.xlsx',engine='openpyxl')
  datos = datos.drop(['Unnamed: 0'],axis=1)
  datos.rename(columns = {'TIPO DE ATENCIÓN':'TIPO_ATENCION',
                          'ESCALA DE DOLOR':'ESCALADOLOR',
                          'HISTOLOGIA DEL TUMOR':'HISTOLOGIATUMOR'}, inplace = True)
df = datos
col1, col2 = st.columns(2)
with col1:
  c1 = sql("select SEXO,count(*) as CANTIDAD from df group by SEXO")
  fig = px.pie(c1, values='CANTIDAD', names='SEXO', title='DISTRIBUCION POR GENERO')
  st.plotly_chart(fig, use_container_width=True)
with col2:
  c1 = sql("select TIPO_ATENCION,count(*) as CANTIDAD from df group by TIPO_ATENCION")
  fig = px.pie(c1, values='CANTIDAD', names='TIPO_ATENCION', title='TIPO DE ATENCION')
  st.plotly_chart(fig, use_container_width=True)

c1 = sql("select DIAGNOSTICO_PPAL,count(*) as CANTIDAD from df group by DIAGNOSTICO_PPAL")
fig = px.pie(c1, values='CANTIDAD', names='DIAGNOSTICO_PPAL', title='DIAGNOSTICO PRINCIPAL')
st.plotly_chart(fig, use_container_width=True)

c1 = sql("select PLANIFICACION,count(*) as CANTIDAD from df group by PLANIFICACION")
fig = px.pie(c1, values='CANTIDAD', names='PLANIFICACION', title='PLANIFICACION')
st.plotly_chart(fig, use_container_width=True)

c1 = sql("select METODO,count(*) as CANTIDAD from df group by METODO")
fig = px.pie(c1, values='CANTIDAD', names='METODO', title='METODO DE PLANIFICACION')
st.plotly_chart(fig, use_container_width=True)
  
c1 = sql("select HISTOLOGIATUMOR,count(*) as CANTIDAD from df group by HISTOLOGIATUMOR")
fig = px.pie(c1, values='CANTIDAD', names='HISTOLOGIATUMOR', title='HISTOLOGIA DEL TUMOR')
st.plotly_chart(fig, use_container_width=True)

c1 = sql("select EDADDIAGNOSTICO,count(*) as CANTIDAD from df group by EDADDIAGNOSTICO")
fig = px.bar(c1, x='EDADDIAGNOSTICO',y='CANTIDAD', title='EDAD DE DIAGNOSTICO')
st.plotly_chart(fig, use_container_width=True)
  
#st.dataframe(df, use_container_width=True)
#st.dataframe(df.columns, use_container_width=True)


 

hide_st_style = """<style>footer {visibility: hidden;}</style>"""
st.markdown(hide_st_style, unsafe_allow_html= True)
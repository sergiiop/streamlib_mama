import streamlit as st
import pandas as pd
from io import StringIO
import seaborn as sns
import cufflinks as cf
import plotly as pl
import json
import plotly.express as px
from textblob.classifiers import DecisionTreeClassifier
from textblob.classifiers import MaxEntClassifier
from textblob.classifiers import NaiveBayesClassifier
from pandasql import sqldf
sql = lambda q: sqldf(q, globals())

def normalize_string(s):
    replacements = (("á", "a"),("é", "e"),("í", "i"),("ó", "o"),("ú", "u"),)
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    s = s.replace('(CT)','')
    return s
with open('./NLP/Train/TrainAlergia.json','r') as file_alergia_train:
  Model_alergia = NaiveBayesClassifier(file_alergia_train,format='json')
with open('./NLP/Train/TrainFumador.json','r') as file_fumador_train:
  Model_fuma = NaiveBayesClassifier(file_fumador_train,format='json')
with open('./NLP/Train/TrainCancerMama.json','r') as file_cm_train:
  Model_Mama = NaiveBayesClassifier(file_cm_train,format='json')
text_prueba = 'hipertension arterial losartan 100 mg dia hidroclorotiazida niega alergias no fumadora quirurgicos: cesarea'
#print(text_prueba)
#print('Modelo Alergia',Model_alergia.classify(text_prueba))
#print('Modelo Fumador',Model_fuma.classify(text_prueba))
#print('Modelo Mama',Model_Mama.classify(text_prueba))

with st.sidebar:
  st.subheader("Fuente de datos")
  if st.button('Volver analizar data'):
    jsonData = './CAMAMAJSON.json'
    with open(jsonData) as archivo_json:
      datos_json = json.load(archivo_json)
    lista_de_diccionarios = datos_json['RECORDS']
    df = pd.DataFrame(lista_de_diccionarios)
    df = sql("select *, FECHAHC-FNACIMIENTO AS EDADDIAGNOSTICO from df")
    df['TIPO DE ATENCIÓN'][df['TIPO DE ATENCIÓN']=='']='Sin data'
    df['ESCALA DE DOLOR'][df['ESCALA DE DOLOR']=='']='Sin data'
    df['PLANIFICACION'][df['PLANIFICACION']=='']='Sin data'
    df['EDAD DE MENARQUÍA'][df['EDAD DE MENARQUÍA']=='']=0
    df['HISTOLOGIA DEL TUMOR'][df['HISTOLOGIA DEL TUMOR']=='']='Sin data'
    df['METODO'][df['METODO']=='']='Sin data'
    df = df.drop(['FECHAHC', 'TIPO_DOC','EDAD', 'PLANTILLA', 'INFORMACIÓN GENERAL','ANAMNESIS','MOTIVO DE LA CONSULTA',
       'FECHA DE DIAGNOSTICO OTRO CANCER', 'TIPO DE CANCER ANTECEDENTE','DIAGNOSTICO','FECHA MUESTRA ESTUDIO HISTOPATOLOGICO','FECHA INFORME ESTUDIO HISTOPATOLOGICO','LABORATORIO INFORME HISTOPATOLOGIA','PRUEBA HER2 ANTES DEL INICIO DE TRATAMIENTO', 'FECHA PRUEBA HER2','CÁNCER COLORECTAL, ESTADIFICACIÓN DUKES','FECHA ESTADIFICACIÓN DUKES', 'CÁNCER DE PROSTATA VALOR DE GLEASON','CLASIFICACIÓN DE RIESGO LEUCEMIAS O LINFOMAS ','FECHA DE CLASIFICACIÓN DEL RIESGO', 'ANTECEDENTES GENITOURINARIOS','UROLOGICOS', 'OTROS', 'GINECO-OBSTETRICOS', 'G/P/A/C/V/M','FECHA ULTIMA MESTRUACIÓN', 'CICLOS','EXAMEN FISICO', 'CABEZA Y CUELLO','CARDIOPULMUNAR', 'ABDOMEN', 'GENITOURINARIO', 'EXTREMIDADES','NEUROLÓGICO', 'TEGUMENTARIO', 'PARACLINICOS','EXAMENES INICIALES', 'EXAMENES DE SEGUIMIENTO','ANTECEDENTES FARMACOLÓGICOS','FECHA DE ESTADIFICACIÓN','TRATAMIENTO', 'OPINIÓN', 'PLAN DE TRATAMIENTO','CUIDADOS PALIATIVOS'],axis=1)
    df['alergia_ap']=''
    df['fuma_ap']=''
    df['mama_af']=''
    for fila in range(len(df)):
      input_ap = normalize_string(str(df['ANTECEDENTES PERSONALES'][fila].replace('.',' ').replace('\n',' ').replace('\r',' ').replace('-','').replace('**','').replace('  ',' ')).lower())
      input_af = normalize_string(str(df['ANTECEDENTES FAMILIARES'][fila].replace('.',' ').replace('\n',' ').replace('\r',' ').replace('-','').replace('**','').replace('  ',' ')).lower())
      if (input_ap.__contains__('aler')):
        df.alergia_ap[fila] = Model_alergia.classify(input_ap[input_ap.find('aler')-3:input_ap.find('aler')]+input_ap[input_ap.find('aler'):input_ap.find('aler')+32])
      else:
        df.alergia_ap[fila] = 'NO'
      if (input_ap.__contains__('fum')):
        df.fuma_ap[fila] = Model_fuma.classify(input_ap[input_ap.find('fum')-3:input_ap.find('fum')]+input_ap[input_ap.find('fum'):input_ap.find('fum')+32])
      else:
        df.fuma_ap[fila] = 'NO'      
      if (input_af.__contains__('ma') or input_af.__contains__('seno')):
        df.mama_af[fila] = Model_Mama.classify(input_af[input_af.find('ma')-3:input_af.find('ma')]+input_af[input_af.find('ma'):input_af.find('ma')+32])
      else:
        df.mama_af[fila] = 'NO'
    #df_sin = sql("select *, FECHAHC-FNACIMIENTO AS EDADDIAGNOSTICO from df")
    df.to_excel('data.xlsx', engine='xlsxwriter') 
    #df_g = sql("select *, MIN(FECHAHC)-FNACIMIENTO AS EDADDIAGNOSTICO from df group by IDAFILIADO")
    df_g = sql("select * from df group by IDAFILIADO")
    df_g.to_excel('data_g.xlsx', engine='xlsxwriter') 
    st.write('Data analizada...')

  paciente_grupo = st.sidebar.radio("Usar datos agrupados por paciente",('Si', 'No'))
  if paciente_grupo=='Si':
    datos = pd.read_excel('data_g.xlsx',engine='openpyxl')
  else:
    datos = pd.read_excel('data.xlsx',engine='openpyxl')
  datos = datos.drop(['Unnamed: 0'],axis=1)
st.header("Modulo Estadistico")
df = datos
filtro = st.sidebar.radio("Activar filtro",('Descactivado', 'Activado'))
Columnas = st.sidebar.multiselect("Seleccione columna para mostrar:",df.columns,)
Grupos = st.sidebar.selectbox("Contar por:",Columnas,)
option = st.selectbox(
        "Que tipo de grafico quiere",
        ("Barra", "Area", "Linea"),)
if filtro=='Activado':
    col1, col2, col3 = st.columns(3)
    with col1:
      in1_f1 = st.selectbox('Variable de filtro',df.columns.to_list())
    with col2:
      in1_f2 = st.selectbox('Operacion',('==','!=','>','<','>=','<='))
    with col3:
      in1_f3 = st.selectbox('Datos unicos',df[in1_f1].unique())
    if in1_f2=='==':
      df = df[df[in1_f1]==in1_f3]
    if in1_f2=='!=':
      df = df[df[in1_f1]!=in1_f3]
    if in1_f2=='>':
      df = df[df[in1_f1]>in1_f3]
    if in1_f2=='>=':
      df = df[df[in1_f1]>=in1_f3]
    if in1_f2=='<':
      df = df[df[in1_f1]<in1_f3]
    if in1_f2=='<=':
      df = df[df[in1_f1]<=in1_f3]

if len(Columnas)!=0:
  df = df[Columnas]
if Grupos:
  df = df[Columnas].groupby(Grupos).count()

if Grupos: #len(Grupos):!=0:
  if option=='Barra':
    st.bar_chart(df)
  if option=='Linea':
    st.line_chart(df)
  if option=='Area':
    st.area_chart(df)
    
st.dataframe(df, use_container_width=True)
if len(Columnas)>2:
  st.subheader('Estadistica descriptiva')
  st.dataframe(df.describe(), use_container_width=True)


hide_st_style = """<style>footer {visibility: hidden;}</style>"""
st.markdown(hide_st_style, unsafe_allow_html= True)
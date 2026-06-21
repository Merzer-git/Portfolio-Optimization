import plotly.express as px
import numpy as np
import pandas as pd
import plotly.graph_objects as go

def plot_barRetornos(df_retornos, df_resultados):
  """
      Calcula y grafica la contribución al retorno de cada activo en el portafolio.
      
      Parámetros:
      - df_retornos: pd.Series o pd.DataFrame con los retornos esperados (index = tickers).
      - df_resultados: pd.DataFrame con columnas ['Activo', 'Proporción'].
  """
  df_plot = df_resultados.copy()
  if isinstance (df_retornos, pd.DataFrame):
    dict_retornos = df_retornos.iloc[:, 0].to_dict()
  else:
    dict_retornos = df_retornos.to_dict()

  df_plot['Retorno_Esperado'] = df_plot['Activo'].map(dict_retornos)
  df_plot['Contribucion'] = df_plot['Proporción'] * (df_plot['Retorno_Esperado'] - 1)
  df_plot = df_plot.sort_values(by='Contribucion', ascending=True)

  fig = go.Figure(go.Bar(
    y= df_plot['Activo'],
    x= df_plot['Contribucion'],
    orientation= 'h',
    marker= dict(
      color= '#0f62fe',
      line= dict(width=0)
    ),
    text= [f"{(val * 100):.2f}%" for val in df_plot['Contribucion']],
    textposition= 'inside',
    textfont= dict(color='white', size=13)
  ))
  fig.update_layout(
    margin=dict(l=0, r=0, t=10, b=0), # Márgenes ajustados al contenedor de Streamlit
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#E0E0E0', family='IBM Plex Sans'),
    xaxis=dict(
        showgrid=False, # Ocultamos la grilla X para evitar ruido visual
        zeroline=True,
        zerolinecolor='#5a5a5a',
        showticklabels=False # Ocultamos los números del eje X porque ya están en las barras
    ),
    yaxis=dict(
        showgrid=False,
        tickfont=dict(size=14, color='white')
    ),
    showlegend=False,
    height=330 # Altura controlada para alinearse con el pie chart
  )
  
  return fig
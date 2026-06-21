from numpy.f2py.auxfuncs import isintent_dict
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def plot_cascada(wealth_actual, df_resultados, df_retornos):
  """
  Calcula y grafica la proyección monetaria del portafolio en un Waterfall chart.
  
  Parámetros:
  - wealth_actual: Int/Float con el capital inicial invertido.
  - df_resultados: pd.DataFrame con columnas ['Activo', 'Proporción'].
  - df_retornos: pd.Series o pd.DataFrame con los retornos esperados.
  """
  df_plot = df_resultados.copy()
  if isinstance (df_retornos, pd.DataFrame):
    dict_retornos = df_retornos.iloc[:,0].to_dict()
  else:
    dict_retornos = df_retornos.to_dict()

  df_plot['Retorno_Esperado'] = df_plot['Activo'].map(dict_retornos)
  df_plot['Capital_Asignado'] = wealth_actual * df_plot['Proporción']
  df_plot['Ganancia_Proyectada'] = df_plot['Capital_Asignado'] * (df_plot['Retorno_Esperado'] - 1)

  nombres = ['Capital Inicial'] + df_plot['Activo'].tolist() + ['Capital Nom. Esperado']
  medidas = ['absolute'] + ['relative'] * len(df_plot) + ['total']
  valores = [wealth_actual] + df_plot['Ganancia_Proyectada'].tolist() + [0]
  textos = [f"${wealth_actual:,.0f}"] + [f"${val:+,.0f}" for val in df_plot['Ganancia_Proyectada']] + [""]

  fig = go.Figure(go.Waterfall(
    name= 'Proyección',
    orientation= 'v',
    measure= medidas,
    x= nombres,
    textposition= 'outside',
    text= textos,
    y= valores,
    connector= {
      'line': {
        'color': '#5a5a5a',
        'width': 1,
        'dash': 'solid'
      }
    },
    decreasing= {
      'marker': {
        'color': '#da1e28'
      }
    },
    increasing= {
      'marker': {
        'color': '#24A148'
      }
    },
    totals= {
      'marker': {
        'color': '#0f62fe'
      }
    }
  ))

  fig.update_layout(
    margin= dict(l=0, r=0, t=25, b=0),
    paper_bgcolor= '#383838',
    plot_bgcolor = '#383838',
    font= dict(color='#e0e0e0', family= 'IBM Plex Sans'),
    xaxis= dict(
      showgrid= False,
      tickfont= dict(size=13, color='White')
    ),
    yaxis= dict(
      showgrid= True,
      gridcolor= '#333333',
      zeroline= True,
      zerolinecolor= '#5a5a5a',
      tickfont= dict(size=13, color='White')
    ),
    showlegend= False,
    height= 330
  )
  return fig
import plotly.express as px
import pandas as pd
import numpy as np

def plot_heatmap(matriz):
  labels_matriz = matriz.columns.tolist()

  fig = px.imshow(
    matriz,
    text_auto= '.2f',
    labels= dict(x="", y="", color= "Covarianza"),
    x= labels_matriz,
    y= labels_matriz,
    color_continuous_scale= 'Blues',
    aspect= 'equal'
  )

  bg_color = '#383838'
  fig.update_layout(
    plot_bgcolor= bg_color,
    paper_bgcolor= bg_color,
    coloraxis_showscale= False,
    xaxis= dict(
      showgrid= False,
      zeroline= False,
      color= 'White',
      side= 'top'
    ),
    yaxis= dict(
      showgrid= False,
      zeroline= False,
      color= 'White',
      autorange= 'reversed'
    ),
    margin= dict(l=40, r=40, t=60, b=40),
    title= dict(
      text= '',
      font= dict(size=18, color= 'white'),
      y= 0.95,
      x= 0.05,
      xanchor= 'left'
    ),
    height= 500
  )

  fig.update_yaxes(tickangle= 90)
  return fig
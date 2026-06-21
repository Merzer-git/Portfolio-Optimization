import plotly.express as px
import pandas as pd
import numpy as np

def plot_piechart(allocation):
  fig = px.pie(
    allocation,
    names= 'Activo',
    values= 'Proporción',
    hole= 0.5,
    template= 'plotly_dark',
    color_discrete_sequence= px.colors.sequential.Blues_r
  )
  fig.update_traces(
    textposition= 'inside',
    textinfo= 'percent+label',
    # hole= "<b>%{label}</b><br>Asignación: %{percent}<br><extra></extra>",
    marker= dict(line=dict(color='#111111', width=2))
  )
  fig.update_layout(
    plot_bgcolor='#383838',
    paper_bgcolor='#383838',
    showlegend= False,
    margin= dict(t=20, b=20, l=20, r=20),
    hoverlabel= dict(bgcolor='#222222', font_size=14),
    height= 300
  )

  return fig
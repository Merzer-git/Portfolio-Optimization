import plotly.graph_objects as go
import pandas as pd

def plot_barchart(df_retornos):
    """
    Toma el DataFrame con factores (ej: 1.205), lo pasa a porcentaje (20.5%),
    y devuelve un gráfico de barras horizontales estilizado.
    """
    porcentajes = (df_retornos['retorno_total'] - 1) * 100
    df_plot = pd.DataFrame({
        'Ticker': porcentajes.index,
        'Retorno (%)': porcentajes.values
    })
    df_plot = df_plot.sort_values(by='Retorno (%)', ascending=True)

    fig = go.Figure(go.Bar(
      y= df_plot['Ticker'],
      x= df_plot['Retorno (%)'],
      orientation= 'h',
      marker= dict(
        color= '#0f62f3',
        line= dict(width=0)
      ),
      text= [f"{val:.2f}%" for val in df_plot['Retorno (%)']],
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
    height=500 # Altura controlada para alinearse con el pie chart
  )
    # fig = px.bar(
    #     df_plot, 
    #     x='Retorno (%)', 
    #     y='Ticker', 
    #     orientation='h',
    #     # Agregamos el símbolo de % al texto de la barra
    #     text=df_plot['Retorno (%)'].apply(lambda x: f"{x:.2f}%"), 
    # )

    # fig.update_layout(
    #     plot_bgcolor='#383838',
    #     paper_bgcolor='#383838',
    #     margin=dict(l=20, r=40, t=40, b=20),
    #     xaxis=dict(showgrid=False, zeroline=False, visible=False), # Ocultamos el eje X
    #     yaxis=dict(showgrid=False, zeroline=False, color="white", title=""),
    #     # Configuración del título
    #     title=''
    # )
    # fig.update_traces(
    #     marker_color="#0f62fe", # El azul de IBM/tu diseño original
    #     textposition="inside", 
    #     textfont_color="white"
    # )

    return fig
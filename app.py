import streamlit as st
import numpy as np
import pandas as pd
import os
from datetime import datetime
from streamlit.elements.lib.column_types import TextColumn
from streamlit_extras.metric_cards import style_metric_cards
from src.loader.data_loader import load_data, get_lista_tickers, filter_data
from src.assets.logica_activos import get_activos
from src.graphs.barchart_retornos import plot_barchart
from src.graphs.heatmap_covarianza import plot_heatmap
from src.connection.conector_ibm import ejecutar_optimizacion_ibm
from src.graphs.barchart_resultados import plot_barRetornos
from src.graphs.piechart_resultados import plot_piechart
from src.graphs.cascada_resultado import plot_cascada
from src.graphs.frontera_eficiente import plot_frontera_eficiente

st.set_page_config(
  page_title= 'Portofolio Optimizer',
  layout= 'wide',
  initial_sidebar_state='collapsed'
)

# Styles CSS
st.markdown("""
  <style>
  /* IBM Plex */
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');
  html, body, [class*="css"] {
      font-family: 'IBM Plex Sans', sans-serif !important;
  }

  /* Reducción del margen superior por defecto */
  .block-container {
    padding-top: 2rem !important;
    padding-bottom: 1rem !important;
  }

  /* Fondo general */
  .stApp {
      background-color: #111111;
      color: white;
  }

  /* Sidebar */
  section[data-testid="stSidebar"] {
      background-color: #303030;
      width: 330px !important;
  }
  section[data-testid="stSidebar"] > div {
      padding-top: 1rem;
  }

  /* Ocultar botón colapsar */
  [data-testid="stSidebarCollapseButton"] {
      display: none !important;
  }

  /* Título sidebar */
  .sidebar-title {
      font-size: 34px;
      font-weight: 300;
      padding-bottom: 20px;
  }

  /* Secciones sidebar */
  .sidebar-section {
      color: #E0E0E0;
      font-size: 14px;
      font-weight: 500;
      margin-top: 25px;
      margin-bottom: 10px;
      letter-spacing: .5px;
  }

  /* 1. Forma y tamaño global para TODOS los botones */
  .stButton button {
      border-radius: 18px !important;
      height: 60px !important;
      width: 100% !important;
      /* font-size: 30px !important; (Descomentá esto si realmente querés la letra tan grande) */
  }
  
  /* 2. Diseño para los botones INACTIVOS (Conservador, etc. cuando no están seleccionados) */
  .stButton button[kind="secondary"] {
      background-color: transparent !important;
      color: white !important;
      border: 1px solid #7a7a7a !important;
  }
  
  .stButton button[kind="secondary"]:hover {
      border-color: white !important;
      background-color: transparent !important; /* Evita el destello de color nativo */
      color: white !important;
  }
  
  /* 3. Diseño BLINDADO para el botón ACTIVO (El que tocaste) */
  .stButton button[kind="primary"] {
      background-color: #0f62fe !important; /* Azul IBM */
      border: 1px solid #0f62fe !important;
      color: white !important;
  }
  
  .stButton button[kind="primary"]:hover {
      background-color: #0353e9 !important; /* Un azul apenitas más oscuro para el hover */
      border-color: #0353e9 !important;
  }

  /* Job Status */
  .job-box {
      position: fixed;
      bottom: 25px;
      left: 25px;
      width: 260px;
      background-color: #222222;
      border: 1px solid #666;
      border-radius: 18px;
      padding: 15px;
  }
  .job-title {
      font-size: 18px;
      font-weight: 600;
  }
  .job-subtitle {
      color: #B0B0B0;
      font-size: 14px;
  }

  /* Título principal */
  .page-title {
      font-size: 56px;
      font-weight: 300;
      margin-bottom: 0;
  }
  .page-subtitle {
      color: #C0C0C0;
      font-size: 24px;
      margin-top: -5px;
  }

  /* Tabla configuración */
  .label {
      color: white;
      font-size: 18px;
      margin-bottom: 18px;
  }
  .value {
      color: white;
      font-size: 18px;
      text-align: right;
      margin-bottom: 18px;
  }
  .connected {
      color: #24A148;
      font-size: 18px;
      text-align: right;
  } /* <-- ACA FALTABA LA LLAVE DE CIERRE */

  /* Forzar altura uniforme en las Metrics Cards */
  div[data-testid="stMetric"] { /* <-- stMetric sin el punto */
    height: 125px !important; /* <-- height bien escrito */
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  /* Tarjetas genéricas con key que contenga la palabra 'tarjeta' */
  div[class*="st-key-tarjeta"] { /* <-- class*= para que funcione como comodín */
    background-color: #383838 !important;
    border: 1px solid #5a5a5a !important; /* <-- # en lugar de $ */
    border-radius: 12px !important;
    padding: 25px !important;
  }
  /* =========================================
       ESTILOS PARA INPUTS (Number y Text)
       ========================================= */
    /* Atrapa cualquier key que empiece con 'mi_input_' */
    div[class*="st-key-input"] div[data-baseweb="input"] {
        background-color: #222222 !important; /* Gris oscuro hundido */
        border: 1px solid #5a5a5a !important;
        border-radius: 6px !important;
    }

    /* =========================================
       ESTILOS PARA SELECTBOX Y MULTISELECT
       ========================================= */
    /* Atrapa la caja principal desplegable */
    div[class*="st-key-select"] div[data-baseweb="select"] {
        background-color: #222222 !important;
        border: 1px solid #5a5a5a !important;
        border-radius: 6px !important;
    }

    /* Pinta las "etiquetas/pastillas" del Multiselect con el azul de IBM */
    div[class*="st-key-select"] span[data-baseweb="tag"] {
        background-color: #0f62fe !important;
        border: none !important;
        color: white !important;
    }

    /* =========================================
       ESTILOS PARA CHECKBOX
       ========================================= */
    /* Apunta al cuadradito específico que se tilda */
    div[class*="st-key-check"] div[data-baseweb="checkbox"] > div:first-child {
        background-color: #222222 !important;
        border: 1px solid #5a5a5a !important;
    }
    /* Cuando el checkbox está seleccionado (azul) */
    div[class*="st-key-check"] input:checked + div {
        background-color: #0f62fe !important;
        border-color: #0f62fe !important;
    }
    .flotante-inferior {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #111111; /* Mismo color de tu fondo */
        border-top: 1px solid #333;
        padding: 20px 0;
        z-index: 9999; /* Para que quede por encima de todo */
    }
    @media print {
      /* 1. Aniquilar la barra lateral, el header y los botones flotantes */
      header, [data-testid="stSidebar"], [data-testid="stToolbar"], .stDeployButton {
          display: none !important;
      }
      
      /* 2. Evitar que las tarjetas y gráficos se corten a la mitad de la hoja */
      div[data-testid="stVerticalBlock"] > div, 
      div[data-testid="stHorizontalBlock"] {
          page-break-inside: avoid !important;
      }
      
      /* 3. Ajustar márgenes de la hoja física */
      @page {
          margin: 1.5cm;
      }
    }
    
  </style>
""", unsafe_allow_html=True)

# Globals
df_base = load_data()
lista_tickers = get_lista_tickers(df_base)
dic_rho = {
  "Conservador": 10,
  "Moderado": 5,
  "Agresivo": 1
}

# SESSION STATE
# 1. Perfil, RHO y Capital (Agrupado y limpio)
if 'perfil_elegido' not in st.session_state:
    st.session_state['perfil_elegido'] = "Moderado"
    st.session_state['rho_cplex'] = dic_rho["Moderado"]
    st.session_state['wealth_cplex'] = 1000
# 2. Las variables de la matemática (Inicializadas en None o DF vacío)
if 'retornos_esperados' not in st.session_state:
    st.session_state['retornos_esperados'] = None
if 'matriz_covarianza' not in st.session_state:
    st.session_state['matriz_covarianza'] = None
# 3. La bandera del semáforo para el botón de Ejecutar
if 'datos_listos' not in st.session_state:
    st.session_state['datos_listos'] = False
if 'pdf' not in st.session_state:
  st.session_state['pdf'] = None

col_header = st.columns([5,2])
with col_header[0]:
  st.markdown("""
    <div class="page-title">
      Portfolio Optimizer
    <div>
    """, unsafe_allow_html=True)

with col_header[1]:
  ruta_db = 'data/database.parquet'
  if os.path.exists(ruta_db):
    timestamp = os.path.getmtime(ruta_db)
    fecha_modificacion = datetime.fromtimestamp(timestamp)
    fecha_str = fecha_modificacion.strftime('%d/%m/%Y')
  else:
    fecha_str = 'Desconocida'
  st.markdown(f"""
      <div style='text-align: right; color: #8a8a8a; font-size: 15px; padding-top: 45px;'>
          Actualización de Activos: {fecha_str}
      </div>
    """, unsafe_allow_html=True)

# Configuración del Modelo y Datos de Entrada
col_mod_data = st.columns(2)
with col_mod_data[0]:
  with st.container(key='tarjeta_info', border=True):
    st.markdown('##### Acerca del Optimizador')
    st.markdown("""
      Esta herramienta construye un portafolio de inversión óptimo analizando datos historicos del mercado de capitales. El objetivo es encontrar la combinacion de activos que maximice la rentabilidad esperada de la cartera respetando el nivel de riesgo asumido por el inversor.

      El motor lógico esta basado en la **Teoría Moderna de Portafolios** fundamentada en la publicación original [*Portfolio Selection* (Harry Markowitz, 1952)](https://www.jstor.org/stable/2975974). Este problema de optimizacion del tipo cuadrático se resuelve en la nube utilizando el solver de **IBM Watson Studio**
      
      El modelo busca maximizar el retorno esperado penalizado por la varianza (riesgo), ponderado por el factor de aversión al riesgo del inversor:
      """)
    st.latex(r"\max \left( \sum_{i=1}^{n} w_i \mu_i - \frac{\rho}{2} \sum_{i=1}^{n} \sum_{j=1}^{n} w_i w_j \sigma_{ij} \right)")
    st.markdown(r"""
      *Donde $w$ son los pesos del portafolio, $\mu$ los retornos esperados, $\sigma$ la matriz de covarianza y $\rho$ la aversión al riesgo.*

      Para asegurar una cartera realista, el solver opera bajo una estrategia *long-only* (sin ventas en corto) y asignación total del capital:
      """)
    st.latex(r"\sum_{i=1}^{n} w_i=1 \quad \text{y} \quad w_i \ge 0")
    # st.divider()
    st.markdown("""
      *Desarrollado por: Brian Alaníz y Juan José Caputo*
      """)

with col_mod_data[1]:
  with st.container(key='tarjeta_config', border=True):
    st.markdown('##### Parámetros del Modelo')
    st.session_state['wealth_cplex'] = st.number_input('Capital inicial de inversión', min_value=1000, max_value=1000000, value=1000, key='input_config')

    st.markdown('###### Selecciona tu perfíl inversion.')
    col_perfiles = st.columns(len(dic_rho))
    for idx, (perfil, valor_rho) in enumerate(dic_rho.items()):
      with col_perfiles[idx]:
        es_primario = 'primary' if st.session_state['perfil_elegido'] == perfil else 'secondary'
        if st.button(perfil, use_container_width=True, type=es_primario):
          st.session_state['perfil_elegido'] = perfil
          st.session_state['rho_cplex'] = valor_rho
          st.rerun()
      st.write('')

with col_mod_data[1]:
  with st.container(key='tarjeta_inversiones', border=True):
    st.markdown('##### Selector de Inversiones')
    inversiones = st.multiselect(
      '',
      options = lista_tickers,
      default= [],
      label_visibility= 'collapsed',
      key= 'select_datos'
    )

    st.markdown('##### Período de Tiempo')
    rango_tiempo = st.selectbox(
      '',
      options= ['1 Año', '3 años', '5 Años', '10 Años', 'Máximo'],
      index= 2,
      label_visibility= 'collapsed',
      key= 'select_tiempo'
    )

    cols_boton_entrada = st.columns([1,2,1])
    with cols_boton_entrada[1]:
      if st.button('Obtener datos', use_container_width=True, key='btn_getDatos'):
        df_filtrado = filter_data(df_base, inversiones)
        ticker_a_descargar = df_filtrado['Ticker'].tolist()
        retornos_esperados, matriz_covarianza, retornos_diarios = get_activos(ticker_a_descargar, rango_tiempo)
        
        st.session_state['datos_activos'] = df_filtrado
        st.session_state['ticker_activos'] = ticker_a_descargar
        st.session_state['retornos_esperados'] = retornos_esperados
        st.session_state['matriz_covarianza'] = matriz_covarianza
        st.session_state['retornos_diarios'] = retornos_diarios
        st.session_state['datos_listos'] = True
        # st.success(f'Datos Obtenidos: {len(inversiones)} activos')

# with st.container(key='tarjeta_graficosEntradas', border=True):
# Graficos sobre datos de entrada

col_entradas = st.columns(2)
if st.session_state['matriz_covarianza'] is not None and st.session_state['retornos_esperados'] is not None:
  matriz = st.session_state['matriz_covarianza']
  retornos = st.session_state['retornos_esperados']

  with col_entradas[0]:
    with st.container(key='tarjeta_retornos', border=True):
      st.markdown('##### Retornos Esperados')
      fig_retornos = plot_barchart(retornos)
      st.session_state['_fig_retornos'] = fig_retornos
      st.plotly_chart(fig_retornos, use_container_width=True)
  with col_entradas[1]:
    with st.container(key='tarjeta_covarianza', border=True):
      st.markdown('##### Matriz de Covarianza')
      fig_covarianza = plot_heatmap(matriz)
      st.session_state['_matriz_covarianza'] = fig_covarianza
      st.plotly_chart(fig_covarianza, use_container_width=True)

# Lógica del Botón
wealth_actual = st.session_state['wealth_cplex']
datos_ok = st.session_state['datos_listos']
modelo_listo = (wealth_actual > 0) and datos_ok

with st.container(vertical_alignment='center'):
  st.markdown("<hr style='margin: 0; border-color: #444;'>", unsafe_allow_html=True)
  cols_bottom = st.columns([1,2,1])

  with cols_bottom[1]:
    st.write('')
    if st.button('▶ Ejecutar Job', use_container_width=True, disabled=not modelo_listo, type='primary'):
      with st.status('Procesando...', expanded=False) as status:
        resultados = ejecutar_optimizacion_ibm(
          df_returns= st.session_state['retornos_esperados'],
          df_covarianza= st.session_state['matriz_covarianza'],
          capital= wealth_actual,
          rho= st.session_state['rho_cplex']
        )

        if resultados['status'] == 'success':
          status.update(label='¡Optimización Completada!', state='complete', expanded=False)
          st.session_state['resultados'] = resultados
        else:
          st.error("Error en en el Solver")
  st.markdown("<hr style='margin: 0; border-color: #444;'>", unsafe_allow_html=True)

if 'resultados' in st.session_state:
  st.write('')

  wealth_actual = st.session_state['wealth_cplex']
  rho_actual = st.session_state['rho_cplex']
  perfil_actual = st.session_state['perfil_elegido']
  matriz_cov = st.session_state['matriz_covarianza']
  tickers_cov = matriz_cov.columns
  df_retornos = st.session_state['retornos_esperados']
  retornos_diarios = st.session_state['retornos_diarios']
  
  resultados_actual = st.session_state['resultados']
  retorno_obtenido = float(resultados_actual['ganancia_proporcion'])
  retorno_neto = (retorno_obtenido - 1) * 100
  
  capital_esperado = float(resultados_actual['ganancia_real'])
  diccionario_pesos = {item['Activo'].replace('_', '').strip(): item['Proporción'] for item in resultados_actual['pesos']}
  df_resultados = pd.DataFrame(list(diccionario_pesos.items()), columns=['Activo', 'Proporción'])
  vector_pesos = np.array([diccionario_pesos.get(t, 0.0) for t in tickers_cov])
  str_wealth = '$' + str(wealth_actual)

  if isinstance(df_retornos, pd.DataFrame):
    dict_ret_temp = df_retornos.iloc[:,0].to_dict()
  else:
    dict_ret_temp = df_retornos.to_dict()
    
  vector_retornos_brutos = np.array([dict_ret_temp.get(t, 0.0) for t in tickers_cov])
  retorno_nominal_bruto = np.dot(vector_pesos.T, vector_retornos_brutos)
  retorno_nominal_pct = (retorno_nominal_bruto - 1) * 100
  capital_esperado_nominal = wealth_actual * retorno_nominal_bruto
  varianza_portafolio = np.dot(vector_pesos.T, np.dot(matriz_cov, vector_pesos))
  volatilidad_portafolio = np.sqrt(varianza_portafolio)
  
  col_metricas_sup = st.columns(5)
  col_metricas_inf = st.columns(5)
  with col_metricas_sup[0]:
    st.metric('Perfil Inversor', value=perfil_actual)
    
  with col_metricas_sup[1]:
    st.metric('Capital Inicial', value=str_wealth)
    
  with col_metricas_sup[2]:
    st.metric('Capital Proyectado', value=f"${capital_esperado_nominal:.2f}", help='Proyección del capital final basada estrictamente en la rentabilidad histórica ponderada, sin descontar penalizaciones por riesgo.')
    
  with col_metricas_sup[3]:
    st.metric('Retorno Proyectado', value=f"{retorno_nominal_pct:.2f}%", help='Ganancia financiera bruta esperada de la cartera óptima.')
    
  with col_metricas_sup[4]:
    st.metric('Score de Utilidad', value=f"{retorno_neto:.2f}%", help='Ganancia proyectada por la función objetivo tras aplicar la penalización de varianza del modelo de Markowitz.')
  
  with col_metricas_inf[0]:
    volatilidad_pct = volatilidad_portafolio * 100
    st.metric('Volatilidad (σ)', value=f"{volatilidad_pct:.2f}%", help='Desviación estándar anualizada. Mide la dispersión de los retornos; a menor valor, mayor estabilidad.')
    
  with col_metricas_inf[1]:
    z_score = 1.645
    var_95 = (z_score * volatilidad_portafolio) - retorno_nominal_bruto
    st.metric('Value at Risk (Var)', value=f'{var_95 * 100:.2f}%', help='Pérdida máxima esperada para el capital con un 95% de nivel de confianza.')
    
  with col_metricas_inf[2]:
    retornos_diarios_portafolio = np.dot(retornos_diarios.values, vector_pesos)
    capital_acumulado = (1 + retornos_diarios_portafolio).cumprod()
    picos_historicos = np.maximum.accumulate(capital_acumulado)
    caidas_diarias = (capital_acumulado - picos_historicos) / picos_historicos
    max_drawdown = np.min(caidas_diarias)
    st.metric('Max Drawdown', value=f'{max_drawdown * 100:.2f}%', help='La peor caída histórica real observada desde un pico hasta un valle. Mide el riesgo de perdida extrema.')
    
  with col_metricas_inf[3]:
    tasa_libre_riesgo = 0.04
    ratio_sharpe = (retorno_nominal_bruto - tasa_libre_riesgo) / volatilidad_portafolio
    st.metric('Ratio de Sharpe', value=f'{ratio_sharpe:.2f}', help='Mide el rendimiento extra generado por cada unidad de riesgo asumida. Valores superiores a 1 indican una asignacion eficiente.')
    
  with col_metricas_inf[4]:
    volatilidades_individuales = np.sqrt(np.diag(matriz_cov))
    riesgo_ponderado = np.dot(vector_pesos, volatilidades_individuales)
    ratio_diversificacion = riesgo_ponderado / volatilidad_portafolio
    st.metric('Ratio de Diversificación', value=f'{ratio_diversificacion:.2f}', help='Demuestra matemáticamente cómo la diversificación redujo el riesgo global del portafolio gracias a la falta de correlación (covarianzas) entre activos. Valores >1 son positivos.')
    
  style_metric_cards(
    background_color= "#383838",
    border_size_px= 1,
    border_color= "#5a5a5a",
    border_radius_px= 12,
    border_left_color= "#383838",
    box_shadow= False
  )

  #Graficos de resultados
  col_graficos_resultados = st.columns(3)
  with col_graficos_resultados[0]:
    with st.container(key='tarjeta_piechart', border=True):
      fig_piechart = plot_piechart(df_resultados)
      st.session_state['_fig_piechart'] = fig_piechart
      st.markdown('##### Asignación Óptima')
      st.plotly_chart(fig_piechart, use_container_width=True)

      all_activos = set(tickers_cov)
      activos_incluidos = set(df_resultados[df_resultados['Proporción'] > 0.001]['Activo'])
      activos_excluidos = list(all_activos - activos_incluidos)
      if activos_excluidos:
        html_pills = "".join(
            [f"<span style='background-color: #2a2a2a; color: #8a8a8a; padding: 4px 10px; "
              f"border-radius: 12px; margin-right: 6px; font-size: 12px; border: 1px solid #444;'>"
              f"{activo}</span>" for activo in activos_excluidos]
        )
        st.markdown(
            f"<div style='margin-top: 5px; text-align: center;'>"
            f"<span style='color: #8a8a8a; font-size: 13px; margin-right: 8px;'>Filtrados por riesgo:</span>"
            f"{html_pills}</div>", 
            unsafe_allow_html=True
        )
      

  with col_graficos_resultados[1]:
    with st.container(key='tarjeta_barResultados', border=True):
      fig_barras = plot_barRetornos(df_retornos, df_resultados)
      st.session_state['_fig_barras'] = fig_barras
      st.markdown('##### Contribución al Retorno')
      st.plotly_chart(fig_barras, use_container_width=True)

  with col_graficos_resultados[2]:
    with st.container(key='tarjeta_waterfall', border=True):
      fig_cascada = plot_cascada(wealth_actual, df_resultados, df_retornos)
      st.session_state['_fig_cascada'] = fig_cascada
      st.markdown('##### Proyección')
      st.plotly_chart(fig_cascada, use_container_width=True)

  with st.container(key='tarjeta_eficiente', border=True):
    st.markdown('##### Frontera Eficiente')
    fig_frontera = plot_frontera_eficiente(
      df_retornos= st.session_state['retornos_esperados'],
      matriz_covarianza = st.session_state['matriz_covarianza'],
      retorno_cplex= (retorno_nominal_bruto - 1),
      volatilidad_cplex= volatilidad_pct
    )
    st.session_state['_fig_frontera'] = fig_frontera
    st.plotly_chart(fig_frontera, use_container_width=True)

  datos_sensibilidad = resultados_actual['sensibilidad']
  df_sensibilidad = pd.DataFrame(datos_sensibilidad)
  df_sensibilidad['Activo'] = df_sensibilidad['Activo'].str.replace('_', '')
  df_sensibilidad['Precio Dual'] = df_sensibilidad['Precio Dual'].apply(lambda x: 0.0 if abs(x) < 1e-5 else x)

  df_sensibilidad['Estado'] = np.where(
    df_sensibilidad['Precio Dual'] >= 0.0,
    'En Portafolio (Óptimo)',
    'Excluido (Penaliza Rendimiento)'
  )

  st.dataframe(
          df_sensibilidad,
          use_container_width=True,
          hide_index=True,
          column_config={
              "Activo": st.column_config.TextColumn(
                  "Ticker", 
                  width="small"
              ),
              "Precio Dual": st.column_config.NumberColumn(
                  "Penalización Marginal",
                  help="Caída en la rentabilidad ajustada por riesgo si se fuerza la compra de este activo.",
                  format="%.4f" 
              ),
              "Estado": st.column_config.TextColumn(
                  "Decisión del Modelo", 
                  width="medium"
              )
          }
      )
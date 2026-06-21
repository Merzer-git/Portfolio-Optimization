import numpy as np
import pandas as pd
import scipy.optimize as sco
import plotly.graph_objects as go

def plot_frontera_eficiente(df_retornos, matriz_covarianza, retorno_cplex, volatilidad_cplex):
    """
    Calcula la frontera eficiente localmente y la grafica junto con el portafolio óptimo de CPLEX.
    """
    
    # 1. Preparar datos (pasamos a retornos netos restando 1)
    if isinstance(df_retornos, pd.DataFrame):
        retornos_netos = df_retornos.iloc[:, 0].values - 1
        tickers = df_retornos.index
    else:
        retornos_netos = df_retornos.values - 1
        tickers = df_retornos.index
        
    cov = matriz_covarianza.values
    num_activos = len(retornos_netos)

    # 2. Función objetivo: Minimizar Volatilidad
    def calc_vol(pesos):
        return np.sqrt(np.dot(pesos.T, np.dot(cov, pesos)))

    bounds = tuple((0, 1) for _ in range(num_activos)) # Solo posiciones en largo (no shorting)

    # 3. Encontrar límites de la curva (Mínima Varianza y Máximo Retorno)
    retorno_max = np.max(retornos_netos)
    
    restriccion_suma = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
    res_min_vol = sco.minimize(calc_vol, num_activos*[1./num_activos,], 
                               method='SLSQP', bounds=bounds, constraints=[restriccion_suma])
    retorno_min = np.sum(res_min_vol.x * retornos_netos)

    # 4. Generar la curva evaluando 25 puntos objetivo
    target_returns = np.linspace(retorno_min, retorno_max, 25)
    frontera_vol = []
    frontera_ret = []

    for target in target_returns:
        restricciones = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'eq', 'fun': lambda x: np.sum(x * retornos_netos) - target}
        ]
        resultado = sco.minimize(calc_vol, num_activos*[1./num_activos,], 
                                 method='SLSQP', bounds=bounds, constraints=restricciones)
        if resultado.success:
            frontera_vol.append(resultado.fun * 100) # Pasamos a porcentaje
            frontera_ret.append(target * 100)        # Pasamos a porcentaje

    # --- INICIO DEL GRÁFICO PLOTLY ---
    fig = go.Figure()

    # A) La curva de la Frontera Eficiente (Calculada localmente)
    fig.add_trace(go.Scatter(
        x=frontera_vol, 
        y=frontera_ret, 
        mode='lines', 
        line=dict(color='#0f62fe', width=3, shape='spline'), # Azul IBM, línea suavizada
        name='Frontera Eficiente'
    ))

    # B) Los activos individuales (Diamantes grises)
    volatilidades_indiv = np.sqrt(np.diag(cov)) * 100
    retornos_indiv = retornos_netos * 100
    
    fig.add_trace(go.Scatter(
        x=volatilidades_indiv, 
        y=retornos_indiv, 
        mode='markers+text',
        marker=dict(symbol='diamond', size=8, color='#e0e0e0'),
        text=tickers,
        textposition="top center",
        textfont=dict(color='#e0e0e0', size=10),
        name='Activos Individuales'
    ))

    # C) El Portafolio Óptimo (El punto de CPLEX - Amarillo/Dorado)
    # Recibe los datos netos que ya calculaste en la UI
    fig.add_trace(go.Scatter(
        x=[volatilidad_cplex], 
        y=[retorno_cplex * 100], 
        mode='markers', 
        marker=dict(symbol='star', size=16, color='#f1c21b', line=dict(width=1, color='white')),
        name='Portafolio Óptimo (CPLEX)'
    ))

    # --- FORMATO ESTÉTICO ---
    fig.update_layout(
        margin=dict(l=0, r=20, t=10, b=0),
        paper_bgcolor='#383838',
        plot_bgcolor='#383838',
        font=dict(color='#E0E0E0', family='IBM Plex Sans'),
        xaxis=dict(
            title="Riesgo / Volatilidad (%)", 
            showgrid=True, gridcolor='#333333', zeroline=False,
            tickfont=dict(size=12, color='#e0e0e0')
        ),
        yaxis=dict(
            title="Retorno Nominal (%)", 
            showgrid=True, gridcolor='#333333', zeroline=False,
            tickfont=dict(size=12, color='#e0e0e0')
        ),
        showlegend=False,
        height=320 # Misma altura que los demás gráficos
    )

    return fig
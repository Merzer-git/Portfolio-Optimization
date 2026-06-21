import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

def calcular_periodo(rango):
  """Toma el String y lo mapea para devolver la fecha en formato YYYY-MM-DD"""
  fin = pd.Timestamp.today()
  dic_years = {
    '1 Año': 1,
    '3 Años': 3,
    '5 Años': 5,
    '10 Años': 10
  }
  if rango in dic_years:
    inicio = fin - pd.DateOffset(years=dic_years[rango])
    return inicio.strftime('%Y-%m-%d'), fin.strftime('%Y-%m-%d')
  else:
    return '1900-01-01', fin.strftime('%Y-%m-%d')
  
@st.cache_data
def get_activos(tickers, rango_tiempo):
  START_DATE, END_DATE = calcular_periodo(rango_tiempo)
  try:
    raw_precios = yf.download(
      tickers,
      start= START_DATE,
      end= END_DATE,
      auto_adjust= True
    )
    if isinstance(raw_precios.columns, pd.MultiIndex):
      df_precios = raw_precios['Close'].dropna()
    else:
      df_precios = pd.DataFrame({tickers[0]: raw_precios['Close']})

    simple_returns = df_precios.pct_change().dropna()
    anual_returns = simple_returns.mean()*252
    retornos = pd.DataFrame((1 + anual_returns), columns=['retorno_total'])

    covarianza = simple_returns.cov() * 252

    print(covarianza)
    return retornos, covarianza
    
  except Exception as e:
    st.error(f'Error al descargar datos de Yahoo Finance: {e}')
    return None, None
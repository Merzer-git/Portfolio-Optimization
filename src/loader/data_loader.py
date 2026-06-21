import pandas as pd
import streamlit as st

@st.cache_data
def load_data(ruta="data/database.parquet"):
  """Carga la base de datos comppleta con las 1000 acciones mas relevantes actualmente."""
  try:
    df = pd.read_parquet(ruta)
    return df
  except Exception as e:
    st.error(f"Error al cargar la base de datos: {e}")
    return pd.DataFrame()

@st.cache_data
def get_lista_tickers(df):
  """Extra los tickers para las acciones elegidas."""
  if not df.empty and 'Nombre' in df.columns:
    return df['Nombre'].unique().tolist()
  return []

@st.cache_data
def filter_data(df, ticker_seleccionados):
  """Filtra el Datafram en base a las acciones elegidas por el usuario en la interfaz"""
  return df[df['Nombre'].isin(ticker_seleccionados)]
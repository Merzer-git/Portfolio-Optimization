import pandas as pd
import requests
import io

url = "https://companiesmarketcap.com/?download=csv"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
respuesta = requests.get(url, headers=headers)

if respuesta.status_code == 200:
    datos_csv = io.StringIO(respuesta.text)
    df = pd.read_csv(datos_csv)
    df_top1000 = df.head(1000).copy()
    df_top1000 = df_top1000.rename(columns={
      'Symbol': 'Ticker',
      'Name': 'Nombre',
      'country': 'Pais'
    })

    df_final = df_top1000[['Ticker', 'Nombre', 'Pais']]
    df_final = df_final.dropna(subset=['Ticker'])
    df_final['Ticker'] = df_final['Ticker'].str.strip()
    
    archivo_salida = 'database.parquet'
    df_final.to_parquet(archivo_salida, engine='pyarrow', index=False)
    print(df_final.head(10))
else:
    print(f"Error: {respuesta.status_code}")
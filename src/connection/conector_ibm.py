import pandas as pd
import time
import requests
import streamlit as st

API_KEY = st.secrets['IBM_API_KEY']
SPACE_ID = "1fa2f4bb-8bc4-4967-b892-2250e978266b"
DEPLOYMENT_ID = "019ecbf5-b0a0-743a-b6ca-c6ceb43a046d"
CONNECTION_ID = "019e5cc8-4919-7730-94ff-971f05c8e5d8"
BUCKET = "portfoliooptimizationbendersdecom-donotdelete-pr-9vecsk0r1heia7"
COS_ENDPOINT = "https://s3.us-south.cloud-object-storage.appdomain.cloud"

def ejecutar_optimizacion_ibm(df_returns, df_covarianza, capital, rho):
  df_covarianza_limpia = df_covarianza.rename_axis(index=None, columns=None)
  df_cov = df_covarianza_limpia.stack().reset_index()
  df_cov.columns = ['inv1', 'inv2', 'val']

  df_wealth = pd.DataFrame({"val": [1.0]})
  df_rho = pd.DataFrame({"val": [rho]})
  df_returns_limpio = pd.DataFrame({
    'inv': df_returns.index,
    'val': df_returns.iloc[:, 0].values
  })
  
  csv_returns = df_returns_limpio.to_csv(index=False)
  csv_covariance = df_cov.to_csv(index=False)
  csv_wealth = df_wealth.to_csv(index=False)
  csv_rho = df_rho.to_csv(index=False)

  # ==========================================
  # 3. AUTENTICACIÓN (Generar Token)
  # ==========================================
  print("\nGenerando Token de IAM en IBM Cloud...")
  token_url = "https://iam.cloud.ibm.com/identity/token"
  token_data = f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={API_KEY}"
  token_headers = {"Content-Type": "application/x-www-form-urlencoded"}
  res_token = requests.post(token_url, data=token_data, headers=token_headers)
  access_token = res_token.json().get("access_token")
  auth_header = {"Authorization": f"Bearer {access_token}"}

  # ==========================================
  # 4. PISAR ARCHIVOS EN EL COS (PUT)
  # ==========================================
  print("Pisando los archivos CSV en el Cloud Object Storage...")
  archivos_a_subir = {
      "InvestReturn.csv": csv_returns,
      "Covariance.csv": csv_covariance,
      "Wealth.csv": csv_wealth,
      "rho.csv": csv_rho
  }
  for nombre, contenido in archivos_a_subir.items():
      url_cos = f"{COS_ENDPOINT}/{BUCKET}/{nombre}"
      headers_cos = {**auth_header, "Content-Type": "text/csv"}
      requests.put(url_cos, headers=headers_cos, data=contenido)
  print("¡Archivos actualizados con éxito!")

  # ==========================================
  # 5. DISPARAR EL TRABAJO (POST)
  # ==========================================
  print("\nEnviando el modelo matemático al motor de optimización...")
  wml_url = "https://us-south.ml.cloud.ibm.com/ml/v4/deployment_jobs?version=2020-09-01"

  payload_job = {
    "name": "Trabajo_YFinance_API",
    "space_id": SPACE_ID,
    "deployment": {"id": DEPLOYMENT_ID},
    "decision_optimization": {
      "input_data_references": [
        {"id": "InvestReturn.csv", "type": "connection_asset", "connection": {"id": CONNECTION_ID}, "location": {"bucket": BUCKET, "file_name": "InvestReturn.csv"}},
        {"id": "Covariance.csv", "type": "connection_asset", "connection": {"id": CONNECTION_ID}, "location": {"bucket": BUCKET, "file_name": "Covariance.csv"}},
        {"id": "Wealth.csv", "type": "connection_asset", "connection": {"id": CONNECTION_ID}, "location": {"bucket": BUCKET, "file_name": "Wealth.csv"}},
        {"id": "rho.csv", "type": "connection_asset", "connection": {"id": CONNECTION_ID}, "location": {"bucket": BUCKET, "file_name": "rho.csv"}}
      ],
      "output_data_references": [
        {"id": "solution.json", "type": "connection_asset", "connection": {"id": CONNECTION_ID}, "location": {"bucket": BUCKET, "file_name": "solution.json"}},
        {"id": "kpis.csv", "type": "connection_asset", "connection": {"id": CONNECTION_ID}, "location": {"bucket": BUCKET, "file_name": "kpis.csv"}}
      ],
      "solve_parameters": {"oaas.logAttachmentName": "log.txt", "oaas.logTailEnabled": "true"}
    }
  }

  res_job = requests.post(wml_url, headers={**auth_header, "Content-Type": "application/json"}, json=payload_job)
  job_data = res_job.json()
  # print(job_data)
  run_id = job_data['metadata']['id']
  print(f"Trabajo creado encolado. ID de Ejecución: {run_id}")

  # ==========================================
  # 6. CONSULTAR ESTADO (GET)
  # ==========================================
  estado = "queued"
  url_status = f"{wml_url.split('?')[0]}/{run_id}?version=2020-09-01&space_id={SPACE_ID}"

  while estado in ["queued", "running"]:
      # print("El motor está procesando, bancá un toque...")
      time.sleep(3)
      res_status = requests.get(url_status, headers=auth_header)

      if res_status.status_code != 200:
          print("\nError en la API de IBM:")
          print(res_status.text)
          estado = "error"
          break

      estado = res_status.json()['entity']['decision_optimization']['status']['state']

  print(f"¡Estado del trabajo: {estado}!")

  # ==========================================
  # 7. RESULTADOS Y DESESCALADO
  # ==========================================
  if estado == "completed":
    url_sol = f'{COS_ENDPOINT}/{BUCKET}/solution.json'
    res_sol = requests.get(url_sol, headers=auth_header)
    datos_solucion = res_sol.json()

    ganancia_proporcion = float(datos_solucion['CPLEXSolution']['header']['objectiveValue'])
    ganancia_real = ganancia_proporcion * capital

    variables_raw = datos_solucion.get('CPLEXSolution', {}).get('variables', [])
    pesos_limpios = []
    precios_duales = []

    for item in variables_raw:
      ticker = item['name'].replace('alloc', '')
      proporcion = float(item['value'])
      costo_reducido = float(item.get('reducedCost', 0.0))
      
      if proporcion > 0.001:
        pesos_limpios.append({
          'Activo': ticker,
          'Proporción': proporcion
        })

      precios_duales.append({
        'Activo': ticker,
        'Precio Dual': costo_reducido
      })

    return {
      'status': 'success',
      'ganancia_proporcion': ganancia_proporcion,
      'ganancia_real': ganancia_real,
      'pesos': pesos_limpios,
      'sensibilidad': precios_duales
    }
  else:
    return {
      'status': 'error',
      'msg': 'El modelo falló en IBM'
    }
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Configuración Inicial
np.random.seed(42)
start_date = datetime(2021, 1, 1)
end_date = datetime(2025, 12, 31)
date_range = pd.date_range(start_date, end_date)
hoteles = ['H01', 'H02', 'H03']

# 1. Catálogos
canales = pd.DataFrame([
    {'id_canal': 1, 'nombre_canal': 'Web Directa', 'comision_porcentaje': 0.0},
    {'id_canal': 2, 'nombre_canal': 'Booking', 'comision_porcentaje': 18.0},
    {'id_canal': 3, 'nombre_canal': 'Expedia', 'comision_porcentaje': 20.0},
    {'id_canal': 4, 'nombre_canal': 'OTA Local', 'comision_porcentaje': 15.0}
])

tipos_hab = pd.DataFrame([
    {'id_tipo': 1, 'nombre_tipo': 'Standard', 'm2_habitacion': 25.0, 'costo_limpieza_std': 12.0, 'costo_amenities_std': 5.0},
    {'id_tipo': 2, 'nombre_tipo': 'Deluxe', 'm2_habitacion': 45.0, 'costo_limpieza_std': 18.0, 'costo_amenities_std': 8.5},
    {'id_tipo': 3, 'nombre_tipo': 'Suite', 'm2_habitacion': 75.0, 'costo_limpieza_std': 30.0, 'costo_amenities_std': 15.0}
])

# 2. Inventario y Mercado (Tablas por Fecha)
inventario_list = []
mercado_list = []
for hotel_id in hoteles:
    hab_fisicas = 50 if hotel_id == 'H01' else (100 if hotel_id == 'H02' else 25)
    m2_hotel = hab_fisicas * 40 # Estimación
    
    for fecha in date_range:
        # Inventario
        hab_ooo = np.random.randint(0, 4) if np.random.random() > 0.9 else 0
        inventario_list.append({
            'id_hotel': hotel_id, 'fecha': fecha, 'hab_totales_fisicas': hab_fisicas,
            'hab_out_of_order': hab_ooo, 'm2_totales_hotel': m2_hotel,
            'hab_disponibles': hab_fisicas - hab_ooo
        })
        
        # Mercado (Compset)
        base_adr = 120 if hotel_id == 'H01' else (180 if hotel_id == 'H02' else 350)
        m_occ = np.random.uniform(0.5, 0.85)
        m_adr = base_adr * np.random.uniform(0.9, 1.1)
        mercado_list.append({
            'id_hotel': hotel_id, 'fecha': fecha, 'compset_adr': m_adr,
            'compset_occ_pct': m_occ, 'compset_revpar': m_adr * m_occ, 'fuente_dato': 'STR_Global'
        })

df_inventario = pd.DataFrame(inventario_list)
df_mercado = pd.DataFrame(mercado_list)

# 3. Reservas y Consumos
reservas_list = []
consumos_list = []
res_id_counter = 100000
cons_id_counter = 500000

for idx, row in df_inventario.iterrows():
    # Determinamos ocupación según temporada
    mes = row['fecha'].month
    occ_target = 0.85 if mes in [7, 8, 12] else 0.55
    num_reservas_hoy = int(row['hab_disponibles'] * occ_target * np.random.uniform(0.8, 1.2))
    
    # Simular que las reservas duran X noches, así que hoy "entran" algunas
    entradas_hoy = int(num_reservas_hoy / 3) 
    
    for _ in range(entradas_hoy):
        canal = canales.sample(1).iloc[0]
        tipo = tipos_hab.sample(1).iloc[0]
        noches = np.random.randint(1, 6)
        pax_a = np.random.randint(1, 3)
        pax_n = np.random.randint(0, 2)
        adr_reserva = tipo['Tarifa_Base'] = (100 if tipo['id_tipo']==1 else (180 if tipo['id_tipo']==2 else 350))
        adr_reserva *= (1.5 if mes in [7,8,12] else 1.0) * np.random.uniform(0.9, 1.1)
        
        id_res = res_id_counter
        res_id_counter += 1
        
        reservas_list.append({
            'id_reserva': id_res, 'id_hotel': row['id_hotel'], 'id_canal': canal['id_canal'], 
            'id_tipo_hab': tipo['id_tipo'], 'fecha_checkin': row['fecha'], 
            'pax_adultos': pax_a, 'pax_ninos': pax_n, 'pax_total': pax_a + pax_n,
            'ingreso_alojamiento_neto': adr_reserva * noches, 'noches': noches, 'estado_reserva': 'Confirmada'
        })
        
        # Gastos Extra (Consumos)
        for _ in range(np.random.randint(1, 4)):
            consumos_list.append({
                'id_consumo': cons_id_counter, 'id_reserva': id_res, 
                'punto_venta': np.random.choice(['Bar', 'Spa', 'Parking', 'Restaurante']),
                'monto_neto': np.random.uniform(10, 100), 'fecha_consumo': row['fecha']
            })
            cons_id_counter += 1

# 4. Gastos No Distribuidos
gastos_list = []
g_id = 1
for hotel_id in hoteles:
    for fecha in pd.date_range(start_date, end_date, freq='ME'):
        for cat in ['Marketing', 'Admin', 'Mantenimiento', 'Suministros Energéticos']:
            monto = 5000 if hotel_id == 'H02' else 2000
            gastos_list.append({
                'id_gasto_fijo': g_id, 'id_hotel': hotel_id, 'fecha': fecha, 
                'categoria': cat, 'monto': monto * np.random.uniform(0.9, 1.1), 'es_gasto_gop': 1
            })
            g_id += 1

# Guardar archivos
base_path = os.path.dirname(__file__)
output_dir = os.path.join(base_path, "..", "data")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

pd.DataFrame(reservas_list).to_csv(os.path.join(output_dir, 'Reservas.csv'), index=False)
pd.DataFrame(consumos_list).to_csv(os.path.join(output_dir, 'Folio_Consumos.csv'), index=False)
df_inventario.to_csv(os.path.join(output_dir, 'Hotel_Inventario.csv'), index=False)
df_mercado.to_csv(os.path.join(output_dir, 'Mercado_CompSet.csv'), index=False)
pd.DataFrame(gastos_list).to_csv(os.path.join(output_dir, 'Gastos_No_Distribuidos.csv'), index=False)

print("Datos generados correctamente para los 3 hoteles.")
import requests
import time

# Dirección de tu API local
URL_API = "http://127.0.0.1:8000/api/prospectos"

# Datos simulados de un cliente que consulta desde la ficha web
nuevo_prospecto = {
    "nombre": "Mariana Garza",
    "telefono": "+52 55 9876 5432",
    "email": "mariana.garza@empresa.com",
    "propiedad_interes_slug": "fuente-de-trivoli-30",
    "presupuesto_maximo": 21500000.0,
    "etapa_kanban": "Nuevo",
    "asesor_asignado": "Irving Said Díaz Montiel"
}

print("🌐 Simulando clic de cliente en botón de WhatsApp / Formulario Web...")
time.sleep(1) # Pausa de 1 segundo para simular la red

# Enviamos la petición POST a la API
respuesta = requests.post(URL_API, json=nuevo_prospecto)

if respuesta.status_code == 200:
    print("✅ ¡ÉXITO! El prospecto fue enviado a la API y registrado en el CRM.")
    print(f"👤 Cliente: {nuevo_prospecto['nombre']}")
    print(f"🏡 Propiedad: {nuevo_prospecto['propiedad_interes_slug']}")
else:
    print(f"❌ Error al enviar prospecto: {respuesta.status_code}")
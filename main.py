# --- ACTUALIZACIÓN DE RUTAS COMPLETAS Y LIMPIAS (2026-08-03) ---
import os
import uuid
import sqlite3
import urllib.parse
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(
    title="API CRM Special Home",
    description="Servidor backend avanzado para la gestión de propiedades, prospectos y asesores",
    version="2.8.4"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOADS_DIR = os.path.join(BASE_DIR, "static", "uploads", "propiedades")
os.makedirs(UPLOADS_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


class PropiedadSchema(BaseModel):
    slug: str
    titulo: str
    categoria_tab: str
    tipo_propiedad: str
    tipo_operacion: str
    imagen_principal: Optional[str] = ""
    galeria_imagenes: Optional[str] = ""
    google_maps_iframe: Optional[str] = ""
    calle_numero: str
    colonia: str
    municipio: str
    estado: str
    cp: str
    coordenadas_lat_lng: Optional[str] = ""
    precio_lista: float
    precio_minimo_oferta: Optional[float] = 0
    precio_renta: Optional[float] = 0
    terreno_m2: float
    construccion_m2: float
    recamaras: Optional[int] = 0
    banos_completos: Optional[int] = 0
    medios_banos: Optional[float] = 0
    estacionamientos: Optional[int] = 0
    niveles: Optional[int] = 1
    agua_potable: Optional[str] = "Red Directa Municipal"
    suministro_gas: Optional[str] = "Gas Natural"
    seguridad: Optional[str] = "Privada 24/7 con Caseta"
    asesor_opcionador: Optional[str] = "Irving Said Díaz Montiel"
    valuador: Optional[str] = "Ing. Kitlanezi León Soto"
    equipamiento_cercano: Optional[str] = ""
    descripcion: Optional[str] = ""
    creador_email: Optional[str] = "adminportal@specialhome.com.mx"

class ProspectoSchema(BaseModel):
    nombre: str
    telefono: str
    email: Optional[str] = None
    propiedad_interes_slug: str
    presupuesto_maximo: Optional[float] = 0
    etapa_kanban: Optional[str] = "Nuevo"
    asesor_asignado: Optional[str] = "Por Asignar"
    comentarios: Optional[str] = ""
    datos_seguimiento: Optional[str] = ""
    historial_toolgates: Optional[str] = ""
    estatus_lead: Optional[str] = "Activo"

class ActualizarEtapaSchema(BaseModel):
    etapa_kanban: str
    datos_seguimiento: Optional[str] = ""
    historial_toolgates: Optional[str] = ""
    estatus_lead: Optional[str] = "Activo"

class AsesorSchema(BaseModel):
    nombre: str
    email: str
    password: str
    whatsapp: str
    rol: Optional[str] = "Asesor"

class LoginSchema(BaseModel):
    email: str
    password: str


@app.on_event("startup")
def inicio():
    database.inicializar_base_de_datos()


# --- RUTAS FRONTEND OFICIALES ---
@app.get("/", response_class=FileResponse, tags=["Vista Web"])
def ver_sitio_publico():
    return os.path.join(BASE_DIR, "index.html")

@app.get("/soluciones-b2b", response_class=FileResponse, tags=["Vista Web"])
def ver_soluciones_b2b():
    return os.path.join(BASE_DIR, "soluciones_b2b.html")

@app.get("/buscador", response_class=FileResponse, tags=["Vista Web"])
def ver_buscador():
    return os.path.join(BASE_DIR, "buscador.html")

@app.get("/propiedad/{slug}", response_class=FileResponse, tags=["Vista Web"])
def ver_detalle_propiedad(slug: str):
    return os.path.join(BASE_DIR, "detalle_propiedad.html")

@app.get("/kanban", response_class=FileResponse, tags=["Vista Web"])
def ver_kanban():
    return os.path.join(BASE_DIR, "kanban.html")

@app.get("/alta-propiedad", response_class=FileResponse, tags=["Vista Web"])
def ver_alta_propiedad():
    return os.path.join(BASE_DIR, "alta_propiedad.html")

@app.get("/editar-propiedad/{propiedad_id}", response_class=FileResponse, tags=["Vista Web"])
def ver_editar_propiedad(propiedad_id: int):
    return os.path.join(BASE_DIR, "editar_propiedad.html")

@app.get("/portal", response_class=FileResponse, tags=["Vista Web"])
def ver_portal_asesor():
    return os.path.join(BASE_DIR, "portal_del_asesor.html")

@app.get("/login", response_class=FileResponse, tags=["Autenticación"])
def ver_login():
    return os.path.join(BASE_DIR, "login.html")

@app.get("/aviso-privacidad", response_class=FileResponse, tags=["Vista Web"])
def ver_aviso_privacidad():
    return os.path.join(BASE_DIR, "aviso_privacidad.html")

@app.get("/terminos-condiciones", response_class=FileResponse, tags=["Vista Web"])
def ver_terminos():
    return os.path.join(BASE_DIR, "terminos_condiciones.html")


# --- ENDPOINTS API ---
@app.post("/api/auth/login", tags=["Autenticación"])
def login_asesor(cred: LoginSchema):
    pwd_hash = database.hash_password(cred.password)
    conexion = sqlite3.connect(os.path.join(BASE_DIR, "special_home_crm.db"))
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, email, whatsapp, rol FROM asesores WHERE email = ? AND password_hash = ?", (cred.email, pwd_hash))
    fila = cursor.fetchone()
    conexion.close()

    if not fila:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas o acceso no autorizado.")

    return {
        "estatus": "exito",
        "asesor": {
            "id": fila[0],
            "nombre": fila[1],
            "email": fila[2],
            "whatsapp": fila[3],
            "rol": fila[4]
        }
    }

@app.get("/api/asesores", tags=["Asesores"])
def listar_asesores():
    conexion = sqlite3.connect(os.path.join(BASE_DIR, "special_home_crm.db"))
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, email, whatsapp, rol FROM asesores ORDER BY id DESC")
    filas = cursor.fetchall()
    conexion.close()
    
    lista = [{"id": f[0], "nombre": f[1], "email": f[2], "whatsapp": f[3], "rol": f[4]} for f in filas]
    return {"asesores": lista}

@app.post("/api/asesores", tags=["Asesores"])
def crear_asesor(asesor: AsesorSchema):
    pwd_hash = database.hash_password(asesor.password)
    conexion = sqlite3.connect(os.path.join(BASE_DIR, "special_home_crm.db"))
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            INSERT INTO asesores (nombre, email, password_hash, whatsapp, rol)
            VALUES (?, ?, ?, ?, ?)
        """, (asesor.nombre, asesor.email, pwd_hash, asesor.whatsapp, asesor.rol or "Asesor"))
        conexion.commit()
        conexion.close()
        return {"estatus": "exito", "mensaje": "Asesor registrado correctamente"}
    except sqlite3.IntegrityError:
        conexion.close()
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")
    except Exception as e:
        conexion.close()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-imagenes", tags=["Multimedia"])
async def subir_imagenes(archivos: List[UploadFile] = File(...)):
    if len(archivos) > 30:
        raise HTTPException(status_code=400, detail="Máximo 30 imágenes.")

    urls_guardadas = []
    try:
        for archivo in archivos:
            ext = os.path.splitext(archivo.filename)[1] or ".jpg"
            nombre_unico = f"{uuid.uuid4().hex}{ext.lower()}"
            ruta_archivo = os.path.join(UPLOADS_DIR, nombre_unico)

            with open(ruta_archivo, "wb") as f:
                f.write(await archivo.read())

            urls_guardadas.append(f"/static/uploads/propiedades/{nombre_unico}")

        return {"estatus": "exito", "urls": urls_guardadas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/propiedades", tags=["Propiedades"])
def listar_propiedades(q: Optional[str] = None, tipo: Optional[str] = None, operacion: Optional[str] = None, creador: Optional[str] = None):
    conexion = sqlite3.connect(os.path.join(BASE_DIR, "special_home_crm.db"))
    cursor = conexion.cursor()
    
    query = """
        SELECT p.id, p.slug, p.titulo, p.categoria_tab, p.tipo_propiedad, p.tipo_operacion, p.calle_numero, p.colonia, p.municipio, p.estado, 
               p.precio_lista, p.terreno_m2, p.construccion_m2, p.recamaras, p.estatus_publicacion, p.imagen_principal, p.descripcion, p.creador_email, a.nombre 
        FROM propiedades p
        LEFT JOIN asesores a ON p.creador_email = a.email
        WHERE 1=1
    """
    params = []
    
    if q:
        query += " AND (p.titulo LIKE ? OR p.colonia LIKE ? OR p.municipio LIKE ? OR p.descripcion LIKE ?)"
        term = f"%{q}%"
        params.extend([term, term, term, term])
        
    if tipo and tipo != "todos":
        query += " AND p.tipo_propiedad = ?"
        params.append(tipo)
        
    if operacion and operacion != "todas":
        query += " AND p.tipo_operacion = ?"
        params.append(operacion)

    if creador:
        query += " AND p.creador_email = ?"
        params.append(creador)
        
    query += " ORDER BY p.id DESC"
    
    cursor.execute(query, params)
    filas = cursor.fetchall()
    conexion.close()

    lista = []
    for f in filas:
        lista.append({
            "id": f[0], "slug": f[1], "titulo": f[2], "categoria_tab": f[3],
            "tipo_propiedad": f[4], "tipo_operacion": f[5], "calle_numero": f[6],
            "colonia": f[7], "municipio": f[8], "estado": f[9], "precio_lista": f[10],
            "terreno_m2": f[11], "construccion_m2": f[12], "recamaras": f[13], "estatus": f[14],
            "imagen_principal": f[15], "descripcion": f[16] or "",
            "creador_email": f[17] or "",
            "asesor_creador": f[18] or "Administrador Maestro"
        })
    return {"total": len(lista), "propiedades": lista}

@app.get("/api/propiedades/slug/{slug}", tags=["Propiedades"])
def obtener_propiedad_por_slug(slug: str):
    conexion = sqlite3.connect(os.path.join(BASE_DIR, "special_home_crm.db"))
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM propiedades WHERE slug = ?", (slug,))
    fila = cursor.fetchone()
    conexion.close()

    if not fila:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")

    return dict(fila)

@app.get("/api/propiedades/{propiedad_id}", tags=["Propiedades"])
def obtener_propiedad_por_id(propiedad_id: int):
    conexion = sqlite3.connect(os.path.join(BASE_DIR, "special_home_crm.db"))
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM propiedades WHERE id = ?", (propiedad_id,))
    fila = cursor.fetchone()
    conexion.close()

    if not fila:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")

    return dict(fila)

@app.post("/api/propiedades", tags=["Propiedades"])
def crear_propiedad(p: PropiedadSchema):
    try:
        database.guardar_propiedad_dict(p.dict())
        return {"estatus": "exito", "mensaje": "Propiedad registrada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/propiedades/{propiedad_id}", tags=["Propiedades"])
def actualizar_propiedad(propiedad_id: int, p: PropiedadSchema):
    conexion = sqlite3.connect(os.path.join(BASE_DIR, "special_home_crm.db"))
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            UPDATE propiedades SET
                slug=?, titulo=?, categoria_tab=?, tipo_propiedad=?, tipo_operacion=?,
                imagen_principal=?, galeria_imagenes=?, google_maps_iframe=?, calle_numero=?,
                colonia=?, municipio=?, estado=?, cp=?, coordenadas_lat_lng=?, precio_lista=?,
                precio_minimo_oferta=?, precio_renta=?, terreno_m2=?, construccion_m2=?,
                recamaras=?, banos_completos=?, medios_banos=?, estacionamientos=?,
                agua_potable=?, suministro_gas=?, seguridad=?, asesor_opcionador=?,
                valuador=?, equipamiento_cercano=?, descripcion=?, creador_email=?
            WHERE id=?
        """, (
            p.slug, p.titulo, p.categoria_tab, p.tipo_propiedad, p.tipo_operacion,
            p.imagen_principal, p.galeria_imagenes, p.google_maps_iframe, p.calle_numero,
            p.colonia, p.municipio, p.estado, p.cp, p.coordenadas_lat_lng, p.precio_lista,
            p.precio_minimo_oferta, p.precio_renta, p.terreno_m2, p.construccion_m2,
            p.recamaras, p.banos_completos, p.medios_banos, p.estacionamientos,
            p.agua_potable, p.suministro_gas, p.seguridad, p.asesor_opcionador,
            p.valuador, p.equipamiento_cercano, p.descripcion, p.creador_email, propiedad_id
        ))
        conexion.commit()
        conexion.close()
        return {"estatus": "exito"}
    except Exception as e:
        conexion.close()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/propiedades/{propiedad_id}", tags=["Propiedades"])
def eliminar_propiedad(propiedad_id: int, admin_email: str):
    conexion = sqlite3.connect(os.path.join(BASE_DIR, "special_home_crm.db"))
    cursor = conexion.cursor()
    
    cursor.execute("SELECT rol FROM asesores WHERE email = ?", (admin_email,))
    fila = cursor.fetchone()
    
    if not fila or fila[0] != "Admin":
        conexion.close()
        raise HTTPException(status_code=403, detail="Acceso denegado: Solo los administradores pueden eliminar propiedades.")
        
    cursor.execute("DELETE FROM propiedades WHERE id = ?", (propiedad_id,))
    conexion.commit()
    conexion.close()
    return {"estatus": "exito", "mensaje": "Propiedad eliminada correctamente."}

@app.get("/api/prospectos", tags=["Prospectos"])
def listar_prospectos(propiedad_slug: Optional[str] = None):
    conexion = sqlite3.connect(os.path.join(BASE_DIR, "special_home_crm.db"))
    cursor = conexion.cursor()
    
    if propiedad_slug and propiedad_slug != "todas":
        cursor.execute("""
            SELECT id, nombre, telefono, email, propiedad_interes_slug, presupuesto_maximo, etapa_kanban, asesor_asignado, comentarios, datos_seguimiento, historial_toolgates, estatus_lead, leido, fecha_registro 
            FROM prospectos 
            WHERE propiedad_interes_slug = ? 
            ORDER BY id DESC
        """, (propiedad_slug,))
    else:
        cursor.execute("""
            SELECT id, nombre, telefono, email, propiedad_interes_slug, presupuesto_maximo, etapa_kanban, asesor_asignado, comentarios, datos_seguimiento, historial_toolgates, estatus_lead, leido, fecha_registro 
            FROM prospectos 
            ORDER BY id DESC
        """)
        
    filas = cursor.fetchall()
    conexion.close()

    lista = []
    for fila in filas:
        lista.append({
            "id": fila[0], 
            "nombre": fila[1], 
            "telefono": fila[2], 
            "email": fila[3], 
            "propiedad_interes": fila[4], 
            "presupuesto_maximo": fila[5], 
            "etapa_kanban": fila[6], 
            "asesor": fila[7], 
            "comentarios": fila[8], 
            "datos_seguimiento": fila[9],
            "historial_toolgates": fila[10] or "",
            "estatus_lead": fila[11] or "Activo",
            "leido": fila[12],
            "fecha_registro": fila[13]
        })
    return {"total": len(lista), "prospectos": lista}

@app.post("/api/prospectos", tags=["Prospectos"])
def crear_prospecto(prospecto: ProspectoSchema):
    timestamp_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
    historial_inicial = f"[{timestamp_actual}] 🟢 [Nuevo]: Registro inicial de prospecto - {prospecto.comentarios or 'Sin comentarios'}"
    
    datos = (
        prospecto.nombre, 
        prospecto.telefono, 
        prospecto.email or "", 
        prospecto.propiedad_interes_slug, 
        prospecto.presupuesto_maximo or 0, 
        prospecto.etapa_kanban or "Nuevo", 
        prospecto.asesor_asignado or "Por Asignar",
        prospecto.comentarios or "",
        prospecto.datos_seguimiento or "",
        historial_inicial,
        "Activo"
    )
    database.guardar_prospecto(datos)

    conexion = sqlite3.connect(os.path.join(BASE_DIR, "special_home_crm.db"))
    cursor = conexion.cursor()
    cursor.execute("SELECT whatsapp FROM asesores WHERE nombre = ?", (prospecto.asesor_asignado,))
    asesor_row = cursor.fetchone()
    conexion.close()
    
    whatsapp_asesor = asesor_row[0] if asesor_row else "No registrado"

    return {
        "estatus": "exito", 
        "mensaje": "Prospecto registrado",
        "alerta_whatsapp_enviada": f"Notificación simulada enviada al asesor {prospecto.asesor_asignado} al número {whatsapp_asesor}"
    }

@app.put("/api/prospectos/{prospecto_id}/etapa", tags=["Prospectos"])
def actualizar_etapa_prospecto(prospecto_id: int, datos: ActualizarEtapaSchema):
    conexion = sqlite3.connect(os.path.join(BASE_DIR, "special_home_crm.db"))
    cursor = conexion.cursor()
    
    cursor.execute("SELECT historial_toolgates FROM prospectos WHERE id = ?", (prospecto_id,))
    row = cursor.fetchone()
    historial_previo = row[0] if row and row[0] else ""
    
    timestamp_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
    linea_con_timestamp = f"[{timestamp_actual}] {datos.historial_toolgates}" if datos.historial_toolgates else ""
    
    nuevo_historial = historial_previo + "\n" + linea_con_timestamp if historial_previo and linea_con_timestamp else (linea_con_timestamp or historial_previo)

    cursor.execute("""
        UPDATE prospectos 
        SET etapa_kanban = ?, datos_seguimiento = ?, historial_toolgates = ?, estatus_lead = ? 
        WHERE id = ?
    """, (datos.etapa_kanban, datos.datos_seguimiento, nuevo_historial, datos.estatus_lead, prospecto_id))
    
    conexion.commit()
    conexion.close()
    return {"estatus": "exito"}

@app.put("/api/prospectos/{prospecto_id}/marcar-leido", tags=["Prospectos"])
def marcar_prospecto_leido(prospecto_id: int):
    conexion = sqlite3.connect(os.path.join(BASE_DIR, "special_home_crm.db"))
    cursor = conexion.cursor()
    cursor.execute("UPDATE prospectos SET leido = 1 WHERE id = ?", (prospecto_id,))
    conexion.commit()
    conexion.close()
    return {"estatus": "exito"}

@app.get("/api/prospectos/{prospecto_id}/whatsapp-link", tags=["WhatsApp Generator"])
def generar_link_whatsapp(prospecto_id: int):
    conexion = sqlite3.connect(os.path.join(BASE_DIR, "special_home_crm.db"))
    cursor = conexion.cursor()
    cursor.execute("SELECT nombre, telefono, propiedad_interes_slug FROM prospectos WHERE id = ?", (prospecto_id,))
    lead = cursor.fetchone()
    conexion.close()

    if not lead: return {"error": "No encontrado"}
    nombre, telefono, slug = lead
    propiedad = database.obtener_propiedad_por_slug(slug)

    if propiedad:
        titulo, precio, terreno, const, colonia, tipo, min_oferta = propiedad
        mensaje = f"Hola {nombre}, un gusto saludarte de Special Home. 🏰\n\nCon respecto a tu consulta por el inmueble ({tipo}) *{titulo}* en {colonia}:\n\n- Precio Lista: ${precio:,.2f} MXN\n- Terreno: {terreno} m²\n- Construcción: {const} m²\n\n¿Te gustaría agendar una visita privada esta semana?"
    else:
        mensaje = f"Hola {nombre}, un gusto saludarte de Special Home. 🏰 ¿En qué momento te gustaría platicar sobre la propiedad de tu interés?"

    tel_limpio = "".join(filter(str.isdigit, telefono))
    url_final = f"https://wa.me/{tel_limpio}?text={urllib.parse.quote(mensaje)}"
    return {"whatsapp_url": url_final}

@app.get("/api/propiedades/slug/{slug}/oferta-minima", tags=["Propiedades"])
def obtener_oferta_minima(slug: str):
    prop = database.obtener_propiedad_por_slug(slug)
    if not prop:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")
    return {"precio_minimo_oferta": prop[6] or 0}
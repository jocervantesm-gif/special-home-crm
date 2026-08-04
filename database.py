import sqlite3
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def inicializar_base_de_datos():
    conexion = sqlite3.connect("special_home_crm.db")
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS propiedades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        titulo TEXT NOT NULL,
        categoria_tab TEXT NOT NULL,
        tipo_propiedad TEXT NOT NULL,
        tipo_operacion TEXT NOT NULL,
        imagen_principal TEXT,
        galeria_imagenes TEXT,
        google_maps_iframe TEXT,
        calle_numero TEXT NOT NULL,
        colonia TEXT NOT NULL,
        municipio TEXT NOT NULL,
        estado TEXT NOT NULL,
        cp TEXT NOT NULL,
        coordenadas_lat_lng TEXT,
        precio_lista REAL NOT NULL,
        precio_minimo_oferta REAL DEFAULT 0,
        precio_renta REAL DEFAULT 0,
        terreno_m2 REAL NOT NULL,
        construccion_m2 REAL NOT NULL,
        recamaras INTEGER DEFAULT 0,
        banos_completos INTEGER DEFAULT 0,
        medios_banos REAL DEFAULT 0,
        estacionamientos INTEGER DEFAULT 0,
        niveles INTEGER DEFAULT 1,
        agua_potable TEXT DEFAULT 'Red Directa',
        suministro_gas TEXT DEFAULT 'Gas Natural',
        drenaje TEXT DEFAULT 'Red Subterránea',
        seguridad TEXT DEFAULT 'Privada 24/7',
        alumbrado TEXT DEFAULT 'Red Aérea / LED',
        equipamiento_cercano TEXT,
        amenidades TEXT,
        verificado_special_home INTEGER DEFAULT 1,
        asesor_opcionador TEXT DEFAULT 'Irving Said Díaz Montiel',
        valuador TEXT DEFAULT 'Ing. Kitlanezi León Soto',
        estatus_publicacion TEXT DEFAULT 'Publicado',
        creador_email TEXT DEFAULT 'adminportal@specialhome.com.mx',
        descripcion TEXT
    )
    """)

    # Migración de seguridad por si la tabla ya existía sin creador_email
    try:
        cursor.execute("ALTER TABLE propiedades ADD COLUMN creador_email TEXT DEFAULT 'adminportal@specialhome.com.mx'")
    except sqlite3.OperationalError:
        pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prospectos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT NOT NULL,
        email TEXT,
        propiedad_interes_slug TEXT,
        presupuesto_maximo REAL,
        etapa_kanban TEXT DEFAULT 'Nuevo',
        asesor_asignado TEXT,
        comentarios TEXT,
        datos_seguimiento TEXT,
        historial_toolgates TEXT DEFAULT '',
        estatus_lead TEXT DEFAULT 'Activo',
        leido INTEGER DEFAULT 0,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (propiedad_interes_slug) REFERENCES propiedades (slug)
    )
    """)

    try:
        cursor.execute("ALTER TABLE prospectos ADD COLUMN leido INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS asesores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        whatsapp TEXT NOT NULL,
        rol TEXT DEFAULT 'Asesor',
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("SELECT id FROM asesores WHERE email = ?", ("adminportal@specialhome.com.mx",))
    if not cursor.fetchone():
        pwd_hash = hash_password("Admin123*")
        cursor.execute("""
            INSERT INTO asesores (nombre, email, password_hash, whatsapp, rol)
            VALUES (?, ?, ?, ?, ?)
        """, ("Administrador Maestro", "adminportal@specialhome.com.mx", pwd_hash, "5512345678", "Admin"))

    conexion.commit()
    conexion.close()

def guardar_propiedad_dict(p):
    conexion = sqlite3.connect("special_home_crm.db")
    cursor = conexion.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO propiedades (
        slug, titulo, categoria_tab, tipo_propiedad, tipo_operacion, imagen_principal, galeria_imagenes, google_maps_iframe,
        calle_numero, colonia, municipio, estado, cp, coordenadas_lat_lng, precio_lista,
        precio_minimo_oferta, precio_renta, terreno_m2, construccion_m2, recamaras, banos_completos,
        medios_banos, estacionamientos, niveles, agua_potable, suministro_gas, drenaje, seguridad,
        alumbrado, equipamiento_cercano, amenidades, verificado_special_home, asesor_opcionador,
        valuador, estatus_publicacion, creador_email, descripcion
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        p["slug"], p["titulo"], p["categoria_tab"], p["tipo_propiedad"], p["tipo_operacion"],
        p.get("imagen_principal", ""), p.get("galeria_imagenes", ""), p.get("google_maps_iframe", ""),
        p["calle_numero"], p["colonia"], p["municipio"], p["estado"], p["cp"],
        p.get("coordenadas_lat_lng", ""), p["precio_lista"], p.get("precio_minimo_oferta", 0),
        p.get("precio_renta", 0), p["terreno_m2"], p["construccion_m2"],
        p.get("recamaras", 0), p.get("banos_completos", 0), p.get("medios_banos", 0),
        p.get("estacionamientos", 0), p.get("niveles", 1), p.get("agua_potable", "Red Directa"),
        p.get("suministro_gas", "Gas Natural"), p.get("drenaje", "Red Subterránea"),
        p.get("seguridad", "Privada 24/7"), p.get("alumbrado", "Red LED"),
        p.get("equipamiento_cercano", ""), p.get("equipamiento_cercano", ""),
        p.get("verificado_special_home", 1),
        p.get("asesor_opcionador", "Irving Said Díaz Montiel"), p.get("valuador", "Ing. Kitlanezi León Soto"),
        p.get("estatus_publicacion", "Publicado"), p.get("creador_email", "adminportal@specialhome.com.mx"),
        p.get("descripcion", "")
    ))
    conexion.commit()
    conexion.close()

def guardar_prospecto(datos):
    conexion = sqlite3.connect("special_home_crm.db")
    cursor = conexion.cursor()
    cursor.execute("""
    INSERT INTO prospectos (
        nombre, telefono, email, propiedad_interes_slug, presupuesto_maximo, etapa_kanban, asesor_asignado, comentarios, datos_seguimiento, historial_toolgates, estatus_lead, leido
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, datos)
    conexion.commit()
    conexion.close()

def obtener_propiedad_por_slug(slug):
    conexion = sqlite3.connect("special_home_crm.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT titulo, precio_lista, terreno_m2, construccion_m2, colonia, tipo_propiedad, precio_minimo_oferta FROM propiedades WHERE slug = ?", (slug,))
    fila = cursor.fetchone()
    conexion.close()
    return fila
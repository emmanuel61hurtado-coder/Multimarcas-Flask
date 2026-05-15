from app import create_app, db
from app.models.repuesto import Repuesto

app = create_app()

repuestos_data = [
    # 🛢️ Aceites y Lubricantes
    ("Aceite 100% Sintético 7100 10W40 4T", "Lubricantes", "Motul", 55000, 20, "Aceite premium para alto rendimiento y protección extrema."),
    ("Aceite Semisintético 5100 15W50", "Lubricantes", "Motul", 42000, 30, "Protección estándar ideal para motos urbanas."),
    ("Aceite Mineral 3000 20W50", "Lubricantes", "Motul", 32000, 25, "Aceite mineral para uso tradicional."),
    ("Aceite Racing 4T 10W40", "Lubricantes", "Castrol", 48000, 15, "Aceite Castrol Power 1 Racing."),
    ("Aceite Actevo 20W50 4T", "Lubricantes", "Castrol", 35000, 20, "Protección continua en todo momento."),
    ("Líquido de Frenos DOT 4", "Fluidos", "Motul", 25000, 15, "Líquido de frenos de alto punto de ebullición."),
    ("Líquido de Frenos DOT 3", "Fluidos", "Brembo", 20000, 10, "Líquido de frenos estándar."),
    ("Refrigerante Anticongelante", "Fluidos", "Motul", 28000, 20, "Motocool Expert, protege el sistema de refrigeración."),
    ("Lubricante de Cadena C2", "Lubricantes", "Motul", 38000, 15, "Spray lubricante para cadenas off-road y urbanas."),
    ("Limpiador de Cadena C1", "Limpieza", "Motul", 35000, 15, "Spray desengrasante para cadenas."),
    ("Grasa de Litio Multipropósito", "Lubricantes", "SKF", 18000, 10, "Grasa para rodamientos y piezas móviles."),
    ("Aceite Suspensión 10W", "Fluidos", "Motul", 40000, 10, "Fork Oil Expert para barras de suspensión."),

    # 🛑 Frenos
    ("Pastillas de Freno Delanteras Sinterizadas", "Frenos", "Brembo", 85000, 10, "Máximo poder de frenado para calle/pista."),
    ("Pastillas de Freno Traseras Orgánicas", "Frenos", "EBC", 45000, 15, "Larga duración y cuidado del disco."),
    ("Bandas de Freno Traseras", "Frenos", "Ichiban", 25000, 20, "Zapatas de freno genéricas de alta calidad."),
    ("Pastillas de Freno Genéricas", "Frenos", "Revo", 18000, 30, "Pastillas económicas para uso diario."),
    ("Disco de Freno Delantero", "Frenos", "OEM Yamaha", 120000, 5, "Disco flotante original."),
    ("Disco de Freno Trasero", "Frenos", "OEM Honda", 95000, 5, "Disco trasero original."),
    ("Línea de Freno Blindada", "Frenos", "Venom", 65000, 8, "Manguera acerada para mayor precisión."),

    # ⚙️ Transmisión (Kits de arrastre)
    ("Kit de Arrastre O-Ring D.I.D", "Transmisión", "DID", 180000, 5, "Cadena reforzada, plato y piñón. Larga vida."),
    ("Kit de Arrastre Estándar", "Transmisión", "Choho", 85000, 12, "Kit de cadena sin O-Ring económico."),
    ("Kit de Arrastre Premium", "Transmisión", "Renthal", 220000, 3, "Kit de aluminio ultra ligero para competición."),
    ("Cadena Reforzada 428H", "Transmisión", "KMC", 45000, 15, "Cadena sola paso 428."),
    ("Cadena O-Ring 520", "Transmisión", "DID", 130000, 5, "Cadena reforzada para motos de alto cilindraje."),
    ("Piñón de Salida 14T", "Transmisión", "JT Sprockets", 25000, 10, "Piñón delantero de acero."),
    ("Plato Trasero 42T", "Transmisión", "JT Sprockets", 55000, 8, "Plato de acero al carbono."),
    ("Seguro de Cadena", "Transmisión", "Genérico", 5000, 50, "Pin de seguridad para cadenas."),

    # ⚡ Sistema Eléctrico y Encendido
    ("Bujía Estándar CPR8EA-9", "Eléctrico", "NGK", 15000, 40, "Bujía original de cobre para múltiples modelos."),
    ("Bujía Iridium CR9EIX", "Eléctrico", "NGK", 45000, 20, "Mejor chispa, menor consumo y larga vida útil."),
    ("Batería YTZ7S Libre de Mantenimiento", "Eléctrico", "Yuasa", 150000, 8, "Batería sellada 12V 6Ah."),
    ("Batería de Gel 12V 7Ah", "Eléctrico", "MAG", 95000, 12, "Batería económica de gel."),
    ("Bombillo Farola LED H4", "Eléctrico", "Phillips", 55000, 15, "Luz blanca 6000k de alta potencia."),
    ("Bombillo Halógeno H4", "Eléctrico", "Osram", 20000, 20, "Bombillo original luz amarilla."),
    ("Bombillo Direccional 12V 10W", "Eléctrico", "Genérico", 3000, 50, "Bombillo tradicional muela."),
    ("Estator/Bobina de Encendido", "Eléctrico", "OEM", 130000, 4, "Corona de bobinas para sistema de carga."),
    ("CDI Racing Sin Límite", "Eléctrico", "BRT", 95000, 5, "CDI sin limitador de RPM."),
    ("Relé de Arranque (Marano)", "Eléctrico", "OEM", 35000, 10, "Chancho o automático de arranque."),
    ("Pito / Bocina 12V", "Eléctrico", "Genérico", 15000, 15, "Bocina estándar tipo caracol."),
    ("Fusibles Muela (Set x10)", "Eléctrico", "Genérico", 10000, 30, "Set de fusibles de 10A, 15A y 20A."),

    # 🌬️ Filtros
    ("Filtro de Aceite de Papel", "Filtros", "K&N", 35000, 15, "Filtro de alto flujo KN."),
    ("Filtro de Aceite Metálico", "Filtros", "OEM", 15000, 30, "Filtro de aceite estándar interno."),
    ("Filtro de Aire Original", "Filtros", "OEM Yamaha", 45000, 10, "Elemento filtrante de aire."),
    ("Filtro de Aire Alto Flujo", "Filtros", "K&N", 120000, 4, "Filtro lavable de larga duración."),
    ("Filtro de Gasolina en línea", "Filtros", "Genérico", 5000, 40, "Filtro de combustible transparente."),

    # 🛵 Motor y Partes Internas
    ("Kit de Cilindro y Pistón", "Motor", "Vini", 180000, 3, "Cilindro completo con anillos y pasador."),
    ("Anillos de Pistón STD", "Motor", "NPR", 45000, 8, "Juego de anillos medida estándar."),
    ("Válvula de Admisión", "Motor", "OEM", 35000, 10, "Válvula original."),
    ("Válvula de Escape", "Motor", "OEM", 40000, 10, "Válvula original de escape."),
    ("Sellos de Válvula (Par)", "Motor", "NOK", 12000, 20, "Retenedores de aceite para válvulas."),
    ("Cadena de Distribución", "Motor", "DID", 55000, 8, "Cadenilla de tiempos."),
    ("Tensor de Cadenilla", "Motor", "OEM", 45000, 5, "Tensor automático de distribución."),
    ("Kit de Empaquetadura Motor", "Motor", "Vesrah", 65000, 6, "Juego completo de empaques para motor."),
    ("Empaque de Culata", "Motor", "OEM", 25000, 15, "Junta de culata metálica."),
    ("Discos de Clutch (Set)", "Motor", "FCC", 75000, 10, "Discos de embrague de fricción."),
    ("Separadores de Clutch", "Motor", "OEM", 40000, 6, "Platos metálicos separadores."),
    ("Rodamiento de Cigüeñal 6205", "Motor", "SKF", 28000, 12, "Balinera de alta revolución."),

    # 🛠️ Suspensión y Dirección
    ("Cunas de Dirección (Rodillos)", "Suspensión", "Triumph", 65000, 8, "Cunas cónicas para dirección suave."),
    ("Cunas de Dirección (Balines)", "Suspensión", "Genérico", 25000, 15, "Cunas estándar."),
    ("Retenedores de Suspensión (Par)", "Suspensión", "NOK", 35000, 12, "Retenedores de barras delanteras."),
    ("Guardapolvos de Suspensión", "Suspensión", "NOK", 25000, 10, "Protectores de barras."),
    ("Amortiguador Trasero Monoshock", "Suspensión", "YSS", 350000, 2, "Amortiguador de gas regulable."),
    ("Amortiguadores Dobles (Par)", "Suspensión", "OEM", 180000, 4, "Suspensión trasera estándar."),

    # ⚙️ Guayas y Cables
    ("Guaya de Acelerador", "Cables", "Control", 18000, 20, "Cable de acelerador lubricado."),
    ("Guaya de Clutch", "Cables", "Control", 20000, 25, "Cable de embrague alta resistencia."),
    ("Guaya de Choke (Estrangulador)", "Cables", "OEM", 15000, 10, "Cable para carburador."),
    ("Guaya de Velocímetro", "Cables", "Genérico", 12000, 15, "Cable para cuenta kilómetros."),

    # 🏍️ Llantas y Ruedas
    ("Llanta Delantera 90/90-17", "Llantas", "Pirelli Diablo", 180000, 6, "Llanta pistera excelente agarre."),
    ("Llanta Trasera 130/70-17", "Llantas", "Michelin Pilot", 250000, 5, "Llanta radial duradera."),
    ("Llanta Enduro 2.75-18", "Llantas", "Metzeler", 150000, 4, "Llanta doble propósito."),
    ("Neumático 17 (Cámara)", "Llantas", "IRC", 25000, 20, "Neumático estándar para llanta con radio."),
    ("Válvula Sellomatic", "Llantas", "Genérico", 8000, 30, "Válvula para llantas sin neumático."),
    ("Rodamiento Rueda Delantera", "Ruedas", "SKF", 18000, 15, "Balinera sellada 6202."),
    ("Cauchos de Campana (Cush Drive)", "Ruedas", "OEM", 25000, 12, "Antivibrantes para la rueda trasera."),

    # 🛵 Carrocería y Accesorios
    ("Espejos Retrovisores (Par)", "Accesorios", "Genérico", 35000, 10, "Espejos tipo originales."),
    ("Espejos Tipo Rizoma", "Accesorios", "Rizoma Replica", 55000, 8, "Espejos deportivos de aluminio."),
    ("Direccionales LED (Par)", "Accesorios", "LighTech", 45000, 12, "Indicadores LED secuenciales."),
    ("Manigueta de Freno", "Carrocería", "OEM", 15000, 20, "Palanca de freno derecho."),
    ("Manigueta de Clutch", "Carrocería", "OEM", 15000, 20, "Palanca de embrague izquierdo."),
    ("Maniguetas Escualizables (Par)", "Accesorios", "Racing", 85000, 5, "Maniguetas regulables de aluminio."),
    ("Mangos / Grips", "Accesorios", "Protaper", 35000, 15, "Mangos de goma suave para manubrio."),
    ("Protector de Tanque", "Accesorios", "Tankpad", 20000, 20, "Pad de resina para evitar rayones."),
    ("Cúpula / Visor", "Carrocería", "Puig Replica", 75000, 4, "Visor aerodinámico ahumado."),
    ("Guardabarros Delantero", "Carrocería", "OEM", 65000, 3, "Pieza plástica original."),
    ("Portaplaca Metálico", "Accesorios", "Genérico", 15000, 25, "Soporte para placa estándar."),
    ("Caja de Dirección (T)", "Carrocería", "OEM", 150000, 2, "Cristo o tija inferior."),
    ("Sliders / Topes Anticaída", "Accesorios", "FireParts", 120000, 5, "Protectores de motor laterales."),
    ("Defensa de Motor", "Accesorios", "Promoto", 95000, 4, "Defensa metálica tubular."),

    # 🛠️ Taller y Consumibles Internos
    ("Limpiador de Carburador", "Químicos", "Simoniz", 18000, 20, "Spray CarbuClean."),
    ("Desengrasante Industrial", "Químicos", "Binner", 25000, 10, "Galón de desengrasante para motor."),
    ("Silicona Alta Temperatura", "Químicos", "Loctite", 15000, 15, "Formador de empaques gris."),
    ("Traba Roscas Azul", "Químicos", "Loctite 242", 28000, 5, "Pegante de tornillos resistencia media."),
    ("Aflojatodo (WD-40)", "Químicos", "WD-40", 22000, 12, "Spray multipropósito penetrante."),
    ("Silicona Restauradora de Partes Negras", "Limpieza", "Meguiars", 45000, 6, "Restaurador de plásticos."),
    ("Champú para Moto", "Limpieza", "Simoniz", 15000, 20, "Jabón con cera carnauba."),

    # 🛑 Carburación y Combustible
    ("Kit de Carburador", "Combustible", "Keyster", 45000, 8, "Punzón, chicleres y empaques."),
    ("Chicler de Alta", "Combustible", "OEM", 8000, 30, "Boquerel principal."),
    ("Chicler de Baja", "Combustible", "OEM", 8000, 30, "Boquerel de mínima."),
    ("Manguera de Gasolina", "Combustible", "Genérico", 5000, 40, "Metro de manguera resistente a hidrocarburos."),
    ("Llave de Paso de Gasolina", "Combustible", "OEM", 25000, 10, "Grifo de combustible del tanque."),
    
    # Extra de mano de obra como "repuesto" por si acaso
    ("Insumos Menores de Taller", "Otros", "Varios", 5000, 100, "Cobro por wipe, amarres, limpiador, etc.")
]

with app.app_context():
    agregados = 0
    for nombre, cat, marca, precio, stock, desc in repuestos_data:
        # Verificar si ya existe para no duplicar
        existe = Repuesto.query.filter_by(nombre=nombre).first()
        if not existe:
            nuevo = Repuesto(
                nombre=nombre,
                categoria=cat,
                marca=marca,
                precio=precio,
                stock=stock,
                descripcion=desc
            )
            db.session.add(nuevo)
            agregados += 1
            
    db.session.commit()
    print(f"✅ Se agregaron {agregados} repuestos a la base de datos.")
    print("Inventario actual: ", Repuesto.query.count())

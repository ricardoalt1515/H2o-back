# app/services/questionnaire_data.py

# ==============================================================================
# ESTRUCTURA COMPLETA DEL CUESTIONARIO PARA HYDROUS AI
# ==============================================================================
# Este archivo contiene la definición estructurada de todas las preguntas
# utilizadas por el QuestionnaireService para guiar la conversación.

QUESTIONNAIRE_STRUCTURE = {
    # --- Saludo Inicial ---
    "initial_greeting": """
# 👋 ¡Bienvenido a Hydrous AI!

Soy el diseñador de soluciones de agua de Hydrous AI, tu asistente experto para diseñar soluciones personalizadas de tratamiento de agua y aguas residuales. Como herramienta de Hydrous, estoy aquí para guiarte paso a paso en la evaluación de las necesidades de agua de tu sitio, la exploración de posibles soluciones y la identificación de oportunidades de ahorro de costos, cumplimiento y sostenibilidad.

💡 *Las soluciones de reciclaje de agua pueden reducir el consumo de agua fresca hasta en un 70% en instalaciones industriales similares.*

¡Empecemos a configurar tu solución ideal!
""",
    # --- Preguntas Iniciales Comunes ---
    "initial_questions": [
        {
            "id": "INIT_0",
            "text": "¿Cuál es el nombre de tu empresa o proyecto?",
            "type": "open",
            "explanation": "Esto nos ayuda a identificar y personalizar tu proyecto desde el inicio.",
            # Asegúrate de que haya una coma si hay más elementos después
        },
        {
            "id": "INIT_1",
            "text": "¿En qué sector principal opera tu empresa?",
            "type": "multiple_choice",
            "options": ["Industrial", "Comercial", "Municipal", "Residencial"],
            "explanation": "Seleccionar el sector nos permite enfocar las preguntas siguientes y entender el contexto general de tus necesidades de agua.",
        },
        {
            "id": "INIT_2",
            "text": "Dentro del sector '{sector}', ¿cuál es el giro específico?",  # Texto con placeholder
            "type": "conditional_multiple_choice",
            "depends_on_key": "selected_sector",  # Clave DEL ESTADO que contiene el valor a buscar
            "conditions": {  # Diccionario con las opciones por cada valor posible
                "Industrial": [
                    "Alimentos y Bebidas",
                    "Textil",
                    "Petroquímica",
                    "Farmacéutica",
                    "Minería",
                    "Petróleo y Gas",
                    "Metal/Automotriz",
                    "Cemento",
                    "Otro",  # Importante tener 'Otro' como opción
                ],
                "Comercial": [
                    "Hotel",
                    "Edificio de oficinas",
                    "Centro comercial/Comercio minorista",
                    "Restaurante",
                    "Otro",
                ],
                "Municipal": [
                    "Gobierno de la ciudad",
                    "Pueblo/Aldea",
                    "Autoridad de servicios de agua",
                    "Otro",
                ],
                "Residencial": [
                    "Vivienda unifamiliar",
                    "Edificio multifamiliar",
                    "Otro",
                ],
            },
            "explanation": "Conocer el giro específico nos ayuda a anticipar los tipos de contaminantes, los usos del agua y las regulaciones más relevantes para tu operación.",
        },
    ],
    # --- Cuestionarios Específicos por Sector y Subsector ---
    "sector_questionnaires": {
        # ==========================
        # === SECTOR INDUSTRIAL ===
        # ==========================
        "Industrial": {
            # --- Subsector: Alimentos y Bebidas ---
            "Alimentos y Bebidas": [
                # Sección: Datos Clave (Ubicación, Costo, Consumo)
                {
                    "id": "IAB_1",
                    "text": "Ubicación (Colonia, Ciudad, Código Postal, Estado/País)",
                    "type": "open",
                    "explanation": "La ubicación influye en la normativa local (ej. NOMs en México), costos de agua, disponibilidad y clima, factores clave para el diseño.",
                },
                {
                    "id": "IAB_2",
                    "text": "¿Cuál es el costo aproximado del agua que pagas actualmente? (Ej: MXN/m³, USD/galón)",
                    "type": "open",
                    "explanation": "El costo actual del agua es fundamental para calcular el potencial de ahorro y el retorno de la inversión (ROI) de la solución propuesta.",
                },
                {
                    "id": "IAB_3",
                    "text": "¿Cuánta agua consume tu instalación aproximadamente? (Especifica volumen y periodo, ej: 500 m³/día, 10,000 m³/mes)",
                    "type": "open",
                    "explanation": "El volumen de consumo diario o mensual nos ayuda a dimensionar correctamente los equipos y tanques del sistema de tratamiento.",
                },
                {
                    "id": "IAB_4",
                    "text": "¿Cuánta agua residual generan aproximadamente? (Si no lo sabes, suele ser 80-90% del consumo. Especifica volumen y periodo)",
                    "type": "open",
                    "explanation": "El flujo de aguas residuales es el parámetro más crítico para diseñar la capacidad de la planta de tratamiento (PTAR).",
                },
                {
                    "id": "IAB_5",
                    "text": "¿Aproximadamente cuántas personas (empleados, visitantes) utilizan las instalaciones diariamente de media?",
                    "type": "multiple_choice",
                    "options": [
                        "Menos de 20",
                        "20 - 49",
                        "50 - 199",
                        "200 - 499",
                        "500 - 999",
                        "1000 - 1999",
                        "2000 - 4999",
                        "5000 o más",
                        "Prefiero proveer un número exacto",
                    ],
                    "explanation": "Esto nos ayuda a estimar la carga hidráulica y orgánica proveniente de usos sanitarios, adicional a la carga del proceso industrial.",
                },
                # Sección: Calidad de Agua y Requerimientos Técnicos
                {
                    "id": "IAB_6",
                    "text": "Describe brevemente los volúmenes promedio y los picos de generación de agua residual (ej. flujo constante, picos en ciertos turnos/días).",
                    "type": "open",
                    "explanation": "Entender la variabilidad del flujo es crucial para diseñar tanques de ecualización que homogenicen el agua antes del tratamiento.",
                },
                {
                    "id": "IAB_7",
                    "text": "¿Tienes análisis fisicoquímicos de tus aguas residuales (recientes o históricos)? Si es así, ¿podrías subir el archivo?",
                    "type": "document_upload",  # Frontend debe manejar la subida
                    "explanation": "Los análisis de agua son VITALES. Nos dicen qué contaminantes tratar (DBO, DQO, SST, GyA, pH) y en qué concentración, lo que define la tecnología necesaria.",
                },
                {
                    "id": "IAB_8",
                    "depends_on": {
                        "id": "IAB_7",
                        "value_is_negative": True,
                    },  # Preguntar solo si NO se subió análisis
                    "text": "Como no tenemos un análisis, ¿podrías estimar (o indicar si son altos/medios/bajos) los siguientes parámetros clave en tus aguas residuales de Alimentos y Bebidas?",
                    "type": "multiple_open",
                    "sub_questions": [
                        {
                            "id": "IAB_8_BOD",
                            "label": "DBO (Demanda Bioquímica de Oxígeno) en mg/L:",
                        },
                        {
                            "id": "IAB_8_COD",
                            "label": "DQO (Demanda Química de Oxígeno) en mg/L:",
                        },
                        {
                            "id": "IAB_8_TSS",
                            "label": "SST (Sólidos Suspendidos Totales) en mg/L:",
                        },
                        {
                            "id": "IAB_8_TDS",
                            "label": "SDT (Sólidos Disueltos Totales) en mg/L (aprox):",
                        },
                        {
                            "id": "IAB_8_PH",
                            "label": "pH (rango típico, ej: 5-6, 9-10):",
                        },
                        {
                            "id": "IAB_8_FOG",
                            "label": "Grasas y Aceites (GyA) (altos/medios/bajos o mg/L):",
                        },
                    ],
                    "explanation": "Estos parámetros son críticos en Alimentos y Bebidas. DBO/DQO miden carga orgánica, SST los sólidos, pH la acidez, y GyA las grasas, todos impactan el tratamiento.",
                },
                {
                    "id": "IAB_9",
                    "text": "¿Cuáles son los principales usos del agua en tu planta?",
                    "type": "multiple_choice",  # Podría ser multiple selection si el frontend lo soporta
                    "options": [
                        "Agua como ingrediente / Materia Prima",
                        "Limpieza y Saneamiento (CIP, lavado de equipos/pisos)",
                        "Procesos de Enfriamiento (torres, chillers)",
                        "Generación de Vapor (calderas)",
                        "Transporte de producto",
                        "Riego de áreas verdes",
                        "Uso sanitario (baños, cocinas)",
                        "Otro (especificar)",
                    ],
                    "explanation": "Conocer los usos nos ayuda a identificar oportunidades de reúso interno del agua tratada para fines no potables y a entender la calidad requerida.",
                },
                {
                    "id": "IAB_10",
                    "text": "¿Cuál es tu fuente principal de abastecimiento de agua?",
                    "type": "multiple_choice",
                    "options": [
                        "Red municipal",
                        "Pozo propio",
                        "Agua superficial (río, lago) - requiere permiso",
                        "Pipa (camión cisterna)",
                        "Cosecha de agua de lluvia",
                        "Otro (especificar)",
                    ],
                    "explanation": "La fuente de agua influye en su calidad inicial (dureza, sales, etc.) y en la necesidad de pretratamiento antes de su uso o tratamiento posterior.",
                },
                # Sección: Agua Potable (Opcional si aplica)
                {
                    "id": "IAB_11",
                    "text": "¿Necesitas también tratamiento para agua potable o purificada para algún proceso o consumo humano dentro de la planta?",
                    "type": "yes_no",  # Opciones: Si / No
                    "options": ["Sí", "No"],
                    "explanation": "Podemos diseñar soluciones integrales. Si necesitas agua potable, preguntaremos sobre sus detalles.",
                },
                {
                    "id": "IAB_12",
                    "depends_on": {"id": "IAB_11", "value": "Sí"},
                    "text": "Para el agua potable/purificada: ¿Cuál es el volumen aproximado requerido y tienes análisis de la calidad del agua de entrada?",
                    "type": "open",  # Podría ser multiple_open o pedir subida
                    "explanation": "Si necesitas agua potable, requerimos saber cuánto y la calidad de la fuente para diseñar el sistema de potabilización/purificación (ej. filtración, ósmosis, UV).",
                },
                # Sección: Objetivos del Proyecto
                {
                    "id": "IAB_13",
                    "text": "¿Cuál es el objetivo principal que buscas al implementar una solución de tratamiento/reciclaje de agua?",
                    "type": "multiple_choice",
                    "options": [
                        "Cumplimiento normativo (evitar multas, cumplir límites de descarga)",
                        "Reducción de la huella ambiental / Sostenibilidad / Metas ESG",
                        "Ahorro de costos (reducir pago de agua y/o descarga) / Proyecto con ROI",
                        "Asegurar mayor disponibilidad de agua / Resiliencia hídrica",
                        "Mejorar imagen corporativa",
                        "Otro (especificar)",
                    ],
                    "explanation": "Entender tu principal motivación (cumplimiento, ahorro, sostenibilidad) nos ayuda a priorizar las tecnologías y enfocar la propuesta en tus metas clave.",
                },
                {
                    "id": "IAB_14",
                    "text": "Si buscas reutilizar el agua tratada, ¿para qué usos específicos la destinarías?",
                    "type": "multiple_choice",  # Podría ser multiple selection
                    "options": [
                        "Riego de áreas verdes",
                        "Reúso en sanitarios (WC)",
                        "Reúso en procesos industriales (ej. lavado inicial, torres enfriamiento)",
                        "Reúso en limpieza general (pisos, vehículos)",
                        "Recarga de acuíferos (si la regulación lo permite)",
                        "Venta a terceros (si aplica)",
                        "Descarga cumpliendo normativa (NOM-001, 002, 003 u otra)",
                        "Otro (especificar)",
                    ],
                    "explanation": "El uso final del agua tratada define la calidad requerida y, por lo tanto, el nivel de tratamiento necesario (secundario, terciario, avanzado).",
                },
                {
                    "id": "IAB_15",
                    "text": "¿Dónde descargas actualmente tus aguas residuales (tratadas o sin tratar)?",
                    "type": "multiple_choice",
                    "options": [
                        "Alcantarillado municipal (requiere cumplir límites específicos)",
                        "Cuerpo de agua natural (río, lago, mar - requiere permiso y cumplir NOM-001)",
                        "Infiltración al subsuelo (requiere permiso y cumplir NOM-001/002)",
                        "Red de drenaje pluvial (generalmente prohibido)",
                        "Servicio de recolección por terceros (pipas)",
                        "No descargo / Evaporación (requiere manejo de lodos/sales)",
                        "Otro (especificar)",
                    ],
                    "explanation": "El punto de descarga actual y sus requisitos normativos son cruciales. Si es alcantarillado, hay límites; si es cuerpo receptor, son más estrictos (NOM-001).",
                },
                # Sección: Restricciones y Consideraciones
                {
                    "id": "IAB_16",
                    "text": "¿Tienes alguna restricción importante para el proyecto? (Marca las que apliquen o describe)",
                    "type": "multiple_choice",  # Podría ser multiple selection
                    "options": [
                        "Limitaciones de espacio físico para la planta",
                        "Restricciones normativas específicas (aparte de las NOMs estándar)",
                        "Calidad de agua de entrada muy compleja o variable",
                        "Preferencia o rechazo por ciertas tecnologías",
                        "Presupuesto de inversión inicial (CAPEX) limitado (indicar rango si es posible)",
                        "Preocupación por costos operativos (OPEX - energía, químicos, personal)",
                        "Dificultad para manejo/disposición de lodos o residuos del tratamiento",
                        "Disponibilidad limitada de energía eléctrica en sitio",
                        "Otro (especificar)",
                    ],
                    "explanation": "Conocer las limitaciones (espacio, presupuesto, energía, etc.) desde el principio nos permite diseñar una solución viable y realista para tu contexto.",
                },
                {  # Pregunta de detalle si mencionan presupuesto limitado
                    "id": "IAB_16_BUDGET",
                    "depends_on": {
                        "id": "IAB_16",
                        "value_contains": "Presupuesto",
                    },  # Simplificado
                    "text": "Mencionaste limitaciones de presupuesto. ¿Podrías indicar un rango estimado (CAPEX) para este proyecto?",
                    "type": "open",
                    "explanation": "Tener una idea del presupuesto nos ayuda a explorar opciones tecnológicas y de financiamiento adecuadas.",
                },
                # Sección: Infraestructura Existente
                {
                    "id": "IAB_17",
                    "text": "¿Cuentas actualmente con algún sistema de tratamiento de agua residual o de potabilización?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "Saber si existe infraestructura nos permite evaluar si se puede modernizar, ampliar o si se requiere un sistema completamente nuevo.",
                },
                {
                    "id": "IAB_18",
                    "depends_on": {"id": "IAB_17", "value": "Sí"},
                    "text": "Si tienes sistema existente: ¿Podrías describir brevemente los procesos/tecnologías que utiliza? (ej. cárcamo, reactor biológico, sedimentador). ¿Funciona correctamente?",
                    "type": "open",
                    "explanation": "Detalles del sistema actual nos ayudan a entender qué funciona, qué no, y qué se puede aprovechar o necesita ser reemplazado.",
                },
                {
                    "id": "IAB_19",
                    "depends_on": {"id": "IAB_17", "value": "Sí"},
                    "text": "Si es posible, ¿podrías subir diagramas de proceso, layouts o fotografías del sistema existente?",
                    "type": "document_upload",
                    "explanation": "La documentación visual o técnica del sistema actual es extremadamente útil para un diagnóstico más preciso.",
                },
                # Sección: Presupuesto, Tiempos y Cierre
                {
                    "id": "IAB_20",
                    "text": "¿Cuál es el presupuesto estimado (CAPEX) que tienes contemplado para invertir en este proyecto de agua? (Si no es fijo, un rango)",
                    "type": "open",
                    "explanation": "Conocer el presupuesto de inversión nos permite proponer tecnologías y alcances acordes a tus posibilidades financieras.",
                },
                {
                    "id": "IAB_21",
                    "text": "¿En qué plazo tienes contemplado implementar este proyecto?",
                    "type": "multiple_choice",
                    "options": [
                        "Inmediato (0-6 meses)",
                        "Corto plazo (6-12 meses)",
                        "Mediano plazo (1-3 años)",
                        "Largo plazo (más de 3 años)",
                        "Aún no definido",
                    ],
                    "explanation": "El plazo deseado influye en la planificación, ingeniería y procura de equipos.",
                },
                {
                    "id": "IAB_22",
                    "text": "¿Cuentas con financiamiento propio para el proyecto o explorarías opciones como arrendamiento, BOO (Build-Own-Operate), etc.?",
                    "type": "multiple_choice",
                    "options": [
                        "Financiamiento propio asegurado",
                        "Buscando opciones de financiamiento / crédito",
                        "Interesado en modelos de servicio (arrendamiento, BOO, etc.)",
                        "Aún no definido",
                    ],
                    "explanation": "Existen diferentes modelos financieros. Saber tu preferencia nos ayuda a estructurar la propuesta económica.",
                },
                {
                    "id": "IAB_23",
                    "text": "¿Sería posible que nos compartieras (subir archivo) un recibo de agua reciente?",
                    "type": "document_upload",
                    "explanation": "El recibo de agua nos da información oficial sobre tu tarifa actual, consumo registrado y cargos, lo cual es muy útil para el análisis de ROI.",
                },
                {
                    "id": "IAB_24",
                    "text": "¿Tienes algún cronograma específico o fases planeadas para la implementación?",
                    "type": "open",
                    "explanation": "Si tienes un plan de implementación, podemos alinear nuestra propuesta a tus fases y tiempos.",
                },
                {
                    "id": "IAB_25",
                    "text": "Finalmente, ¿hay planes de crecimiento o expansión de tu producción/instalación en el futuro cercano que debamos considerar para el diseño?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "Es importante diseñar con visión a futuro. Si planeas crecer, podemos prever la capacidad de ampliación del sistema.",
                },
                {
                    "id": "IAB_26",
                    "depends_on": {"id": "IAB_25", "value": "Sí"},
                    "text": "Si planeas crecer, ¿en qué porcentaje aproximado y en qué plazo?",
                    "type": "open",
                    "explanation": "Estimar el crecimiento futuro nos permite diseñar un sistema modular o con capacidad de expansión adecuada.",
                },
            ],
            # --- Subsector: Textil ---
            "Textil": [
                # Sección: Datos Clave (Ubicación, Costo, Consumo) - Repetir o referenciar comunes
                {
                    "id": "ITX_1",
                    "text": "Ubicación (Colonia, Ciudad, Código Postal, Estado/País)",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "ITX_2",
                    "text": "¿Costo aproximado del agua? (Ej: MXN/m³, USD/galón)",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "ITX_3",
                    "text": "¿Consumo aproximado de agua? (Volumen y periodo)",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "ITX_4",
                    "text": "¿Generación aproximada de agua residual? (Volumen y periodo)",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "ITX_5",
                    "text": "¿Personas promedio en instalaciones?",
                    "type": "multiple_choice",
                    "options": ["Menos de 20", "20-49", ...],
                    "explanation": "...",
                },  # Usar mismas opciones
                # Sección: Calidad de Agua y Requerimientos Técnicos (Específico Textil)
                {
                    "id": "ITX_6",
                    "text": "Describe volúmenes promedio y picos de generación de AR.",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "ITX_7",
                    "text": "¿Tienes análisis fisicoquímicos de tus aguas residuales?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "ITX_8",
                    "depends_on": {"id": "ITX_7", "value_is_negative": True},
                    "text": "Estimación de parámetros clave en aguas residuales Textiles:",
                    "type": "multiple_open",
                    "sub_questions": [
                        {
                            "id": "ITX_8_COLOR",
                            "label": "Color (Intenso/Medio/Bajo o unidades Pt-Co):",
                        },
                        {
                            "id": "ITX_8_TSS",
                            "label": "SST (Sólidos Suspendidos Totales) en mg/L:",
                        },
                        {
                            "id": "ITX_8_PH",
                            "label": "pH (rango típico, ej: 9-11 en teñido):",
                        },
                        {
                            "id": "ITX_8_METALS",
                            "label": "Metales pesados (presencia Sí/No, o cuáles):",
                        },  # Cromo, cobre, etc.
                        {
                            "id": "ITX_8_COD",
                            "label": "DQO (Demanda Química de Oxígeno) en mg/L:",
                        },
                        {
                            "id": "ITX_8_BOD",
                            "label": "DBO (Demanda Bioquímica de Oxígeno) en mg/L:",
                        },
                        {
                            "id": "ITX_8_TDS",
                            "label": "SDT (Sólidos Disueltos Totales) en mg/L (aprox):",
                        },  # Importante por sales
                    ],
                    "explanation": "En textil, el Color, pH alcalino, Metales (de tintes), DQO alta y Sales (SDT) son los desafíos principales para el tratamiento.",
                },
                {
                    "id": "ITX_9",
                    "text": "¿Cuáles son los principales usos del agua en tu planta textil?",
                    "type": "multiple_choice",
                    "options": [
                        "Lavado de materia prima (lana, algodón)",
                        "Teñido e impresión",
                        "Enjuague y acabado",
                        "Generación de Vapor (calderas)",
                        "Agua de Enfriamiento",
                        "Uso sanitario",
                        "Otro (especificar)",
                    ],
                    "explanation": "Identificar los usos (especialmente teñido y acabado) nos indica dónde se generan las aguas más contaminadas y dónde se podría reutilizar agua tratada.",
                },
                {
                    "id": "ITX_10",
                    "text": "¿Fuente principal de abastecimiento de agua?",
                    "type": "multiple_choice",
                    "options": ["Red municipal", ...],
                    "explanation": "...",
                },
                # Sección: Agua Potable (Común)
                {
                    "id": "ITX_11",
                    "text": "¿Necesitas también tratamiento para agua potable/purificada?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "ITX_12",
                    "depends_on": {"id": "ITX_11", "value": "Sí"},
                    "text": "Para agua potable: ¿Volumen requerido y análisis de entrada?",
                    "type": "open",
                    "explanation": "...",
                },
                # Sección: Objetivos del Proyecto (Común)
                {
                    "id": "ITX_13",
                    "text": "¿Objetivo principal del proyecto?",
                    "type": "multiple_choice",
                    "options": ["Cumplimiento normativo", ...],
                    "explanation": "...",
                },
                {
                    "id": "ITX_14",
                    "text": "¿Usos específicos para el agua tratada/reutilizada?",
                    "type": "multiple_choice",
                    "options": ["Riego", ...],
                    "explanation": "...",
                },
                {
                    "id": "ITX_15",
                    "text": "¿Dónde descargas actualmente tus aguas residuales?",
                    "type": "multiple_choice",
                    "options": ["Alcantarillado", ...],
                    "explanation": "...",
                },
                # Sección: Restricciones y Consideraciones (Común)
                {
                    "id": "ITX_16",
                    "text": "¿Restricciones importantes del proyecto?",
                    "type": "multiple_choice",
                    "options": ["Limitaciones de espacio", ...],
                    "explanation": "...",
                },
                {
                    "id": "ITX_16_BUDGET",
                    "depends_on": {"id": "ITX_16", "value_contains": "Presupuesto"},
                    "text": "Rango de presupuesto estimado (CAPEX)?",
                    "type": "open",
                    "explanation": "...",
                },
                # Sección: Infraestructura Existente (Común)
                {
                    "id": "ITX_17",
                    "text": "¿Cuentas con sistema de tratamiento existente?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "ITX_18",
                    "depends_on": {"id": "ITX_17", "value": "Sí"},
                    "text": "Si existe: ¿Descripción breve y estado?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "ITX_19",
                    "depends_on": {"id": "ITX_17", "value": "Sí"},
                    "text": "Si existe: ¿Puedes subir diagramas/fotos?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                # Sección: Presupuesto, Tiempos y Cierre (Común)
                {
                    "id": "ITX_20",
                    "text": "¿Presupuesto estimado (CAPEX)?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "ITX_21",
                    "text": "¿Plazo de implementación deseado?",
                    "type": "multiple_choice",
                    "options": ["Inmediato (0-6 meses)", ...],
                    "explanation": "...",
                },
                {
                    "id": "ITX_22",
                    "text": "¿Financiamiento propio o buscas opciones?",
                    "type": "multiple_choice",
                    "options": ["Propio", ...],
                    "explanation": "...",
                },
                {
                    "id": "ITX_23",
                    "text": "¿Puedes compartir recibo de agua?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "ITX_24",
                    "text": "¿Cronograma o fases planeadas?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "ITX_25",
                    "text": "¿Planes de crecimiento futuro?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "ITX_26",
                    "depends_on": {"id": "ITX_25", "value": "Sí"},
                    "text": "Si planeas crecer: ¿Porcentaje y plazo?",
                    "type": "open",
                    "explanation": "...",
                },
            ],
            # --- Subsector: Petroquímica ---
            "Petroquímica": [
                # Datos Clave
                {
                    "id": "IPQ_1",
                    "text": "Ubicación...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IPQ_2",
                    "text": "Costo agua...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IPQ_3",
                    "text": "Consumo agua...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IPQ_4",
                    "text": "Generación AR...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IPQ_5",
                    "text": "Personas...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                # Calidad Agua (Específico Petroquímica)
                {
                    "id": "IPQ_6",
                    "text": "Volúmenes promedio y picos AR...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IPQ_7",
                    "text": "¿Análisis de AR?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "IPQ_8",
                    "depends_on": {"id": "IPQ_7", "value_is_negative": True},
                    "text": "Estimación de parámetros clave en aguas residuales Petroquímicas:",
                    "type": "multiple_open",
                    "sub_questions": [
                        {
                            "id": "IPQ_8_TDS",
                            "label": "SDT (Sólidos Disueltos Totales) en mg/L:",
                        },  # Sales, alta conductividad
                        {
                            "id": "IPQ_8_HYDROCARBONS",
                            "label": "Hidrocarburos (TPH, BTEX) (Altos/Medios/Bajos o mg/L):",
                        },
                        {"id": "IPQ_8_PH", "label": "pH (rango típico):"},
                        {
                            "id": "IPQ_8_COD",
                            "label": "DQO (Demanda Química de Oxígeno) en mg/L:",
                        },  # A menudo alta y recalcitrante
                        {
                            "id": "IPQ_8_METALS",
                            "label": "Metales pesados (presencia Sí/No, cuáles):",
                        },  # Vanadio, Níquel, etc.
                        {"id": "IPQ_8_PHENOLS", "label": "Fenoles (Sí/No o mg/L):"},
                        {"id": "IPQ_8_AMMONIA", "label": "Amoniaco (Sí/No o mg/L):"},
                    ],
                    "explanation": "En petroquímica, Hidrocarburos, DQO alta/tóxica, Sales (SDT), Metales, Fenoles y Amoniaco son los contaminantes críticos a tratar.",
                },
                {
                    "id": "IPQ_9",
                    "text": "¿Cuáles son los principales usos del agua en tu planta petroquímica?",
                    "type": "multiple_choice",
                    "options": [
                        "Agua de Enfriamiento (muy común, grandes volúmenes)",
                        "Agua de Proceso (reacciones, dilución, lavado)",
                        "Generación de Vapor (calderas de alta presión)",
                        "Agua contra Incendios",
                        "Servicios generales / Uso sanitario",
                        "Otro (especificar)",
                    ],
                    "explanation": "El agua de enfriamiento y la generación de vapor suelen ser los mayores consumidores, y las purgas de estos sistemas generan aguas residuales con alta salinidad.",
                },
                {
                    "id": "IPQ_10",
                    "text": "¿Fuente principal de agua?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                # Agua Potable
                {
                    "id": "IPQ_11",
                    "text": "¿Necesitas tratamiento agua potable?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "IPQ_12",
                    "depends_on": {"id": "IPQ_11", "value": "Sí"},
                    "text": "Agua potable: ¿Volumen y análisis?",
                    "type": "open",
                    "explanation": "...",
                },
                # Objetivos, Restricciones, Infraestructura, Cierre (Comunes)
                {
                    "id": "IPQ_13",
                    "text": "Objetivo principal...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IPQ_14",
                    "text": "Usos para agua tratada...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IPQ_15",
                    "text": "Descarga actual AR...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IPQ_16",
                    "text": "Restricciones proyecto...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IPQ_16_BUDGET",
                    "depends_on": {"id": "IPQ_16", "value_contains": "Presupuesto"},
                    "text": "Rango presupuesto...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IPQ_17",
                    "text": "¿Sistema existente?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "IPQ_18",
                    "depends_on": {"id": "IPQ_17", "value": "Sí"},
                    "text": "Descripción sistema...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IPQ_19",
                    "depends_on": {"id": "IPQ_17", "value": "Sí"},
                    "text": "¿Subir diagramas/fotos?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "IPQ_20",
                    "text": "Presupuesto estimado...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IPQ_21",
                    "text": "Plazo implementación...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IPQ_22",
                    "text": "Financiamiento...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IPQ_23",
                    "text": "¿Compartir recibo agua?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "IPQ_24",
                    "text": "¿Cronograma/fases?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IPQ_25",
                    "text": "¿Planes crecimiento?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "IPQ_26",
                    "depends_on": {"id": "IPQ_25", "value": "Sí"},
                    "text": "Detalles crecimiento...",
                    "type": "open",
                    "explanation": "...",
                },
            ],
            # --- Subsector: Farmacéutica ---
            "Farmacéutica": [
                # Datos Clave
                {
                    "id": "IFM_1",
                    "text": "Ubicación...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IFM_2",
                    "text": "Costo agua...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IFM_3",
                    "text": "Consumo agua...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IFM_4",
                    "text": "Generación AR...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IFM_5",
                    "text": "Personas...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                # Calidad Agua (Específico Farmacéutica)
                {
                    "id": "IFM_6",
                    "text": "Volúmenes promedio y picos AR...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IFM_7",
                    "text": "¿Análisis de AR?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "IFM_8",
                    "depends_on": {"id": "IFM_7", "value_is_negative": True},
                    "text": "Estimación de parámetros clave en aguas residuales Farmacéuticas:",
                    "type": "multiple_open",
                    "sub_questions": [
                        {
                            "id": "IFM_8_COD",
                            "label": "DQO (Demanda Química de Oxígeno) en mg/L:",
                        },  # Puede ser alta y variable
                        {
                            "id": "IFM_8_TOC",
                            "label": "COT (Carbono Orgánico Total) en mg/L:",
                        },  # A veces se usa en lugar de DQO
                        {
                            "id": "IFM_8_TDS",
                            "label": "SDT (Sólidos Disueltos Totales) / Conductividad (µS/cm):",
                        },  # Por sales y solventes
                        {
                            "id": "IFM_8_PH",
                            "label": "pH (rango típico, puede variar mucho):",
                        },
                        {
                            "id": "IFM_8_API",
                            "label": "Presencia de APIs (Principios Activos) / Antibióticos (Sí/No):",
                        },  # Contaminantes de preocupación emergente
                        {
                            "id": "IFM_8_SOLVENTS",
                            "label": "Presencia de Solventes orgánicos (Sí/No):",
                        },
                        {
                            "id": "IFM_8_SANITIZERS",
                            "label": "Presencia de Desinfectantes/Sanitizantes (Sí/No):",
                        },  # Pueden inhibir tratamiento biológico
                    ],
                    "explanation": "En farma, DQO/COT, SDT, pH variable, y la presencia de APIs, solventes y sanitizantes son cruciales. El tratamiento debe poder manejar compuestos complejos y potencialmente tóxicos.",
                },
                {
                    "id": "IFM_9",
                    "text": "¿Cuáles son los principales usos del agua en tu planta farmacéutica?",
                    "type": "multiple_choice",
                    "options": [
                        "Agua Purificada (PW) / Agua para Inyección (WFI) para formulación",
                        "Limpieza y esterilización de equipos (CIP/SIP)",
                        "Procesos de enfriamiento",
                        "Generación de vapor limpio/puro",
                        "Laboratorios / Investigación y Desarrollo",
                        "Servicios generales / Uso sanitario",
                        "Otro (especificar)",
                    ],
                    "explanation": "El uso de agua de alta pureza (PW/WFI) es central. Las aguas residuales provienen de su producción (rechazo de OI), limpieza y procesos, cada una con características distintas.",
                },
                {
                    "id": "IFM_10",
                    "text": "¿Cuál es tu fuente principal de agua cruda (antes de purificarla)?",
                    "type": "multiple_choice",
                    "options": [
                        "Red municipal",
                        "Pozo propio",
                        "Agua superficial (río, lago)",
                        "Otro (especificar)",
                    ],
                    "explanation": "La calidad del agua de entrada afecta directamente el diseño y costo del sistema de pretratamiento y purificación.",
                },
                # Agua Potable (Menos relevante si ya producen PW/WFI, pero puede ser para oficinas)
                {
                    "id": "IFM_11",
                    "text": "¿Necesitas tratamiento adicional para agua de servicios generales/oficinas?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "IFM_12",
                    "depends_on": {"id": "IFM_11", "value": "Sí"},
                    "text": "Para agua de servicios: ¿Volumen y análisis?",
                    "type": "open",
                    "explanation": "...",
                },
                # Objetivos, Restricciones, Infraestructura, Cierre (Comunes)
                {
                    "id": "IFM_13",
                    "text": "Objetivo principal...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IFM_14",
                    "text": "Usos para agua tratada...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IFM_15",
                    "text": "Descarga actual AR...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IFM_16",
                    "text": "Restricciones proyecto...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IFM_16_BUDGET",
                    "depends_on": {"id": "IFM_16", "value_contains": "Presupuesto"},
                    "text": "Rango presupuesto...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IFM_17",
                    "text": "¿Sistema existente?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "IFM_18",
                    "depends_on": {"id": "IFM_17", "value": "Sí"},
                    "text": "Descripción sistema...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IFM_19",
                    "depends_on": {"id": "IFM_17", "value": "Sí"},
                    "text": "¿Subir diagramas/fotos?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "IFM_20",
                    "text": "Presupuesto estimado...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IFM_21",
                    "text": "Plazo implementación...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IFM_22",
                    "text": "Financiamiento...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IFM_23",
                    "text": "¿Compartir recibo agua?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "IFM_24",
                    "text": "¿Cronograma/fases?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IFM_25",
                    "text": "¿Planes crecimiento?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "IFM_26",
                    "depends_on": {"id": "IFM_25", "value": "Sí"},
                    "text": "Detalles crecimiento...",
                    "type": "open",
                    "explanation": "...",
                },
            ],
            # --- Subsector: Minería ---
            "Minería": [
                # Datos Clave
                {
                    "id": "IMN_1",
                    "text": "Ubicación...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IMN_2",
                    "text": "Costo agua (si aplica, a menudo es fuente propia)...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IMN_3",
                    "text": "Consumo agua...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IMN_4",
                    "text": "Generación AR (Drenaje ácido de mina, aguas de proceso)...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IMN_5",
                    "text": "Personas (campamento, operación)...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                # Calidad Agua (Específico Minería)
                {
                    "id": "IMN_6",
                    "text": "Volúmenes promedio y picos AR...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IMN_7",
                    "text": "¿Análisis de AR (drenaje ácido, agua de proceso, etc.)?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "IMN_8",
                    "depends_on": {"id": "IMN_7", "value_is_negative": True},
                    "text": "Estimación de parámetros clave en aguas residuales de Minería:",
                    "type": "multiple_open",
                    "sub_questions": [
                        {
                            "id": "IMN_8_PH",
                            "label": "pH (rango típico, puede ser MUY bajo en drenaje ácido):",
                        },
                        {
                            "id": "IMN_8_METALS",
                            "label": "Metales Pesados (Sí/No, cuáles y concentración aprox.):",
                        },  # Fe, Cu, Zn, Pb, As, Cd, etc.
                        {
                            "id": "IMN_8_TSS",
                            "label": "SST (Sólidos Suspendidos Totales) en mg/L (muy altos a menudo):",
                        },
                        {
                            "id": "IMN_8_TDS",
                            "label": "SDT (Sólidos Disueltos Totales) / Sulfatos (SO₄²⁻) en mg/L:",
                        },  # Altos por disolución mineral
                        {
                            "id": "IMN_8_ACIDITY",
                            "label": "Acidez / Alcalinidad (mg/L CaCO₃):",
                        },
                        {
                            "id": "IMN_8_CYANIDE",
                            "label": "Cianuro (en minería de oro/plata) (Sí/No o mg/L):",
                        },
                        {
                            "id": "IMN_8_REAGENTS",
                            "label": "Otros reactivos de flotación/lixiviación (Sí/No):",
                        },
                    ],
                    "explanation": "En minería, el pH extremo (ácido), altas cargas de Metales Pesados, Sólidos (SST/SDT), Sulfatos y potencialmente Cianuro/Reactivos son los mayores retos.",
                },
                {
                    "id": "IMN_9",
                    "text": "¿Cuáles son los principales usos del agua en la operación minera?",
                    "type": "multiple_choice",
                    "options": [
                        "Procesamiento de minerales (flotación, lixiviación, molienda)",
                        "Supresión de polvo (caminos, pilas)",
                        "Refrigeración de equipos",
                        "Transporte de pulpas/relaves",
                        "Consumo humano / Servicios en campamento",
                        "Riego / Revegetación",
                        "Otro (especificar)",
                    ],
                    "explanation": "El procesamiento de minerales consume grandes cantidades. El reúso es clave, especialmente en zonas áridas. El agua de contacto con minerales (drenaje) es la más contaminada.",
                },
                {
                    "id": "IMN_10",
                    "text": "¿Fuente principal de abastecimiento de agua?",
                    "type": "multiple_choice",
                    "options": [
                        "Agua superficial (río, lago cercano)",
                        "Agua subterránea (pozos, galerías de mina)",
                        "Agua de mar (si está en costa, requiere desalinización)",
                        "Reutilización interna / Agua recuperada de relaves",
                        "Pipa (menos común para grandes volúmenes)",
                        "Otro (especificar)",
                    ],
                    "explanation": "Las minas a menudo dependen de fuentes propias (pozos, ríos) o recirculación interna, enfrentando desafíos de disponibilidad y calidad.",
                },
                # Agua Potable (Para campamentos)
                {
                    "id": "IMN_11",
                    "text": "¿Necesitas tratamiento de agua potable para campamentos/oficinas?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "IMN_12",
                    "depends_on": {"id": "IMN_11", "value": "Sí"},
                    "text": "Agua potable: ¿Volumen y análisis fuente?",
                    "type": "open",
                    "explanation": "...",
                },
                # Objetivos, Restricciones, Infraestructura, Cierre (Comunes, con énfasis minero)
                {
                    "id": "IMN_13",
                    "text": "Objetivo principal (Cumplimiento ambiental estricto, gestión del agua, cierre de mina...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IMN_14",
                    "text": "Usos para agua tratada (Reúso en proceso, descarga segura, revegetación...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IMN_15",
                    "text": "Descarga actual AR (Presa de relaves, cuerpo receptor, ZLD...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IMN_16",
                    "text": "Restricciones (Ubicación remota, clima extremo, manejo de lodos/sales, energía...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IMN_16_BUDGET",
                    "depends_on": {"id": "IMN_16", "value_contains": "Presupuesto"},
                    "text": "Rango presupuesto...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IMN_17",
                    "text": "¿Sistema existente (Plantas de neutralización, espesadores...)?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "IMN_18",
                    "depends_on": {"id": "IMN_17", "value": "Sí"},
                    "text": "Descripción sistema...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IMN_19",
                    "depends_on": {"id": "IMN_17", "value": "Sí"},
                    "text": "¿Subir diagramas/fotos?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "IMN_20",
                    "text": "Presupuesto estimado...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IMN_21",
                    "text": "Plazo implementación...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IMN_22",
                    "text": "Financiamiento...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IMN_23",
                    "text": "¿Compartir recibo agua (si aplica)?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "IMN_24",
                    "text": "¿Cronograma/fases?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IMN_25",
                    "text": "¿Planes expansión/cierre mina?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "IMN_26",
                    "depends_on": {"id": "IMN_25", "value": "Sí"},
                    "text": "Detalles expansión/cierre...",
                    "type": "open",
                    "explanation": "...",
                },
            ],
            # --- Subsector: Petróleo y Gas (Oil & Gas) ---
            "Petróleo y Gas": [
                # Datos Clave
                {
                    "id": "IOG_1",
                    "text": "Ubicación (Campo, refinería, plataforma)...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IOG_2",
                    "text": "Costo agua (si no es agua producida)...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IOG_3",
                    "text": "Consumo agua externa...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IOG_4",
                    "text": "Generación AR (Agua producida, purgas, aguas de refinería)...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IOG_5",
                    "text": "Personas...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                # Calidad Agua (Específico O&G)
                {
                    "id": "IOG_6",
                    "text": "Volúmenes promedio y picos AR...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IOG_7",
                    "text": "¿Análisis de AR (agua producida, etc.)?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "IOG_8",
                    "depends_on": {"id": "IOG_7", "value_is_negative": True},
                    "text": "Estimación de parámetros clave en aguas residuales de Oil & Gas:",
                    "type": "multiple_open",
                    "sub_questions": [
                        {
                            "id": "IOG_8_TDS",
                            "label": "SDT (Sólidos Disueltos Totales) / Salinidad (mg/L o ppm):",
                        },  # MUY ALTOS en agua producida
                        {
                            "id": "IOG_8_HYDROCARBONS",
                            "label": "Hidrocarburos (TPH, Aceites y Grasas) en mg/L:",
                        },  # Contaminante principal
                        {
                            "id": "IOG_8_TSS",
                            "label": "SST (Sólidos Suspendidos Totales) en mg/L:",
                        },
                        {
                            "id": "IOG_8_METALS",
                            "label": "Metales (pesados y otros como Bario, Estroncio) (Sí/No, cuáles):",
                        },
                        {
                            "id": "IOG_8_H2S",
                            "label": "Sulfuro de Hidrógeno (H₂S) / Sulfuros (Sí/No):",
                        },  # Olor y toxicidad
                        {
                            "id": "IOG_8_COD",
                            "label": "DQO (Demanda Química de Oxígeno) en mg/L:",
                        },
                        {
                            "id": "IOG_8_RADIOACTIVITY",
                            "label": "Radioactividad (NORM/TENORM) (Sí/No):",
                        },  # Posible en agua producida
                    ],
                    "explanation": "En O&G, la alta Salinidad (SDT), Hidrocarburos, Sólidos, Metales y potencialmente H₂S o Radioactividad en el agua producida son los grandes desafíos.",
                },
                {
                    "id": "IOG_9",
                    "text": "¿Cuáles son los principales usos del agua en la operación?",
                    "type": "multiple_choice",
                    "options": [
                        "Recuperación mejorada de petróleo (EOR - inyección de agua/vapor)",
                        "Fluidos de perforación y fracturamiento hidráulico (Fracking)",
                        "Procesos de refinería (destilación, enfriamiento, etc.)",
                        "Generación de vapor",
                        "Pruebas hidrostáticas",
                        "Servicios generales / Uso sanitario",
                        "Otro (especificar)",
                    ],
                    "explanation": "La inyección para EOR y el fracking consumen grandes volúmenes. Tratar y reutilizar el agua producida es una prioridad económica y ambiental.",
                },
                {
                    "id": "IOG_10",
                    "text": "¿Fuente principal de agua (aparte de producida)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                # Agua Potable
                {
                    "id": "IOG_11",
                    "text": "¿Necesitas tratamiento agua potable?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "IOG_12",
                    "depends_on": {"id": "IOG_11", "value": "Sí"},
                    "text": "Agua potable: ¿Volumen y análisis?",
                    "type": "open",
                    "explanation": "...",
                },
                # Objetivos, Restricciones, Infraestructura, Cierre (Comunes)
                {
                    "id": "IOG_13",
                    "text": "Objetivo principal (Reúso EOR, cumplimiento descarga, reducción costos...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IOG_14",
                    "text": "Usos para agua tratada (Re-inyección, descarga, otros...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IOG_15",
                    "text": "Descarga actual AR (Re-inyección, evaporación, cuerpo receptor...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IOG_16",
                    "text": "Restricciones (Ubicación, manejo sales/NORM, H2S...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IOG_16_BUDGET",
                    "depends_on": {"id": "IOG_16", "value_contains": "Presupuesto"},
                    "text": "Rango presupuesto...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IOG_17",
                    "text": "¿Sistema existente (Separadores API, IGF, WEMCO...)?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "IOG_18",
                    "depends_on": {"id": "IOG_17", "value": "Sí"},
                    "text": "Descripción sistema...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IOG_19",
                    "depends_on": {"id": "IOG_17", "value": "Sí"},
                    "text": "¿Subir diagramas/fotos?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "IOG_20",
                    "text": "Presupuesto estimado...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IOG_21",
                    "text": "Plazo implementación...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IOG_22",
                    "text": "Financiamiento...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IOG_23",
                    "text": "¿Compartir recibo agua externa?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "IOG_24",
                    "text": "¿Cronograma/fases?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IOG_25",
                    "text": "¿Planes expansión/cierre campo?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "IOG_26",
                    "depends_on": {"id": "IOG_25", "value": "Sí"},
                    "text": "Detalles expansión/cierre...",
                    "type": "open",
                    "explanation": "...",
                },
            ],
            # --- Subsector: Metal/Automotriz ---
            "Metal/Automotriz": [
                # Datos Clave
                {
                    "id": "IMA_1",
                    "text": "Ubicación...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IMA_2",
                    "text": "Costo agua...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IMA_3",
                    "text": "Consumo agua...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IMA_4",
                    "text": "Generación AR...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IMA_5",
                    "text": "Personas...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                # Calidad Agua (Específico Metal/Auto)
                {
                    "id": "IMA_6",
                    "text": "Volúmenes promedio y picos AR...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IMA_7",
                    "text": "¿Análisis de AR?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "IMA_8",
                    "depends_on": {"id": "IMA_7", "value_is_negative": True},
                    "text": "Estimación de parámetros clave en aguas residuales Metal/Automotriz:",
                    "type": "multiple_open",
                    "sub_questions": [
                        {
                            "id": "IMA_8_METALS",
                            "label": "Metales Pesados (Cr, Ni, Zn, Cu, Pb, Cd) (Sí/No, cuáles y aprox mg/L):",
                        },  # Clave de galvanoplastia, pintura
                        {
                            "id": "IMA_8_FOG",
                            "label": "Aceites y Grasas (emulsionados?) (Altos/Medios/Bajos o mg/L):",
                        },  # De maquinado, lubricantes
                        {
                            "id": "IMA_8_TSS",
                            "label": "SST (Sólidos Suspendidos Totales) en mg/L:",
                        },
                        {
                            "id": "IMA_8_PH",
                            "label": "pH (rango típico, puede ser ácido o alcalino):",
                        },
                        {
                            "id": "IMA_8_COD",
                            "label": "DQO (Demanda Química de Oxígeno) en mg/L:",
                        },  # Por aceites, solventes
                        {
                            "id": "IMA_8_TDS",
                            "label": "SDT / Conductividad (µS/cm):",
                        },  # Por sales de procesos
                        {
                            "id": "IMA_8_CYANIDE",
                            "label": "Cianuro (en algunos procesos galvánicos) (Sí/No):",
                        },
                    ],
                    "explanation": "En metalmecánica/automotriz, los Metales Pesados, Aceites y Grasas, Sólidos y pH variable son los principales problemas. El tratamiento físico-químico suele ser necesario.",
                },
                {
                    "id": "IMA_9",
                    "text": "¿Cuáles son los principales usos del agua en la planta?",
                    "type": "multiple_choice",
                    "options": [
                        "Lavado de piezas / Desengrase",
                        "Acabado de metales (galvanoplastia, fosfatizado, pintura, anodizado)",
                        "Sistemas de enfriamiento (maquinaria, hornos)",
                        "Corte y maquinado (refrigerantes)",
                        "Pruebas de estanqueidad",
                        "Generación de vapor",
                        "Servicios generales / Uso sanitario",
                        "Otro (especificar)",
                    ],
                    "explanation": "Los procesos de acabado superficial (galvanoplastia, pintura) y el lavado/desengrase generan las aguas residuales más complejas y contaminadas con metales y aceites.",
                },
                {
                    "id": "IMA_10",
                    "text": "¿Fuente principal de agua?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                # Agua Potable
                {
                    "id": "IMA_11",
                    "text": "¿Necesitas tratamiento agua potable?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "IMA_12",
                    "depends_on": {"id": "IMA_11", "value": "Sí"},
                    "text": "Agua potable: ¿Volumen y análisis?",
                    "type": "open",
                    "explanation": "...",
                },
                # Objetivos, Restricciones, Infraestructura, Cierre (Comunes)
                {
                    "id": "IMA_13",
                    "text": "Objetivo principal...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IMA_14",
                    "text": "Usos para agua tratada...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IMA_15",
                    "text": "Descarga actual AR...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IMA_16",
                    "text": "Restricciones proyecto...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IMA_16_BUDGET",
                    "depends_on": {"id": "IMA_16", "value_contains": "Presupuesto"},
                    "text": "Rango presupuesto...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IMA_17",
                    "text": "¿Sistema existente?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "IMA_18",
                    "depends_on": {"id": "IMA_17", "value": "Sí"},
                    "text": "Descripción sistema...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IMA_19",
                    "depends_on": {"id": "IMA_17", "value": "Sí"},
                    "text": "¿Subir diagramas/fotos?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "IMA_20",
                    "text": "Presupuesto estimado...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IMA_21",
                    "text": "Plazo implementación...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IMA_22",
                    "text": "Financiamiento...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "IMA_23",
                    "text": "¿Compartir recibo agua?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "IMA_24",
                    "text": "¿Cronograma/fases?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "IMA_25",
                    "text": "¿Planes crecimiento?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "IMA_26",
                    "depends_on": {"id": "IMA_25", "value": "Sí"},
                    "text": "Detalles crecimiento...",
                    "type": "open",
                    "explanation": "...",
                },
            ],
            # --- Subsector: Cemento ---
            "Cemento": [
                # Datos Clave
                {
                    "id": "ICM_1",
                    "text": "Ubicación...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "ICM_2",
                    "text": "Costo agua...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "ICM_3",
                    "text": "Consumo agua...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "ICM_4",
                    "text": "Generación AR (Aguas de proceso, enfriamiento, escorrentía)...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "ICM_5",
                    "text": "Personas...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                # Calidad Agua (Específico Cemento)
                {
                    "id": "ICM_6",
                    "text": "Volúmenes promedio y picos AR...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "ICM_7",
                    "text": "¿Análisis de AR?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "ICM_8",
                    "depends_on": {"id": "ICM_7", "value_is_negative": True},
                    "text": "Estimación de parámetros clave en aguas residuales de Cemento:",
                    "type": "multiple_open",
                    "sub_questions": [
                        {
                            "id": "ICM_8_PH",
                            "label": "pH (rango típico, MUY ALCALINO > 11):",
                        },  # Clave del cemento
                        {
                            "id": "ICM_8_TSS",
                            "label": "SST (Sólidos Suspendidos Totales) en mg/L (MUY ALTOS):",
                        },  # Partículas finas
                        {
                            "id": "ICM_8_TDS",
                            "label": "SDT / Conductividad (µS/cm) / Dureza (mg/L CaCO₃):",
                        },  # Calcio, silicatos
                        {"id": "ICM_8_SULFATES", "label": "Sulfatos (SO₄²⁻) en mg/L:"},
                        {
                            "id": "ICM_8_METALS",
                            "label": "Metales (Cr(VI) - Cromo Hexavalente) (Sí/No o mg/L):",
                        },  # Contaminante preocupante
                        {
                            "id": "ICM_8_COD",
                            "label": "DQO (Demanda Química de Oxígeno) en mg/L (generalmente baja):",
                        },
                    ],
                    "explanation": "En cementeras, el pH extremadamente alto, los Sólidos Suspendidos muy elevados, la Dureza/SDT y la posible presencia de Cromo Hexavalente son los puntos críticos.",
                },
                {
                    "id": "ICM_9",
                    "text": "¿Cuáles son los principales usos del agua en la planta de cemento?",
                    "type": "multiple_choice",
                    "options": [
                        "Enfriamiento de equipos (hornos, molinos)",
                        "Supresión de polvo (muy importante)",
                        "Mezclado de concreto / Producción de mortero (si aplica)",
                        "Lavado de equipos y áreas",
                        "Generación de vapor",
                        "Servicios generales / Uso sanitario",
                        "Otro (especificar)",
                    ],
                    "explanation": "El enfriamiento y la supresión de polvo son grandes consumidores. Las aguas residuales suelen venir del contacto con el material (polvo, escorrentía) y purgas.",
                },
                {
                    "id": "ICM_10",
                    "text": "¿Fuente principal de agua?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                # Agua Potable
                {
                    "id": "ICM_11",
                    "text": "¿Necesitas tratamiento agua potable?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "ICM_12",
                    "depends_on": {"id": "ICM_11", "value": "Sí"},
                    "text": "Agua potable: ¿Volumen y análisis?",
                    "type": "open",
                    "explanation": "...",
                },
                # Objetivos, Restricciones, Infraestructura, Cierre (Comunes)
                {
                    "id": "ICM_13",
                    "text": "Objetivo principal...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "ICM_14",
                    "text": "Usos para agua tratada...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "ICM_15",
                    "text": "Descarga actual AR...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "ICM_16",
                    "text": "Restricciones proyecto...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "ICM_16_BUDGET",
                    "depends_on": {"id": "ICM_16", "value_contains": "Presupuesto"},
                    "text": "Rango presupuesto...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "ICM_17",
                    "text": "¿Sistema existente (Sedimentadores, balsas...)?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "ICM_18",
                    "depends_on": {"id": "ICM_17", "value": "Sí"},
                    "text": "Descripción sistema...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "ICM_19",
                    "depends_on": {"id": "ICM_17", "value": "Sí"},
                    "text": "¿Subir diagramas/fotos?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "ICM_20",
                    "text": "Presupuesto estimado...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "ICM_21",
                    "text": "Plazo implementación...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "ICM_22",
                    "text": "Financiamiento...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "ICM_23",
                    "text": "¿Compartir recibo agua?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "ICM_24",
                    "text": "¿Cronograma/fases?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "ICM_25",
                    "text": "¿Planes crecimiento?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "ICM_26",
                    "depends_on": {"id": "ICM_25", "value": "Sí"},
                    "text": "Detalles crecimiento...",
                    "type": "open",
                    "explanation": "...",
                },
            ],
            # --- Subsector: Otro Industrial ---
            "Otro": [
                # Usar un conjunto genérico de preguntas, similar a Alimentos y Bebidas
                # pero pidiendo más descripción en parámetros y usos.
                {
                    "id": "IOT_1",
                    "text": "Ubicación...",
                    "type": "open",
                    "explanation": "...",
                },
                # ... (copiar estructura de IAB, ajustando IDs a IOT_*) ...
                {
                    "id": "IOT_8",
                    "depends_on": {"id": "IOT_7", "value_is_negative": True},
                    "text": "Como tu sector es 'Otro', describe los parámetros clave que CREES relevantes en tus aguas residuales (ej. DQO, SST, pH, metales, aceites, color, etc.):",
                    "type": "open",  # Pregunta abierta más descriptiva
                    "explanation": "Al ser un sector no especificado, necesitamos que nos orientes sobre los principales contaminantes esperados.",
                },
                {
                    "id": "IOT_9",
                    "text": "Describe los principales usos del agua en tu proceso industrial específico:",
                    "type": "open",
                    "explanation": "Detallar los usos nos ayuda a entender la naturaleza de tu operación y las posibles fuentes de contaminación.",
                },
                # ... (Resto de preguntas comunes adaptadas con ID IOT_*) ...
                {
                    "id": "IOT_26",
                    "depends_on": {"id": "IOT_25", "value": "Sí"},
                    "text": "Detalles crecimiento...",
                    "type": "open",
                    "explanation": "...",
                },
            ],
        },
        # =========================
        # === SECTOR COMERCIAL ===
        # =========================
        "Comercial": {
            # --- Subsector: Hotel ---
            "Hotel": [
                # Datos Clave
                {
                    "id": "CHT_1",
                    "text": "Ubicación (Nombre Hotel, Dirección)...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CHT_2",
                    "text": "Costo agua...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CHT_3",
                    "text": "Consumo agua (m³/mes o m³/día)...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CHT_4",
                    "text": "Generación AR...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CHT_5",
                    "text": "¿Número promedio de huéspedes por día y número de empleados?",
                    "type": "multiple_open",
                    "sub_questions": [
                        {"id": "CHT_5_GUESTS", "label": "Huéspedes promedio/día:"},
                        {"id": "CHT_5_EMPLOYEES", "label": "Empleados:"},
                    ],
                    "explanation": "El número de ocupantes (huéspedes + empleados) es la base para estimar la carga hidráulica y orgánica en hoteles.",
                },
                # Calidad Agua (Específico Hotel - Agua de red y AR doméstica/lavandería)
                {
                    "id": "CHT_6",
                    "text": "Volúmenes promedio y picos AR (ej. picos mañana/noche, temporada alta)...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CHT_7",
                    "text": "¿Análisis de AR (mezcla de aguas grises y negras)?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "CHT_8",
                    "depends_on": {"id": "CHT_7", "value_is_negative": True},
                    "text": "Estimación de parámetros clave en aguas residuales de Hotel (tipo doméstico + lavandería):",
                    "type": "multiple_open",
                    "sub_questions": [
                        {"id": "CHT_8_BOD", "label": "DBO (mg/L, aprox 200-400):"},
                        {"id": "CHT_8_COD", "label": "DQO (mg/L, aprox 400-800):"},
                        {"id": "CHT_8_TSS", "label": "SST (mg/L, aprox 200-400):"},
                        {
                            "id": "CHT_8_FOG",
                            "label": "Grasas y Aceites (de cocina/restaurante?) (Altos/Medios/Bajos):",
                        },
                        {"id": "CHT_8_N", "label": "Nitrógeno Total (mg/L):"},
                        {
                            "id": "CHT_8_P",
                            "label": "Fósforo Total (mg/L):",
                        },  # Nutrientes
                    ],
                    "explanation": "Las aguas residuales de hotel son similares a las domésticas, pero pueden tener más carga de lavandería (detergentes) y cocina (grasas).",
                },
                {  # Calidad de agua de entrada (Potable)
                    "id": "CHT_9",
                    "text": "Para el agua de entrada (municipal o pozo): ¿Conoces su calidad? (ej. dureza, cloro, sales). ¿Tienes análisis?",
                    "type": "open",  # O document_upload
                    "explanation": "La calidad del agua de entrada es importante si se requiere tratamiento para calderas, piscinas, o mejorar la experiencia del huésped (agua suave).",
                },
                {
                    "id": "CHT_10",
                    "text": "¿Cuáles son los principales usos del agua en el hotel?",
                    "type": "multiple_choice",
                    "options": [
                        "Habitaciones (duchas, WC, lavabos)",
                        "Lavandería",
                        "Cocina / Restaurante",
                        "Piscina / Spa",
                        "Riego de jardines / áreas verdes",
                        "Sistemas de enfriamiento (HVAC)",
                        "Limpieza general",
                        "Otro (especificar)",
                    ],
                    "explanation": "Identificar los grandes consumidores (habitaciones, lavandería, piscina, riego) ayuda a priorizar el tratamiento y las oportunidades de reúso.",
                },
                {
                    "id": "CHT_11",
                    "text": "¿Fuente principal de agua?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                # Agua Potable (Generalmente ya es potable, pero puede requerir mejora)
                {
                    "id": "CHT_12",
                    "text": "¿Requieres algún tratamiento adicional para el agua potable suministrada (ej. suavización, filtración)?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "CHT_13",
                    "depends_on": {"id": "CHT_12", "value": "Sí"},
                    "text": "Si requieres mejora: ¿Qué buscas (quitar dureza, cloro, etc.) y para qué áreas?",
                    "type": "open",
                    "explanation": "...",
                },
                # Objetivos, Restricciones, Infraestructura, Cierre (Comunes)
                {
                    "id": "CHT_14",
                    "text": "Objetivo principal (Ahorro, imagen verde, cumplir norma...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CHT_15",
                    "text": "Usos para agua tratada (Riego, WC, torres...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CHT_16",
                    "text": "Descarga actual AR (Alcantarillado, infiltración...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CHT_17",
                    "text": "Restricciones (Espacio limitado, ruido, estética, presupuesto...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CHT_17_BUDGET",
                    "depends_on": {"id": "CHT_17", "value_contains": "Presupuesto"},
                    "text": "Rango presupuesto...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CHT_18",
                    "text": "¿Sistema existente (Fosa séptica, PTAR antigua...)?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "CHT_19",
                    "depends_on": {"id": "CHT_18", "value": "Sí"},
                    "text": "Descripción sistema...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CHT_20",
                    "depends_on": {"id": "CHT_18", "value": "Sí"},
                    "text": "¿Subir diagramas/fotos?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "CHT_21",
                    "text": "Presupuesto estimado...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CHT_22",
                    "text": "Plazo implementación...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CHT_23",
                    "text": "Financiamiento...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CHT_24",
                    "text": "¿Compartir recibo agua?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "CHT_25",
                    "text": "¿Cronograma/fases?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CHT_26",
                    "text": "¿Planes expansión hotel?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "CHT_27",
                    "depends_on": {"id": "CHT_26", "value": "Sí"},
                    "text": "Detalles expansión...",
                    "type": "open",
                    "explanation": "...",
                },
            ],
            # --- Subsector: Edificio de oficinas ---
            "Edificio de oficinas": [
                # Similar a Hotel, pero sin lavandería/piscina/cocina (generalmente)
                # Carga principal es sanitaria + HVAC
                {
                    "id": "CEO_1",
                    "text": "Ubicación (Nombre Edificio, Dirección)...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CEO_2",
                    "text": "Costo agua...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CEO_3",
                    "text": "Consumo agua (m³/mes)...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CEO_4",
                    "text": "Generación AR...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CEO_5",
                    "text": "¿Número aproximado de ocupantes diarios (empleados + visitantes)?",
                    "type": "open",  # O multiple choice como antes
                    "explanation": "La ocupación diaria determina la carga sanitaria, principal fuente de AR en oficinas.",
                },
                # Calidad Agua (AR Doméstica + Purgas HVAC)
                {
                    "id": "CEO_6",
                    "text": "Volúmenes promedio y picos AR (picos mediodía, días laborales)...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CEO_7",
                    "text": "¿Análisis de AR?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "CEO_8",
                    "depends_on": {"id": "CEO_7", "value_is_negative": True},
                    "text": "Estimación de parámetros clave en aguas residuales de Oficinas:",
                    "type": "multiple_open",
                    "sub_questions": [
                        {"id": "CEO_8_BOD", "label": "DBO (mg/L, similar doméstico):"},
                        {"id": "CEO_8_COD", "label": "DQO (mg/L, similar doméstico):"},
                        {"id": "CEO_8_TSS", "label": "SST (mg/L, similar doméstico):"},
                        {
                            "id": "CEO_8_TDS_HVAC",
                            "label": "SDT en purgas de HVAC (si aplica) (Alto/Medio/Bajo):",
                        },
                        {"id": "CEO_8_N", "label": "Nitrógeno Total (mg/L):"},
                        {"id": "CEO_8_P", "label": "Fósforo Total (mg/L):"},
                    ],
                    "explanation": "Principalmente aguas sanitarias, pero las purgas de torres de enfriamiento (HVAC) pueden añadir sales y químicos.",
                },
                {  # Calidad de agua de entrada
                    "id": "CEO_9",
                    "text": "Calidad del agua de entrada (dureza, cloro, sales). ¿Análisis?",
                    "type": "open",
                    "explanation": "Importante para proteger sistemas HVAC y tuberías, y para consumo humano.",
                },
                {
                    "id": "CEO_10",
                    "text": "¿Principales usos del agua en el edificio?",
                    "type": "multiple_choice",
                    "options": [
                        "Uso sanitario (WC, lavabos)",
                        "Sistemas de enfriamiento (HVAC / Torres de enfriamiento)",
                        "Limpieza general",
                        "Cafetería / Pequeña cocina",
                        "Riego de jardines (si aplica)",
                        "Otro (especificar)",
                    ],
                    "explanation": "El uso sanitario y el HVAC suelen ser los mayores consumidores en edificios de oficinas.",
                },
                {
                    "id": "CEO_11",
                    "text": "¿Fuente principal de agua?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                # Agua Potable (Generalmente ya es potable, pero puede requerir mejora en bebederos)
                {
                    "id": "CEO_12",
                    "text": "¿Requieres tratamiento adicional para agua potable (ej. filtros bebederos)?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "CEO_13",
                    "depends_on": {"id": "CEO_12", "value": "Sí"},
                    "text": "Si requieres mejora: ¿Qué buscas y dónde?",
                    "type": "open",
                    "explanation": "...",
                },
                # Objetivos, Restricciones, Infraestructura, Cierre (Comunes)
                {
                    "id": "CEO_14",
                    "text": "Objetivo principal (Ahorro, Certificación LEED/Verde...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CEO_15",
                    "text": "Usos para agua tratada (WC, riego, HVAC makeup...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CEO_16",
                    "text": "Descarga actual AR...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CEO_17",
                    "text": "Restricciones (Espacio sótano, ruido, presupuesto...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CEO_17_BUDGET",
                    "depends_on": {"id": "CEO_17", "value_contains": "Presupuesto"},
                    "text": "Rango presupuesto...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CEO_18",
                    "text": "¿Sistema existente?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "CEO_19",
                    "depends_on": {"id": "CEO_18", "value": "Sí"},
                    "text": "Descripción sistema...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CEO_20",
                    "depends_on": {"id": "CEO_18", "value": "Sí"},
                    "text": "¿Subir diagramas/fotos?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "CEO_21",
                    "text": "Presupuesto estimado...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CEO_22",
                    "text": "Plazo implementación...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CEO_23",
                    "text": "Financiamiento...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CEO_24",
                    "text": "¿Compartir recibo agua?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "CEO_25",
                    "text": "¿Cronograma/fases?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CEO_26",
                    "text": "¿Planes expansión edificio/ocupación?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "CEO_27",
                    "depends_on": {"id": "CEO_26", "value": "Sí"},
                    "text": "Detalles expansión...",
                    "type": "open",
                    "explanation": "...",
                },
            ],
            # --- Subsector: Centro comercial/Comercio minorista ---
            "Centro comercial/Comercio minorista": [
                # Similar a Edificio de Oficinas, pero puede incluir área de comida (Food Court)
                {
                    "id": "CCC_1",
                    "text": "Ubicación (Nombre CC, Dirección)...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CCC_2",
                    "text": "Costo agua...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CCC_3",
                    "text": "Consumo agua (m³/mes)...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CCC_4",
                    "text": "Generación AR...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CCC_5",
                    "text": "¿Número aproximado de visitantes diarios y empleados?",
                    "type": "open",
                    "explanation": "La afluencia de visitantes es clave para estimar la carga sanitaria y de posibles áreas de comida.",
                },
                # Calidad Agua (AR Doméstica + Food Court + HVAC)
                {
                    "id": "CCC_6",
                    "text": "Volúmenes promedio y picos AR (picos fines de semana, horarios comida)...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CCC_7",
                    "text": "¿Análisis de AR?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "CCC_8",
                    "depends_on": {"id": "CCC_7", "value_is_negative": True},
                    "text": "Estimación de parámetros clave en aguas residuales de Centro Comercial:",
                    "type": "multiple_open",
                    "sub_questions": [
                        {"id": "CCC_8_BOD", "label": "DBO (mg/L):"},
                        {"id": "CCC_8_COD", "label": "DQO (mg/L):"},
                        {"id": "CCC_8_TSS", "label": "SST (mg/L):"},
                        {
                            "id": "CCC_8_FOG",
                            "label": "Grasas y Aceites (si hay Food Court) (Altos/Medios/Bajos):",
                        },
                        {
                            "id": "CCC_8_TDS_HVAC",
                            "label": "SDT en purgas de HVAC (si aplica) (Alto/Medio/Bajo):",
                        },
                        {"id": "CCC_8_N", "label": "Nitrógeno Total (mg/L):"},
                        {"id": "CCC_8_P", "label": "Fósforo Total (mg/L):"},
                    ],
                    "explanation": "Similar a oficinas, pero con potencial alta carga de Grasas y Aceites si hay área de comida.",
                },
                {
                    "id": "CCC_9",
                    "text": "Calidad del agua de entrada. ¿Análisis?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CCC_10",
                    "text": "¿Principales usos del agua en el centro comercial?",
                    "type": "multiple_choice",
                    "options": [
                        "Uso sanitario (baños públicos y de personal)",
                        "Área de comida / Food Court (cocinas, lavado)",
                        "Sistemas de enfriamiento (HVAC)",
                        "Limpieza general",
                        "Fuentes decorativas",
                        "Riego de jardines / áreas comunes",
                        "Tiendas individuales (algunas pueden tener usos específicos)",
                        "Otro (especificar)",
                    ],
                    "explanation": "Los baños públicos, HVAC y el food court (si existe) son los puntos clave de consumo y generación de AR.",
                },
                {
                    "id": "CCC_11",
                    "text": "¿Fuente principal de agua?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                # Agua Potable
                {
                    "id": "CCC_12",
                    "text": "¿Requieres tratamiento adicional agua potable?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "CCC_13",
                    "depends_on": {"id": "CCC_12", "value": "Sí"},
                    "text": "Si requieres mejora: ¿Qué buscas y dónde?",
                    "type": "open",
                    "explanation": "...",
                },
                # Objetivos, Restricciones, Infraestructura, Cierre (Comunes)
                {
                    "id": "CCC_14",
                    "text": "Objetivo principal...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CCC_15",
                    "text": "Usos para agua tratada...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CCC_16",
                    "text": "Descarga actual AR...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CCC_17",
                    "text": "Restricciones...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CCC_17_BUDGET",
                    "depends_on": {"id": "CCC_17", "value_contains": "Presupuesto"},
                    "text": "Rango presupuesto...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CCC_18",
                    "text": "¿Sistema existente?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "CCC_19",
                    "depends_on": {"id": "CCC_18", "value": "Sí"},
                    "text": "Descripción sistema...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CCC_20",
                    "depends_on": {"id": "CCC_18", "value": "Sí"},
                    "text": "¿Subir diagramas/fotos?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "CCC_21",
                    "text": "Presupuesto estimado...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CCC_22",
                    "text": "Plazo implementación...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CCC_23",
                    "text": "Financiamiento...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CCC_24",
                    "text": "¿Compartir recibo agua?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "CCC_25",
                    "text": "¿Cronograma/fases?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CCC_26",
                    "text": "¿Planes expansión CC?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "CCC_27",
                    "depends_on": {"id": "CCC_26", "value": "Sí"},
                    "text": "Detalles expansión...",
                    "type": "open",
                    "explanation": "...",
                },
            ],
            # --- Subsector: Restaurante ---
            "Restaurante": [
                # Datos Clave
                {
                    "id": "CRS_1",
                    "text": "Ubicación (Nombre Restaurante, Dirección)...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CRS_2",
                    "text": "Costo agua...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CRS_3",
                    "text": "Consumo agua (m³/mes)...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CRS_4",
                    "text": "Generación AR...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CRS_5",
                    "text": "¿Número promedio de comensales por día y empleados?",
                    "type": "multiple_open",
                    "sub_questions": [
                        {"id": "CRS_5_GUESTS", "label": "Comensales promedio/día:"},
                        {"id": "CRS_5_EMPLOYEES", "label": "Empleados:"},
                    ],
                    "explanation": "El volumen de operación (comensales, empleados) se relaciona con la generación de AR, especialmente de cocina y baños.",
                },
                # Calidad Agua (AR Cocina + Sanitaria)
                {
                    "id": "CRS_6",
                    "text": "Volúmenes promedio y picos AR (picos horarios comida, fines de semana)...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CRS_7",
                    "text": "¿Análisis de AR?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "CRS_8",
                    "depends_on": {"id": "CRS_7", "value_is_negative": True},
                    "text": "Estimación de parámetros clave en aguas residuales de Restaurante:",
                    "type": "multiple_open",
                    "sub_questions": [
                        {
                            "id": "CRS_8_FOG",
                            "label": "Grasas y Aceites (GyA) (MUY ALTOS?) (mg/L):",
                        },  # Principal problema
                        {
                            "id": "CRS_8_BOD",
                            "label": "DBO (mg/L) (Alta por carga orgánica):",
                        },
                        {
                            "id": "CRS_8_COD",
                            "label": "DQO (mg/L) (Alta por carga orgánica y grasas):",
                        },
                        {
                            "id": "CRS_8_TSS",
                            "label": "SST (mg/L) (Por restos de comida):",
                        },
                        {"id": "CRS_8_PH", "label": "pH (rango típico):"},
                        {"id": "CRS_8_N", "label": "Nitrógeno Total (mg/L):"},
                        {"id": "CRS_8_P", "label": "Fósforo Total (mg/L):"},
                    ],
                    "explanation": "En restaurantes, la alta concentración de Grasas y Aceites (GyA), DBO/DQO y Sólidos provenientes de la cocina es el mayor desafío. Se requiere pretratamiento (trampa de grasa).",
                },
                {
                    "id": "CRS_9",
                    "text": "Calidad del agua de entrada. ¿Análisis?",
                    "type": "open",
                    "explanation": "Importante para máquinas de hielo, café, lavavajillas.",
                },
                {
                    "id": "CRS_10",
                    "text": "¿Principales usos del agua en el restaurante?",
                    "type": "multiple_choice",
                    "options": [
                        "Cocina (preparación, cocción, lavado de alimentos)",
                        "Lavado de vajilla / Lavavajillas",
                        "Máquinas de hielo / Bebidas",
                        "Uso sanitario (baños clientes y personal)",
                        "Limpieza general (pisos, equipos)",
                        "Riego (si aplica)",
                        "Otro (especificar)",
                    ],
                    "explanation": "La cocina y el lavado de vajilla son los mayores generadores de aguas residuales cargadas de grasa y materia orgánica.",
                },
                {
                    "id": "CRS_11",
                    "text": "¿Fuente principal de agua?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                # Agua Potable (Ya es potable, pero puede requerir filtración/suavización)
                {
                    "id": "CRS_12",
                    "text": "¿Requieres tratamiento adicional para agua de cocina/bebidas (ej. filtros, suavizador)?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "CRS_13",
                    "depends_on": {"id": "CRS_12", "value": "Sí"},
                    "text": "Si requieres mejora: ¿Qué buscas (sabor, dureza) y para qué equipos?",
                    "type": "open",
                    "explanation": "...",
                },
                # Objetivos, Restricciones, Infraestructura, Cierre (Comunes)
                {
                    "id": "CRS_14",
                    "text": "Objetivo principal (Cumplir norma descarga GyA, ahorro...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CRS_15",
                    "text": "Usos para agua tratada (Riego, WC...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CRS_16",
                    "text": "Descarga actual AR (Alcantarillado con/sin trampa grasa...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CRS_17",
                    "text": "Restricciones (Espacio MUY limitado, olores, presupuesto...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CRS_17_BUDGET",
                    "depends_on": {"id": "CRS_17", "value_contains": "Presupuesto"},
                    "text": "Rango presupuesto...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CRS_18",
                    "text": "¿Sistema existente (Trampa de grasa, PTAR pequeña...)?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "CRS_19",
                    "depends_on": {"id": "CRS_18", "value": "Sí"},
                    "text": "Descripción sistema...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CRS_20",
                    "depends_on": {"id": "CRS_18", "value": "Sí"},
                    "text": "¿Subir diagramas/fotos?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "CRS_21",
                    "text": "Presupuesto estimado...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CRS_22",
                    "text": "Plazo implementación...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CRS_23",
                    "text": "Financiamiento...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "CRS_24",
                    "text": "¿Compartir recibo agua?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "CRS_25",
                    "text": "¿Cronograma/fases?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "CRS_26",
                    "text": "¿Planes expansión restaurante?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "CRS_27",
                    "depends_on": {"id": "CRS_26", "value": "Sí"},
                    "text": "Detalles expansión...",
                    "type": "open",
                    "explanation": "...",
                },
            ],
            # --- Subsector: Otro Comercial ---
            "Otro": [
                # Conjunto genérico similar a "Otro Industrial"
                {
                    "id": "COT_1",
                    "text": "Ubicación...",
                    "type": "open",
                    "explanation": "...",
                },
                # ... (copiar estructura adaptando IDs a COT_*) ...
                {
                    "id": "COT_8",
                    "depends_on": {"id": "COT_7", "value_is_negative": True},
                    "text": "Describe los parámetros clave que CREES relevantes en tus aguas residuales comerciales:",
                    "type": "open",
                    "explanation": "Al ser un sector comercial no especificado, orientanos sobre los contaminantes principales.",
                },
                {
                    "id": "COT_10",  # Ajustar ID según secuencia
                    "text": "Describe los principales usos del agua en tu negocio comercial específico:",
                    "type": "open",
                    "explanation": "Detallar los usos nos ayuda a entender tu operación.",
                },
                # ... (Resto de preguntas comunes adaptadas con ID COT_*) ...
                {
                    "id": "COT_27",
                    "depends_on": {"id": "COT_26", "value": "Sí"},
                    "text": "Detalles expansión...",
                    "type": "open",
                    "explanation": "...",
                },
            ],
        },
        # =========================
        # === SECTOR MUNICIPAL ===
        # =========================
        "Municipal": {
            # --- Subsector: Gobierno de la ciudad (Planta Municipal) ---
            "Gobierno de la ciudad": [
                # Datos Clave PTAR Municipal
                {
                    "id": "MGC_1",
                    "text": "Ubicación de la Planta de Tratamiento (PTAR) o área a servir:",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MGC_2",
                    "text": "Costo de tratamiento actual (si existe) o tarifa de agua/drenaje:",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MGC_3",
                    "text": "Caudal de diseño de la PTAR (existente o requerida) (m³/día o L/s):",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MGC_4",
                    "text": "Caudal promedio actual que recibe la PTAR (m³/día o L/s):",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MGC_5",
                    "text": "¿Población actual servida por el sistema de alcantarillado/PTAR?",
                    "type": "open",  # Número
                    "explanation": "La población servida es clave para estimar la carga y verificar el diseño.",
                },
                # Calidad Agua (AR Municipal Mezclada)
                {
                    "id": "MGC_6",
                    "text": "Describe variaciones de caudal (diarias, estacionales, lluvias). ¿Hay infiltración significativa?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MGC_7",
                    "text": "¿Cuentan con análisis fisicoquímicos del agua residual cruda (influente)?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "MGC_8",
                    "depends_on": {"id": "MGC_7", "value_is_negative": True},
                    "text": "Estimación de parámetros típicos del agua residual municipal:",
                    "type": "multiple_open",
                    "sub_questions": [
                        {"id": "MGC_8_BOD", "label": "DBO₅ (mg/L, ej: 150-300):"},
                        {"id": "MGC_8_COD", "label": "DQO (mg/L, ej: 300-600):"},
                        {"id": "MGC_8_TSS", "label": "SST (mg/L, ej: 150-350):"},
                        {
                            "id": "MGC_8_N",
                            "label": "Nitrógeno Total (NTK o N-Total) (mg/L):",
                        },
                        {"id": "MGC_8_P", "label": "Fósforo Total (P-Total) (mg/L):"},
                        {"id": "MGC_8_FOG", "label": "Grasas y Aceites (GyA) (mg/L):"},
                        {
                            "id": "MGC_8_COLIFORMS",
                            "label": "Coliformes Fecales (NMP/100mL) (Muy altos):",
                        },
                    ],
                    "explanation": "Las aguas municipales tienen cargas orgánicas (DBO/DQO), sólidos (SST), nutrientes (N, P) y patógenos (coliformes) que deben tratarse según la norma de descarga.",
                },
                {  # Calidad agua tratada requerida
                    "id": "MGC_9",
                    "text": "¿Cuál es la normativa de descarga que debe cumplir el efluente tratado? (ej. NOM-001-SEMARNAT, NOM-003-SEMARNAT para reúso)",
                    "type": "open",
                    "explanation": "La norma aplicable define los límites máximos permitidos para cada contaminante en el agua tratada, dictando el nivel de tratamiento.",
                },
                {
                    "id": "MGC_10",
                    "text": "¿Hay industrias importantes conectadas al alcantarillado que aporten contaminantes específicos?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "Descargas industriales pueden introducir metales pesados, químicos tóxicos, etc., que complican el tratamiento municipal.",
                },
                {
                    "id": "MGC_10_DETAILS",
                    "depends_on": {"id": "MGC_10", "value": "Sí"},
                    "text": "Si hay industrias: ¿Qué tipo y qué contaminantes aportan?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MGC_11",
                    "text": "¿Fuente principal de agua potable para la ciudad?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                # Agua Potable (Generalmente es otra planta, pero preguntar si el proyecto incluye algo)
                {
                    "id": "MGC_12",
                    "text": "¿Este proyecto incluye también mejoras/construcción de planta de agua potable (ETAP)?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "MGC_13",
                    "depends_on": {"id": "MGC_12", "value": "Sí"},
                    "text": "Si incluye ETAP: ¿Capacidad requerida y análisis fuente?",
                    "type": "open",
                    "explanation": "...",
                },
                # Objetivos, Restricciones, Infraestructura, Cierre (Comunes)
                {
                    "id": "MGC_14",
                    "text": "Objetivo principal (Ampliar capacidad, mejorar calidad efluente, reúso...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "MGC_15",
                    "text": "Usos para agua tratada (Riego público, agricultura, industrial, recarga...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "MGC_16",
                    "text": "Descarga actual efluente (Río, mar, reúso...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "MGC_17",
                    "text": "Restricciones (Terreno disponible, presupuesto municipal, aceptación pública...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "MGC_17_BUDGET",
                    "depends_on": {"id": "MGC_17", "value_contains": "Presupuesto"},
                    "text": "Rango presupuesto...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MGC_18",
                    "text": "¿Sistema PTAR existente?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "MGC_19",
                    "depends_on": {"id": "MGC_18", "value": "Sí"},
                    "text": "Descripción PTAR existente (Tecnología, edad, estado)...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MGC_20",
                    "depends_on": {"id": "MGC_18", "value": "Sí"},
                    "text": "¿Subir diagramas/fotos?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "MGC_21",
                    "text": "Presupuesto estimado...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MGC_22",
                    "text": "Plazo implementación...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "MGC_23",
                    "text": "Financiamiento (Fondos federales/estatales, crédito, APP...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "MGC_24",
                    "text": "¿Compartir datos operativos PTAR (si existe)?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "MGC_25",
                    "text": "¿Cronograma/fases?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MGC_26",
                    "text": "¿Proyección crecimiento población/caudal?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "MGC_27",
                    "depends_on": {"id": "MGC_26", "value": "Sí"},
                    "text": "Detalles crecimiento proyectado...",
                    "type": "open",
                    "explanation": "...",
                },
            ],
            # --- Subsector: Pueblo/Aldea (Sistemas más pequeños) ---
            "Pueblo/Aldea": [
                # Similar a Gobierno Ciudad, pero escalas menores y tecnologías más simples
                {
                    "id": "MPA_1",
                    "text": "Ubicación del Pueblo/Aldea:",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MPA_2",
                    "text": "Tarifa de agua/drenaje actual (si existe):",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MPA_3",
                    "text": "Caudal de diseño requerido (m³/día):",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MPA_4",
                    "text": "Caudal promedio estimado a tratar (m³/día):",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MPA_5",
                    "text": "¿Población actual a servir?",
                    "type": "open",
                    "explanation": "...",
                },
                # Calidad Agua (Doméstica Rural)
                {
                    "id": "MPA_6",
                    "text": "Variaciones de caudal...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MPA_7",
                    "text": "¿Análisis de AR?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "MPA_8",
                    "depends_on": {"id": "MPA_7", "value_is_negative": True},
                    "text": "Estimación de parámetros típicos del agua residual doméstica rural:",
                    "type": "multiple_open",
                    "sub_questions": [  # Suelen ser cargas algo menores que urbanas
                        {"id": "MPA_8_BOD", "label": "DBO₅ (mg/L, ej: 100-250):"},
                        {"id": "MPA_8_COD", "label": "DQO (mg/L, ej: 250-500):"},
                        {"id": "MPA_8_TSS", "label": "SST (mg/L, ej: 100-300):"},
                        {"id": "MPA_8_N", "label": "Nitrógeno Total (mg/L):"},
                        {"id": "MPA_8_P", "label": "Fósforo Total (mg/L):"},
                        {
                            "id": "MPA_8_COLIFORMS",
                            "label": "Coliformes Fecales (NMP/100mL):",
                        },
                    ],
                    "explanation": "Agua residual principalmente doméstica, importante tratarla para proteger salud pública y cuerpos de agua locales.",
                },
                {
                    "id": "MPA_9",
                    "text": "¿Normativa de descarga aplicable (NOM-001, estatal...)?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MPA_10",
                    "text": "¿Hay alguna pequeña industria o agroindustria conectada?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "MPA_10_DETAILS",
                    "depends_on": {"id": "MPA_10", "value": "Sí"},
                    "text": "Si hay industria: ¿Tipo y contaminantes?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MPA_11",
                    "text": "¿Fuente principal de agua potable?",
                    "type": "multiple_choice",
                    "options": ["Pozo comunitario", "Red", "Río", ...],
                    "explanation": "...",
                },
                # Agua Potable
                {
                    "id": "MPA_12",
                    "text": "¿Proyecto incluye mejoras/construcción de sistema de agua potable?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "MPA_13",
                    "depends_on": {"id": "MPA_12", "value": "Sí"},
                    "text": "Si incluye potable: ¿Capacidad y análisis fuente?",
                    "type": "open",
                    "explanation": "...",
                },
                # Objetivos, Restricciones, Infraestructura, Cierre (Comunes)
                {
                    "id": "MPA_14",
                    "text": "Objetivo principal (Saneamiento básico, reúso riego...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "MPA_15",
                    "text": "Usos para agua tratada (Riego local, descarga segura...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "MPA_16",
                    "text": "Descarga actual AR (Letrinas, campo, arroyo...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "MPA_17",
                    "text": "Restricciones (Presupuesto limitado, terreno, falta personal capacitado, energía...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "MPA_17_BUDGET",
                    "depends_on": {"id": "MPA_17", "value_contains": "Presupuesto"},
                    "text": "Rango presupuesto...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MPA_18",
                    "text": "¿Sistema existente (Lagunas, fosa comunal...)?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "MPA_19",
                    "depends_on": {"id": "MPA_18", "value": "Sí"},
                    "text": "Descripción sistema...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MPA_20",
                    "depends_on": {"id": "MPA_18", "value": "Sí"},
                    "text": "¿Subir fotos?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "MPA_21",
                    "text": "Presupuesto estimado...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MPA_22",
                    "text": "Plazo implementación...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "MPA_23",
                    "text": "Financiamiento (Apoyos gobierno, comunidad...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "MPA_24",
                    "text": "¿Compartir datos (si hay)?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "MPA_25",
                    "text": "¿Cronograma/fases?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MPA_26",
                    "text": "¿Proyección crecimiento población?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "MPA_27",
                    "depends_on": {"id": "MPA_26", "value": "Sí"},
                    "text": "Detalles crecimiento...",
                    "type": "open",
                    "explanation": "...",
                },
            ],
            # --- Subsector: Autoridad de servicios de agua (Organismo Operador) ---
            "Autoridad de servicios de agua": [
                # Similar a Gobierno Ciudad, enfocado en la gestión del organismo
                {
                    "id": "MAS_1",
                    "text": "Nombre del Organismo Operador y Municipio(s) que atiende:",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MAS_2",
                    "text": "Tarifas actuales de agua potable y alcantarillado:",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MAS_3",
                    "text": "Capacidad instalada total de PTARs bajo su gestión (m³/día):",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MAS_4",
                    "text": "Caudal total tratado promedio actualmente (m³/día):",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MAS_5",
                    "text": "Población total cubierta por el servicio de alcantarillado:",
                    "type": "open",
                    "explanation": "...",
                },
                # Calidad Agua (Promedio o de una PTAR específica si el proyecto es puntual)
                {
                    "id": "MAS_6",
                    "text": "Variaciones de caudal / Infiltración...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MAS_7",
                    "text": "¿Análisis del influente promedio o de la PTAR objetivo?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "MAS_8",
                    "depends_on": {"id": "MAS_7", "value_is_negative": True},
                    "text": "Estimación de parámetros promedio del agua residual:",
                    "type": "multiple_open",
                    "sub_questions": [
                        {"id": "MAS_8_BOD", "label": "DBO₅ (mg/L):"},
                        {"id": "MAS_8_COD", "label": "DQO (mg/L):"},
                        {"id": "MAS_8_TSS", "label": "SST (mg/L):"},
                        {"id": "MAS_8_N", "label": "Nitrógeno Total (mg/L):"},
                        {"id": "MAS_8_P", "label": "Fósforo Total (mg/L):"},
                        {"id": "MAS_8_FOG", "label": "Grasas y Aceites (GyA) (mg/L):"},
                        {
                            "id": "MAS_8_COLIFORMS",
                            "label": "Coliformes Fecales (NMP/100mL):",
                        },
                    ],
                    "explanation": "Caracterizar el agua residual promedio del sistema.",
                },
                {
                    "id": "MAS_9",
                    "text": "¿Normativa de descarga que deben cumplir las PTARs?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MAS_10",
                    "text": "¿Programa de control de descargas industriales?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "MAS_10_DETAILS",
                    "depends_on": {"id": "MAS_10", "value": "Sí"},
                    "text": "Detalles del programa...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MAS_11",
                    "text": "¿Fuente(s) de agua potable?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                # Agua Potable
                {
                    "id": "MAS_12",
                    "text": "¿Proyecto incluye mejoras en sistema de agua potable?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "MAS_13",
                    "depends_on": {"id": "MAS_12", "value": "Sí"},
                    "text": "Si incluye potable: ¿Alcance y capacidad?",
                    "type": "open",
                    "explanation": "...",
                },
                # Objetivos, Restricciones, Infraestructura, Cierre (Enfocado a gestión del OO)
                {
                    "id": "MAS_14",
                    "text": "Objetivo principal (Eficiencia operativa, reducción costos, aumento cobertura, calidad agua...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "MAS_15",
                    "text": "Usos/Destino actual y potencial del agua tratada y lodos?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MAS_16",
                    "text": "Punto(s) de descarga actual?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MAS_17",
                    "text": "Restricciones (Financieras, técnicas, sociales, regulatorias...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "MAS_17_BUDGET",
                    "depends_on": {"id": "MAS_17", "value_contains": "Presupuesto"},
                    "text": "Rango presupuesto...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MAS_18",
                    "text": "Descripción general de la infraestructura de tratamiento existente:",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MAS_19",
                    "text": "¿Puedes compartir inventario de PTARs, diagnósticos o planes maestros?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "MAS_20",
                    "text": "¿Presupuesto asignado para este proyecto específico?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MAS_21",
                    "text": "Plazo implementación...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "MAS_22",
                    "text": "Fuente de financiamiento...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "MAS_23",
                    "text": "¿Compartir datos operativos/financieros relevantes?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "MAS_24",
                    "text": "¿Cronograma/fases?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "MAS_25",
                    "text": "¿Planes de desarrollo urbano/industrial que afecten caudales?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "MAS_26",
                    "depends_on": {"id": "MAS_25", "value": "Sí"},
                    "text": "Detalles de planes de desarrollo...",
                    "type": "open",
                    "explanation": "...",
                },
            ],
            # --- Subsector: Otro Municipal ---
            "Otro": [
                # Genérico Municipal
                {
                    "id": "MOT_1",
                    "text": "Ubicación y descripción del proyecto municipal:",
                    "type": "open",
                    "explanation": "...",
                },
                # ... (adaptar preguntas de Gobierno de la Ciudad con IDs MOT_*) ...
                {
                    "id": "MOT_27",
                    "depends_on": {"id": "MOT_26", "value": "Sí"},
                    "text": "Detalles crecimiento...",
                    "type": "open",
                    "explanation": "...",
                },
            ],
        },
        # ===========================
        # === SECTOR RESIDENCIAL ===
        # ===========================
        "Residencial": {
            # --- Subsector: Vivienda unifamiliar ---
            "Vivienda unifamiliar": [
                # Datos Clave Casa
                {
                    "id": "RVU_1",
                    "text": "Ubicación de la vivienda (Dirección):",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "RVU_2",
                    "text": "Costo actual del agua:",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "RVU_3",
                    "text": "Consumo promedio de agua (m³/mes):",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "RVU_4",
                    "text": "Generación estimada de AR (80-90% consumo):",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "RVU_5",
                    "text": "¿Cuántas personas habitan la vivienda regularmente?",
                    "type": "open",  # Número
                    "explanation": "Número de habitantes para estimar carga.",
                },
                # Calidad Agua (Doméstica Típica)
                {
                    "id": "RVU_6",
                    "text": "Picos de consumo/descarga (mañanas, noches, fines de semana)...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "RVU_7",
                    "text": "¿Análisis de AR (poco común, pero preguntar)?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "RVU_8",
                    "depends_on": {"id": "RVU_7", "value_is_negative": True},
                    "text": "Parámetros típicos de agua residual doméstica:",
                    "type": "confirmation",  # Solo informativo, no requiere input
                    "confirmation_text": "Generalmente contiene materia orgánica (DBO, DQO), sólidos, nutrientes y patógenos. El tratamiento se enfoca en remover esto.",
                    "explanation": "El agua residual de una casa es de tipo doméstico estándar.",
                },
                {  # Calidad agua de entrada
                    "id": "RVU_9",
                    "text": "Calidad del agua de entrada (dura, con cloro, etc.). ¿Tienes problemas con ella?",
                    "type": "open",
                    "explanation": "Importante para saber si necesitas suavizador, filtros, etc., además del tratamiento de AR.",
                },
                {
                    "id": "RVU_10",
                    "text": "¿Principales usos del agua en casa?",
                    "type": "multiple_choice",
                    "options": [
                        "Duchas / Baños",
                        "WC (Inodoros)",
                        "Lavadora de ropa",
                        "Lavavajillas / Lavado de trastes",
                        "Cocina (preparación alimentos)",
                        "Bebida",
                        "Riego de jardín / plantas",
                        "Limpieza",
                        "Piscina / Jacuzzi (si aplica)",
                        "Otro (especificar)",
                    ],
                    "explanation": "Identificar usos ayuda a pensar en separación de aguas grises/negras y potencial de reúso.",
                },
                {
                    "id": "RVU_11",
                    "text": "¿Fuente principal de agua (Red, pozo)?",
                    "type": "multiple_choice",
                    "options": ["Red municipal", "Pozo propio", "Pipa", "Otro"],
                    "explanation": "...",
                },
                # Agua Potable (Mejoras)
                {
                    "id": "RVU_12",
                    "text": "¿Buscas mejorar la calidad del agua potable (filtros, purificador, suavizador)?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "RVU_13",
                    "depends_on": {"id": "RVU_12", "value": "Sí"},
                    "text": "Si buscas mejora: ¿Qué problema quieres resolver (sarro, sabor, bacterias)?",
                    "type": "open",
                    "explanation": "...",
                },
                # Objetivos, Restricciones, Infraestructura, Cierre (Comunes)
                {
                    "id": "RVU_14",
                    "text": "Objetivo principal (Reúso riego/WC, cumplir norma local, no tener fosa séptica...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "RVU_15",
                    "text": "Usos para agua tratada (Riego, WC, lavado auto...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "RVU_16",
                    "text": "Descarga actual AR (Drenaje, fosa séptica, campo infiltración...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "RVU_17",
                    "text": "Restricciones (Espacio MUY limitado, presupuesto, estética, ruido, olores...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "RVU_17_BUDGET",
                    "depends_on": {"id": "RVU_17", "value_contains": "Presupuesto"},
                    "text": "Rango presupuesto...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "RVU_18",
                    "text": "¿Sistema existente (Fosa, biodigestor antiguo...)?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "RVU_19",
                    "depends_on": {"id": "RVU_18", "value": "Sí"},
                    "text": "Descripción sistema...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "RVU_20",
                    "depends_on": {"id": "RVU_18", "value": "Sí"},
                    "text": "¿Subir fotos?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "RVU_21",
                    "text": "Presupuesto estimado...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "RVU_22",
                    "text": "Plazo implementación...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "RVU_23",
                    "text": "Financiamiento...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "RVU_24",
                    "text": "¿Compartir recibo agua?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "RVU_25",
                    "text": "¿Cronograma/fases?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "RVU_26",
                    "text": "¿Planes remodelación/ampliación casa?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "RVU_27",
                    "depends_on": {"id": "RVU_26", "value": "Sí"},
                    "text": "Detalles remodelación...",
                    "type": "open",
                    "explanation": "...",
                },
            ],
            # --- Subsector: Edificio multifamiliar ---
            "Edificio multifamiliar": [
                # Similar a Vivienda Unifamiliar pero escalado y centralizado
                {
                    "id": "REM_1",
                    "text": "Ubicación del edificio (Dirección):",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "REM_2",
                    "text": "Costo actual del agua:",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "REM_3",
                    "text": "Consumo promedio de agua total del edificio (m³/mes):",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "REM_4",
                    "text": "Generación estimada de AR:",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "REM_5",
                    "text": "¿Número total de departamentos/unidades y habitantes estimados?",
                    "type": "multiple_open",
                    "sub_questions": [
                        {"id": "REM_5_UNITS", "label": "Número de Deptos/Unidades:"},
                        {
                            "id": "REM_5_PEOPLE",
                            "label": "Habitantes totales estimados:",
                        },
                    ],
                    "explanation": "Número de unidades y habitantes para dimensionar sistema centralizado.",
                },
                # Calidad Agua (Doméstica Concentrada)
                {
                    "id": "REM_6",
                    "text": "Picos de consumo/descarga...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "REM_7",
                    "text": "¿Análisis de AR?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "REM_8",
                    "depends_on": {"id": "REM_7", "value_is_negative": True},
                    "text": "Parámetros típicos de agua residual doméstica:",
                    "type": "confirmation",
                    "confirmation_text": "Agua residual doméstica estándar, similar a la municipal pero más concentrada.",
                    "explanation": "Agua residual doméstica.",
                },
                {
                    "id": "REM_9",
                    "text": "Calidad del agua de entrada. ¿Problemas?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "REM_10",
                    "text": "¿Principales usos del agua en el edificio?",
                    "type": "multiple_choice",
                    "options": [
                        "Uso en departamentos (duchas, WC, cocina, lavado)",
                        "Áreas comunes (limpieza, riego jardines)",
                        "Piscina / Gimnasio / Amenidades (si aplica)",
                        "Sistema contra incendios",
                        "Otro (especificar)",
                    ],
                    "explanation": "Similar a casa, pero concentrado. Identificar si hay grandes consumidores comunes (piscina, riego).",
                },
                {
                    "id": "REM_11",
                    "text": "¿Fuente principal de agua?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                # Agua Potable (Mejoras centralizadas)
                {
                    "id": "REM_12",
                    "text": "¿Buscan mejorar la calidad del agua potable para todo el edificio?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "REM_13",
                    "depends_on": {"id": "REM_12", "value": "Sí"},
                    "text": "Si buscan mejora: ¿Qué problema (sarro, sabor)?",
                    "type": "open",
                    "explanation": "...",
                },
                # Objetivos, Restricciones, Infraestructura, Cierre (Comunes)
                {
                    "id": "REM_14",
                    "text": "Objetivo principal (Reúso áreas comunes, cumplir norma, reducir cuotas...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "REM_15",
                    "text": "Usos para agua tratada (Riego, WC comunes...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "REM_16",
                    "text": "Descarga actual AR (Drenaje, fosa común...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "REM_17",
                    "text": "Restricciones (Espacio azotea/sótano, presupuesto condominio, ruido...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "REM_17_BUDGET",
                    "depends_on": {"id": "REM_17", "value_contains": "Presupuesto"},
                    "text": "Rango presupuesto...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "REM_18",
                    "text": "¿Sistema existente?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "REM_19",
                    "depends_on": {"id": "REM_18", "value": "Sí"},
                    "text": "Descripción sistema...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "REM_20",
                    "depends_on": {"id": "REM_18", "value": "Sí"},
                    "text": "¿Subir fotos/planos?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "REM_21",
                    "text": "Presupuesto estimado...",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "REM_22",
                    "text": "Plazo implementación...",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "REM_23",
                    "text": "Financiamiento (Cuotas condominos, crédito...)?",
                    "type": "multiple_choice",
                    "options": [...],
                    "explanation": "...",
                },
                {
                    "id": "REM_24",
                    "text": "¿Compartir recibo agua Gral?",
                    "type": "document_upload",
                    "explanation": "...",
                },
                {
                    "id": "REM_25",
                    "text": "¿Cronograma/fases?",
                    "type": "open",
                    "explanation": "...",
                },
                {
                    "id": "REM_26",
                    "text": "¿Planes expansión edificio?",
                    "type": "yes_no",
                    "options": ["Sí", "No"],
                    "explanation": "...",
                },
                {
                    "id": "REM_27",
                    "depends_on": {"id": "REM_26", "value": "Sí"},
                    "text": "Detalles expansión...",
                    "type": "open",
                    "explanation": "...",
                },
            ],
            # --- Subsector: Otro Residencial ---
            "Otro": [
                # Genérico Residencial
                {
                    "id": "ROT_1",
                    "text": "Ubicación y descripción del proyecto residencial:",
                    "type": "open",
                    "explanation": "...",
                },
                # ... (adaptar preguntas de Vivienda Unifamiliar con IDs ROT_*) ...
                {
                    "id": "ROT_27",
                    "depends_on": {"id": "ROT_26", "value": "Sí"},
                    "text": "Detalles crecimiento...",
                    "type": "open",
                    "explanation": "...",
                },
            ],
        },
    },
}

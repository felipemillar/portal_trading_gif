# **Especificación Técnica de Arquitectura: Agente Autónomo de Extracción de Datos (BCCh BDE) en Google Antigravity**

El presente documento constituye una especificación técnica de nivel arquitectónico, diseñada exhaustivamente para guiar la construcción, el despliegue y la operación de un agente de inteligencia artificial enteramente autónomo. Este sistema operará sobre la plataforma de infraestructura Google Antigravity, asumiendo la responsabilidad crítica de la ingesta, el procesamiento asíncrono y la gestión de resiliencia de los datos macroeconómicos provenientes de la Base de Datos Estadísticos (BDE) del Banco Central de Chile (BCCh). La convergencia de interfaces de programación de aplicaciones (APIs) de diseño heredado con entornos de orquestación de agentes paralelos de última generación requiere un análisis minucioso de las topologías de red, los vectores de seguridad, las asimetrías en las estructuras de datos y las estrategias de mitigación de fallos en cascada.  
A través del análisis profundo de los servicios web provistos por el Banco Central de Chile y las capacidades declarativas del SDK de Antigravity, este informe detalla los mecanismos precisos de autenticación, el mapeo exacto de los endpoints de datos, las estrategias matemáticas de mitigación de límites de tasa y la implementación algorítmica requerida para un entorno de producción de misión crítica, asegurando que el agente opere sin requerir intervención o supervisión humana continua.

## **1. Análisis del Modelo de Autenticación y Seguridad Autónoma**

El diseño de un agente de software autónomo impone que la gestión de identidades, la inyección de secretos y el control de accesos operen de forma imperceptible y automatizada. La infraestructura de la API de la Base de Datos Estadísticos del Banco Central de Chile presenta un modelo de autenticación de tipo legado (legacy) que introduce desafíos arquitectónicos significativos cuando se expone a un entorno de agentes impulsados por Modelos de Lenguaje Grande (LLMs).

### **1.1 Flujo Exacto de Autenticación y Vulnerabilidades Inherentes**

A diferencia de los estándares modernos de la industria informática, tales como OAuth 2.0, los tokens web JSON (JWT) o la transmisión de credenciales mediante cabeceras HTTP cifradas (por ejemplo, Authorization: Bearer), la API de la BDE del BCCh fundamenta su esquema de validación de identidad en el uso de parámetros de consulta (Query Parameters). Este flujo exige la inyección de los argumentos user y pass directamente en la cadena de la URL para las peticiones HTTP GET y POST1. La dirección base principal para el consumo de este servicio de tipo REST es https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx1.  
El ciclo de vida de la identidad comienza con un proceso manual: un operador humano debe registrarse inicialmente en el portal del Banco Central (si3.bcentral.cl), un procedimiento de única vez donde se aceptan los términos de uso oficiales2. Una vez completado, este proceso otorga acceso gratuito e indefinido al servicio, convirtiendo el correo electrónico y la contraseña seleccionados en los tokens persistentes para todas las peticiones subsecuentes a la API3.  
La transmisión de credenciales directamente en la URL expone al sistema a múltiples vectores de ataque pasivos y activos. En arquitecturas empresariales, las URLs completas (incluyendo sus parámetros de consulta) suelen ser registradas en texto plano por servidores proxy inversos, firewalls de aplicaciones web (WAFs), historiales de enrutamiento y herramientas de telemetría de red. En el contexto de un agente de inteligencia artificial alojado en Antigravity, existe un riesgo emergente conocido como Inyección Indirecta de Prompts (Indirect Prompt Injection)4. Si un atacante logra manipular un archivo del espacio de trabajo que el agente lee rutinariamente, podría instruir al LLM para que filtre estas credenciales a un servidor externo. Por lo tanto, para mitigar este vector de ataque en un entorno autónomo, la arquitectura debe garantizar que las peticiones se realicen exclusivamente a través de canales cifrados mediante Transport Layer Security (TLS 1.2 o superior) y que el cliente HTTP implementado en el agente suprima explícitamente el registro (logging) de las URLs completas, enmascarando los parámetros sensibles antes de cualquier salida estándar o volcado de memoria.

### **1.2 Ciclo de Vida de Credenciales y Mecanismos de Renovación**

Las investigaciones exhaustivas sobre la plataforma tecnológica de la BDE indican que el registro genera credenciales que no poseen un tiempo de expiración inherente (Time-To-Live o TTL). Actúan como tokens de larga duración y, por lo tanto, no expiran bajo condiciones normales de operación3.  
Al carecer de un mecanismo de expiración basado en tiempo, similar al parámetro expires_in de los flujos de concesión de OAuth 2.0, la arquitectura del agente se exime de la necesidad de implementar un flujo algorítmico de rotación de tokens (Refresh Token Flow). Sin embargo, el diseño del agente no debe asumir una disponibilidad perpetua de la identidad. El sistema debe estar preparado algorítmicamente para un escenario de revocación forzada de credenciales, lo cual podría ocurrir si los sistemas de seguridad del Banco Central detectan anomalías, violaciones a la política de uso razonable, o intentos de fuerza bruta desde la dirección IP del agente.  
En la eventualidad de una revocación o suspensión de la cuenta, la API del BCCh responderá alterando la propiedad de estado interno de la respuesta (generalmente un código interno distinto de cero en el JSON de respuesta o un código HTTP 401/403 a nivel de transporte)5. La lógica de recuperación autónoma del agente debe clasificar este evento como un error permanente (Permanent Failure). La respuesta del sistema no debe consistir en la ejecución de reintentos infinitos, lo cual agravaría el bloqueo, sino en la interrupción controlada del bucle de ejecución (Agentic Loop), seguida de la emisión de una alerta de alta prioridad a través de un canal de operaciones (por ejemplo, un Webhook hacia una plataforma de gestión de incidentes), indicando que se requiere intervención humana para restablecer o rotar las credenciales en el portal del banco.

### **1.3 Inyección Segura de Secretos en el Entorno Antigravity**

Google Antigravity opera como un entorno de orquestación masivamente paralelo diseñado para flujos de trabajo autónomos. A medida que delegamos la autonomía a estos agentes, permitiéndoles leer código, ejecutar comandos de terminal y razonar sobre arquitecturas, la superficie de exposición de secretos se amplifica drásticamente4. Codificar (hardcodear) el usuario y la contraseña del Banco Central en el código fuente de las herramientas del agente, o peor aún, inyectarlos directamente en el bloque de instrucciones del sistema (System Prompt), representa un fallo arquitectónico crítico que viola los principios fundamentales de confianza cero (Zero Trust).  
Las mejores prácticas sugeridas para la plataforma Antigravity establecen la separación estricta entre la lógica de ejecución del agente y la configuración del entorno. Esto se logra mediante el uso de variables de entorno inyectadas externamente, o idealmente, integrando un gestor de secretos robusto (como Google Cloud Secret Manager) accesible a través de las Credenciales Predeterminadas de la Aplicación (Application Default Credentials - ADC)6. El objeto de configuración LocalAgentConfig, provisto por el SDK de Antigravity para Python, facilita la instanciación de agentes sin exponer el estado de los secretos en los archivos físicos del proyecto6.  
La inyección segura requiere que las credenciales residan exclusivamente en la memoria del entorno de ejecución aislado del contenedor, siendo recuperadas únicamente en el milisegundo exacto en que la herramienta asíncrona de Python ensambla la petición HTTP, asegurando que el LLM subyacente nunca tenga acceso al texto plano de la contraseña. La configuración del agente debe regirse por un principio de mínimo privilegio ("deny by default"), implementando políticas declarativas que permitan únicamente las acciones explícitamente autorizadas y bloqueando la impresión de variables de entorno en la salida estándar de la interfaz de chat6.

## **2. Catálogo Completo de Endpoints, Parámetros y Estructuras de Datos**

La API del Banco Central proporciona dos métodos primarios para el consumo programático de su Base de Datos Estadísticos: GetSeries y SearchSeries. La tecnología subyacente que soporta este servicio está cimentada en el ecosistema Microsoft ASP.NET, exponiendo puntos finales tanto para arquitecturas orientadas a servicios clásicas (SOAP mediante archivos .asmx) como para manejadores web más ligeros orientados a transferencias de estado representacional (REST-like mediante archivos .ashx)1. Para la integración con un agente basado en LLM, donde la densidad de información y la eficiencia del análisis (parsing) son críticas, la interfaz .ashx que retorna objetos JSON es la arquitectura objetivo.

### **2.1 Análisis Exhaustivo del Endpoint SearchSeries**

El método SearchSeries funciona como un catálogo de descubrimiento dinámico y metadatos. En un sistema autónomo, este endpoint es fundamental para dotar al agente de autoconocimiento sobre el universo de datos disponibles, permitiéndole mapear qué series temporales existen y cómo están categorizadas según su frecuencia de actualización sin depender de un catálogo estático preprogramado1.

| Parámetro | Naturaleza | Tipo de Dato | Descripción Funcional y Restricciones |
| :---- | :---- | :---- | :---- |
| user | Obligatorio | Cadena (String) | El correo electrónico registrado y validado en la plataforma de la BDE. |
| pass | Obligatorio | Cadena (String) | La contraseña asociada a la identidad del usuario. |
| frequency | Obligatorio | Cadena (String) | Define el intervalo temporal de agregación de la serie. Los únicos valores escalares permitidos por el contrato de la API son: DAILY (Diaria), MONTHLY (Mensual), QUARTERLY (Trimestral) o ANNUAL (Anual)1. |
| function | Obligatorio | Cadena (String) | Actúa como un enrutador interno para el manejador HTTP. Debe completarse estrictamente con el valor exacto SearchSeries1. |

La respuesta estructurada de este endpoint devuelve un documento JSON que encapsula el estado de la transacción en la raíz del objeto. El atributo base "Codigo" retorna 0 en caso de éxito, acompañado del atributo "Descripcion" con el valor "Success"1. El valor analítico real reside en un arreglo de objetos denominado "SeriesInfos". Este arreglo anidado proporciona la metadata fundacional que el agente debe almacenar en su memoria a largo plazo o base de datos vectorial para consultas futuras. La estructura interna de cada objeto dentro de "SeriesInfos" contiene el "seriesId" (el identificador único indispensable para el endpoint de extracción), descripciones bilingües ("spanishTitle", "englishTitle"), y los límites temporales de disponibilidad del dato ("firstObservation", "lastObservation")1.  
El diseño del agente autónomo debe contemplar una tarea programada en segundo plano (background worker) que consuma este endpoint con una periodicidad prudente (por ejemplo, semanalmente). Este proceso de reconciliación permite al agente descubrir nuevas series macroeconómicas agregadas por el Banco Central, actualizando su índice interno de forma completamente autónoma, expandiendo así sus capacidades analíticas sin necesidad de despliegues adicionales de código.

### **2.2 Análisis Exhaustivo del Endpoint GetSeries**

El método GetSeries constituye el motor transaccional de extracción de datos. Su función es retornar las observaciones numéricas históricas o la última medición actual para una serie de tiempo específica y singularizada1.

| Parámetro | Naturaleza | Tipo de Dato | Descripción Funcional y Restricciones |
| :---- | :---- | :---- | :---- |
| user | Obligatorio | Cadena (String) | Correo electrónico registrado en la BDE. |
| pass | Obligatorio | Cadena (String) | Contraseña de la cuenta BDE. |
| timeseries | Obligatorio | Cadena (String) | Código alfanumérico único de la serie a consultar. Este código sigue una nomenclatura taxonómica estricta (ej. F022.TPM.TIN.D001.NO.Z.D para la Tasa de Política Monetaria)1. |
| firstdate | Opcional | Cadena (String) | Límite temporal inferior de la consulta. Requiere un formato ISO 8601 estricto: YYYY-MM-DD. Si el agente omite este parámetro, la API recogerá por defecto desde el primer dato histórico disponible en la base de datos1. |
| lastdate | Opcional | Cadena (String) | Límite temporal superior de la consulta. Requiere formato YYYY-MM-DD. Si se omite, retorna hasta la última observación oficial publicada1. |
| function | Opcional | Cadena (String) | Enrutador del manejador. De no completarse, el sistema asume el valor GetSeries por defecto, aunque se recomienda su inclusión explícita para evitar ambigüedades en el enrutamiento1. |

Un análisis de tercer orden sobre la topología de la respuesta JSON revela un desafío arquitectónico crítico de normalización de datos que el agente autónomo debe solventar ineludiblemente: las asimetrías severas en los formatos de serialización y tipado.  
La respuesta exitosa enruta los datos a un objeto anidado "Series", el cual contiene un sub-arreglo denominado "Obs" (Observaciones)1. Cada observación dentro del arreglo presenta la fecha en el campo "indexDateString", el valor numérico en el campo "value", y un indicador de estado en "statusCode". La discrepancia principal radica en que, mientras los parámetros de entrada (firstdate y lastdate) exigen inexcusablemente el estándar ISO 8601 (YYYY-MM-DD)1, el cuerpo de la respuesta devuelve el campo "indexDateString" formateado según convenciones locales latinas (DD-MM-YYYY)1. Un algoritmo de extracción ingenuo que intente inyectar estos datos en un almacén de series de tiempo (como InfluxDB o TimescaleDB) o en el contexto de un LLM fallará estrepitosamente al ordenar cronológicamente los datos si no ejecuta una conversión explícita de formato en la capa del cliente.  
Además de la inversión en el formato de fecha, el campo de magnitud "value" se serializa sistemáticamente como una cadena de texto (String, ej. "1.5"), en contraposición al estándar JSON de proveer magnitudes en formato de punto flotante nativo (Float). El propio Banco Central emite una salvedad arquitectónica: pueden observarse diferencias tenues a partir del decimoquinto dígito significativo al comparar las respuestas de la API con los archivos Excel descargables de la BDE1. Esto es un artefacto de la representación computacional de coma flotante de doble precisión (IEEE 754) en el proceso de serialización, y no constituye un error estadístico. El agente de Antigravity debe implementar una fase de coerción de tipos (Type Coercion) para transformar estos Strings en variables numéricas nativas de Python antes de ejecutar cálculos de variaciones porcentuales o inyectar los datos en modelos matemáticos. Finalmente, para las consultas de series con frecuencia diaria, es imperativo gestionar los intervalos sin datos correspondientes a días no hábiles (fines de semana y feriados legales); el agente debe estar dotado de lógica de normalización, como el transporte analítico del último valor válido (Forward-Fill), para garantizar la continuidad de la matriz de datos requerida por las inferencias estadísticas2.

### **2.3 Endpoints Ocultos, Protocolos Alternativos y Limitaciones de Eventos**

La investigación exhaustiva de la superficie de ataque y los protocolos públicos del Banco Central de Chile concluye de manera determinante que no existen interfaces nativas operativas para arquitecturas basadas en grafos de consulta, tales como GraphQL, ni se provee soporte nativo para el envío de eventos asíncronos mediante Webhooks desde los servidores de la BDE hacia aplicaciones de terceros. La infraestructura fundacional descansa en el paradigma de solicitud-respuesta (Request-Response) anclado en componentes clásicos de Microsoft IIS1.  
Se ha identificado la presencia paralela de un endpoint basado en el Protocolo Simple de Acceso a Objetos (SOAP), accesible a través del archivo sietews.asmx, el cual brinda soporte completo para las especificaciones SOAP 1.1 y SOAP 1.29. Si bien el uso de SOAP respaldado por un documento WSDL (Web Services Description Language) ofrece la ventaja de un contrato de tipos estático y estricto, el procesamiento y análisis sintáctico de árboles XML introduce una sobrecarga computacional prohibitiva e innecesaria. Para un agente autónomo de inteligencia artificial que consume ancho de banda de contexto, el uso exclusivo del endpoint REST/JSON (SieteRestWS.ashx) es categóricamente superior. JSON reduce sustancialmente el tamaño de los paquetes de red (payload size), minimiza el consumo de tokens cuando el modelo de lenguaje necesita inspeccionar el texto crudo para depuración, y provee una abstracción mucho más limpia para la manipulación en diccionarios de Python.  
La ausencia de un sistema de Webhooks implica que el agente no puede suscribirse de forma pasiva a notificaciones de eventos (por ejemplo, recibir un push instantáneo cuando el BCCh publica el nuevo Índice de Precios al Consumidor). Por consiguiente, la arquitectura del agente autónomo debe contemplar el diseño de un planificador (Scheduler) interno o un sistema de Long Polling atenuado. Este mecanismo debe programarse para alinearse de forma inteligente con el calendario oficial de publicaciones del Banco Central, minimizando así las peticiones redundantes e infructuosas que agotarían las cuotas de red.

## **3. Resiliencia, Límites y Manejo de Errores Computacionales (Edge Cases)**

En la era del cómputo en la nube, los entornos de agentes impulsados por modelos paralelos poseen la capacidad inherente de generar cientos de hilos de ejecución asíncronos y emitir ráfagas masivas de peticiones de red en fracciones de milisegundo4. Sin la implementación de salvaguardas explícitas y cuellos de botella controlados, el agente alojado en Antigravity sometería a la infraestructura del BCCh a un ataque involuntario de denegación de servicio (DDoS), lo que precipitaría un bloqueo severo y permanente a nivel de capa de red (IP Ban). La ingeniería de resiliencia no es una optimización post-despliegue; es un pilar crítico de la viabilidad del sistema.

### **3.1 Limitaciones de Tasa (Rate Limits) y Control de Concurrencia**

Las políticas oficiales de términos de servicio del Banco Central imponen una restricción perimetral inflexible para salvaguardar la estabilidad de su base de datos: el servicio autoriza un máximo absoluto de 5 peticiones simultáneas por segundo, por cuenta registrada2. Es imperativo destacar que la API no cuenta con mecanismos de descarga en bloque (bulk fetching), paginación eficiente para agrupaciones de indicadores, ni permite consultas en paralelo para múltiples series dentro del cuerpo de una única petición HTTP2. Cada serie temporal requiere una conexión HTTP individual.  
Para satisfacer esta restricción volumétrica dentro de un entorno de agentes donde se pueden desencadenar razonamientos de múltiples pasos (por ejemplo, un agente encargado de redactar un informe que requiere el análisis concurrente de 50 indicadores sectoriales distintos), la arquitectura debe forzar un control de concurrencia a nivel de la capa de transporte del cliente. En el ecosistema de Python, este patrón se cristaliza mediante el uso de semáforos asíncronos (asyncio.Semaphore(5)) y la implementación de algoritmos de conformado de tráfico (Traffic Shaping), tales como el modelo *Token Bucket*, que restringen matemáticamente el caudal de peticiones en vuelo (in-flight requests) hacia el host de destino si3.bcentral.cl.

### **3.2 Topología Estructural de Códigos de Error**

El diseño del web service del Banco Central emplea un patrón arquitectónico común en sistemas de la década anterior, donde los errores de lógica de negocio (Application-Level Errors) se encapsulan engañosamente dentro de respuestas HTTP que retornan un código de estado de éxito (HTTP 200 OK). Por tanto, la confiabilidad de la transacción debe evaluarse inspeccionando el cuerpo del JSON, donde la propiedad "Codigo" actúa como la verdadera fuente de la verdad:

| Condición de Estado | Evaluador Interno | Comportamiento del Sistema y Significado |
| :---- | :---- | :---- |
| **Éxito Total** | "Codigo": 0 | La extracción de datos finalizó correctamente. La propiedad "Descripcion" retornará una cadena vacía o el texto "Success"5. |
| **Error de Negocio** | "Codigo": != 0 | Representa fallos permanentes imputables al cliente. Ejemplos incluyen: credenciales invalidadas, sintaxis de fecha incompatible, o la solicitud de un código de serie inexistente. El atributo "Descripcion" alojará el mensaje de error textual. El agente no debe reintentar estas peticiones. |
| **Límite de Tasa** | HTTP 429 | El agente ha violado el umbral de 5 peticiones simultáneas11. Requiere la activación inmediata del algoritmo de retroceso exponencial (Backoff). |
| **Fallo de Infraestructura** | HTTP 500, 502, 503, 504 | La pasarela de aplicaciones del BCCh o los servidores de base de datos se encuentran inalcanzables debido a mantenimiento programado, particiones de red o sobrecarga temporal12. Clasificados como errores transitorios. |

A nivel del protocolo de control de transmisión (TCP), el cliente también experimentará excepciones intrínsecas de transporte (Transport Errors), tales como TimeoutError, ConnectError o ConnectionResetError. Estos errores ocurren típicamente debido a la volatilidad de la latencia en el enrutamiento internacional hacia los servidores localizados en Chile y demandan un mecanismo de gestión de reintentos robusto.

### **3.3 Diseño Matemático de la Estrategia de Reintentos (Exponential Backoff y Jitter)**

El manejo algorítmico de los errores transitorios determina la madurez de un sistema autónomo. Un antipatrón recurrente en implementaciones ingenuas consiste en la ejecución de reintentos inmediatos, repetitivos e inflexibles tras presenciar un fallo de red. Cuando un clúster de agentes paralelos experimenta un fallo temporal en la API, intentar la reconexión simultánea crea el problema de la estampida o la "manada en estampida" (Thundering Herd Problem), colapsando el servidor objetivo en el momento exacto en que este intenta recuperarse14.  
La solución arquitectónica dictamina que el agente de Antigravity implemente una estrategia de retroceso exponencial acoplada con fluctuación estocástica (Exponential Backoff and Jitter). El retroceso exponencial multiplica progresivamente el tiempo de espera entre intentos fallidos, mientras que el "Jitter" introduce una variable aleatoria en ese cálculo temporal, desincronizando las peticiones de los múltiples hilos del agente y suavizando la carga sobre la red14. En Python, el estándar corporativo definitivo para la orquestación de este patrón de resiliencia es la adopción de la biblioteca tenacity, combinada íntimamente con un cliente de red asíncrono como httpx12. El decorador de tenacity evaluará dinámicamente si el error pertenece al dominio transitorio (ej. un código HTTP 429) e invocará la función wait_exponential_jitter para espaciar las retentativas de forma segura12.

## **4. Evaluación Arquitectónica: Librerías Oficiales vs. Peticiones Raw en Entornos Autónomos**

La comunidad de desarrolladores y el propio Banco Central ofrecen abstracciones para facilitar la comunicación con la BDE. El BCCh publica y brinda mantenimiento oficial a la librería bcchapi (cuyo último release es la versión 1.1.2) distribuida a través del Python Package Index (PyPI)3. Sin embargo, la selección del cliente de red adecuado debe ponderar las peculiaridades de un entorno gobernado por bucles de eventos asíncronos y modelos de lenguaje de gran escala.

### **4.1 Análisis de la Librería Oficial bcchapi**

El paquete bcchapi fue diseñado con una vocación analítica, exponiendo clases estructurales robustas (como Siete y Stat) orientadas a simplificar la búsqueda de series temporales y la generación inmediata de cuadros estadísticos comparativos3. La principal propuesta de valor de esta herramienta radica en que encapsula el pre-procesamiento, proporcionando utilidades para el cálculo de estadísticas sumarias, promedios móviles, y variaciones interanuales, y devolviendo la información estandarizada dentro de un objeto DataFrame2.  
Sus dependencias fundacionales son las librerías requests y pandas3. Aunque esta arquitectura resulta extraordinaria para científicos de datos operando entornos interactivos de cuadernos computacionales (como Jupyter Notebooks) enfocados en el escrutinio humano3, su inclusión dentro del ecosistema de Antigravity presenta limitaciones de rendimiento severas e incompatibilidades paradigmáticas:

> 1. **Bloqueo Monolítico del Hilo de Entrada/Salida (I/O Blocking):** La dependencia subyacente de requests impone una naturaleza sincrónica. El núcleo de ejecución de Antigravity funciona sobre rutinas asíncronas de I/O (asyncio). Cuando una herramienta invoca un método sincrónico, bloquea enteramente el bucle de eventos (Event Loop)6. Esto anula la capacidad del agente para procesar interrupciones generadas por el usuario, actualizar dinámicamente el estado de los pensamientos del modelo (thoughts traces) en la interfaz gráfica, o ejecutar operaciones secundarias en paralelo, transformando un sistema reactivo en uno pasivo y latente.  
> 2. **Inflación del Consumo de Memoria y Overhead:** La inclusión de pandas arrastra consigo un ecosistema complejo que incluye librerías precompiladas de C (como NumPy). Esto aumenta masivamente el tamaño del paquete de distribución (wheel sizes) y ensancha desproporcionadamente la huella de memoria en el contenedor del agente3. En el escenario donde el agente autónomo únicamente requiere aislar el escalar del Índice de Precios al Consumidor (IPC) del último cuatrimestre para redactar un párrafo semántico, forzar la carga de todo el motor analítico de Pandas constituye una ineficiencia arquitectónica injustificable. Las transformaciones matemáticas complejas pueden ser delegadas a las capacidades deductivas del propio modelo fundacional (Gemini), o manejadas de manera liviana a través de estructuras de datos estándar de Python.

### **4.2 Superioridad del Cliente HTTP Directo Asíncrono (httpx)**

Para sostener los requisitos de alta concurrencia, resiliencia estricta y bajo acoplamiento que exige el entorno autónomo de Antigravity, la estrategia superior consiste en declinar el uso de envoltorios de terceros y construir un cliente HTTP directo haciendo uso de httpx.AsyncClient13.  
Esta aproximación otorga un control de grano fino sobre cada aspecto del ciclo de vida de la petición. El uso nativo de async/await certifica operaciones de red no bloqueantes, permitiendo la transmisión en tiempo real de flujos de eventos asíncronos hacia el usuario6. Además, httpx permite la declaración explícita de límites dimensionales (mediante httpx.Limits) para administrar la reserva de conexiones simultáneas y la reutilización de descriptores de sockets (Connection Pooling), lo que reduce la sobrecarga del saludo inicial criptográfico (TLS Handshake) en peticiones subsecuentes13. Acoplado sinérgicamente con el motor de reintentos tenacity, esta combinación produce un subsistema de comunicaciones virtualmente irrompible.

## **5. Formato de Entrega y Manual de Implementación Directa en Antigravity**

La orquestación, gestión de dependencias y despliegue del agente están administrados en su totalidad por el SDK de Google Antigravity para Python6. El framework permite definir herramientas algorítmicas (Tools) como funciones asíncronas puras de Python y registrarlas para que el modelo predictivo (Gemini) las ejecute bajo demanda6. Simultáneamente, para evitar la saturación de la ventana de contexto del LLM, el agente utilizará el estándar de metadatos semánticos denominado *Skills* (SKILL.md), el cual carga dinámicamente la lógica del Banco Central únicamente cuando el razonamiento del modelo lo requiere18.

### **5.1 Implementación de Extracción con Resiliencia Extrema (Snippet de Producción)**

El siguiente fragmento de código (snippet) ha sido diseñado para operar en un entorno de producción. Encapsula herméticamente la semaforización de concurrencia requerida por el límite del BCCh, la inyección segura de identidades desde el gestor de secretos, la normalización temporal de fechas y la inyección matemática de fluctuación para la gestión de reintentos de tenacity12.

```python
import os
import asyncio
import httpx
from datetime import datetime
from typing import Optional, Dict, Any
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
    retry_if_result,
    before_sleep_log
)

# Configuración de telemetría para monitoreo de la resiliencia
logger = logging.getLogger("BCChAutonomousTool")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Barrera de Concurrencia: Límite estricto de 4 peticiones en vuelo simultáneas.
# Operar al 80% del límite oficial del BCCh (5 RPS) absorbe picos de latencia imprevistos.
concurrency_limiter = asyncio.Semaphore(4)

# Definición explícita de errores a nivel de capa de transporte que requieren reintento.
TRANSIENT_EXCEPTIONS = (
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
    httpx.RemoteProtocolError,
)

def evaluate_retry_necessity(result: Dict[str, Any]) -> bool:
    """
    Función de evaluación determinista para la política de reintentos de Tenacity.
    Inspecciona si el payload enrutó un código de error de pasarela HTTP camuflado.
    """
    status_code = result.get("_http_status", 200)
    # Errores 429 (Too Many Requests) y 50x (Gateway Failures) inician el Backoff
    if status_code in {429, 500, 502, 503, 504}:
        return True
    return False

@retry(
    # Fusión lógica condicional: reintentar si la red falla O si el servidor pide retroceso
    retry=(retry_if_exception_type(TRANSIENT_EXCEPTIONS) | retry_if_result(evaluate_retry_necessity)),
    # Retroceso exponencial con Jitter: base 2 segundos, máximo 60 segundos de espera entre intentos
    wait=wait_exponential_jitter(initial=2, max=60), 
    stop=stop_after_attempt(5),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True
)
async def fetch_macro_series_resilient(
    timeseries_id: str, 
    firstdate: Optional[str] = None, 
    lastdate: Optional[str] = None
) -> Dict[str, Any]:
    """
    Núcleo asíncrono para la ingesta de una serie temporal del Banco Central de Chile.
    Aísla las credenciales y ejecuta la petición mediante httpx.
    """
    # Las credenciales se recuperan del entorno protegido de Antigravity, nunca están impresas.
    user = os.environ.get("BCCH_USER")
    password = os.environ.get("BCCH_PASS")
    
    if not user or not password:
        raise ValueError("Excepción de Integridad de Secretos: Falta BCCH_USER o BCCH_PASS en el entorno de ejecución.")

    url = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"
    
    params = {
        "user": user,
        "pass": password,
        "function": "GetSeries",
        "timeseries": timeseries_id
    }
    
    # Inyección de fechas condicional (Formato estricto requerido por BCCh: YYYY-MM-DD)
    if firstdate:
        params["firstdate"] = firstdate
    if lastdate:
        params["lastdate"] = lastdate

    # Configuración de los umbrales operativos de red (Limits y Timeouts) para prevenir agotamiento de descriptores
    limits = httpx.Limits(max_connections=10, max_keepalive_connections=5)
    timeout = httpx.Timeout(connect=5.0, read=15.0, write=5.0, pool=5.0)

    async with concurrency_limiter:
        async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
            response = await client.get(url, params=params)
            
            # Interceptación de estados de falla de red; delegamos la responsabilidad de reintento a Tenacity
            if response.status_code != 200:
                logger.warning(f"El servidor BCCh retornó código inusual: {response.status_code}. Preparando backoff.")
                return {"_http_status": response.status_code, "error": f"Fallo en la Pasarela, Código {response.status_code}"}
            
            data = response.json()
            
            # Evaluación del código lógico de estado interno (El BCCh codifica '0' como operación exitosa)
            if data.get("Codigo") != 0:
                # Los errores estructurales (ej. ID no válido) son fallos permanentes. Se aborta la ejecución inmediatamente sin reintentos.
                raise RuntimeError(f"Fallo Semántico de API BCCh: {data.get('Descripcion')}")
                
            # Fase de Extracción, Transformación y Carga (ETL On-the-fly)
            # Reversión y estandarización del formato temporal para evitar alucinaciones del LLM
            try:
                observaciones = data.get("Series", {}).get("Obs", [])
                for obs in observaciones:
                    raw_date = obs.get("indexDateString")
                    if raw_date:
                        # Traducción de "DD-MM-YYYY" (latino) a "YYYY-MM-DD" (ISO 8601)
                        parsed_date = datetime.strptime(raw_date, "%d-%m-%Y")
                        obs["indexDateString"] = parsed_date.strftime("%Y-%m-%d")
                    # Conversión explícita (Type Coercion) de magnitudes String a variables flotantes nativas
                    raw_val = obs.get("value")
                    if raw_val is not None:
                        obs["value"] = float(raw_val)
            except Exception as parse_error:
                logger.error(f"Fallo crítico en el motor de parseo del payload: {type(parse_error).__name__} (detalles omitidos por seguridad)")
                
            return data
```

### **5.2 Integración Segura y Declarativa de la Herramienta en el SDK de Antigravity**

El diseño arquitectónico de Antigravity permite inyectar la función asíncrona de extracción directamente como un nodo cognitivo (Tool) para el flujo de razonamiento del agente. Al inicializar el objeto LocalAgentConfig, el desarrollador configura políticas estrictas de seguridad (Policies), dictaminando un modelo de confianza cero donde todas las herramientas y capacidades están denegadas por defecto, salvo que se autoricen afirmativamente6.

```python
import asyncio
from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig
from google.antigravity.hooks.policy import allow, deny

# Interfaz funcional expuesta al Modelo Base. 
# Los Docstrings detallados son cruciales, el LLM lee esta documentación para saber cómo orquestar los parámetros.
async def tool_get_chilean_indicator(series_id: str, start_date: str = None, end_date: str = None) -> str:
    """
    Ejecuta una petición para recuperar datos históricos de series macroeconómicas de Chile, gestionadas por el Banco Central (BCCh).
    series_id: Requerido. El código identificador oficial de la base de datos BDE (ej. 'F022.TPM.TIN.D001.NO.Z.D' para Tasa de Política Monetaria).
    start_date: Opcional. Fecha de inicio del análisis en formato YYYY-MM-DD.
    end_date: Opcional. Fecha de finalización del análisis en formato YYYY-MM-DD.
    """
    try:
        # Se invoca la función interna con toda la lógica de resiliencia encapsulada
        dataset = await fetch_macro_series_resilient(series_id, start_date, end_date)
        # Antigravity absorbe la representación textual del diccionario y la inserta en el Context Window del modelo
        return str(dataset)
    except Exception as e:
        return f"El subsistema de extracción detuvo la tarea debido a una excepción: {type(e).__name__}"

async def initialize_autonomous_agent():
    # Declaración del Manifiesto de Seguridad (Deny by Default)
    # Se bloquean llamadas arbitrarias a la terminal o accesos al sistema de archivos local.
    security_policies = [
        deny("*"), 
        allow("tool_get_chilean_indicator")
    ]

    # La configuración aísla la lógica; las credenciales ya deben existir en el entorno del sistema operativo
    agent_configuration = LocalAgentConfig(
        system_instructions="Eres un analista macroeconómico experto. Analiza con rigor las variaciones estadísticas, extrae los indicadores económicos del Banco Central de Chile y emite informes precisos.",
        tools=[tool_get_chilean_indicator],
        policies=security_policies,
        capabilities=CapabilitiesConfig() 
    )

    # El bloque de contexto asíncrono administra el ciclo de vida, descubrimiento de binarios e inicialización de hooks
    async with Agent(agent_configuration) as data_agent:
        # Petición asíncrona no bloqueante
        agent_response = await data_agent.chat(
            "Extrae y analiza el valor de la Tasa de Política Monetaria chilena (Serie: F022.TPM.TIN.D001.NO.Z.D) para el período entre el 10 y el 15 de Octubre de 2021. Detalla su evolución diaria."
        )
        
        # Consumo de la respuesta iterativa (Streaming). 
        # Emite tanto los tokens textuales conversacionales como los flujos de herramientas y razonamiento interno del LLM en tiempo real.
        async for token in agent_response:
            print(token, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(initialize_autonomous_agent())
```

### **5.3 Definición de Antigravity Skill (SKILL.md) y Activación Semántica**

Cargar instrucciones masivas sobre cómo interactuar con el Banco Central dentro del bloque primario de instrucciones del sistema (System Prompt) de un agente generalista conlleva un desperdicio continuo de tokens y aumenta la confusión del modelo cognitivo19. En su lugar, el paradigma de Antigravity emplea un estándar abierto llamado *Skills*.  
Un Skill es una extensión de capacidad modular basada en un directorio, que incluye un manifiesto YAML en su interior (SKILL.md). El agente no carga este archivo en memoria hasta que ejecuta una operación de Activación Semántica (Semantic Triggering): mediante similitud vectorial, evalúa la intención de la consulta del usuario contra la propiedad description del archivo; si el usuario pregunta sobre inflación o tasas en Chile, el agente activa el entorno, asimila las reglas procedimentales para el BCCh, y ejecuta las herramientas pertinentes18. A diferencia de los servidores del Model Context Protocol (MCP) que se especializan en mantener conexiones persistentes y con estado hacia bases de datos o repositorios completos7, los Skills actúan como el motor deductivo que dirige el comportamiento del agente sobre las herramientas inyectadas.  
Para habilitar este flujo, el equipo de desarrollo debe guardar el siguiente manifiesto en el sistema de archivos del espacio de trabajo del proyecto en la ruta obligatoria `.agents/skills/bcch-extractor/SKILL.md`20:

```yaml
---
name: bcch-macro-extractor
description: Proporciona la lógica, el conocimiento taxonómico y las capacidades de extracción para recolectar estadísticas, tasas de interés, inflación (IPC), índices de actividad económica (Imacec) e indicadores financieros oficiales para la República de Chile directamente desde la API del Banco Central de Chile (BCCh BDE). El agente debe activar automáticamente esta habilidad cada vez que el usuario solicite un análisis de datos económicos, financieros o tendencias macroeconómicas que correspondan al territorio chileno.
---

# Lógica de Análisis y Extracción de Datos Macro-Económicos (Banco Central de Chile)

## Propósito Operativo  
Este módulo de conocimiento entrena e instruye al agente sobre la metodología exacta requerida para consultar, sanear, e interpretar datos macroeconómicos chilenos aprovechando la herramienta de Python nativa `tool_get_chilean_indicator` disponible en tu entorno de ejecución.

## Metodología y Procedimiento Obligatorio de Extracción  
Al activarse esta habilidad, el agente debe seguir inexorablemente la siguiente secuencia de razonamiento:  
1. **Identificación Taxonómica:** Identifica si la consulta del usuario hace referencia a un indicador económico ampliamente conocido (Ej: TPM, IPC, Imacec).  
2. **Invocación de la Herramienta:** Invoca el puente asíncrono `tool_get_chilean_indicator(series_id, start_date, end_date)`.   
   - Las variables temporales que suministres **deben** estar forzosamente en el estándar internacional `YYYY-MM-DD`. Jamás utilices formatos latinos para los parámetros de entrada.  
   - Para evaluar trayectorias históricas, inyecta invariablemente los valores `start_date` y `end_date` correspondientes al marco de tiempo solicitado.  
3. **Interpretación y Saneamiento del Payload:** El diccionario JSON retornado por la herramienta ya ha superado una fase de transformación (ETL). Observarás que el campo interno `indexDateString` se presenta saneado al formato `YYYY-MM-DD`, y los valores se muestran como variables de punto flotante válidas.  
4. **Manejo de Interpolación Discreta:** El Banco Central no produce registros numéricos durante días inhábiles, feriados legales y fines de semana. Si el análisis encomendado por el usuario requiere procesar la serie temporal como un bloque numérico continuo y sin vacíos, debes aplicar una heurística matemática de "Forward-Fill" (arrastrar la observación válida del día inmediatamente anterior hacia adelante) antes de calcular desviaciones estándar o variaciones promediadas.  
5. **Reporte y Transparencia:** Estructura los resultados haciendo un uso óptimo de tablas en lenguaje Markdown. Presenta conclusiones analíticas nítidas, citando siempre como fuente oficial primaria a la "Base de Datos Estadísticos del Banco Central de Chile".

## Condición de Éxito (End State)  
El ciclo del agente se declara como exitoso cuando el usuario visualiza los datos macroeconómicos con una precisión milimétrica, presentados bajo un formato tabular fácilmente asimilable, asegurando que las desviaciones de días inhábiles han sido mitigadas matemáticamente y que la narrativa contextual generada sea impecable.
```

## **Conclusiones Arquitectónicas**

La edificación de un agente de inteligencia artificial enteramente autónomo, operando dentro del ecosistema de Google Antigravity e interactuando contra la infraestructura de datos del Banco Central de Chile, exige trascender los enfoques tradicionales de programación reactiva para adoptar principios de ingeniería proactiva de sistemas distribuidos. Las conclusiones fundacionales derivadas de esta especificación técnica certifican que:  
La autenticación de la identidad debe abstraerse por completo del ciclo operativo del agente. Al estar cimentada en un paradigma heredado que expone secretos como parámetros mutables de la URL, la responsabilidad recae unívocamente sobre la infraestructura perimetral del agente. La inyección de dependencias mediante variables de entorno y políticas de confianza cero dictaminan que el Modelo de Lenguaje jamás visualiza, almacena ni registra los vectores de identidad en texto plano.  
Asimismo, el uso de dependencias externas monolíticas (como la biblioteca oficial bcchapi) constituye una penalización arquitectónica inasumible para la concurrencia. Bloquear el hilo de operaciones de red en un sistema de orquestación de eventos elimina la principal ventaja competitiva de Antigravity: la paralelización asíncrona. Construir clientes HTTP directos de bajo peso y acoplamiento (mediante httpx) es obligatorio para garantizar un comportamiento fluído, escalable y respetuoso de los recursos computacionales del contenedor.  
Finalmente, la integración de la resiliencia en la capa más profunda de la herramienta (a través de retroceso exponencial iterativo acoplado con desviación aleatoria mediante tenacity), y la rectificación de asimetrías severas de datos (la dicotomía de serialización de fechas y coerciones de tipos numéricos) antes de que la información penetre la ventana de contexto del LLM, garantizan la supresión de alucinaciones algorítmicas, consolidando una plataforma capaz de analizar la macroeconomía nacional con una solidez técnica irrefutable y exenta de supervisión humana continuada.

#### **Fuentes citadas**

> 1. API para Base de Datos Estadísticos - API BDE - Banco Central, [https://si3.bcentral.cl/estadisticas/Principal1/Web_Services/doc_es.htm](https://si3.bcentral.cl/estadisticas/Principal1/Web_Services/doc_es.htm)  
> 2. GitHub - airarrazaval/bcchapi: Node.js wrapper for the Banco Central de Chile API. Features a fully typed API client and utility tools to streamline macroeconomic data integration., [https://github.com/airarrazaval/bcchapi](https://github.com/airarrazaval/bcchapi)  
> 3. BCChAPI: A python interface to the Central Bank of Chile statistical database API, [https://www.bis.org/ifc/publ/ifcb66_06.pdf](https://www.bis.org/ifc/publ/ifcb66_06.pdf)  
> 4. Zero-G, Zero Trust: How Antigravity Floats Away with Your Secrets - Medium, [https://idanhabler.medium.com/zero-g-zero-trust-how-antigravity-floats-away-with-your-secrets-886a2739936f](https://idanhabler.medium.com/zero-g-zero-trust-how-antigravity-floats-away-with-your-secrets-886a2739936f)  
> 5. WEB SERVICES - Base de datos Estadísticos, [https://si3.bcentral.cl/estadisticas/Principal1/web_services/webservices/MT.pdf](https://si3.bcentral.cl/estadisticas/Principal1/web_services/webservices/MT.pdf)  
> 6. GitHub - google-antigravity/antigravity-sdk-python: A Python library for building AI agents that leverage the full power of Google Antigravity., [https://github.com/google-antigravity/antigravity-sdk-python](https://github.com/google-antigravity/antigravity-sdk-python)  
> 7. MCP - Google Antigravity Docs, [https://antigravity.google/docs/mcp](https://antigravity.google/docs/mcp)  
> 8. Overview + Quick Start - Google Antigravity Docs, [https://antigravity.google/docs/sdk/overview](https://antigravity.google/docs/sdk/overview)  
> 9. SieteWS Web Service, [https://si3.bcentral.cl/sietews/sietews.asmx?op=GetSeries](https://si3.bcentral.cl/sietews/sietews.asmx?op=GetSeries)  
> 10. API BDE using Python, [https://si3.bcentral.cl/estadisticas/Principal1/Web_Services/webservices/API%20BDE%20using%20Python.pdf](https://si3.bcentral.cl/estadisticas/Principal1/Web_Services/webservices/API%20BDE%20using%20Python.pdf)  
> 11. API Usage Guide - CBORG AI Portal, [https://cborg.lbl.gov/api_faq/](https://cborg.lbl.gov/api_faq/)  
> 12. Python Resilience Patterns for Fault-Tolerant Applications - Get Claude Skills, [https://www.getclaudeskills.com/skills/python-resilience-patterns-wshobson](https://www.getclaudeskills.com/skills/python-resilience-patterns-wshobson)  
> 13. 5 httpx Backoff Clients That Save Your Throughput | by Praxen - Medium, [https://medium.com/@Praxen/5-httpx-backoff-clients-that-save-your-throughput-55f4319f0c50](https://medium.com/@Praxen/5-httpx-backoff-clients-that-save-your-throughput-55f4319f0c50)  
> 14. Exponential Backoff, Jitter, and Multi-Agent LangGraph RAG - C# Corner, [https://www.c-sharpcorner.com/article/exponential-backoff-jitter-and-multi-agent-langgraph-rag/](https://www.c-sharpcorner.com/article/exponential-backoff-jitter-and-multi-agent-langgraph-rag/)  
> 15. Retry Pattern: Handling Transient Failures in Distributed Systems - DEV Community, [https://dev.to/diek/retry-pattern-handling-transient-failures-in-distributed-systems-i7a](https://dev.to/diek/retry-pattern-handling-transient-failures-in-distributed-systems-i7a)  
> 16. Python Requests - How To Retry Failed Requests (2026 Guide) - ScrapeOps, [https://scrapeops.io/python-web-scraping-playbook/python-requests-retry-failed-requests/](https://scrapeops.io/python-web-scraping-playbook/python-requests-retry-failed-requests/)  
> 17. bcchapi · PyPI, [https://pypi.org/project/bcchapi/](https://pypi.org/project/bcchapi/)  
> 18. Authoring Google Antigravity Skills - Codelabs, [https://codelabs.developers.google.com/getting-started-with-antigravity-skills](https://codelabs.developers.google.com/getting-started-with-antigravity-skills)  
> 19. How to Use Antigravity Skills: Complete Guide for Developers (2026) - Cloudvyn, [https://www.cloudvyn.com/blog/how-to-use-antigravity-skills](https://www.cloudvyn.com/blog/how-to-use-antigravity-skills)  
> 20. Skills - Google Antigravity Docs, [https://antigravity.google/docs/skills](https://antigravity.google/docs/skills)

# **Optimización de la Extracción de Información Estructurada Mediante Modelos de Lenguaje Pequeños y Orquestación de Razonamiento en Cadena**

La transición hacia sistemas de Software 3.0, donde los agentes basados en modelos de lenguaje interactúan de manera autónoma con interfaces de programación de aplicaciones y bases de datos, ha convertido la extracción de información estructurada en una capacidad crítica para la infraestructura tecnológica moderna.1 En este contexto, la dependencia de modelos de gran escala se ha visto desafiada por la emergencia de modelos de lenguaje pequeños (SLM, por sus siglas en inglés) que, con parámetros iguales o inferiores a los 14 mil millones, ofrecen una latencia reducida, menores costes operativos y la posibilidad de despliegue local en hardware de consumo.4 El presente informe técnico analiza en profundidad las estrategias para maximizar la precisión en la estructuración de datos JSON mediante el uso de estos modelos, integrando técnicas de razonamiento en cadena y motores de decodificación restringida.

## **Paisaje Tecnológico de los Modelos de Lenguaje Pequeños (\<=14B)**

La selección de un modelo para tareas de extracción estructurada ya no depende exclusivamente del conteo total de parámetros, sino de la eficiencia de su entrenamiento y su capacidad de seguimiento de instrucciones complejas. El mercado de 2025 y 2026 ha consolidado familias de modelos que superan en tareas específicas de lógica y razonamiento a modelos significativamente más grandes del pasado.5

### **Evaluación de Arquitecturas y Rendimiento de Modelos Compactos**

Los modelos actuales han sido optimizados mediante procesos de destilación de conocimiento, donde los patrones de razonamiento de modelos de parámetros masivos (superiores a 600B) se transfieren a arquitecturas más densas y manejables.9 Esta evolución permite que sistemas de 7B o 14B parámetros mantengan una coherencia lógica interna suficiente para procesar esquemas JSON anidados y relaciones de datos complejas.4

| Familia de Modelo | Parámetros Activos | Ventana de Contexto | Fortalezas en Extracción de Datos |
| :---- | :---- | :---- | :---- |
| DeepSeek-R1-Distill-Qwen | 7B / 14B | 128,000 tokens | Razonamiento matemático superior y autoverificación integrada.4 |
| Qwen 3.5-Instruct | 7B / 14B | 128,000 tokens | Excelente cumplimiento de instrucciones y soporte multilingüe.5 |
| Phi-4-mini-instruct | 3.8B | 128,000 tokens | Optimización para dispositivos de borde y lógica matemática robusta.7 |
| Ministral 14B Reasoning | 14B | 128,000 tokens | Diseñado específicamente para razonamiento en entornos locales.4 |
| Gemma 3-IT | 4B / 12B | 128,000 tokens | Arquitectura multimodal nativa con alta precisión en razonamiento.7 |
| SmolLM3-3B | 3B | 64,000+ tokens | Soporte de modo dual con y sin pensamiento para eficiencia de costes.7 |

El rendimiento de estos modelos en tareas de estructuración está intrínsecamente ligado a su capacidad de razonamiento matemático. Modelos como el DeepSeek-R1-Distill-Qwen-7B han demostrado alcanzar puntuaciones en el benchmark AIME 2025 que rivalizan con modelos propietarios de mayor tamaño, lo cual se traduce directamente en una menor tasa de alucinación de campos y una mejor interpretación de tipos de datos dentro de un esquema JSON.4

### **El Rol de la Destilación de Razonamiento**

La técnica de destilación ha permitido que los modelos pequeños no solo imiten el formato de salida de sus maestros, sino que internalicen el proceso lógico de descomposición de problemas. Los modelos DeepSeek-R1 destilados, por ejemplo, utilizan datos de "arranque en frío" y aprendizaje por refuerzo a gran escala para desarrollar comportamientos de reflexión y corrección de errores antes de emitir la respuesta final.10 En una tubería de extracción, esto significa que el modelo es capaz de identificar discrepancias entre el texto fuente y el esquema requerido, ajustando su salida de manera dinámica.10

## **Fundamentos de la Decodificación Restringida y Motores de Gramática**

Incluso los modelos con mejores capacidades de razonamiento pueden fallar en la generación de sintaxis JSON válida debido a la naturaleza probabilística de la predicción de tokens. La decodificación restringida surge como la solución de infraestructura para garantizar una adherencia del 100% al esquema definido, interviniendo directamente en la distribución de probabilidad de los tokens durante la inferencia.12

### **Mecanismos de Intervención en el Vocabulario**

Un modelo de lenguaje genera texto prediciendo el siguiente token basado en la secuencia anterior: ![][image1]. Sin restricciones, el modelo podría elegir un token que rompa la estructura JSON, como una coma mal posicionada o una clave no definida en el esquema.12 Los motores de decodificación restringida insertan un procesador de logits que actúa como un filtro basado en una máquina de estados finitos (FSM) o una gramática libre de contexto (CFG) derivada del esquema JSON.12

El proceso técnico implica que, en cada paso de generación, el motor identifica qué tokens del vocabulario total (que suele oscilar entre 32,000 y 128,000 términos) son gramaticalmente válidos según el estado actual del esquema JSON. Los logits de los tokens inválidos se establecen en ![][image2], forzando al modelo a seleccionar únicamente entre opciones que mantengan la validez estructural.3

### **Comparativa de Motores de Generación Estructurada**

La eficiencia de estos motores es vital para no comprometer la latencia del sistema. Mientras que las primeras implementaciones introducían cuellos de botella significativos, las soluciones de 2025 han logrado una sobrecarga cercana a cero mediante el uso de cachés adaptativos y compilación justo a tiempo (JIT).12

| Motor de Decodificación | Enfoque Técnico | Ventaja Competitiva | Escenario de Uso Ideal |
| :---- | :---- | :---- | :---- |
| XGrammar | Autómata de Pila (PDA) | Hasta 100x más rápido en esquemas complejos y recursivos.12 | Producción de alta concurrencia y agentes dinámicos. |
| Outlines | Máquina de Estados Finitos (FSM) | Extremadamente flexible y fácil de integrar con Python.3 | Desarrollo rápido y esquemas basados en expresiones regulares. |
| llguidance | Gramática Libre de Contexto (CFG) | Soporte robusto para gramáticas arbitrarias y esquemas recursivos.12 | Aplicaciones que requieren validación de gramáticas de código o lenguajes específicos. |
| BAML | Análisis Alineado al Esquema (SAP) | Capacidad única para extraer datos de salidas "sucias" o con preámbulos.18 | Extracción de modelos que tienden a ser conversacionales o verbosos. |
| DOMINO | Alineación de Subpalabras | Sobrecarga cero mediante decodificación especulativa.15 | Optimización extrema de latencia en sistemas de tiempo real. |

El motor XGrammar representa el estado del arte al dividir los tokens en conjuntos dependientes e independientes del contexto. Al pre-computar máscaras de bits para la mayoría del vocabulario, reduce la inspección de la pila en tiempo de ejecución al mínimo necesario, permitiendo que incluso modelos de 14B procesen esquemas JSON extensos con una latencia imperceptible para el usuario final.12

## **Implementación de Razonamiento en Cadena (Chain of Thought)**

El uso de Chain of Thought (CoT) en modelos pequeños es una técnica de andamiaje cognitivo que permite al modelo procesar información intermedia antes de comprometerse con la estructura final del JSON. Esta estrategia es especialmente valiosa cuando la extracción requiere normalización de unidades, deducción lógica o manejo de ambigüedades en el texto fuente.11

### **Estrategias de Ubicación del Pensamiento**

La forma en que se solicita al modelo que "piense" influye en su capacidad para seguir el esquema JSON. Existen tres patrones predominantes en la arquitectura de pipelines para SLMs.4

1. **Razonamiento Externo mediante Etiquetas:** El modelo utiliza etiquetas específicas, como \<think\>... \</think\>, para generar su monólogo interno antes de abrir la llave inicial del JSON. Este patrón es el estándar para modelos como DeepSeek-R1 y permite que el motor de decodificación ignore el texto de pensamiento y solo aplique restricciones al bloque de respuesta final.4  
2. **Campos Internos de Razonamiento:** Se incluye una clave como "razonamiento" o "explicacion" dentro del propio objeto JSON. Aunque esto garantiza que el pensamiento esté vinculado a la salida, puede forzar al modelo a seguir restricciones gramaticales durante el proceso creativo de razonamiento, lo que a veces degrada la calidad de la deducción lógica.14  
3. **Orden de Campos Prioritario:** Al diseñar el esquema JSON, colocar los campos que requieren mayor deducción al principio del objeto aprovecha la naturaleza autoregresiva del modelo. El contenido generado para los primeros campos sirve como contexto de atención para los campos subsiguientes, mejorando la coherencia global.14

### **El Desafío del "Bleed" Conversacional en Modelos Pequeños**

Uno de los problemas recurrentes en modelos de menos de 14B es su tendencia a incluir texto explicativo antes o después del bloque JSON, como "Aquí tienes la información solicitada:". Esto se conoce como sangrado conversacional.14 La combinación de CoT con decodificación restringida resuelve este problema de raíz: el motor de decodificación simplemente no permite la generación de tokens que no formen parte de la estructura \<think\> o del esquema {... }, eliminando la necesidad de costosos post-procesamientos basados en expresiones regulares.12

## **Arquitecturas de Pipeline Multietapa y Colaboración entre Modelos**

En escenarios donde la complejidad de la extracción supera las capacidades de un único modelo pequeño, se emplean arquitecturas multietapa que descomponen la tarea en pasos lógicos manejables. Estas arquitecturas permiten que modelos de 7B alcancen niveles de precisión comparables a modelos de 70B o superiores.22

### **El Marco de Trabajo DICE y la Refinación de Salidas**

El marco DICE (Guiding SLMs to Think with Chain-of-thought Correction) propone un enfoque de colaboración donde un modelo más grande (LLM) genera una respuesta inicial en lenguaje natural y un SLM entrenado específicamente actúa como refinador estructurado.30

Este proceso se divide en:

* **Generación Desacoplada:** El LLM produce una respuesta rica en contexto sin preocuparse por el formato JSON, lo que preserva su capacidad de razonamiento profundo.30  
* **Análisis del SLM:** El modelo pequeño analiza la salida del LLM, identifica las entidades relevantes y las mapea al esquema JSON requerido utilizando un patrón de "analizar-luego-responder".30  
* **Corrección de Formato:** El SLM asegura que se cumplan todas las restricciones de tipos y campos obligatorios, actuando como un guardián de calidad estructural.30

### **LITECOST: Transferencia de Comportamiento Estructurado**

El marco LITECOST se centra en transferir la disciplina de formato y razonamiento de los modelos grandes a los pequeños mediante el ajuste fino (fine-tuning). Se utiliza un LLM para generar "trazas de razonamiento" de alta calidad y esquemas de salida serializados que sirven como datos de entrenamiento para que el SLM internalice no solo el qué, sino el cómo de la extracción.22 Esto permite que, en tiempo de ejecución, el SLM genere estructuras que son funcionalmente equivalentes a las de un modelo de frontera pero con una fracción del coste y la latencia.22

### **Razonamiento Multitrayectoria con SLM-MATRIX**

Para aplicaciones de misión crítica, el sistema SLM-MATRIX introduce una metodología de verificación basada en múltiples agentes y búsqueda en árbol de Monte Carlo (MCTS).11 En lugar de confiar en una única generación, el sistema:

1. Genera múltiples trayectorias de razonamiento utilizando diferentes SLMs o diferentes semillas de muestreo.29  
2. Utiliza un módulo discriminador para evaluar la consistencia entre las trayectorias.29  
3. Realiza una verificación cruzada para asegurar que los resultados extraídos sean fieles al documento fuente, logrando precisiones superiores al 92% en dominios técnicos complejos.29

## **Ingeniería de Prompts Específica para la Estructuración en SLMs**

La sensibilidad de los modelos pequeños a la estructura del prompt es significativamente mayor que en modelos de gran escala. Un diseño de prompt subóptimo puede llevar a una degradación rápida de la adherencia al esquema, incluso con decodificación restringida.14

### **Patrones de Diseño de Prompts para Extracción**

| Técnica | Implementación Práctica | Impacto en el Modelo |
| :---- | :---- | :---- |
| Esquema Primero | Definir el JSON Schema al inicio del prompt, antes de las instrucciones o el texto fuente.27 | Reduce la carga cognitiva al establecer el objetivo de salida desde el primer token. |
| Delimitadores XML | Envolver cada sección en etiquetas claras: \<texto\>, \<instrucciones\>, \<esquema\>.27 | Ayuda al modelo a separar semánticamente el contenido de las reglas. |
| Ejemplos de Frontera | Usar 1-3 ejemplos few-shot que muestren casos ambiguos o difíciles, no solo los fáciles.27 | Define los límites de las categorías y previene el sobreajuste a patrones simples. |
| Etiquetas de Recordatorio | Finalizar el prompt con una etiqueta \<recordatorio\>Solo JSON\</recordatorio\>.27 | Combate el fenómeno de "olvido" de instrucciones en prompts de contexto largo. |

Es crucial evitar el uso de demasiados ejemplos de pocos disparos (few-shot). En modelos con ventanas de contexto limitadas o donde el coste por token es un factor, cada ejemplo consume espacio que podría ser utilizado para el texto fuente o para el razonamiento interno del modelo. Se ha observado que la mejora marginal después del tercer ejemplo es mínima en modelos de 7B y 14B.27

### **Manejo del Sesgo de Posición y Longitud de Contexto**

La investigación sobre el "sesgo de posición" indica que los SLMs prestan mucha más atención a la información situada al principio y al final de un prompt, ignorando frecuentemente los detalles enterrados en el medio.23 Para la extracción de datos de documentos largos, esto implica que las instrucciones críticas y el esquema JSON deben residir en los extremos del prompt, mientras que el material de referencia puede ocupar la sección central.23

## **Cuantización y Optimización de Hardware para Inferencia**

El despliegue de modelos de 14B en entornos locales o de borde requiere a menudo técnicas de cuantización para reducir los requisitos de memoria de vídeo (VRAM) y aumentar la velocidad de procesamiento. Sin embargo, reducir la precisión numérica tiene efectos directos sobre la capacidad de razonamiento lógico necesaria para la extracción estructurada.33

### **Comparativa de Formatos de Precisión y su Impacto**

La cuantización de FP16 a formatos de 8 u 4 bits es una necesidad económica en la producción de 2026\. Los datos indican que el formato FP8 se ha convertido en el estándar de facto para inferencia en centros de datos debido a su equilibrio casi perfecto entre velocidad y fidelidad.33

| Formato de Cuantización | Degradación en Razonamiento (MMLU-Pro) | Ahorro de Memoria | Ganancia de Throughput |
| :---- | :---- | :---- | :---- |
| FP16 / BF16 | 0.0% (Base) | 0% | 1.0x |
| FP8 (E4M3) | \~0.4% | 50% | 1.5x \- 1.7x.33 |
| INT8 | \~0.7% | 50% | 1.4x.33 |
| AWQ-4 / GPTQ-4 | \~1.6% | 75% | 3.1x.33 |
| INT3 / GGUF Q3 | \~6.0% | \>80% | \>4.0x.33 |

Para tareas de extracción que dependen fuertemente del razonamiento en cadena, la caída a 3 bits suele ser inaceptable, ya que el modelo pierde la capacidad de mantener la coherencia lógica durante secuencias largas de pensamiento.33 Sin embargo, la cuantización AWQ de 4 bits es altamente efectiva para modelos de la serie Qwen y Llama, ya que protege las capas sensibles del transformador (como las proyecciones de atención) manteniendo la precisión donde más importa para la extracción de datos.33

### **Capacidad de Concurrencia y Caché KV**

Un aspecto crítico para los modelos de razonamiento (como los basados en DeepSeek-R1) es el tamaño del caché de claves y valores (KV). Dado que estos modelos generan miles de tokens de "pensamiento" antes de la respuesta JSON, consumen el caché KV mucho más rápido que los modelos estándar.7

En una GPU H100 con 80GB de VRAM:

* Un modelo de 32B en **BF16** deja solo 4.4 GB para el caché KV, permitiendo apenas 4 usuarios concurrentes con un contexto de 4K tokens.36  
* El mismo modelo en **INT4** libera 47.3 GB para el caché KV, lo que permite escalar hasta 47 usuarios concurrentes, incrementando la eficiencia operativa por un factor de 12\.36

Esta ganancia en concurrencia es fundamental para viabilizar económicamente el uso de Chain of Thought en sistemas de producción a gran escala.

## **Métricas de Evaluación y Benchmarking de Salida Estructurada**

La evaluación del éxito en la extracción de información estructurada no debe limitarse a la validez sintáctica del JSON. Es necesario distinguir entre la adherencia al esquema (Schema Accuracy) y la exactitud de los datos extraídos (Value Accuracy).2

### **Desglose de Benchmarks Especializados**

Existen varios conjuntos de datos diseñados para medir específicamente la robustez de los modelos en la generación estructurada y el cumplimiento de contratos de datos.38

| Benchmark | Foco de Evaluación | Complejidad |
| :---- | :---- | :---- |
| SchemaBench | Capacidad del modelo para seguir esquemas JSON complejos y anidados.40 | Alta: Incluye restricciones lógicas y tipos profundos. |
| ExtractBench | Evaluación de la exactitud de los valores finales comparados con la verdad de campo.38 | Media-Alta: Crucial para medir alucinaciones de contenido. |
| FIRE / FIRE-Refined | Extracción de entidades financieras y contextuales de informes de negocios.39 | Específica de dominio: Mide precisión en nombres, fechas y valores económicos. |
| PII Recognition | Extracción y clasificación de información de identificación personal en 56 categorías.39 | Alta: Requiere alta fidelidad para seguridad y cumplimiento. |
| Insurance Claims | Extracción de datos de formularios escaneados y notas de seguros.39 | Operacional: Evalúa la robustez ante texto ruidoso o proveniente de OCR. |

Los resultados actuales muestran que, mientras que los modelos de frontera alcanzan una precisión de esquema cercana al 100%, la exactitud de los valores (Value Accuracy) puede ser tan baja como el 83% en texto y descender drásticamente en modalidades como audio o imagen.38 Esto subraya la importancia de implementar capas de verificación adicionales y procesos de autocrítica dentro del pipeline de razonamiento.

### **Métricas de Precisión de Campo vs. Precisión de Salida**

Para una evaluación granular, se utilizan dos métricas principales:

* **Field Accuracy:** Mide la proporción de campos individuales extraídos correctamente. Es útil para identificar qué partes del esquema son más difíciles para el modelo.39  
* **Output Accuracy:** Considera que la salida es incorrecta si falla un solo campo. Esta es la métrica más realista para aplicaciones donde el JSON debe integrarse en un flujo de trabajo automatizado sin intervención humana.39

## **Despliegue en Producción y Ecosistema de Herramientas**

El despliegue de un pipeline de extracción estructurada requiere una integración estrecha entre el servidor de inferencia, la lógica de la aplicación y la validación de tipos.14

### **Orquestación con vLLM y Servidores Compatibles con OpenAI**

El ecosistema vLLM ha integrado de forma nativa motores como XGrammar y Guidance, permitiendo que las restricciones se apliquen mediante parámetros simples en las solicitudes de API.19

Python

\# Ejemplo de configuración de backend en vLLM  
vllm serve "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B" \\  
    \--structured-outputs-config backend=xgrammar \\  
    \--reasoning-parser deepseek\_r1

Esta configuración permite que el servidor maneje automáticamente el análisis de los bloques de pensamiento y aplique la gramática JSON solo a la sección de respuesta, optimizando el rendimiento mediante el uso de cachés de máscaras de tokens.16

### **Librerías de Validación y Tipado**

En el lado de la aplicación, el uso de librerías de validación como Pydantic (Python) o Zod (TypeScript) es esencial para cerrar el ciclo de confianza. Estas herramientas permiten definir el esquema una sola vez y generar tanto el JSON Schema para el modelo de lenguaje como los objetos tipados para el resto del código.14

| Librería | Ecosistema | Ventaja en Estructuración |
| :---- | :---- | :---- |
| Instructor | Python | Facilita reintentos automáticos si la validación de Pydantic falla.18 |
| Pydantic AI | Python | Trata la salida estructurada como un ciudadano de primera clase en agentes.18 |
| Vercel AI SDK | TypeScript | Soporte nativo para Zod y transmisión (streaming) de objetos parciales.14 |
| BAML | Multi-lenguaje | Genera clientes seguros para múltiples lenguajes desde un único esquema .baml.18 |

La capacidad de realizar reintentos automáticos proporcionada por librerías como Instructor es una de las defensas más efectivas contra fallas esporádicas. Si el modelo genera un valor fuera de rango, el sistema puede reenviar el mensaje de error del validador al modelo para que este corrija el campo específico en una segunda iteración.18

## **Conclusiones y Recomendaciones Estratégicas**

El desarrollo de un proyecto de extracción y estructuración mediante SLMs de hasta 14B parámetros es una solución viable y altamente eficiente si se aplican los principios de orquestación adecuados. La clave del éxito no reside únicamente en la potencia del modelo, sino en la robustez del pipeline que lo rodea.

Para maximizar la eficacia del sistema, se recomienda:

* **Priorizar modelos destilados con capacidades de razonamiento nativas:** Modelos como la serie DeepSeek-R1-Distill-Qwen o Ministral 14B ofrecen la base lógica necesaria para manejar CoT de manera efectiva sin degradar el formato de salida.4  
* **Implementar decodificación restringida a nivel de servidor:** Utilizar motores como XGrammar integrados en vLLM garantiza la validez sintáctica total y reduce la latencia mediante el pre-cómputo de máscaras de tokens.12  
* **Adoptar arquitecturas multietapa para tareas complejas:** El uso de marcos como DICE permite que los modelos pequeños se enfoquen en la estructuración mientras que modelos más grandes o procesos previos manejan la carga del razonamiento abstracto.30  
* **Utilizar cuantización inteligente (FP8/AWQ-4):** Esto permite maximizar la concurrencia y manejar el gran volumen de tokens generado por los procesos de pensamiento interno sin comprometer significativamente la precisión de los datos extraídos.33  
* **Validar siempre a nivel de aplicación:** Nunca se debe confiar ciegamente en la salida del modelo. El uso de Pydantic o Zod para la validación final es obligatorio para asegurar la integridad de los datos antes de su inserción en sistemas críticos.14

La integración de estas técnicas transforma a los modelos de lenguaje pequeños de simples generadores de texto a motores de extracción de datos precisos y confiables, capaces de operar a gran escala con una eficiencia de recursos sin precedentes en el panorama actual de la inteligencia artificial.

#### **Obras citadas**

1. arxiv.org, fecha de acceso: mayo 7, 2026, [https://arxiv.org/html/2510.08623v1](https://arxiv.org/html/2510.08623v1)  
2. SLOT: Structuring the Output of Large Language Models \- ACL Anthology, fecha de acceso: mayo 7, 2026, [https://aclanthology.org/2025.emnlp-industry.32.pdf](https://aclanthology.org/2025.emnlp-industry.32.pdf)  
3. Generate structured output from LLMs with Dottxt Outlines in AWS | Artificial Intelligence, fecha de acceso: mayo 7, 2026, [https://aws.amazon.com/blogs/machine-learning/generate-structured-output-from-llms-with-dottxt-outlines-in-aws/](https://aws.amazon.com/blogs/machine-learning/generate-structured-output-from-llms-with-dottxt-outlines-in-aws/)  
4. Top 10 Open-source Reasoning Models in 2026 \- Clarifai, fecha de acceso: mayo 7, 2026, [https://www.clarifai.com/blog/top-10-open-source-reasoning-models-in-2026](https://www.clarifai.com/blog/top-10-open-source-reasoning-models-in-2026)  
5. Small Language Models \- Emergent Mind, fecha de acceso: mayo 7, 2026, [https://www.emergentmind.com/topics/small-language-models](https://www.emergentmind.com/topics/small-language-models)  
6. Small Language Models for Agentic Systems: A Survey of Architectures, Capabilities, and Deployment Trade-offs \- arXiv, fecha de acceso: mayo 7, 2026, [https://arxiv.org/pdf/2510.03847](https://arxiv.org/pdf/2510.03847)  
7. The Best Open-Source Small Language Models (SLMs) in 2026 \- BentoML, fecha de acceso: mayo 7, 2026, [https://www.bentoml.com/blog/the-best-open-source-small-language-models](https://www.bentoml.com/blog/the-best-open-source-small-language-models)  
8. Best Open Source LLMs in 2025 \- Koyeb, fecha de acceso: mayo 7, 2026, [https://www.koyeb.com/blog/best-open-source-llms-in-2025](https://www.koyeb.com/blog/best-open-source-llms-in-2025)  
9. Best Small Language Models: Top Open Source SLMs & Guide \- Ubiai, fecha de acceso: mayo 7, 2026, [https://ubiai.tools/best-small-language-models-open-source-guide/](https://ubiai.tools/best-small-language-models-open-source-guide/)  
10. deepseek-ai/DeepSeek-R1-Distill-Qwen-7B \- Hugging Face, fecha de acceso: mayo 7, 2026, [https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B)  
11. Reasoning Beyond Limits: Advances and Open Problems for LLMs \- arXiv, fecha de acceso: mayo 7, 2026, [https://arxiv.org/html/2503.22732v1](https://arxiv.org/html/2503.22732v1)  
12. How Structured Outputs and Constrained Decoding Work | Let's Data Science, fecha de acceso: mayo 7, 2026, [https://letsdatascience.com/blog/structured-outputs-making-llms-return-reliable-json](https://letsdatascience.com/blog/structured-outputs-making-llms-return-reliable-json)  
13. Tool-Call Hallucination: The Fix Stack | by Gupta Karmesh | Apr, 2026 | Medium, fecha de acceso: mayo 7, 2026, [https://medium.com/@gupta.00karmesh/tool-call-hallucination-the-fix-stack-2279e45081c5](https://medium.com/@gupta.00karmesh/tool-call-hallucination-the-fix-stack-2279e45081c5)  
14. LLM Structured Outputs: The Practical Guide \[2026\] \- TECHSY, fecha de acceso: mayo 7, 2026, [https://techsy.io/en/blog/llm-structured-outputs-guide](https://techsy.io/en/blog/llm-structured-outputs-guide)  
15. Beyond Free-Form Text: How Constrained Decoding is Reshaping Structured Generation in LLMs | by Brijesh Nambiar | Medium, fecha de acceso: mayo 7, 2026, [https://medium.com/@brijeshrn/beyond-free-form-text-how-constrained-decoding-is-reshaping-structured-generation-in-llms-5f7a38bef259](https://medium.com/@brijeshrn/beyond-free-form-text-how-constrained-decoding-is-reshaping-structured-generation-in-llms-5f7a38bef259)  
16. XGrammar-2: Efficient Dynamic Structured Generation Engine for Agentic LLMs \- arXiv, fecha de acceso: mayo 7, 2026, [https://arxiv.org/pdf/2601.04426](https://arxiv.org/pdf/2601.04426)  
17. Structured Decoding in vLLM: A Gentle Introduction \- BentoML, fecha de acceso: mayo 7, 2026, [https://www.bentoml.com/blog/structured-decoding-in-vllm-a-gentle-introduction](https://www.bentoml.com/blog/structured-decoding-in-vllm-a-gentle-introduction)  
18. 8 Best LLM Structured Output Libraries \[2026\] | TECHSY, fecha de acceso: mayo 7, 2026, [https://techsy.io/en/blog/best-llm-structured-output-libraries](https://techsy.io/en/blog/best-llm-structured-output-libraries)  
19. guidance-ai/llguidance: Super-fast Structured Outputs \- GitHub, fecha de acceso: mayo 7, 2026, [https://github.com/guidance-ai/llguidance](https://github.com/guidance-ai/llguidance)  
20. Using Outlines to get structured output from R1 \- GitHub Gist, fecha de acceso: mayo 7, 2026, [https://gist.github.com/cpfiffer/e98fc71d4fcb35ba827fc9e679112895](https://gist.github.com/cpfiffer/e98fc71d4fcb35ba827fc9e679112895)  
21. Guiding LLMs The Right Way: Fast, Non-Invasive Constrained Generation \- arXiv, fecha de acceso: mayo 7, 2026, [https://arxiv.org/html/2403.06988v1](https://arxiv.org/html/2403.06988v1)  
22. LONG-DOCUMENT QA WITH CHAIN-OF-STRUCTURED- THOUGHT AND FINE-TUNED SLMS \- OpenReview, fecha de acceso: mayo 7, 2026, [https://openreview.net/pdf?id=faECRsdRav](https://openreview.net/pdf?id=faECRsdRav)  
23. A Developer's Guide to Effective Prompt Engineering for AI | by Ankit Kumar \- Medium, fecha de acceso: mayo 7, 2026, [https://medium.com/engineering-intelligence/a-developers-guide-to-effective-prompt-engineering-for-ai-023923f1e45d](https://medium.com/engineering-intelligence/a-developers-guide-to-effective-prompt-engineering-for-ai-023923f1e45d)  
24. Schema Lineage Extraction at Scale: Multilingual Pipelines, Composite Evaluation, and Language-Model Benchmarks \- arXiv, fecha de acceso: mayo 7, 2026, [https://arxiv.org/html/2508.07179v1](https://arxiv.org/html/2508.07179v1)  
25. Structured Outputs \- vLLM, fecha de acceso: mayo 7, 2026, [https://docs.vllm.ai/en/stable/features/structured\_outputs/](https://docs.vllm.ai/en/stable/features/structured_outputs/)  
26. Structured model outputs | OpenAI API, fecha de acceso: mayo 7, 2026, [https://developers.openai.com/api/docs/guides/structured-outputs](https://developers.openai.com/api/docs/guides/structured-outputs)  
27. Training Small Language Models (SLMs) for agentic systems: a practitioner's guide, fecha de acceso: mayo 7, 2026, [https://levelup.gitconnected.com/training-small-language-models-smls-for-agentic-systems-a-practitioners-guide-b40bdcca2bf9](https://levelup.gitconnected.com/training-small-language-models-smls-for-agentic-systems-a-practitioners-guide-b40bdcca2bf9)  
28. LLM Structured Output in 2026: Stop Parsing JSON with Regex and Do It Right, fecha de acceso: mayo 7, 2026, [https://dev.to/pockit\_tools/llm-structured-output-in-2026-stop-parsing-json-with-regex-and-do-it-right-34pk](https://dev.to/pockit_tools/llm-structured-output-in-2026-stop-parsing-json-with-regex-and-do-it-right-34pk)  
29. (PDF) SLM-MATRIX: a multi-agent trajectory reasoning and verification framework for enhancing language models in materials data extraction \- ResearchGate, fecha de acceso: mayo 7, 2026, [https://www.researchgate.net/publication/394708968\_SLM-MATRIX\_a\_multi-agent\_trajectory\_reasoning\_and\_verification\_framework\_for\_enhancing\_language\_models\_in\_materials\_data\_extraction](https://www.researchgate.net/publication/394708968_SLM-MATRIX_a_multi-agent_trajectory_reasoning_and_verification_framework_for_enhancing_language_models_in_materials_data_extraction)  
30. DICE: Structured Reasoning in LLMs through SLM-Guided Chain-of-Thought Correction \- ACL Anthology, fecha de acceso: mayo 7, 2026, [https://aclanthology.org/2025.emnlp-main.355.pdf](https://aclanthology.org/2025.emnlp-main.355.pdf)  
31. DICE: Structured Reasoning in LLMs through SLM-Guided Chain-of-Thought Correction, fecha de acceso: mayo 7, 2026, [https://arxiv.org/html/2510.09211v1](https://arxiv.org/html/2510.09211v1)  
32. DICE: Structured Reasoning in LLMs through SLM-Guided Chain-of-Thought Correction \- arXiv, fecha de acceso: mayo 7, 2026, [https://arxiv.org/pdf/2510.09211](https://arxiv.org/pdf/2510.09211)  
33. Quantization Tradeoffs: 4-bit vs 8-bit vs FP8 Data \- Digital Applied, fecha de acceso: mayo 7, 2026, [https://www.digitalapplied.com/blog/quantization-tradeoffs-4bit-8bit-fp8-performance-data](https://www.digitalapplied.com/blog/quantization-tradeoffs-4bit-8bit-fp8-performance-data)  
34. From Precision to Quantization: A Practical Guide to Faster, Cheaper LLMs \- DeepInfra, fecha de acceso: mayo 7, 2026, [https://deepinfra.com/blog/precision-to-quantization-faster-cheaper-llms](https://deepinfra.com/blog/precision-to-quantization-faster-cheaper-llms)  
35. Mixed-Precision Quantization for Language Models: Techniques and Prospects \- arXiv, fecha de acceso: mayo 7, 2026, [https://arxiv.org/html/2510.16805v1](https://arxiv.org/html/2510.16805v1)  
36. LLM Quantization: BF16 vs FP8 vs INT4 \- AIMultiple, fecha de acceso: mayo 7, 2026, [https://aimultiple.com/llm-quantization](https://aimultiple.com/llm-quantization)  
37. A Deep Dive into LLM Quantization: FP32, BF16, INT8, NF4 & QLoRA \- Medium, fecha de acceso: mayo 7, 2026, [https://medium.com/@saurad44/a-deep-dive-into-llm-quantization-fp32-bf16-int8-nf4-qlora-830ff4936f3f](https://medium.com/@saurad44/a-deep-dive-into-llm-quantization-fp32-bf16-int8-nf4-qlora-830ff4936f3f)  
38. A Multi-Source Benchmark for Evaluating Structured Output Quality in Large Language Models \- arXiv, fecha de acceso: mayo 7, 2026, [https://arxiv.org/html/2604.25359v1](https://arxiv.org/html/2604.25359v1)  
39. LLM Structured Output Benchmarks are Riddled with Mistakes \- Cleanlab, fecha de acceso: mayo 7, 2026, [https://cleanlab.ai/blog/structured-output-benchmark/](https://cleanlab.ai/blog/structured-output-benchmark/)  
40. Learning to Generate Structured Output with Schema Reinforcement Learning \- arXiv, fecha de acceso: mayo 7, 2026, [https://arxiv.org/html/2502.18878v1](https://arxiv.org/html/2502.18878v1)  
41. Structured outputs in vLLM: Guiding AI responses | Red Hat Developer, fecha de acceso: mayo 7, 2026, [https://developers.redhat.com/articles/2025/06/03/structured-outputs-vllm-guiding-ai-responses](https://developers.redhat.com/articles/2025/06/03/structured-outputs-vllm-guiding-ai-responses)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGEAAAAYCAYAAADqK5OqAAAEC0lEQVR4Xu2ZachNaxTHl9k1ZboS4iTTzZRMmY/hEykk+UDee5WhKCUZisxTSomSwmvMWPhilinD/UAkt64MmUkkUUj8/6293/NYZ5+998t+6z1v51f/OnutZ+9n72c9z1rP3kekQIECydMaOmSNCdDQGvKMBtARqJ51JE0N6CKUMvYk4HXznaHQSaiKdSTJZmiWNSbEaWvIU7ZB86zR0lP0gd9C36H/vGPqgmffDjX2T/DoAH2UsltuFSUIvaFX0B/WEcRe0SB0Mva/oE+SPSjroK3GliS2v3zmITTDGoN4Aj21Ro9bogFq79jYdpxznDQVKQjF0FlrtHQRHeRd1gHqiK4EihWftBJtz/PKiooUhMnQe2u0zBEd1H+sA0wT9S11bKM9W33H5tJHdBCvi86AXqIFag8032kXRlAQiqCr0E3RCcN8ux/aB43INCt3DBQdr6bW4XJKtFEbx8ZZXwS9hlZBlR3fTOibc+zSWXSAuIIIt5rvoK7QatF+fF8YNghF0ALR7R6LHK9zA2okuoFgcMorfqax9bYEDshn0UZ88HPQY9H0swXqlmlawmzopTV6bIBaer8riV7rgHe8Fpri/fYZArUzNmKDcEz0eoQ7M94vJwMDwpUwyPP5cBIFrWxLrv7jwBfVMdYYAMeD95s29hJGSu56kAs+PFdIFB1Fr/23dTjchgZYo2QHwWW66HU5CEEshw5DD6wjgFz9h8G0sgk6L1p0o2gher98eQuEM5cNJllHCBOgr9YYgD9YKWP3+RP6AFWzDtEUmQtup/+3RkNaooMQ1n8cFkq8IDANcRx6WIfPfYlRNAzDRc+pax2iAfKLOFPIPceXgtZ7v1eIzsJnorOeKcbFDUJV0fZjoerQG/n5HWWUZK+2tGQHIQVN9X5H9R+HuEHoLzpeTayDcDnT+a91ROCfZ+sFvyWxYHPHwgL9Bbrk+TiQu6Hu3jFZKfogQbhBYN5mf3zh8XdrPJdwNvP7jJ0QackOwkTRGsV7IWH9xyFuEJhlstJ3P+ia6CDxgV6IzgbO8Lg8lMysclkDnYDuQIOh4574hs3AuPAe0sbm4waBn0ZYfLkL4oAPg65AB6ElojskS1r0HsOw/XPLzYHNJW7NXWjbYWxBbBTNConDff9RaywFtUVfYGqKfpeyXxrDakIc0tAjY3OJ6j8ODMJOawyAmWa8NSZBX9Hi3Mw6YsI86aeqRZJJET5JBIGpxyUlmdUb1X8cGISoXWVb6Ln82vVjwRQx1xpjUks0BTJfDjI+8jtBYO3g2znfdRZLJuW4NSGq/zCYHhmAy9Bd73fKbeBQLKXbeZYaLmN+mmhuHQnwO0EoL7AmRq2UROCXVe6GkmaZNeQZ/Hv2jOiKK1CgQCA/AGWn1wqvYMwJAAAAAElFTkSuQmCC>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACIAAAAXCAYAAABu8J3cAAABNklEQVR4Xu3TMSjEYRjH8YdOCIsiJJYrEQalDIaLbEYWZbNYJDFSRgZlNRhQyqIMilsMknSDUlJWo8kmA9+n54/3ngz633+g3l996n/P89z13HvvicTExMT8ndRiGB2+EaQeQ+jyjSySww4e8YR3lDAZzFRjGc84wDYO0R3MVJwlrCXP+o3n8Sq20CyqsItrdCZzmlaxZbRfcfQ0TnyRjOMFb9jHDZrKJiwzYrNfGUXxl07RaG+TXmwmzz4TYqeiRlzvMwNY9cU0yWPDF4Ncii1yhQbX0wxi3RfTRH8aPaWfMoVbHIkts4easgk7jWlXS51FrASvdbkF3ItdzjqciS2jS4+hWexfdCEZXVaNfpDek3Ns4QHHaA9m9CTmcCff90ZnWoKZzNKGAvpd3acPPb4YE/Nv8gHioDcivO0vOwAAAABJRU5ErkJggg==>
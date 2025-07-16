# tools/propose_tags.py

from nextcloud_client import NextCloudClient

import json

# Cargar etiquetas y definiciones desde archivo local (formato Markdown con secciones ## NombreEtiqueta)

def load_tags(md_path: str) -> dict:
    tags = {}
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_tag = None
    buffer = []

    for line in lines:
        if line.startswith('## '):
            if current_tag:
                tags[current_tag] = ''.join(buffer).strip()
                buffer = []
            current_tag = line.replace('## ', '').strip()
        elif current_tag:
            buffer.append(line)

    if current_tag and buffer:
        tags[current_tag] = ''.join(buffer).strip()

    return tags

# Prototipo simple de herramienta MCP
def propose_tags(title: str, file_path: str, tags_md_path: str) -> dict:
    """Propone etiquetas adecuadas para un título a partir de su contenido y una lista existente."""
    try:
        import ollama
    except ImportError:
        raise ImportError("El módulo ollama no está instalado. Instálalo con `pip install ollama`.")

    # 1. Leer contenido del libro
    client = NextCloudClient()
    text = client.read_text_file(file_path, max_chars=6000)
    print("⟶ Fragmento del contenido del libro extraído (primeras 1000 letras):")
    print(text[:1000])
    print("⟶ Fragmento del contenido del libro extraído:")
    print(text[:500])

    # 2. Cargar etiquetas existentes
    tags = load_tags(tags_md_path)
    print("⟶ Fragmento de las etiquetas existentes cargadas:")
    print(json.dumps(list(tags.keys())[:10], ensure_ascii=False, indent=2))
    tag_list = json.dumps([{"nombre": k, "descripcion": v} for k, v in tags.items()], ensure_ascii=False)

    # 3. Construir prompt
    prompt = f"""
Eres un modelo experto en análisis semántico y clasificación temática de textos espirituales y filosóficos.

A continuación tienes una lista de etiquetas existentes, cada una con su descripción. Deberás usarlas para etiquetar el siguiente libro. Si encuentras un tema claramente central que no esté cubierto por ninguna etiqueta existente, puedes proponer una nueva etiqueta, pero debes justificar su creación de forma explícita basándote en el contenido. Ignora completamente el nombre del autor o su estilo general: decide basándote solo en el contenido proporcionado.

{tag_list}

Tu tarea es proponer etiquetas relevantes para el siguiente libro:

Título: {title}

Contenido extraído:
{text}

Instrucciones:
- Usa únicamente etiquetas existentes, salvo que identifiques un tema claramente central no cubierto, la nueva etiqueta tiene potencial de aplicación a otros libros de la biblioteca y puedes justificar brevemente por qué es necesaria.
- Justifica toda nueva etiqueta de forma explícita y concisa.
- No uses comentarios fuera del JSON.
- Tu respuesta debe ser exclusivamente un objeto JSON válido con la siguiente estructura:

{{
  "etiquetas_existentes": ["..."] ,
  "etiquetas_nuevas": [ {{"nombre": "...", "justificacion": "..."}} ]
}}
"""

    # 4. Llamar al modelo con Ollama (Llama3 por ejemplo)
    try:
        output = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
    except Exception as e:
        return {"error": f"Error al ejecutar el modelo: {e}"}

    # 5. Extraer JSON
    try:
        content = output['message']['content']
        
        # Encuentra el primer '{' y el último '}' para aislar el objeto JSON.
        start = content.find('{')
        end = content.rfind('}') + 1
        
        if start != -1 and end != 0 and end > start:
            json_str = content[start:end]
            # Carga el JSON
            response = json.loads(json_str)
            return response
        else:
            # Si no se encuentra un JSON válido, devuelve un error.
            return {
                "error": "No valid JSON object found in the model's output.",
                "output": content
            }
    except Exception as e:
        return {
            "error": f"An exception occurred while parsing JSON: {e}",
            "output": output['message']['content'] if 'message' in output else str(output)
        }

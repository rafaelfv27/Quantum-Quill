import streamlit as st
import ollama
import time

def get_available_models():
    try:
        models = ollama.list()
        return [model['name'] for model in models['models']]
    except Exception as e:
        st.error(f"Error fetching models: {str(e)}")
        return []

def get_revision_prompt(language, text):
    if language == "English":
        return f"""
You will receive a text written in English by a non-native speaker. Your goal is to correct this text by making the following adjustments:

- Spelling correction: Fix any spelling errors.
- Grammatical adjustments: Reorganize sentences to ensure they make more grammatical sense.
- Add context and fluidity: Ensure that the text is clear and cohesive, and adjust any sentences that sound awkward or could cause confusion.
- Add connectives: Add connectives to make the text more cohesive and logical.
- Context and fluidity: Ensure that the text is clear and cohesive, and adjust any sentences that sound awkward or could cause confusion.
- Tone and style: Maintain the author's original writing style, but make it more natural and appropriate for a native English speaker.

{text}

Revised text:"""
    elif language == "Portuguese":
        return f"""Você receberá um texto escrito em inglês por uma pessoa que não é nativa da língua. Seu objetivo é corrigir esse texto, fazendo as seguintes alterações: 

- Correção ortográfica: Corrija quaisquer erros de grafia. 
- Ajustes gramaticais: Reorganize frases para que elas façam mais sentido gramaticalmente. 
- Adicione contexto e fluidez: Garanta que o texto esteja claro e coeso, e ajuste frases que soem desajeitadas ou que possam causar confusão.
- Adicione conectivos: Adicione conectivos para tornar o texto mais coeso e lógico.
- Contexto e fluidez: Verifique se o texto está claro e coeso, e ajuste frases que soem artificiais ou que possam causar confusão. 
- Tons e estilos: Mantenha o estilo de escrita original do autor, mas torne-o mais natural e apropriado para um falante nativo de inglês.:

{text}

Texto revisado:"""

def revise_scientific_text(text, model, language, timeout=60):
    prompt = get_revision_prompt(language, text)
    
    try:
        start_time = time.time()
        stream = ollama.generate(model=model, prompt=prompt, stream=True)
        
        response = ""
        for chunk in stream:
            response += chunk['response']
            yield response
            
            if time.time() - start_time > timeout:
                yield response + "\n\n[Response truncated due to timeout]"
                break
    except ollama._types.ResponseError as e:
        yield f"Error: {str(e)}. Please make sure the selected model is available."
    except Exception as e:
        yield f"An unexpected error occurred: {str(e)}"

st.title("Simplified Bilingual Scientific Text Revision App")

available_models = get_available_models()
if not available_models:
    st.error("No models found. Please make sure you have at least one model installed via Ollama.")
    st.stop()

default_model = "llama3.1:8b" if "llama3.1:8b" in available_models else available_models[0]
selected_model = st.selectbox("Select model:", available_models, index=available_models.index(default_model))

model_to_use = selected_model 
language = st.radio("Select revision language:", ["English", "Portuguese"])

timeout = st.slider("Timeout (seconds):", min_value=10, max_value=300, value=60, step=10)

user_input = st.text_area("Enter the scientific text you want to revise:", height=200)

if st.button("Revise Text"):
    if user_input:
        revision_placeholder = st.empty()
        for revised_text in revise_scientific_text(user_input, model_to_use, language, timeout):
            revision_placeholder.markdown(revised_text)
    else:
        st.warning("Please enter some text to revise.")

import streamlit as st
import spacy
from annotated_text import annotated_text
from PyPDF2 import PdfFileReader

@st.cache(show_spinner=False, allow_output_mutation=True, suppress_st_warning=True)
def load_models():
    french_model = spacy.load("./fr/")
    english_model = spacy.load("./en/")
    models = {"fr": french_model,"en": english_model}
    return models

def read_pdf(file):
	pdfReader = PdfFileReader(file)
	count = pdfReader.numPages
	all_page_text = ""
	for i in range(count):
		page = pdfReader.getPage(i)
		all_page_text += page.extractText()

	return all_page_text

def text_process(input, selected_entities,bool_anon=False):
    tokens = []
    for token in input:
        if (token.ent_type_ == "PERSON") & ("PER" in selected_entities):
            tokens.append((token.text, "Person", "#faa"))
        elif (token.ent_type_ in ["GPE", "LOC"]) & ("LOC" in selected_entities):
            tokens.append((token.text, "Location", "#fda"))
        elif (token.ent_type_ == "ORG") & ("ORG" in selected_entities):
            tokens.append((token.text, "Organization", "#afa"))
        else:
            tokens.append(" " + token.text + " ")
    
    if bool_anon:
        anonimized_tokens = []
        for token in tokens:
            if type(token) == tuple:
                #anonimized_tokens.append(("[REDACTED]"),token[1],token[2])
                anonimized_tokens.append(("[REDACTED]"))
            else:
                anonimized_tokens.append(token)
        return anonimized_tokens
    return tokens

    


models = load_models()

selected_language = st.sidebar.selectbox("Selectionnez une langue", options=["fr","en"])

selected_model=models[selected_language]

selected_entities = st.sidebar.multiselect(
    "Selectionez les entités à detecter",
    options=["LOC", "PER", "ORG"],
    default=["LOC", "PER", "ORG"],
)
st.title ('CV Anonyme - Oceanet')

text_input = st.text_area("Tapez un texte à anonimiser")

uploaded_file = st.file_uploader("ou Telechargez un fichier", type=["pdf", "txt"])
if uploaded_file is not None:
    if uploaded_file.type == 'txt':
        text_input = uploaded_file.getvalue()
        text_input = text_input.decode("utf-8")
    elif uploaded_file.type =="application/pdf":
        reader = PdfFileReader(uploaded_file)
        if reader.isEncrypted:
            reader.decrypt('')
        number_of_pages = reader.numPages
        page = reader.pages[0]
        text_input = page.extractText()

anonymize = st.checkbox("rendre anonyme")
input = selected_model(text_input)
tokens = text_process(input,selected_entities)

annotated_text(*tokens)

if anonymize:
    st.markdown("**Texte anonymisé**")
    st.markdown("---")
    anonymized_tokens = text_process(input, selected_entities, anonymize)
    annotated_text(*anonymized_tokens)

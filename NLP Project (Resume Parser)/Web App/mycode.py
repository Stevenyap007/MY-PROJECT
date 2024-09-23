import streamlit as st
import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
import json
from sklearn.model_selection import train_test_split
import sys
import fitz

# cv_data = json.load(open('Python/NLP/dataset.json', 'r'))


def load_ner_model():
    # Update this path to your local NER model path
    model_path = 'model/model/output/model-best'
    return spacy.load(model_path)


def main():
    st.title("Resume Parser Web App")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        st.subheader("Uploaded PDF Content:")
        file_buffer = uploaded_file.read()
        doc = fitz.open("pdf", file_buffer)
        text = " ".join(page.get_text("text") for page in doc)
        st.write(text)

        st.success('You have been upload a PDF!')

        st.subheader("Extracted Entities:")
        ner_model = load_ner_model()
        doc = ner_model(text)
        for ent in doc.ents:
            st.write(f"{ent.label_} = {ent.text}")
    


if __name__ == "__main__":
    main()


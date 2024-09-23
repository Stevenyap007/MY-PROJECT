from google.colab import drive
drive.mount('/content/drive')

import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
import json

cv_data = json.load(open('/content/drive/MyDrive/Colab Notebooks/ResumeParser/dataset.json', 'r'))

pip install tensorflow-gpu==2.8.0
python -m spacy init fill-config "/content/drive/MyDrive/Colab Notebooks/ResumeParser/config/base_config.cfg" "/content/drive/MyDrive/Colab Notebooks/ResumeParser/config/config.cfg"


def get_spacy_doc(file, data):
  nlp = spacy.blank("en")
  db = DocBin()

  for text, annot in tqdm(data):
    doc = nlp.make_doc(text)
    annot = annot['entities']

    ents = []
    entity_indices = []

    for start, end, label in annot:
      skip_entity = False
      for idx in range(start, end):
        if idx in entity_indices:
          skip_entity = True
          break
      if skip_entity == True:
        continue

      entity_indices = entity_indices + list(range(start, end))

      try:
        span = doc.char_span(start, end, label = label, alignment_mode = 'strict')
      except:
        continue

      if span is None:
        err_data = str([start, end]) + "    " + str(text) + "\n"
        file.write(err_data)

      else:
        ents.append(span)

    try:
      doc.ents = ents
      db.add(doc)

    except:
      pass

  return db

from sklearn.model_selection import train_test_split
train, test = train_test_split(cv_data, test_size = 0.3)

from sklearn.model_selection import train_test_split
train, test = train_test_split(cv_data, test_size = 0.3)

python -m spacy train '/content/drive/MyDrive/Colab Notebooks/ResumeParser/config/config.cfg' --output '/content/drive/MyDrive/Colab Notebooks/ResumeParser/model/output' --paths.train '/content/drive/MyDrive/Colab Notebooks/ResumeParser/model/train_data.spacy' --paths.dev '/content/drive/MyDrive/Colab Notebooks/ResumeParser/model/test_data.spacy' --gpu-id 0

nlp = spacy.load('/content/drive/MyDrive/Colab Notebooks/ResumeParser/model/output/model-best')

pip install PyMuPDF

import sys, fitz

fname = '/content/drive/MyDrive/Colab Notebooks/ResumeParser/test/picker.pdf'
doc = fitz.open(fname)

text = " "
for page in doc:
  text = text + str(page.get_text())

text
doc = nlp(text)
for ent in doc.ents:
  print(ent.text, "  ->>>>> ", ent.label_)
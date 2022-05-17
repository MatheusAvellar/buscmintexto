import os
import re
import xml.dom.minidom as dom
import logging
import nltk
import string
# Função local de limpar strings
from bmt_util import cleanup

if __name__ == "__main__":
  logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

STEMMER = False
LEIA = []
ESCREVA = ""

# Lê o arquivo de configuração, pega nomes de arquivos a serem lidos/criados
with open("../GLI.CFG", "r") as config_file:
  logging.info("Arquivo de configuração aberto")
  for line in config_file:
    if line.startswith("STEMMER"):
      # Se encontra STEMMER, liga a flag
      # Caso contrário, assume que NOSTEMMER está presente
      STEMMER = True
    elif line.startswith("LEIA="):
      _leia = line[5:].strip()
      LEIA.append(_leia)
      logging.info(f"Configuração 'LEIA': '{_leia}'")
    elif line.startswith("ESCREVA="):
      ESCREVA = line[8:].strip()
      logging.info(f"Configuração 'ESCREVA': '{ESCREVA}'")

words = {}

# Para cada arquivo definido na configuração
logging.info(f"Lendo {len(LEIA)} arquivos")
it = 0
succ = 0
for path in LEIA:
  # Lê arquivo XML
  xml_doc = dom.parse(path).documentElement
  all_records = xml_doc.getElementsByTagName("RECORD")
  # Para toda tag <RECORD>
  for record in all_records:
    # Assume que todo <RECORD> possui único <RECORDNUM>
    rnum = int(record.getElementsByTagName("RECORDNUM")[0].firstChild.nodeValue.strip())
    it += 1

    # Tenta pegar <ABSTRACT>
    all_stracts = record.getElementsByTagName("ABSTRACT")
    # Caso não possua <ABSTRACT>, pega <EXTRACT>
    if not all_stracts:
      all_stracts = record.getElementsByTagName("EXTRACT")

    if not all_stracts:
      logging.info(f"Documento '{rnum}' não possui ABSTRACT ou EXTRACT :(")
    else:
      succ += 1

    # Para cada texto descritivo (apelidado "stract"), provavelmente só 1 mesmo
    for stract in all_stracts:
      # Faz a arrumação normal, ';', etc
      text = cleanup(stract.firstChild.nodeValue, STEMMER)
      # Tokenização
      nltk_tokens = nltk.word_tokenize(text)
      # Remove pontuação
      # [Ref] https://stackoverflow.com/a/38734861/4824627
      tokens = [x for x in nltk_tokens if not re.fullmatch('[' + string.punctuation + ']+', x)]
      # Adiciona no dicionário de palavras encontradas
      for token in tokens:
        if token not in words:
          words[token] = []
        words[token].append(rnum)

logging.info(f"Processados {it} registros, dos quais {succ} tinham conteúdo")
logging.info(f"Escrevendo {len(words)} linhas no arquivo de ESCREVA")
# Escreve palavras no arquivo de lista invertida
with open(ESCREVA, "w") as file:
  for key in words:
    file.write(f"{key};{words[key]}\n")
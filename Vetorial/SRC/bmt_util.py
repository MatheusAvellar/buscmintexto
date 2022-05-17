import re
import unicodedata
# porter.py
from porter import PorterStemmer

# Função que transforma strings "bagunçadas" em texto ASCII
# sem acentos, sem whitespace duplo, sem ';', todo em maiúsculas
def cleanup(string, use_stemmer):
  # Remove separadores ';', espaço em branco repetido e em volta
  stripped = re.sub("\s{2,}", " ", string).replace(";", "").strip()
  # Remove acentos, converte para minúsculas
  # [Ref] https://stackoverflow.com/a/517974
  nfkd_form = unicodedata.normalize("NFKD", stripped)
  lower_ascii = nfkd_form.encode("ASCII", "ignore").decode("utf-8").lower()
  # Se não precisa de stemmer, retorna
  if not use_stemmer:
    return lower_ascii

  # Caso contrário, faz stemming
  stemmer = PorterStemmer()
  output = []
  word = ""
  # Para cada caracter
  for character in lower_ascii:
    # Se é letra, adiciona na palavra
    if character.isalpha():
      word += character.lower()
    else:
      # Caso contrário, se já temos alguma palavra formada
      if word:
        # Faz stemming, e adiciona no output
        output.append(stemmer.stem(word, 0,len(word)-1))
        word = ""
      # Adiciona então o caractere não-letra no output
      output.append(character.lower())
  # Retorna o resultado
  return "".join(output)
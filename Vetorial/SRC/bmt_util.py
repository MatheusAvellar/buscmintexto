import re
import unicodedata

# Função que transforma strings "bagunçadas" em texto ASCII
# sem acentos, sem whitespace duplo, sem ';', todo em maiúsculas
def cleanup(string):
  # Remove separadores ';', espaço em branco repetido e em volta
  stripped = re.sub("\s{2,}", " ", string).replace(";", "").strip()
  # Remove acentos
  # [Ref] https://stackoverflow.com/a/517974
  nfkd_form = unicodedata.normalize("NFKD", stripped)
  only_ascii = nfkd_form.encode("ASCII", "ignore").decode("utf-8")
  # Retorna texto em maiúsculas
  return only_ascii.upper()
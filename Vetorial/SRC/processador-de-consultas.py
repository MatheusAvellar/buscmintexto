import os
import re
import xml.dom.minidom as dom
import logging
# Função local de limpar strings
from bmt_util import cleanup

if __name__ == "__main__":
  logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

def get_votes(score_attr):
  # Conta votos não-0 de uma string
  # e.g.: "0101"->2, "2121"->4
  return len(score_attr.replace("0", ""))

LEIA = ""
CONSULTAS = ""
ESPERADOS = ""

# Lê o arquivo de configuração, pega nomes de arquivos a serem lidos/criados
with open("../PC.CFG", "r") as config_file:
  logging.info("Arquivo de configuração aberto")
  for line in config_file:
    if line.startswith("LEIA="):
      LEIA = line[5:].strip()
      logging.info(f"Configuração 'LEIA': '{LEIA}'")
    elif line.startswith("CONSULTAS="):
      CONSULTAS = line[10:].strip()
      logging.info(f"Configuração 'CONSULTAS': '{CONSULTAS}'")
    elif line.startswith("ESPERADOS="):
      ESPERADOS = line[10:].strip()
      logging.info(f"Configuração 'ESPERADOS': '{ESPERADOS}'")

consultas_str = []
esperados_str = []

# Lê arquivo XML
xml_doc = dom.parse(LEIA).documentElement
# Pega todas as tags <QUERY>
all_queries = xml_doc.getElementsByTagName("QUERY")
logging.info(f"Encontrado {len(all_queries)} tags <QUERY> no XML")
# Para toda tag <QUERY>
for query in all_queries:
  # Assume que existe somente 1 <QueryNumber> e 1 <QueryText> dentro
  # Pega o texto deles
  query_number = query.getElementsByTagName("QueryNumber")[0].firstChild.nodeValue
  text = cleanup(query.getElementsByTagName("QueryText")[0].firstChild.nodeValue)
  consultas_str.append(f"{query_number};{text}")

  # Para cada <Records> dessa <QUERY> (deve ter só um)
  for record in query.getElementsByTagName("Records"):
    # Para cada <Item>
    for item in record.getElementsByTagName("Item"):
      # Pega o texto dele
      doc_number = item.firstChild.nodeValue
      # Pega o valor do atributo 'score'
      doc_votes = get_votes(item.getAttribute("score"))
      esperados_str.append(f"{query_number};{doc_number};{doc_votes}")

logging.info(f"Escrevendo {len(consultas_str)} linhas no arquivo de CONSULTAS")
# Escreve o arquivo de consultas
with open(CONSULTAS, "w") as file:
  file.write("QueryNumber;QueryTexto\n")
  file.write("\n".join(consultas_str))

logging.info(f"Escrevendo {len(esperados_str)} linhas no arquivo de ESPERADOS")
# Escreve o arquivo de esperados
with open(ESPERADOS, "w") as file:
  file.write("QueryNumber;DocNumber;DocVotes\n")
  file.write("\n".join(esperados_str))

import json
from docx import Document

def docx_para_json(caminho_arquivo_docx, caminho_arquivo_json):
    # Carrega o documento .docx
    doc = Document(caminho_arquivo_docx)
    
    # Estrutura para armazenar as questões extraídas
    questoes = []

    # Inicializa uma variável para armazenar a questão atual
    questao = {}
    enunciado_partes = []
    nova_questao_encontrada = False

    for paragrafo in doc.paragraphs:
        texto = paragrafo.text.strip()

        # Ignora parágrafos vazios
        if not texto:
            continue

        # Detecta o início de uma nova questão
        if texto == "### Nova Questão":
            # Se houver uma questão atual sendo montada, adiciona ao array de questões
            if nova_questao_encontrada:
                questao["enunciado"] = enunciado_partes
                questoes.append(questao)

            # Reinicia as variáveis para a nova questão
            questao = {}
            enunciado_partes = []
            nova_questao_encontrada = True
            continue

        # Identifica e armazena os diferentes campos
        if texto.startswith("Matéria:"):
            questao["materia"] = texto.replace("Matéria:", "").strip()
        elif texto.startswith("Assunto:"):
            questao["assunto"] = texto.replace("Assunto:", "").strip()
        elif texto.startswith("Dificuldade:"):
            questao["dificuldade"] = int(texto.replace("Dificuldade:", "").strip())
        elif texto.startswith("Explicação:"):
            questao["explicacao"] = texto.replace("Explicação:", "").strip()
        elif texto.startswith("A)"):
            questao["alternativa_a"] = texto[2:].strip()
        elif texto.startswith("B)"):
            questao["alternativa_b"] = texto[2:].strip()
        elif texto.startswith("C)"):
            questao["alternativa_c"] = texto[2:].strip()
        elif texto.startswith("D)"):
            questao["alternativa_d"] = texto[2:].strip()
        elif texto.startswith("E)"):
            questao["alternativa_e"] = texto[2:].strip()
        elif texto.startswith("Correta:"):
            questao["alternativa_correta"] = texto.replace("Correta:", "").strip()
        elif texto.startswith("Imagem:"):
            # Adiciona uma imagem como parte do enunciado
            imagem_url = texto.replace("Imagem:", "").strip()
            enunciado_partes.append({"tipo": "imagem", "conteudo": imagem_url})
        else:
            # Adiciona qualquer outro texto como parte do enunciado
            enunciado_partes.append({"tipo": "texto", "conteudo": texto})

    # Adiciona a última questão ao array de questões
    if nova_questao_encontrada:
        questao["enunciado"] = enunciado_partes
        questoes.append(questao)

    # Salva as questões em um arquivo JSON
    with open(caminho_arquivo_json, 'w', encoding='utf-8') as json_file:
        json.dump(questoes, json_file, ensure_ascii=False, indent=4)

    print(f"Conteúdo salvo em {caminho_arquivo_json}")

# Caminhos dos arquivos
caminho_arquivo_docx = 'data/questoes.docx'
caminho_arquivo_json = 'data/resultado.json'

# Chama a função para converter o documento
docx_para_json(caminho_arquivo_docx, caminho_arquivo_json)

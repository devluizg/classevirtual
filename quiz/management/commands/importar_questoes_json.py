from django.core.management.base import BaseCommand
from quiz.models import Materia, Assunto, Questao
import json

class Command(BaseCommand):
    help = 'Importa questões de um arquivo JSON com suporte a imagens intercaladas no enunciado'

    def handle(self, *args, **kwargs):
        caminho_arquivo = 'data/resultado.json'

        with open(caminho_arquivo, 'r', encoding='utf-8') as file:
            questoes = json.load(file)

        for questao_data in questoes:
            # Cria ou obtém a matéria e o assunto
            materia, _ = Materia.objects.get_or_create(nome=questao_data['materia'])
            assunto, _ = Assunto.objects.get_or_create(nome=questao_data['assunto'], materia=materia)

            # Monta o enunciado com imagens e texto intercalados
            enunciado_html = ""
            for parte in questao_data['enunciado']:
                if parte['tipo'] == 'texto':
                    enunciado_html += f"<p>{parte['conteudo']}</p>"
                elif parte['tipo'] == 'imagem':
                    enunciado_html += f'<img src="{parte["conteudo"]}" alt="Imagem da questão" style="max-width: 100%; height: auto;">'

            # Cria a questão no banco de dados
            Questao.objects.create(
                enunciado=enunciado_html.strip(),
                alternativa_a=questao_data['alternativa_a'],
                alternativa_b=questao_data['alternativa_b'],
                alternativa_c=questao_data['alternativa_c'],
                alternativa_d=questao_data['alternativa_d'],
                alternativa_e=questao_data['alternativa_e'],
                alternativa_correta=questao_data['alternativa_correta'],
                materia=materia,
                assunto=assunto,
                dificuldade=questao_data['dificuldade'],
                explicacao=questao_data.get('explicacao', '')
            )

        self.stdout.write(self.style.SUCCESS('Questões importadas com sucesso'))

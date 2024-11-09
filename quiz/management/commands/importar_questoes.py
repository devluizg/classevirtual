from django.core.management.base import BaseCommand
from quiz.models import Materia, Assunto, Questao
import pandas as pd
import logging
from typing import Dict, Optional, List, Tuple
from difflib import get_close_matches
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Importa questões de um arquivo Excel para o banco de dados'

    def add_arguments(self, parser):
        parser.add_argument('arquivo_excel', type=str, help='Caminho para o arquivo Excel')

    def setup_logger(self):
        logger = logging.getLogger('question_importer')
        logger.setLevel(logging.INFO)
        
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        fh = logging.FileHandler(f'logs/import_{timestamp}.log')
        fh.setLevel(logging.INFO)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger

    def normalize_dificuldade(self, value: str) -> Optional[int]:
        # Mapeamento para converter valores textuais de dificuldade para números
        dificuldade_map = {
            'fácil': 1,
            'facil': 1,
            'médio': 2,
            'medio': 2,
            'difícil': 3,
            'dificil': 3
        }
        
        normalized = value.lower().strip()
        return dificuldade_map.get(normalized)

    def validate_question(self, row: Dict, index: int) -> List[Dict]:
        errors = []
        
        required_fields = ['enunciado', 'alternativa_a', 'alternativa_b', 'alternativa_c', 
                           'alternativa_d', 'alternativa_e', 'resposta_correta', 'materia', 
                           'assunto', 'dificuldade']
                         
        for field in required_fields:
            if field not in row or pd.isna(row[field]) or str(row[field]).strip() == '':
                errors.append({
                    'linha': index + 2,
                    'campo': field,
                    'valor': 'vazio',
                    'mensagem': f'Campo obrigatório {field} está vazio'
                })
                
        if 'dificuldade' in row and not pd.isna(row['dificuldade']):
            dificuldade_value = str(row['dificuldade'])
            dificuldade_norm = self.normalize_dificuldade(dificuldade_value)
            
            if dificuldade_norm is None:
                errors.append({
                    'linha': index + 2,
                    'campo': 'dificuldade',
                    'valor': dificuldade_value,
                    'mensagem': 'Valor de dificuldade inválido',
                    'sugestao': 'Use valores como "Fácil", "Médio" ou "Difícil"'
                })
                
        if 'resposta_correta' in row and not pd.isna(row['resposta_correta']):
            resposta = str(row['resposta_correta']).strip().upper()
            if resposta not in ['A', 'B', 'C', 'D', 'E']:
                errors.append({
                    'linha': index + 2,
                    'campo': 'resposta_correta',
                    'valor': resposta,
                    'mensagem': 'Resposta correta deve ser A, B, C, D ou E'
                })
                
        return errors

    def import_question(self, row: Dict) -> bool:
        try:
            dificuldade_num = self.normalize_dificuldade(str(row['dificuldade']))
            
            if dificuldade_num is None:
                raise ValueError(f"Dificuldade inválida para a questão: {row['enunciado']}")
            
            materia, _ = Materia.objects.get_or_create(nome=row['materia'])
            assunto, _ = Assunto.objects.get_or_create(nome=row['assunto'], materia=materia)
            
            questao = Questao.objects.create(
                enunciado=row['enunciado'],
                materia=materia,
                assunto=assunto,
                dificuldade=dificuldade_num,
                alternativa_a=row['alternativa_a'],
                alternativa_b=row['alternativa_b'],
                alternativa_c=row['alternativa_c'],
                alternativa_d=row['alternativa_d'],
                alternativa_e=row['alternativa_e'],
                alternativa_correta=row['resposta_correta'],
                explicacao=row.get('explicacao', '')
            )
            
            return True
        except Exception as e:
            self.logger.error(f"Erro ao importar questão: {str(e)}")
            return False

    def handle(self, *args, **options):
        self.logger = self.setup_logger()
        arquivo_excel = options['arquivo_excel']
        
        try:
            df = pd.read_excel(arquivo_excel)
            total_rows = len(df)
            success_count = 0
            error_count = 0
            
            self.logger.info(f"Iniciando importação de {total_rows} questões...")
            
            for index, row in df.iterrows():
                errors = self.validate_question(row, index)
                
                if errors:
                    error_count += 1
                    for error in errors:
                        msg = f"Linha {error['linha']}: {error['mensagem']} - Campo '{error['campo']}' com valor '{error['valor']}'"
                        if 'sugestao' in error:
                            msg += f" (Sugestão: '{error['sugestao']}')"
                        self.logger.warning(msg)
                else:
                    if self.import_question(row):
                        success_count += 1
                    else:
                        error_count += 1
            
            self.logger.info("\n=== Resumo da Importação ===")
            self.logger.info(f"Total de questões processadas: {total_rows}")
            self.logger.info(f"Questões importadas com sucesso: {success_count}")
            self.logger.info(f"Questões com erro: {error_count}")
            
            self.stdout.write(
                self.style.SUCCESS(f'Importação concluída. {success_count} questões importadas com sucesso.')
            )
            
        except Exception as e:
            self.logger.error(f"Erro durante a importação: {str(e)}")
            raise

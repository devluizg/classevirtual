import pandas as pd

# Dados de exemplo para questões
dados_questoes = {
    'enunciado': [
        'Qual é o maior planeta do Sistema Solar?',
        'Qual é a capital do Brasil?',
        'Quem escreveu "Dom Casmurro"?',
        'Quanto é 8 x 7?',
        'Qual é o símbolo químico do Ouro?'
    ],
    'alternativa_a': [
        'Marte',
        'Rio de Janeiro',
        'José de Alencar',
        '54',
        'Ag'
    ],
    'alternativa_b': [
        'Júpiter',
        'São Paulo',
        'Machado de Assis',
        '56',
        'Au'
    ],
    'alternativa_c': [
        'Saturno',
        'Brasília',
        'Lima Barreto',
        '58',
        'Cu'
    ],
    'alternativa_d': [
        'Urano',
        'Salvador',
        'Jorge Amado',
        '60',
        'Fe'
    ],
    'alternativa_e': [
        'Netuno',
        'Recife',
        'Graciliano Ramos',
        '62',
        'Pt'
    ],
    'resposta_correta': [
        'B',
        'C',
        'B',
        'B',
        'B'
    ],
    'materia': [
        'Ciências',
        'Geografia',
        'Literatura',
        'Matemática',
        'Química'
    ],
    'assunto': [
        'Sistema Solar',
        'Geografia do Brasil',
        'Literatura Brasileira',
        'Multiplicação',
        'Tabela Periódica'
    ],
    'dificuldade': [
        'Fácil',
        'Fácil',
        'Médio',
        'Fácil',
        'Médio'
    ],
    'explicacao': [
        'Júpiter é o maior planeta do Sistema Solar, com um diâmetro de aproximadamente 139.820 km.',
        'Brasília é a capital federal do Brasil desde 21 de abril de 1960.',
        'Machado de Assis escreveu Dom Casmurro, publicado em 1899.',
        '8 x 7 = 56, uma das multiplicações básicas da tabuada.',
        'Au (Aurum em latim) é o símbolo químico do elemento Ouro.'
    ],
    'url_imagem': [
        'https://exemplo.com/jupiter.jpg',
        'https://exemplo.com/brasilia.jpg',
        '',
        '',
        'https://exemplo.com/ouro.jpg'
    ]
}

# Criar DataFrame
df = pd.DataFrame(dados_questoes)

# Salvar como Excel
df.to_excel('questoes_exemplo.xlsx', index=False)

print("Planilha de exemplo criada com sucesso!")
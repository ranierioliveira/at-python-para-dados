import pandas as pd
import json 
import urllib.request
import requests 
from bs4 import BeautifulSoup 

def exibir_menu():
  print("\n----------------------------------------")
  print("Escolha uma opção: ")
  print("1 - Exibir plataformas")
  print("2 - Exibir lista das urls válidas")
  print("3 - Exibir título das páginas válidas")
  print("4 - Informações de jogos das páginas:")
  print("5 - Converte jogos por plataformas em Json")
  print("6 - Lista amigos exclusivos")
  print("12 - Encerrar escolha de opções")

controle_de_id = 1

def carregar_dados():
    global controle_de_id #usado para coloar um id 
    '''
    Carrega o arquivo json e preenche alguns campos
    
    Retorna uma lista de dicionários
    '''
    with open('INFwebNet_Data.json', 'r', encoding='utf-8') as arquivo_json:
        dados = json.load(arquivo_json)
        for dado in dados:
            if dado['id'] == '':
                dado['id'] = controle_de_id
                controle_de_id += 1  
    df_dados = pd.DataFrame(dados)
    df_dados_formatados = df_dados.fillna('Não informado')
    return df_dados_formatados
           
def converte_para_tuplas(df):
    '''
    A partir do df coloca os jogos em tuplas
    
    Parâmetro:
    df (df): df com as informações dos usuários
    
    Retorna:
    jogos_convertidos (list): uma lista de tuplas
    '''
    jogos_convertidos = []
    jogos_lista = df['jogos'].tolist() #converte os jogos em lista
    
    for linha in jogos_lista:
        linha = str(linha)
        linha = linha.strip('[]') #remove os colchetes
        if linha: 
            linha = linha.replace("\'", '')#tira as aspas
            nova_lista = linha.split('), (')#dá um split a partir dos separadores
            for item in nova_lista:
                #De cada elemento a partir do split, vai 'limpar', separar e converter para tuplas
                item = item.replace('(', '').replace(')', '')
                elementos = item.split(', ')
                if len(elementos) == 2: #verifica se tem dois elementos 
                    jogos_convertidos.append(tuple(elementos))  #Adiciona como tupla na lista final
                else:
                    print(f"Formato inesperado: {item}")
    return jogos_convertidos
        
        
           
def extracao_plataformas(df):
    '''
    Extrai do df as plataformas de jogos
    
    Parâmetros:
    df (df): df com as informações dos usuários
    
    Retorna:
    plataformas (set): set com o nome das plataformas
    '''
    jogos_convertidos = converte_para_tuplas(df)
   
    plataformas = set() 
    
    for _, plataforma in jogos_convertidos:
        plataformas.add(plataforma)
    return plataformas

def gera_arquivo_txt(set, nome_arquivo):
    '''
    Escreve cada elementodo set em uma linha de um arquivo
    
    Parâmetros:
    set (set): set com as plataformas
    nome_arquivo (str): nome do arquivo onde var ser gravada as informações
    
    Retorna:
    Escreve o nome das plataformas em uma linha diferente do arq.
    '''
    with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
        for elemento in set:
            arquivo.write(elemento + '\n')
           
def carregar_plataformas(nome_arquivo):
    '''
    Retorna as plataformas armazenado no arquivo
    
    Parâmetro:
    nome_arquivo (str): nome do arquivo onde foi gravada as plataformas
    
    Retorna: 
    Retorna a lista ou none caso o caminho especificado não tenha o arquivo e o usuário deseje sair

    '''
    while True:
        try:
            with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
                plataformas = [linha.strip() for linha in arquivo.readlines()]
                return plataformas
        except FileNotFoundError:
            print(f"Arquivo {nome_arquivo} não encontrado")
            opcao = input("Digite o caminho correto ou 'sair' para encerrar o programa: '").strip().lower()
            if opcao == 'sair':
                print('Encerrando o programa...')
                return None
            nome_arquivo = opcao #serve para atualizar o caminho onde var ser procurado
        
def baixar_paginas_wikipedia(plataformas):
    '''
    Verifica se há listas de jogos para plataformas no wikipédia
    
    Parâmetros:
    plataforamas (list): lista das plataformas
    
    Retorna: 
    A lista com as urls válidas, além de criar html para as páginas existentes e criar um arquivo com as urls que não foram válidas
    '''
    urls = []
    erros_url = []
    for plataforma in plataformas:
        plataforma_formatada = plataforma.replace(' ', '_').strip()
        url = f'https://pt.wikipedia.org/wiki/Lista_de_jogos_para_{plataforma_formatada}'
        
        try:
            #requisição do página
            resposta = urllib.request.urlopen(url)
            html = resposta.read().decode('utf-8')
            nome_arquivo = f'plataforma_{plataforma_formatada.lower()}.html'

            with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
                arquivo.write(html)
                urls.append(url)
        
        except (urllib.error.HTTPError, urllib.error.URLError):
            print(f"Erro ao tentar acessar '{url}'")
            erros_url.append(url)
            
            with open ('erros_download.txt', 'w', encoding='utf-8') as arquivo:
                for erro_url in erros_url:
                    arquivo.write(erro_url + '\n')
        except Exception:
            print(f"Erro inesperado")       
            
    return urls    

def parsear_paginas(urls, plataformas):
    '''
    Pega o título das páginas urls
    
    Parâmetros:
    urls (list): lista das urls válidas
    plataformas (list): lista das plataformas 
    
    Retorna:
    titulos (list): lista com os títulos das páginas
    '''
    titulos = []
    plataformas_formatadas = [plataforma.lower() for plataforma in plataformas]
    for url in urls:
        resposta = requests.get(url)
        conteudo = resposta.content
        site = BeautifulSoup(conteudo, 'html.parser')
        
        titulo = site.find('span', attrs={'class': 'mw-page-title-main'})
        
        if titulo:
            titulo_formatado = titulo.text.lower()
            titulos.append(titulo.text)
            
            plataforma_encontrada = False
            for plataforma in plataformas_formatadas:
                if plataforma in titulo_formatado:
                    plataforma_encontrada = True
                    break
            if not plataforma_encontrada:
                with open('erros_parse.txt', 'a', encoding='utf-8') as arquivo:
                    arquivo.write(f"Erro: Plataforma não encontrada no título da página {url}.\n")
    return titulos    
        
def informacao_dos_jogos(urls):
    '''
    Retorna uma lista de dicionários contendo os jogos das plataformas
    
    Parâmetros:
    urls (lista): Lista de dicionários
    
    Retorna:
    dados (list): uma lista de dicionários com os jogos das plataformas
    '''
    plataformas_por_jogo = []
    plataformas = extrai_nome_plataformas_com_url_validas(urls)
    dados = []
    
    for url in urls:
        resposta = requests.get(url)
        conteudo = resposta.content
        site = BeautifulSoup(conteudo, 'html.parser')
            
        tabela = site.find('table', attrs={'class': 'wikitable'})
        
        if tabela:
            jogos = []
            for tr in tabela.find_all('tr')[1:]:
                colunas = tr.find_all('td')
                
                if len(colunas) >= 4:
                    nome_jogo = colunas[0].text.strip()
                    desenvolvedora = colunas[1].text.strip()
                    publicadora = colunas[2].text.strip()

                    jogo = {"nome_jogo": nome_jogo,
                            "dados_jogo": {
                        "desenvolvedora": desenvolvedora,
                        "publicadora": publicadora,
                    }}
                    jogos.append(jogo)  
            dados.append(jogos)   
    
    for i in range(len(plataformas)):
        informacao_plataforma = {"plataforma": plataformas[i], "jogos": dados[i]}
        plataformas_por_jogo.append(informacao_plataforma)
        
    return plataformas_por_jogo

def extrai_nome_plataformas_com_url_validas(urls_plataformas):
    '''
    Extrai o nome das plataformas a partir das urls
    
    Parâmetros:
    urls_plataformas (list): lista com o nome das plataformas
    
    Retorna:
    nome_plataformas_validas (list): lista com o nome das plataformas
    '''
    nome_plataformas_validas = []
    for plataforma in urls_plataformas:
        nome_platoforma = plataforma.split('para_')
        nome_platoforma_formatado = nome_platoforma[1].replace("_", " ")
        nome_plataformas_validas.append(nome_platoforma_formatado)
    return nome_plataformas_validas
          
def exportar_dados_jogos(jogos_plataformas):
    '''
    Converter dicionário com as informações dos jogos por plataforma em json
    
    Parâmetros:
    jogos_plataformas (dict): dicionários com as informações dos jogos por plataforma
    
    Retorna:
    Converte as informações em um arquivo json
    '''
    with open('dados_jogos_plataforma.json', 'w', encoding='utf-8') as arquivo_json:
        json.dump(jogos_plataformas, arquivo_json, ensure_ascii=False, indent=4)


dados_usuarios = carregar_dados()
plataformas = extracao_plataformas(dados_usuarios)
gera_arquivo_txt(plataformas, 'plataformas.txt')
plataformas = carregar_plataformas('plataformas.txt')
urls_validas = baixar_paginas_wikipedia(plataformas)
jogos_por_plataforma = informacao_dos_jogos(urls_validas)

while True:
    exibir_menu()
    opcao = input("\nDigite o número da opção escolhida: ").lower().strip()
    if opcao == "1":
        print('')
        for plataforma in plataformas:
            print(plataforma)
        print('')
    elif opcao == "2":
        print('')
        for url_valida in urls_validas:
            print(url_valida)
        print('')
    elif opcao == "3":
        titulos_das_paginas = parsear_paginas(urls_validas, plataformas)
        print(titulos_das_paginas)
    elif opcao == "4":
        for plataforma in jogos_por_plataforma:
            print(plataforma)
            print("")
    elif opcao == "5":
        exportar_dados_jogos(jogos_por_plataforma)
    elif opcao == "12":
        print("\nMenu encerrado!")
        break
    else: 
        print("\nEscolha errada, tente novamente!\n")    
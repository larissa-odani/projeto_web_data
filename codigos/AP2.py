# dupla: Larissa Mayumi Odani e Leonardo Moiano Lima

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd
import re
import os

# Configurações iniciais
navegador = webdriver.Chrome()
navegador.get('https://www.mistral.com.br/especiais/best-buys')
time.sleep(2)

# Aceita modal de boas-vindas
try:
    botao_aceitar = navegador.find_element(By.XPATH, '//*[@id="pg-modal-bemvindo"]/div/a[1]')
    botao_aceitar.click()
    time.sleep(1)
except NoSuchElementException:
    print("Modal de boas-vindas não encontrado.")

# Aceita cookies
try:
    botao_aceitar_cookies = navegador.find_element(By.XPATH, '//*[@id="lgpd-cookies"]/div/a')
    botao_aceitar_cookies.click()
    time.sleep(1)
except NoSuchElementException:
    print("Botão de cookies não encontrado.")

# Aplica filtro
try:
    botao_filtro = navegador.find_element(By.XPATH, '//*[@id="selectOrdem"]')
    botao_filtro.click()
    time.sleep(0.5)
    menor = navegador.find_element(By.XPATH, '//*[@id="selectOrdem"]/option[2]')
    menor.click()
    time.sleep(2)
except NoSuchElementException:
    print("Filtro de ordenação não encontrado.")

# Coletar produtos
lista_produtos = []
for produto in range(0, 35):
    try:
        xpath = f'/html/body/div[14]/section/article[2]/div[1]/div/div[{produto}]/div[2]/div[4]/a/h2'
        dado_produto = navegador.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        try:
            xpath = f'/html/body/div[15]/section/article[2]/div[1]/div/div[{produto}]/div[2]/div[4]/a/h2'
            dado_produto = navegador.find_element(By.XPATH, xpath).text
        except NoSuchElementException:
            continue
    if dado_produto:
        lista_produtos.append(dado_produto)

# Coletar ml
lista_ml = []
for ml in range(0, 35):
    try:
        xpath = f'/html/body/div[14]/section/article[2]/div[1]/div/div[{ml}]/div[2]/div[2]/p'
        texto = navegador.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        try:
            xpath = f'/html/body/div[15]/section/article[2]/div[1]/div/div[{ml}]/div[2]/div[2]/p'
            texto = navegador.find_element(By.XPATH, xpath).text
        except NoSuchElementException:
            continue
    numeros = re.findall(r'\d+', texto)
    if numeros:
        lista_ml.append(int(numeros[0]))

# Coletar preços
lista_precos = []
for preco in range(0, 35):
    try:
        xpath = f'/html/body/div[14]/section/article[2]/div[1]/div/div[{preco}]/div[2]/div[4]/a/p[4]'
        texto = navegador.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        try:
            xpath = f'/html/body/div[15]/section/article[2]/div[1]/div/div[{preco}]/div[2]/div[4]/a/p[4]'
            texto = navegador.find_element(By.XPATH, xpath).text
        except NoSuchElementException:
            continue
    numeros = re.findall(r'\d+', texto)
    if numeros:
        lista_precos.append(float(numeros[0]))

# Coletar parcelas
lista_parcela = []
for parcela in range(0, 35):
    try:
        xpath = f'/html/body/div[14]/section/article[2]/div[1]/div/div[{parcela}]/div[2]/div[4]/p/b[1]'
        dado_parcela = navegador.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        try:
            xpath = f'/html/body/div[15]/section/article[2]/div[1]/div/div[{parcela}]/div[2]/div[4]/p/b[1]'
            dado_parcela = navegador.find_element(By.XPATH, xpath).text
        except NoSuchElementException:
            continue
    numero_parcela = re.findall(r'\d+', dado_parcela)
    if numero_parcela:
        lista_parcela.append(numero_parcela[0])

# Criando DataFrames
tabela1 = pd.DataFrame(lista_produtos, columns=['Produto'])
tabela2 = pd.DataFrame(lista_ml, columns=['Volume (ML)'])
tabela3 = pd.DataFrame(lista_precos, columns=['Precos'])
tabela4 = pd.DataFrame(lista_parcela, columns=['Parcela'])

df_original = pd.concat([tabela1, tabela2, tabela3, tabela4], axis=1)
os.makedirs('../bases_originais', exist_ok=True)
df_original.to_csv('../bases_originais/dados_brutos.csv', sep=';', index=True, encoding='UTF-8')

df = df_original.copy()
df.fillna(0, inplace=True)

# Tratando duplicatas
df = df.drop_duplicates()

# Tratando outliers
df.loc[df['Precos'] > 999, 'Precos'] = 999
df.loc[df['Precos'] < 0, 'Precos'] = 0

os.makedirs('../bases_tratadas', exist_ok=True)
df.to_csv('../bases_tratadas/dados_tratados.csv', sep=';', index=True, encoding='UTF-8')

# Encerra o navegador
navegador.quit()

print("Coleta e tratamento finalizados com sucesso!")
import sys
import os
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import json
import time
import logging
from contextlib import contextmanager

# Configura o nível de log para suprimir mensagens do DevTools
LOGGER.setLevel(logging.WARNING)

@contextmanager
def suppress_output():
    print("==== Iniciando a supressão ====")
    """Suprime saídas padrão e de erro temporariamente."""
    devnull = "nul" if os.name == "nt" else "/dev/null"
    with open(devnull, "w") as devnull_file:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull_file
        sys.stderr = devnull_file
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

def configure_chrome_service():
    """Configura o serviço do Chrome para redirecionar logs."""
    service = Service(ChromeDriverManager().install())
    if os.name == "nt":
        service.creationflags = 0x08000000  # CREATE_NO_WINDOW para Windows
    else:
        service.log_output = "nul" if os.name == "nt" else "/dev/null"
    return service

def get_driver():
    """Configura e retorna o driver do Chrome com saída redirecionada."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = configure_chrome_service()
    return webdriver.Chrome(service=service, options=chrome_options)

def get_global_500_data():
    url = "https://fortune.com/api/getRankingSearchYear/global500/2024/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            items_data = data.get("items", [])
            return items_data
        else:
            print(f"Erro ao acessar a API Fortune. Código: {response.status_code}")
            return []
    except Exception as e:
        print(f"Erro ao obter dados da Fortune: {e}")
        return []

def search_company_on_globaldata(company_name):
    search_url = f"https://www.globaldata.com/search/index/?SearchText={company_name}"
    with suppress_output():
        driver = get_driver()

    try:
        driver.get(search_url)
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="TableView001"]/tbody/tr[1]/td[1]/a')))
        company_slug = element.text # element.get_attribute("href").split("/")[-1]
        company_label = element.text
        if company_slug:
            company_slug = company_slug.replace(" ", "-")
        return company_slug, company_label
    except Exception as e:
        print(f"Erro ao buscar empresa '{company_name}' no GlobalData: {e}")
        page_source = driver.page_source
        print("Fonte da página carregada:", page_source[:500])  # Mostra os primeiros 500 caracteres da página
        return None, None
    finally:
        driver.quit()

def get_locations_from_globaldata(company_slug):
    url = f"https://www.globaldata.com/company-profile/{company_slug}/locations/?utm_source=chatgpt.com"
    with suppress_output():
        driver = get_driver()

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        locations_element = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/main/div[4]/div/div[2]/div[2]/div[4]/div')))
        locations = locations_element.text.split('\n')
        return locations
    except Exception as e:
        print(f"Erro ao obter localizações para '{company_slug}': {e}")
        return []
    finally:
        driver.quit()

def integrate_scraping():
    global_500_data = get_global_500_data()
    combined_data = []

    for company in global_500_data:
        company_name = company.get("name")  # Corrigido para buscar o nome correto
        if not company_name:
            print(f"Empresa sem nome encontrado: {company}")
            company_name = "Unknown Company"

        print(f"Processando empresa: {company_name}")

        company_slug, company_label = search_company_on_globaldata(company_name)

        if company_slug:
            # Substituir espaços em branco no company_slug por '-'
            company_slug = company_slug.replace(" ", "-")
            locations = get_locations_from_globaldata(company_slug)
            combined_data.append({
                "fortune_company_name": company_name,
                "globaldata_company_name": company_label,
                "company_slug": company_slug,
                "locations": locations
            })
        else:
            combined_data.append({
                "fortune_company_name": company_name,
                "globaldata_company_name": None,
                "company_slug": None,
                "locations": []
            })

    with open("integrated_data.json", "w", encoding="utf-8") as file:
        json.dump(combined_data, file, indent=4, ensure_ascii=False)
    print("Dados integrados salvos em 'integrated_data.json'.")

if __name__ == "__main__":
    integrate_scraping()
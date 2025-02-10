from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

def scrape_companies(base_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    companies = []
    try:
        driver.get(base_url)
        time.sleep(5)  # Aguarda carregamento da página

        # Identificar o seletor HTML que contém a lista de empresas
        company_elements = driver.find_elements(By.CSS_SELECTOR, ".company-name-selector")  # Substitua pelo seletor correto

        for element in company_elements:
            companies.append(element.text)

        # Adicione lógica para lidar com a paginação, se necessário

    except Exception as e:
        print(f"Erro ao raspar dados: {e}")
    finally:
        driver.quit()

    return companies

# URL base da listagem
base_url = "https://www.globaldata.com/companies/"
companies = scrape_companies(base_url)

# Salvar no arquivo JSON
if companies:
    with open("companies.json", "w", encoding="utf-8") as file:
        json.dump(companies, file, indent=4, ensure_ascii=False)
    print("Dados salvos em 'companies.json'.")

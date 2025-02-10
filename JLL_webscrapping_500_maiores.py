from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
import json
import time

# Função para obter os dados das 500 maiores empresas
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
            with open("global_500_items.json", "w", encoding="utf-8") as file:
                json.dump(items_data, file, indent=4, ensure_ascii=False)
            print("Dados de 'items' salvos no arquivo 'global_500_items.json'.")
            return items_data
        else:
            print(f"Erro ao acessar a API. Código de status: {response.status_code}")
            return None
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return None

# Função para raspar os locais de operação de uma empresa
def scrape_locations(url, xpath):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get(url)
        time.sleep(5)
        locations_element = driver.find_element(By.XPATH, xpath)
        locations = locations_element.text.split('\n')
        return locations
    except Exception as e:
        print(f"Erro ao raspar dados: {e}")
        return ["Informação não encontrada"]
    finally:
        driver.quit()

# Função principal para combinar os dois códigos
def combine_data_and_scrape_locations():
    xpath = "/html/body/main/div[4]/div/div[2]/div[2]/div[4]/div"
    base_url = "https://www.globaldata.com/company-profile"

    # Carregar os dados das 500 maiores empresas
    global_500_items = get_global_500_data()
    if not global_500_items:
        print("Não foi possível obter os dados das 500 maiores empresas.")
        return

    combined_data = []
    for company in global_500_items:
        company_name = company.get("name")
        slug = company.get("slug")
        
        if not slug:
            print(f"Slug não encontrado para {company_name}.")
            continue
        
        profile_url = f"{base_url}{slug}locations/"
        print(f"Buscando locais para {company_name} em {profile_url}")
        locations = scrape_locations(profile_url, xpath)
        
        combined_data.append({
            "name": company_name,
            "rank": company.get("rank"),
            "data": company.get("data"),
            "locations": locations
        })
    
    with open("global_500_with_locations.json", "w", encoding="utf-8") as file:
        json.dump(combined_data, file, indent=4, ensure_ascii=False)

    print("Dados combinados salvos em 'global_500_with_locations.json'.")

# Executar a função principal
combine_data_and_scrape_locations()

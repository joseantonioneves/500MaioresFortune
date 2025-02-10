from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

def scrape_locations(url, xpath):
    # Configurações do Selenium Wire
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executa o navegador em modo headless
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Configuração do driver usando webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Acessar a URL
        driver.get(url)
        time.sleep(5)  # Aguarda o carregamento da página (ajuste conforme necessário)

        # Localizar o elemento pelo XPath
        locations_element = driver.find_element(By.XPATH, xpath)
        
        # Extrair o texto do elemento
        locations = locations_element.text.split('\n')  # Divide em linhas, se houver várias localizações

        # Criar JSON com as localizações
        data = {"locations": locations}

        return data

    except Exception as e:
        print(f"Erro ao raspar dados: {e}")
        return None
    finally:
        driver.quit()

# URL e XPath fornecidos
url = "https://www.globaldata.com/company-profile/volkswagen-ag/locations/?utm_source=chatgpt.com"
xpath = "/html/body/main/div[4]/div/div[2]/div[2]/div[4]/div"

# Raspar dados
locations_data = scrape_locations(url, xpath)

# Salvar em um arquivo JSON
if locations_data:
    with open("locations.json", "w", encoding="utf-8") as file:
        json.dump(locations_data, file, indent=4, ensure_ascii=False)

    print("Dados salvos em 'locations.json'.")

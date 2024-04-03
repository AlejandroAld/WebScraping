import re

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Web driver para EDGE
# s = Service('C:\\Users\\Abima\\Downloads\\edgedriver_win64\\msedgedriver.exe')
# driver = webdriver.Edge(service=s)

# Web driver para Chrome
webdriver_path = 'C:/Users/Alejandro/chrome/chromedriver.exe'
driver = webdriver.Chrome(webdriver_path)


def scrape_intercompras(URL):
    # Abre la URL
    driver.get(URL)

    # Espera explícita para que los elementos estén presentes
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.divContentProductInfo'))
    )

    # Obtén el contenido de la página
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Lista para almacenar la información de los televisores
    tvs = []

    # Encuentra los elementos que contienen la información de los televisores
    tv_elements = soup.find_all('div', class_='divContentProductInfo')

    for tv_element in tv_elements:
        title = tv_element.select_one('a.spanProductListInfoTitle').text.strip()
        price = tv_element.select_one('div.divProductListPrice').text.strip()
        resolution_div = tv_element.find('div', text=re.compile('Resolución de la pantalla'))
        resolution = resolution_div.find_next_sibling('div').text.strip() if resolution_div else 'No disponible'
        screen_size_div = tv_element.find('div', text=re.compile('Tamaño de pantalla'))
        screen_size = screen_size_div.find_next_sibling('div').text.strip() if screen_size_div else 'No disponible'

        # Añade la información del televisor a la lista
        tvs.append({
            'Titulo': title,
            'Precio': price,
            'Resolución': resolution,
            'Tamaño de pantalla': screen_size
        })

    return tvs


# URLs a scrapear
urls = [
    'https://intercompras.com/c/tvs-pantallas-1143?ft_resolucion_de_la_pantalla=1366%20x%20768%20Pixeles',
    'https://intercompras.com/c/tvs-pantallas-1143?ft_resolucion_de_la_pantalla=1920%20x%201080%20Pixeles',
    'https://intercompras.com/c/tvs-pantallas-1143?ft_resolucion_de_la_pantalla=3840%20x%202160%20Pixeles'
]

# DataFrame para recopilar los datos de todas las URLs
all_tvs = pd.DataFrame()

for url in urls:
    # Scrapear cada URL y añadir los datos al DataFrame
    tvs_data = scrape_intercompras(url)
    all_tvs = pd.concat([all_tvs, pd.DataFrame(tvs_data)], ignore_index=True)

# Guardar los datos en un archivo Excel
all_tvs.to_excel('pantallas_intercompras.xlsx', index=False)

# Cerrar el WebDriver
driver.quit()

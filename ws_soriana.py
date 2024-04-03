import multiprocessing

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Función para realizar el scraping de Soriana y almacenar los resultados en el diccionario compartido
def scrape_soriana(urls, shared_dict, shared_dict_total):
    # Listas para almacenar los productos de cada categoría de resolución
    resolution_1_data = []
    resolution_2_data = []
    resolution_3_data = []
    data = []
    for URL in urls:
        driver = setup_driver()
        # Abre la URL
        driver.get(URL)
        wait = WebDriverWait(driver, 10)

        # Desplazarse por la página para asegurar que se cargan todos los productos
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Esperar hasta que los productos se carguen después de desplazarse
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.product-tile--wrapper')))

        # Analizar el contenido de la página con BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        productos = soup.select('div.product-tile--wrapper')

        for producto in productos:
            try:
                titulo = producto.select_one('a.product-tile--link').get_text(strip=True)
                precio = producto.select_one('span.price-plp').get_text(strip=True)
                url_imagen = producto.select_one('img.tile-image')['src'].strip()
                resolucion = extract_resolution(titulo)
                # Añade la información del producto a la lista
                data.append({
                    'Titulo': titulo,
                    'Precio': precio,
                    'Resolución': resolucion,
                    'URL Imagen': url_imagen
                })
            except Exception as e:
                print(f"Error al procesar un producto: {e}")

        # Agregar los productos a las listas de cada categoría de resolución
        resolution_1_data.extend([product for product in data if product['Resolución'] == 'HD 1366 x 768'])
        resolution_2_data.extend([product for product in data if product['Resolución'] == 'FHD 1920 x 1080'])
        resolution_3_data.extend([product for product in data if product['Resolución'] == '4K UHD 3840 x 2160'])

        # Cerrar el WebDriver
        driver.quit()

    # Add data to dictionary shared_dict_total
    shared_dict_total['soriana'] = data
    # Encontrar el producto más económico en cada categoría de resolución después de procesar todas las URLs

    resolution_1_min = min(resolution_1_data, key=lambda x: precio_a_numero(x['Precio']))

    resolution_2_min = min(resolution_2_data, key=lambda x: precio_a_numero(x['Precio']))

    resolution_3_min = min(resolution_3_data, key=lambda x: precio_a_numero(x['Precio']))

    # Almacenar los productos más económicos en el diccionario compartido
    # Only if actual value is worse than the new one
    if resolution_1_data and (not shared_dict.get('resolution_1') or precio_a_numero(
            shared_dict.get('resolution_1', {}).get('Precio', 'Infinity')) > precio_a_numero(
        resolution_1_min['Precio'])):
        shared_dict['resolution_1'] = resolution_1_min
    if resolution_2_data and (not shared_dict.get('resolution_2') or precio_a_numero(
            shared_dict.get('resolution_2', {}).get('Precio', 'Infinity')) > precio_a_numero(
        resolution_2_min['Precio'])):
        shared_dict['resolution_2'] = resolution_2_min
    if resolution_3_data and (not shared_dict.get('resolution_3') or precio_a_numero(
            shared_dict.get('resolution_3', {}).get('Precio', 'Infinity')) > precio_a_numero(
        resolution_3_min['Precio'])):
        shared_dict['resolution_3'] = resolution_3_min


def precio_a_numero(precio):
    # Elimina el símbolo de moneda y las comas, y convierte el resultado a float and remove any value after string .00
    # Divide por el carácter de nueva línea y toma la primera parte
    precio_sin_ofertas = precio.split('\n')[0]
    return float(precio_sin_ofertas.replace('$', '').replace(',', ''))


# Web driver para Chrome
def setup_driver():
    # Web driver para EDGE
    # s = Service('C:\\Users\\Abima\\Downloads\\edgedriver_win64\\msedgedriver.exe')
    # driver = webdriver.Edge(service=s)

    # Web driver para Chrome
    webdriver_path = 'C:/Users/Alejandro/chrome/chromedriver.exe'
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.geolocation": 2,
    }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(webdriver_path, options=options)
    return driver


# Define la función para extraer la resolución del título
def extract_resolution(title):
    if "4K" in title or "UHD" in title or "3840" in title:
        return "4K UHD 3840 x 2160"
    elif "FHD" in title or "1920" in title:
        return "FHD 1920 x 1080"
    elif "HD" in title or "1366" in title:
        return "HD 1366 x 768"
    else:
        return "FHD 1920 x 1080"


if __name__ == '__main__':
    # Crear un diccionario compartido para almacenar los resultados
    shared_data = multiprocessing.Manager().dict()

    # URLs a scrapear en Soriana
    soriana_urls = [
        'https://www.soriana.com/buscar?q=pantalla+hd&search-button=',
        'https://www.soriana.com/buscar?q=Pantalla+JVC+43+Pulg+Roku+Framless&search-button=',
        'https://www.soriana.com/buscar?q=Pantalla+4k&search-button='
    ]

    process_soriana = multiprocessing.Process(target=scrape_soriana, args=(soriana_urls, shared_data, []))
    process_soriana.start()
    process_soriana.join()

    # Recuperar los resultados del diccionario compartido
    soriana_data = shared_data.get('soriana', [])

    # Crear un DataFrame con los datos de Soriana
    soriana_df = pd.DataFrame(soriana_data)

    # Guardar los datos en un archivo Excel
    # soriana_df.to_excel('pantallas_soriana.xlsx', index=False)

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import multiprocessing


# Función para realizar el scraping de PCEL y almacenar los resultados en el diccionario compartido
def scrape_pcel(urls, shared_dict, shared_dict_total):
    monitors = []
    regex = re.compile(
        r"(?P<tipo>[\w\s]+)\sde\s(?P<pulgadas>\d+(\.\d+)?\")?.*?Resolución\s*(?P<resolucion>[\d\sx]+)?.*?(?P<ms>\d+\sms)?")

    for base_url in urls:
        driver = setup_driver()
        # Abre la URL
        driver.get(base_url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        next_page = True
        while next_page:
            monitor_elements = soup.find_all('div', class_='name')
            for monitor_element in monitor_elements:
                description = monitor_element.a.text
                match = regex.search(description)
                if match:
                    price_div = monitor_element.find_next('div', class_='price')
                    price = price_div.text.strip() if price_div else 'No disponible'

                    # Buscar el elemento de imagen al mismo nivel que el elemento de nombre
                    image_div = monitor_element.find_next('div', class_='image')
                    image_url = image_div.find('img')['src'] if image_div else 'No disponible'

                    monitor_info = match.groupdict()
                    monitor_info['Precio'] = price
                    monitor_info['URL Imagen'] = image_url
                    monitor_info['Tienda'] = 'PCEL'
                    monitors.append(monitor_info)

                # Busca si hay una página siguiente
                next_li_element = soup.find('li', class_='next')
                if next_li_element and next_li_element.find('a'):
                    next_page_url = next_li_element.find('a', href=True)['href']
                    driver.get(base_url + next_page_url)
                    page_source = driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')
                else:
                    next_page = False

        driver.quit()

    # Lista para almacenar los datos de productos de cada categoría de resolución
    resolution_1_data = []
    resolution_2_data = []
    resolution_3_data = []

    for monitor in monitors:
        if '1366 x 768' in monitor['resolucion']:
            resolution_1_data.append(monitor)
        elif '1920 x 1080' in monitor['resolucion']:
            resolution_2_data.append(monitor)
        elif '3840 x 2160' in monitor['resolucion']:
            resolution_3_data.append(monitor)

    # Encontrar el producto más económico en cada categoría de resolución
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

    # Generate another dictionary with all the data monitors, but only columns tipo, resolucion, Precio y URL Imagen
    data = []
    for monitor in monitors:
        data.append({
            'Titulo': monitor['tipo'],
            'Precio': monitor['Precio'],
            'Resolución': monitor['resolucion'],
            'URL Imagen': monitor['URL Imagen']
        })

    # Add data to dictionary shared_dict_total
    shared_dict_total['pcel'] = data


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
    # Define los headers para el request HTTP
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    # }

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


if __name__ == '__main__':
    # Crear un diccionario compartido para almacenar los resultados
    shared_data = multiprocessing.Manager().dict()

    # URLs a scrapear en PCEL
    pcel_urls = [
        'https://pcel.com/index.php?route=product/search&filter_name=televisión 1366',
        'https://pcel.com/index.php?route=product/search&filter_name=televisión 1920',
        'https://pcel.com/index.php?route=product/search&filter_name=Televisi%C3%B3n%203840'
    ]

    # Crear procesos para realizar el scraping de PCEL
    process_pcel = multiprocessing.Process(target=scrape_pcel, args=(pcel_urls, shared_data, []))
    process_pcel.start()
    process_pcel.join()

    # Recuperar los resultados del diccionario compartido
    pcel_data = shared_data.get('data', [])

    # Crear un DataFrame con los datos de PCEL
    pcel_df = pd.DataFrame(pcel_data)

    # Guardar los datos en un archivo Excel
    pcel_df.to_excel('pantallas_pcel.xlsx', index=False)

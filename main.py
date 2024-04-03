# hey
import multiprocessing

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ws_cyberpuerta import precio_a_numero, scrape_cyberpuerta
from ws_pcel import precio_a_numero, scrape_pcel
from ws_soriana import precio_a_numero, scrape_soriana

from niceposter import Create
import glob
import os
import requests
from PIL import Image
from io import BytesIO

import numpy as np


def setup_driver():
    # Web driver para EDGE
    # s = Service('C:\\Users\\Abima\\Downloads\\edgedriver_win64\\msedgedriver.exe')
    # driver = webdriver.Edge(service=s)

    # Web driver para Chrome
    # driver = webdriver.Chrome()
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


# Función para cerrar pop-ups
def close_popups(driver_):
    close_button_selectors = [
        'button.close',
        'div.popup-close',
        'a.popup-close',
    ]

    for selector in close_button_selectors:
        try:
            close_button = WebDriverWait(driver_, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            close_button.click()
        except Exception as e:
            print(f"No se encontró o no se pudo hacer clic en el pop-up con el selector: {selector}. Error: {e}")


if __name__ == '__main__':
    # Creamos un diccionario compartido para almacenar los productos más económicos
    shared_dict = multiprocessing.Manager().dict()
    shared_dict_total = multiprocessing.Manager().dict()

    # Definimos las URLs de cada tienda
    soriana_urls = [
        'https://www.soriana.com/buscar?q=pantalla+hd&search-button=',
        'https://www.soriana.com/buscar?q=Pantalla+JVC+43+Pulg+Roku+Framless&search-button=',
        'https://www.soriana.com/buscar?q=Pantalla+4k&search-button='
    ]
    pcel_urls = [
        'https://pcel.com/index.php?route=product/search&filter_name=televisión 1366',
        'https://pcel.com/index.php?route=product/search&filter_name=televisión 1920',
        'https://pcel.com/index.php?route=product/search&filter_name=Televisi%C3%B3n%203840'
    ]
    cyberpuerta_urls = [
        'https://www.cyberpuerta.mx/Audio-y-Video/TV-y-Pantallas/Pantallas/Filtro/Tipo-HD/HD/',
        'https://www.cyberpuerta.mx/Pantallas-FullHD/',
        'https://www.cyberpuerta.mx/TV-4K-Ultra-HD/'
    ]

    # Creamos procesos para cada tienda
    soriana_process = multiprocessing.Process(target=scrape_soriana,
                                              args=(soriana_urls, shared_dict, shared_dict_total))
    pcel_process = multiprocessing.Process(target=scrape_pcel, args=(pcel_urls, shared_dict, shared_dict_total))
    cyberpuerta_process = multiprocessing.Process(target=scrape_cyberpuerta,
                                                  args=(cyberpuerta_urls, shared_dict, shared_dict_total))

    # Iniciamos los procesos
    soriana_process.start()
    pcel_process.start()
    cyberpuerta_process.start()

    # Esperamos a que todos los procesos terminen
    soriana_process.join()
    print("Soriana terminado")
    pcel_process.join()
    print("PCEL terminado")
    cyberpuerta_process.join()
    print("Cyberpuerta terminado")

    # Obtenemos los productos más económicos de cada categoría
    resolution_1 = shared_dict['resolution_1']
    resolution_2 = shared_dict['resolution_2']
    resolution_3 = shared_dict['resolution_3']

    # Imprimimos los productos más económicos
    print("Producto más económico (1366 x 768 Pixeles):")
    if resolution_1['URL Imagen'].startswith('https://www.soriana.com/'):
        resolution_1['Tienda'] = 'Soriana'
    elif resolution_1['URL Imagen'].startswith('https://images.pcel.com/'):
        resolution_1['Tienda'] = 'PCEL'
    elif resolution_1['URL Imagen'].startswith('https://www.cyberpuerta.mx/'):
        resolution_1['Tienda'] = 'Cyberpuerta'
    print(resolution_1)

    print("Producto más económico (1920 x 1080 Pixeles):")
    if resolution_2['URL Imagen'].startswith('https://www.soriana.com/'):
        resolution_2['Tienda'] = 'Soriana'
    elif resolution_2['URL Imagen'].startswith('https://images.pcel.com/'):
        resolution_2['Tienda'] = 'PCEL'
    elif resolution_2['URL Imagen'].startswith('https://www.cyberpuerta.mx/'):
        resolution_2['Tienda'] = 'Cyberpuerta'
    print(resolution_2)

    print("Producto más económico (3840 x 2160 Pixeles):")
    if resolution_3['URL Imagen'].startswith('https://www.soriana.com/'):
        resolution_3['Tienda'] = 'Soriana'
    elif resolution_3['URL Imagen'].startswith('https://images.pcel.com/'):
        resolution_3['Tienda'] = 'PCEL'
    elif resolution_3['URL Imagen'].startswith('https://www.cyberpuerta.mx/'):
        resolution_3['Tienda'] = 'Cyberpuerta'
    print(resolution_3)

    # Obtenemos los datos de todos los productos
    soriana_data = shared_dict_total['soriana']
    pcel_data = shared_dict_total['pcel']
    cyberpuerta_data = shared_dict_total['cyberpuerta']

    # Convert soriana_data, pcel_data y cyberpuerta_data to DataFrame
    soriana_df = pd.DataFrame(soriana_data)
    pcel_df = pd.DataFrame(pcel_data)
    cyberpuerta_df = pd.DataFrame(cyberpuerta_data)
    # Concatenate all DataFrames
    all_data = pd.concat([soriana_df, pcel_df, cyberpuerta_df])

    soriana_df['Tienda'] = 'Soriana'
    pcel_df['Tienda'] = 'PCEL'
    cyberpuerta_df['Tienda'] = 'Cyberpuerta'

    all_data['Precio'] = all_data['Precio'].apply(precio_a_numero)

    # Unimos los DataFrames para la visualización
    complete_data = pd.concat([soriana_df, pcel_df, cyberpuerta_df])
    resolution_mapping = {
        'HD 1366 x 768': '1366 x 768',
        'FHD 1920 x 1080': '1920 x 1080',
        '4K UHD 3840 x 2160': '3840 x 2160',
        '1920 x 1080 ': '1920 x 1080',
        '3840 x 2160 ': '3840 x 2160',
        ': 1366 x 768 Pixeles': '1366 x 768',
        ': 1920 x 1080 Pixeles': '1920 x 1080',
        ': 3840 x 2160 Pixeles': '3840 x 2160'
    }

    # Reemplazar los valores en la columna 'Resolución'
    complete_data['Resolución'] = complete_data['Resolución'].replace(resolution_mapping)
    complete_data['Precio'] = complete_data['Precio'].apply(precio_a_numero)
    complete_data['Precio'] = pd.to_numeric(complete_data['Precio'], errors='coerce')
    # Remove row of complete_data with ': 1280 x 720 Pixeles' in 'Resolución'
    complete_data = complete_data[complete_data['Resolución'] != ': 1280 x 720 Pixeles']
    # Export complete_data to .xlsx
    complete_data.to_excel('complete_data.xlsx', index=False)

    # 1 Crear un gráfico de cajas para cada resolución
    for resolution in complete_data['Resolución'].unique():
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=complete_data[complete_data['Resolución'] == resolution],
                    x='Tienda', y='Precio', palette="Set1")
        plt.title(f'Comparación de precios para {resolution}')
        plt.ylabel('Precio ($)')
        plt.xlabel('Tienda')
        plt.savefig(f'boxplot_{resolution}.jpg')
        plt.show()

    # 2. Gráfica de dispersión por tamaño/presentación
    plt.figure(figsize=(14, 8))
    sns.scatterplot(data=complete_data.sort_values('Precio'),
                    x='Titulo', y='Precio', hue='Tienda', style='Tienda', s=100)
    plt.xticks(rotation=90)  # Rota las etiquetas del eje x para mejor lectura
    plt.title('Comparación de precios por producto y tienda')
    plt.ylabel('Precio ($)')
    plt.xlabel('Producto')
    plt.legend(title='Tienda')
    plt.savefig('scatterplot.jpg')
    plt.show()

    # Lista de URLs de las imágenes
    image_urls = [
        # obtain url of resolution_1
        resolution_1['URL Imagen'],
        # obtain url of resolution_2
        resolution_2['URL Imagen'],
        # obtain url of resolution_3
        resolution_3['URL Imagen']
    ]

    # Carpeta de destino para guardar las imágenes
    output_folder = 'source'

    # Crea la carpeta de destino si no existe
    os.makedirs(output_folder, exist_ok=True)
    i = 1

    for url in image_urls:
        try:
            # Realiza una solicitud GET para obtener la imagen desde la URL
            response = requests.get(url)

            if response.status_code == 200:
                # Lee la imagen desde la respuesta y crea una instancia de imagen
                image = Image.open(BytesIO(response.content))

                # Redimensiona la imagen a 300x300 píxeles
                image = image.resize((1000, 800))
                # Save image in source folder
                image.save(f'source/{i}.jpg')
            else:
                print(f'Error al descargar la imagen desde {url}')
        except Exception as e:
            print(f'Error: {e}')
        i += 1

    # Crear poster de hd
    bg_image = Create.Poster(img_name='HD.png')
    background_files = glob.glob('media/backgrounds/*')
    filename = np.random.choice(background_files)
    slogan = "Aprovecha esta oferta, Televisión HD 1366 x 768 Pixeles"

    bg_image.add_image(filename, position='cc', scale='fit')
    # Add image of resolution_1
    bg_image.add_image('source/1.jpg', position='cc', scale=30)
    bg_image.text(slogan, position=(35, 10), align='center', textbox_width=450, font_style='media/fonts/Poster_Font.ttf',
                  color='red')
    # obtain precio of resolution_1
    bg_image.text(resolution_1['Precio'].split('\n')[0], position=(190, 350), align='center', textbox_width=450,
                  font_style='media/fonts/Poster_Font_3.ttf', color='red', text_size=50)
    # obtain Tienda of resolution_1 and apppend to final of sentence: "Solo en "
    bg_image.text('Solo en ' + resolution_1['Tienda'], position=(120, 420), align='center', textbox_width=450,
                  font_style='media/fonts/Poster_Font.ttf', color='red')
    bg_image.frame(thickness=8)
    bg_image.filter(rgb=(255, 255, 255), opacity=0)

    # Crear poster de fhd
    bg_image = Create.Poster(img_name='FHD.png')
    background_files = glob.glob('media/backgrounds/*')
    filename = np.random.choice(background_files)
    slogan = "Aprovecha esta oferta, Televisión FHD 1920 x 1080 Pixeles"

    bg_image.add_image(filename, position='cc', scale='fit')

    bg_image.add_image('source/2.jpg', position='cc', scale=30)
    bg_image.text(slogan, position=(35, 10), align='center', textbox_width=450,
                  font_style='media/fonts/Poster_Font.ttf',
                  color='red')

    bg_image.text(resolution_2['Precio'].split('\n')[0], position=(190, 350), align='center', textbox_width=450,
                  font_style='media/fonts/Poster_Font_3.ttf', color='red', text_size=50)

    bg_image.text('Solo en ' + resolution_2['Tienda'], position=(120, 420), align='center', textbox_width=450,
                  font_style='media/fonts/Poster_Font.ttf', color='red')
    bg_image.frame(thickness=8)
    bg_image.filter(rgb=(255, 255, 255), opacity=0)

    # Crear poster de 4k
    bg_image = Create.Poster(img_name='4k.png')
    background_files = glob.glob('media/backgrounds/*')
    filename = np.random.choice(background_files)
    slogan = "Aprovecha esta oferta, Televisión 4K UHD 3840 x 2160 Pixeles"

    bg_image.add_image(filename, position='cc', scale='fit')

    bg_image.add_image('source/3.jpg', position='cc', scale=30)
    bg_image.text(slogan, position=(35, 10), align='center', textbox_width=450,
                  font_style='media/fonts/Poster_Font.ttf',
                  color='red')

    bg_image.text(resolution_3['Precio'].split('\n')[0], position=(190, 350), align='center', textbox_width=450,
                  font_style='media/fonts/Poster_Font_3.ttf', color='red', text_size=50)

    bg_image.text('Solo en ' + resolution_3['Tienda'], position=(120, 420), align='center', textbox_width=450,
                  font_style='media/fonts/Poster_Font.ttf', color='red')
    bg_image.frame(thickness=8)
    bg_image.filter(rgb=(255, 255, 255), opacity=0)
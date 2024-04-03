# WebScraping

Este proyecto de WebScraping se enfoca en la extracción de información de tres sitios web distintos: Soriana, PCEL y Cyberpuerta. Se utilizan las tecnologías Python, Matplotlib, Seaborn y Selenium para realizar el scraping en paralelo utilizando multitreading. El objetivo es buscar tres tipos de productos en cada sitio web: pantallas HD, FHD y 4K. Se realizan un total de 9 búsquedas simultáneas en las tres páginas web.

## Funcionalidades

- Extracción de información de productos desde los sitios web Soriana, PCEL y Cyberpuerta.
- Búsqueda de pantallas HD, FHD y 4K en paralelo utilizando multiprocessing.
- Almacenamiento de los productos en una memoria compartida (diccionario de Python) y en un spreadsheet de Excel.
- Cálculo del producto más barato de cada categoría.
- Generación de carteles para cada producto utilizando la librería Python llamada `niceposter`, utilizando la imagen e información del producto obtenidas de las páginas web mediante Selenium.
- Representación y análisis de datos mediante gráficos de cajas utilizando Seaborn y Matplotlib:
  - Un gráfico de cajas para cada resolución de pantalla.
  - Una gráfica de dispersión por tamaño/presentación.

## Requisitos

- Python
- Selenium
- Niceposter
- Seaborn
- Matplotlib

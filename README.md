# Clickbaits Detector

Clasificador capaz de distinguir entre noticias de contenido clickbait y noticias más serias.

---- Instrucciones ----

sh prestart.sh (se instalarán automáticamente las librerías de Python necesarias)

*Para instalar newspaper:

(Con macOS)
1. brew install libxml2 libxslt
2. brew install libtiff libjpeg webp little-cms2

(Con Linux)
1. sudo apt-get install libxml2-dev libxslt-dev
2. sudo apt-get install libjpeg-dev zlib1g-dev libpng12-dev

3. curl https://raw.githubusercontent.com/codelucas/newspaper/master/download_corpora.py | python
4. pip install git+https://github.com/codelucas/newspaper.git@python-2-head

=======================================================================================
Para ejecutar los distintos módulos:

cd code

1. python clawler.py (ejecuta módulo crawler, que obtiene URLs de artículos)
2. python scraper.py (ejecuta módulo scraper, que extrae atributos de esos artículos y genera los datasets)
3. python comparator.py (ejecuta módulo comparator, que compara clasificadores y genera los dos mejores)

=======================================================================================
Para usar la aplicación:

cd code

python classifier.py (Introducir URL de un artículo en inglés o español y presionar enter)
	



	


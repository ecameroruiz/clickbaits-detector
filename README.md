# Clickbaits Detector

Clasificador capaz de distinguir entre noticias de contenido clickbait y noticias más serias.

---- *Instrucciones* ----

Ejecutar prestart.sh (se instalarán automáticamente las librerías de Python necesarias)

=======================================================================================
Para ejecutar los distintos módulos:

cd code
	-> python clawler.py (ejecuta módulo crawler, que obtiene URLs de artículos)
	-> python scraper.py (ejecuta módulo scraper, que extrae atributos de esos artículos y genera los datasets)
	-> python comparator.py (ejecuta módulo comparator, que implementa varios tipos de clasificadores usando de conjunto de entrenamiento distintas combinaciones de los atributos que se encuentran en los datasets y compara sus precisiones, genera los 2 clasificadores con mejores resultados)

=======================================================================================
Para usar la aplicación:

cd code
	-> python classifier.py (Introducir URL de un artículo en inglés o español, presionar enter y devolverá el resultado del clasificador correspondiente)

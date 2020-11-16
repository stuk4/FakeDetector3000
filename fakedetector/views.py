from django.shortcuts import render
from django.http import HttpResponse
# ML
import pickle
import pandas as pd
import string

from nltk.corpus import stopwords

from langdetect import detect
from django.http import JsonResponse




import json
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializer import NoticiaSerializer

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
import os


# Directorio de mis mdoelos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELOS_DIR  = os.path.join(BASE_DIR,'modelos/')


def limpiar_stopwrods(noticia):
    idioma = detect(noticia)
    if(idioma == 'en'):
        print('USANDO STOPWRODS INGLES')
        stop = set(stopwords.words('english'))
    elif (idioma == 'es'): 
        print('USANDO STOPWRODS SPANISH')
        stop = set(stopwords.words('spanish'))
    else:
        stop = set(stopwords.words('english'))
  
    punctuation = list(string.punctuation)
    stop.update(punctuation)

    texto_limpio = []
    for i in noticia.split():
        # Si la cadena de texto no esta en la stopwords(stop)
        #Entonces mando la cadena de texto sin las stopwords          
        if i.strip().lower() not in stop:
            texto_limpio.append(i.strip())
    return " ".join(texto_limpio)
def search(noticiaUrl):

    web = noticiaUrl
    req = Request(web, headers={'User-Agent': 'Mozilla/5.0'})
    # datos = urllib.request.urlopen(web).read().decode()
    datos = urlopen(req).read()
    soup =  BeautifulSoup(datos,'html.parser')
    #tags = soup('p')
    tags = soup.find_all("p")
    #title = soup.find('title')
    title = soup.find("meta",  property="og:title")
    if title:
        texto = title["content"] +' '+ ''.join(str(tag.text) for tag in tags)
    else:
        texto = ''.join(str(tag.text) for tag in tags)
    return texto
def predecir(noticia):
    idioma = detect(noticia)
    print(type(idioma))
    if(idioma == 'en'):
        print('USANDO MODELO INGLES')
        nombre_archivo_modelo = 'randomforestIngles.sav'
        nombre_archivo_transform = 'stringtomatrizIngles.sav'
    elif (idioma == 'es'): 
        print('USANDO MODELO ESPAÑOL')
        nombre_archivo_modelo = 'randomforestEspanol.sav'
        nombre_archivo_transform = 'stringtomatrizEspanol.sav'

    loaded_model = pickle.load(open(MODELOS_DIR+nombre_archivo_modelo, 'rb'))
    load_model_matriz = pickle.load(open(MODELOS_DIR+nombre_archivo_transform, 'rb'))
    # Valido si el string que llega es solo de nuemros
    if noticia.isnumeric():
        return {'cuerpo': False}
        
    # Limpio mi texto de stopwords
    noticia = limpiar_stopwrods(noticia)
    # Paso mi  notica a una serie de pandas
    testdta = pd.Series([noticia])
    # transformo mi noticia a una matriz
    a_predecir = load_model_matriz.transform(testdta)
    # Hago la prediccion de mi noticia
    resultado = loaded_model.predict(a_predecir)
    # Detectar el idioma de la noticia
    

        
    # Transformo a string mi noticia
    prediccion = str(resultado[0])
    json = {'prediccion':prediccion,'idioma':idioma,'cuerpo':noticia}

    return json

def validar_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    resutlado = re.match(regex, url) is not None
    return resutlado

# Get aun no terminado
class prediccion(APIView):
    # def get(self,request):
    #     nombre_archivo_modelo = 'randomforestIngles.sav'
    #     nombre_archivo_transform = 'stringtomatrizIngles.sav'
    #     loaded_model = pickle.load(open('./modelos/'+nombre_archivo_modelo, 'rb'))
    #     load_model_matriz = pickle.load(open('./modelos/'+nombre_archivo_transform, 'rb'))
    #     noticia = 'Bitter John McCain Calls Trump ‘Ill Informed’ in Nasty OpEd: ‘We don’t answer to him’What the heck! Senator John McCain just admitted that he doesn t answer to President Trump! Can you imagine if a Senator had done this to Obama? McCain s OpEd in The Washington Post is a horrible hit on Trump. Shame on him!It starts out with a statement about how horrible the white supremacists are and then goes on to discuss Congress getting back to order. It s a snoozer of an OpEd until you get to the last part In a shocking slam on President Trump s character and knowledge of government, McCain shows his bitterness towards Trump. He claims that,  We don t answer to him   but also say that,  We must respect his authority WTH!MCCAIN: IT S TIME CONGRESS RETURNS TO REGULAR ORDER: We can fight like hell for our ideas to prevail. But we have to respect each other or at least respect the fact that we need each other.That has never been truer than today, when Congress must govern with a president who has no experience of public office, is often poorly informed and can be impulsive in his speech and conduct.We must respect his authority and constitutional responsibilities. We must, where we can, cooperate with him. But we are not his subordinates. We don t answer to him. We answer to the American people. We must be diligent in discharging our responsibility to serve as a check on his power. And we should value our identity as members of Congress more than our partisan affiliation.I argued during the health-care debate for a return to regular order, letting committees of jurisdiction do the principal work of crafting legislation and letting the full Senate debate and amend their efforts.We won t settle all our differences that way, but such an approach is more likely to make progress on the central problems confronting our constituents. We might not like the compromises regular order requires, but we can and must live with them if we are to find real and lasting solutions. And all of us in Congress have the duty, in this sharply polarized atmosphere, to defend the necessity of compromise before the American public.SEE WHAT HE DID THERE? He basically said our president is clueless and impulsive so we don t need to listen to him. Unreal! Is McCain bitter and trying to get back at Trump? It s unheard of for a sitting Senator of the party in power trashes the president that is from the same party! Read more: WaPo'
    #     sin_limpiar = noticia
    #     noticia = limpiar_stopwrods(noticia)
    #     testdta = pd.Series([noticia])
    #     a_predecir = load_model_matriz.transform(testdta)
    #     resultado = loaded_model.predict(a_predecir)
    #     # Detectar el idioma de la noticia
    #     idioma = detect(noticia)
    #     prediccion = str(resultado[0])
    #     print('BODY============',request.data)
    #     # print('Lenguaje ',detect(noticia))
    #     # print('Resultado =========== ',resultado[0])
    #     # return HttpResponse('asdasd')
    #     json = {'prediccion':prediccion,'idioma':idioma,'cuerpo':noticia}
    #     my_serializer = NoticiaSerializer(data=json)
    #     my_serializer.is_valid(True)
    
    #     print(type(request.data))
    #     return Response(my_serializer.data)



    def post(self, request):
        validar_campos = NoticiaSerializer(data=request.data)
        if validar_campos.is_valid() == False :
            return Response(validar_campos.errors,status=status.HTTP_400_BAD_REQUEST)
        elif  type(request.data['cuerpo'])  != str: 
            return Response({'Error':'El campo [cuerpo] debe ser str'},status=status.HTTP_400_BAD_REQUEST)  
        noticia = request.data['cuerpo']
        if(validar_url(noticia)):
            noticia = search(noticia)
        else:
            noticia = request.data['cuerpo']
        
        
        json = predecir(noticia)
        my_serializer = NoticiaSerializer(data=json)
        my_serializer.is_valid(True)
        return Response(my_serializer.data) 




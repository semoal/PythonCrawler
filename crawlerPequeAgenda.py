#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc import WordPressPage
import requests 
from bs4 import BeautifulSoup
from urllib2 import urlopen 
import re
import codecs
from wordpress_xmlrpc.methods import posts
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media
from PIL import Image
from io import BytesIO
import base64
import urllib2
import xmlrpclib
from random import randint
import random, string
import unicodedata

client=Client('http://www.peque-agenda.com/xmlrpc.php','user','pwd')
def randomword(length):
   return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

def toWP(single_event) :
    
    
    #tituloFoto = uuid.uuid4()
    tituloFoto = randomword(9)
    
    data = {
            'name': tituloFoto+'.jpg',
            'type': 'image/jpeg',  # mimetype
    }
    
    file = get_url_content(single_event['foto'])
    
    data['bits'] = xmlrpc_client.Binary(file)
    
    response = client.call(media.UploadFile(data))
    
    
    attachment_id = response['id']
    widget = WordPressPost()
    widget.post_type = 'event_type'
    widget.title = single_event['title']
    widget.content = single_event['descripcion']
    widget.thumbnail = attachment_id
    widget.custom_fields = []
    widget.custom_fields.append({
            'key': 'coord',
            'value': {
            "address": single_event['direccion'],
            "lat": single_event['latitude'],
            "lng": single_event['longitude']
          }
    })
    widget.custom_fields.append({
            'key': 'fecha_inicio',
            'value': single_event['fecha_inicio']
    })
    widget.custom_fields.append({
            'key': 'direccion',
            'value': single_event['direccion']
    })
    widget.custom_fields.append({
            'key': 'fecha_fin',
            'value': single_event['fecha_fin']
    })
    widget.custom_fields.append({
            'key': 'telefono',
            'value': ""
    })
    widget.custom_fields.append({
            'key': 'correo_electronico',
            'value': ""
    })
    widget.custom_fields.append({
            'key': 'pagina_web',
            'value': "www.peque-agenda.com"
    })
    widget.custom_fields.append({
            'key': 'edad',
            'value': single_event['edadMin']+';'+single_event['edadMax']
    })
    widget.custom_fields.append({
            'key': 'precio',
            'value': single_event['precio']
    })
    widget.custom_fields.append({
            'key': 'imagen_evento',
            'value': randint(400,718)
    })
    
    widget.id = client.call(posts.NewPost(widget))
    
    
def get_url_content(url):
    try: 
        content = urllib2.urlopen(url)
        return content.read()
    except:
        print ('error!')

events = list()
titles = list()
products = client.call(posts.GetPosts({'post_type': 'event_type', 'number': 100}))
for product in products:
    if isinstance(product.title,unicode):
        titles.append(product.title.encode('utf-8').strip())
    else:
        titles.append(product.title)

i = 0
url=""
url_master='https://superpeque.com'
page = requests.get("https://superpeque.com/es/poblaciones.htm")
soup = BeautifulSoup(page.content, 'html.parser')
ul = soup.find_all('ul', {'class': 'list-links'})[0]
li = ul.find_all('li', {'class': 'col-sm-offset-2'})
for com in range(0,5) :
    l = li[com]
    link = l.find('a').get('href')
    link = url_master+link
    
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    boxlist = soup.find_all('div', {'class': 'list-box'})
    
    for event in boxlist:
        
        if 'featured' not in event.attrs['class']:
            
            single_event = {}
            #titulo
            titulo = list(event.find_all('h2', {'class': 'list-title'}))
            for t in titulo:
            	titulo = t.get_text().encode('utf-8').strip()
            	
            if titulo not in titles:
                single_event['title']=titulo
                print(titulo)
                titles.append(titulo)
            	
                listaItem = event.select('.list-details')
                for item in listaItem:
                	#direccion
                	direccion = item.find_all('li')[0].get_text()
                	single_event['direccion']=direccion
                	#fechas
                	fecha = item.find_all('li')[1].get_text()
                	fechas = fecha.split(' ')
                	fechaInicial = fechas[1]
                	fechaFin = fechas[3]
                	single_event['fecha_inicio'] = fechaInicial
                	single_event['fecha_fin'] = fechaFin
                	#edad
                	edad = item.find_all('li')[2].get_text()
                	edades = edad.split(' ');
                	edadMin = edades[3]
                	edadMax = edades[5]
                	single_event['edadMin']=edadMin
                	single_event['edadMax']=edadMax
                
                foto = event.find_all('div',{'class':'list-image'})
                for f in foto:
                    url = url_master+event.find('img').parent['href']
                    single_event['foto']=url
                    foto = f['style']
                    foto = foto.replace('background-image: url(\'', '').replace('\')', '')
                single_event['foto']=foto
                
                precio = event.find_all('div',{'class':'btn-primary'})
                for item in precio:
                	precio = item.get_text()
                	single_event['precio']=precio
            
                
                page = requests.get(url)
                soup = BeautifulSoup(page.content, 'html.parser')
                main = soup.find(id='main')
                boxlist = main.find_all('div', {'class' : 'container'})
                mapa = list(main.find_all('div', {'class' : 'page-map'}))[0]
                latitude = mapa.get('data-latitude')
                single_event['latitude'] = latitude
                longitude = mapa.get('data-longitude')
                single_event['longitude'] = longitude
                descripcion = list(main.find_all('div', {'class' : 'page-description'}))[0].get_text()
                single_event['descripcion'] = descripcion
                toWP(single_event)
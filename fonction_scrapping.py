import requests
from bs4 import BeautifulSoup
from math import *
import wget
import re
import csv 

#fonction 1 : récupère les infos sur un livre
def scrapping_one_book(url):
    response = requests.get(url)   
    if response.ok:
        
        response.encoding = 'utf-8'
        soup = BeautifulSoup (response.text, 'lxml')
        product_page_url = url #le paramètre de ma fonction
        title = soup.find('h1')
        tds = soup.findAll('td') #liste des 7 tds
        universal_product_code = tds[0].text
        price_excluding_tax = tds[2].text
        price_including_tax = tds[3].text
        number_available = tds[5].text
        image= soup.find('div',{'class' : 'item active'}).find('img')
        image_url = 'http://books.toscrape.com/'+ image['src'][6:]
        rating = soup.find('p', {'class' : 'star-rating'})
        review_rating = rating['class'][1]
        category_find = soup.find('ul', {'class' : 'breadcrumb'}).findAll('li')
        category = category_find[2].text
        regex = re.compile('[\n\r\t]')
        category = regex.sub(" ", category)
        description = soup.find('article', {'class' : 'product_page'}).findAll('p')
        product_description = description[3].text
        
        
        book_info = {
            'product_page_url': product_page_url, 
            'universal_product_code(upc)': universal_product_code,
            'title': title.text,
            'price_including_tax': price_including_tax,
            'price_excluding_tax': price_excluding_tax,
            'number_available' : number_available,
            'product_description': product_description.replace(',',';'),
            'category': category,
            'review_rating': review_rating,
            'image_url':  image_url            
        }
             
        
    return book_info

#fonction 2: qui récupère le nom de la catégorie
def scrapp_category(url):
    response = requests.get(url)   
    if response.ok:
        soup = BeautifulSoup(response.text, 'lxml')
        category = soup.find('div', {'class' : 'page-header action'}).find('h1')
       
    return category.text

#fonction 3 : récupère la liste des liens des livres d'une catégorie
def scrapping_one_category(url_category): 
    response = requests.get(url_category)#requete ds les urls de la catégorie
    links = []
    soup = BeautifulSoup(response.text, 'lxml')
    nombre_livres = soup.find('form', {'class' : 'form-horizontal'}).find('strong')
    nombre_pages = ceil(int(nombre_livres.text) / int(20))
    
    if nombre_pages > 1:
        for i in range(1, nombre_pages+1):
            url_pages= url_category.replace('index.html','page-' + str(i) + '.html') #pour que ça parcourt toutes les pages
            response = requests.get(url_pages)
            if response.ok:
                soup = BeautifulSoup(response.text,'lxml')
                livre = soup.findAll('article')
                for article in livre:
                    a = article.find('a')
                    link = a['href'] #donne les urls incomplètes
                    links.append('http://books.toscrape.com/catalogue/' + link[9:]) #complète l'url
                    
            

    else: 
        response = requests.get(url_category)
        if response.ok:
            soup = BeautifulSoup(response.text,'lxml')
            livre = soup.findAll('article')
            for article in livre:
                a = article.find('a')
                link = a['href']
                links.append('http://books.toscrape.com/catalogue/' + link[9:])
                

    return links


#fonction 4: récupère la liste des urls des catégories
def scrapping_all_category(url_site):
    urls = [] #liste des catégories
    response = requests.get(url_site)
    soup = BeautifulSoup(response.text,'lxml')
    link = soup.find('ul', {'class' : 'nav nav-list'}).findAll('li')
    for li in link: # ou for li in li_link
        a=li.find('a')
        urls.append(a['href'])

    return urls

#fonction 5: récupère les urls des images
def scrapping_images(url_livres):
    response = requests.get(url_livres)
    if response.ok:
        soup = BeautifulSoup(response.text, 'lxml')
        image= soup.find('div',{'class' : 'item active'}).find('img')
        image_url = 'http://books.toscrape.com/'+ image['src'][6:]

    return image_url


#fonction 6 : écrit les infos ds fichier csv
def category_book_to_csv(links,categorie):
    """
    Les infos de tous les livres d'une catégorie : car on boucle sur les liens de la catégorie
    """
    books_infos = [] #création d'une liste vide
    for link in links: #boucle for : je cherche dans les liens
        books_infos.append(scrapping_one_book(link)) #j'appelle fonction 1 qui renvoie les infos de tous les livres + je les mets ds une liste

    with open ('books_infos_' + categorie + '.csv', 'w+', newline ='') as csvfile:
        fieldnames = ['product_page_url', 'universal_product_code(upc)', 'title', 'price_including_tax', 'price_excluding_tax', 'number_available', 'product_description', 'category', 'review_rating', 'image_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()
        for book_info in books_infos: 
            writer.writerow(book_info)  


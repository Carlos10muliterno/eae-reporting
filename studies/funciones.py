# -*- coding: utf-8 -*-
"""
Created on Sun Apr 18 16:56:55 2021

@author: Grupo 3
"""


def makePlot():
    import matplotlib.pyplot as plt
    import io
    import urllib, base64
    plt.switch_backend('agg')
    plt.plot(range(10),'g^')
    plt.rcParams.update({'font.size': 22})
    fig = plt.gcf()
    #convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf,format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri =  urllib.parse.quote(string)
    return uri




def collectData(busqueda,languaje):
    from . import keys
    import tweepy
    import requests
    import json
    list_details = []
    print('Llamamos a la funcion de busqueda')
    list_details = get_reviews(busqueda)
    print('Maps obtenido')
    
    
    list_of_tweets = []
    number_of_tweets = 3
    
    print('Llamamos a la funcion de twitter')
    list_of_tweets, count = get_Tweets(busqueda,number_of_tweets,languaje)
    print(count, ' Tweets obtenidos')
    return list_details, list_of_tweets


'''
Función para obtener los tweets de twitter basado en el lenguaje y cantidad y el hastag
Devuelve el numero de tweets conseguidos y una lista con todos los tweets
'''

def get_Tweets(busqueda,number_of_tweets,languaje):
    import tweepy
    ##--------Twitter API Call--------##
    consumer_key = 'cLHFEXgvxQkk2oZMsCHv1M3kv'
    consumer_secret = '5S6QDZ5MsPxEPyQA5lAK1gi4PI2VY4BpSoPPqQJd7Hof8CUUwI'
    access_token = '1370390230348484612-AhsfvSHP32bAqjM6hzcgHiSiU2LIhW'
    access_token_secret = 'yVzd0NDTirE86T6f9zlctvd7F6nL16S1wqn26QFs9nrn4'

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth,wait_on_rate_limit=True)
    list_of_tweets = []
    if busqueda[0] != '#':
        busqueda = '#' + busqueda
    count = 0
    for tweet in tweepy.Cursor(api.search,q=busqueda,
                            lang=languaje,count=number_of_tweets).items(number_of_tweets):
        if 'https://t.co/' in tweet.text :
            
            #tweet.text = tweet.text[:-23]
            print('Tiene url\n', tweet.text[:-23])
            print('url\n',)
        list_of_tweets.append(tweet)
        count += 1
    return list_of_tweets, count

'''
Función para obtener los datos de google maps
'''




def get_reviews(busqueda):
    from . import keys
    import requests
    import json
    print(busqueda)
    key = keys.oauth_maps()
    
    def connect_to_endpoint(url):
        return requests.request("GET", url)
    
        
    list_countries = ["spain","USA","france","uk","italy","portugal","germany","canada","mexico","brasil","argentina"]
    list_place_ids = []
    
    
    ##--------Place Search--------##
    
    required_params = {"input": busqueda,
                       "inputtype": "textquery",
                       "fields": "place_id",
                       "api_key": key["API_key"]
                       }
    
    for country in list_countries:
    
        search_url="https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=" \
            + required_params["input"]+ " " + country \
            +"&inputtype=" + required_params["inputtype"]  \
            +"&fields="+ required_params["fields"] \
            +"&key=" + required_params["api_key"]
        
        response=connect_to_endpoint(search_url)
        # print(json.loads(response.text)['status'])
        # print(type(json.loads(response.text)['status']))
        if json.loads(response.text)['status'] != "ZERO_RESULTS": 
            place_id = json.loads(response.text)['candidates'][0]['place_id']
            list_place_ids.append(place_id)
    
    list_place_ids = list(set(list_place_ids)) #elimina duplicados 
    
    
    ##--------Place Details--------##
    
    list_details = []
    print('Obteniendo los google maps')
    
    required_params_details = {"fields": "name,geometry,rating,review,user_ratings_total",
                                "api_key": key["API_key"]
                                }
    for place_id in list_place_ids:
        
        search_url_details="https://maps.googleapis.com/maps/api/place/details/json?place_id=" \
            + place_id +"&fields=" + required_params_details["fields"] \
            + "&key=" + required_params_details["api_key"]
        
        response_details=connect_to_endpoint(search_url_details)
        if json.loads(response_details.text)['status'] == "OK":
            list_details.append(json.loads(response_details.text)['result'])
    
    return list_details




def treatment(data_googlemaps,data_twitter):    
    import json
    import sys, os
    from nltk.sentiment import SentimentIntensityAnalyzer
        
    import pandas as pd
    import gmaps
    import keys
    
    from bokeh.io import show
    from bokeh.plotting import gmap
    from bokeh.models import GMapOptions
    from bokeh.models import ColumnDataSource
    from bokeh.models import HoverTool
    
    import numpy as np
    from geopy.geocoders import Nominatim
    
    import nltk
    from nltk import tokenize
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.probability import FreqDist
    import matplotlib.pyplot as plt
    
    
    
    df_googlemaps= pd.DataFrame(data_googlemaps)
    df_twitter= pd.DataFrame(data_twitter) 
    
    # Eliminamos colummnas innecesarias del dataframe y renombramos
    df_googlemaps.rename(columns={'name': 'Name',
                                  'rating': 'Rating',
                                  'reviews': 'Reviews',
                                  'user_ratings_total': 'Total_Ratings',
                                  'geometry.location.lat':'Latitude',
                                  'geometry.location.lng':'Longitud',
                                  },inplace=True)
    
    df_twitter.rename(columns={ 'lang': 'Lang',
                                'text': 'Tweet',
                                'public_metrics.like_count': 'Likes',
                                'public_metrics.quote_count': 'Quotes',
                                'public_metrics.reply_count':'Replies',
                                'public_metrics.retweet_count':'Retweets',
                                'geo.place_id':'Place_id'
                                },inplace=True)
    
    latitud = []
    longitud = []
    for row in range(len(df_googlemaps)):
        latitud.append(df_googlemaps['geometry'][row]['location']['lat'])
        longitud.append(df_googlemaps['geometry'][row]['location']['lng'])
    
    df_googlemaps['Latitud'] = latitud
    df_googlemaps['Longitud'] = longitud
    
    likes = []
    replies = []
    retweets = []
    quotes = []
    for row in range(len(df_twitter)):
        retweets.append(df_twitter['public_metrics'][row]['retweet_count'])
        replies.append(df_twitter['public_metrics'][row]['reply_count'])
        likes.append(df_twitter['public_metrics'][row]['like_count'])
        quotes.append(df_twitter['public_metrics'][row]['quote_count'])
    
    df_twitter['Retweets'] = retweets
    df_twitter['Likes'] = likes
    df_twitter['Quotes'] = quotes
    df_twitter['Replies'] = replies
        
    
    df_googlemaps.drop(columns=['geometry','Reviews'],axis=1,inplace=True)
    df_twitter.drop(columns=['id','public_metrics','geo'],axis=1,inplace=True)
    
    # Pasamos los tweets por la libreria NLTK
    sia = SentimentIntensityAnalyzer()
    sentiments_positive = []
    sentiments_negative = []
    sentiments_neutral = []
    sentiments_compound = []
    
    for row in range(len(df_twitter)):
        sentiments_positive.append(sia.polarity_scores(df_twitter['Tweet'][row])['pos'])
        sentiments_negative.append(sia.polarity_scores(df_twitter['Tweet'][row])['neg'])
        sentiments_neutral.append(sia.polarity_scores(df_twitter['Tweet'][row])['neu'])
        sentiments_compound.append(sia.polarity_scores(df_twitter['Tweet'][row])['compound'])
    
    df_twitter['Positive_sentiment']= sentiments_positive
    df_twitter['Negative_sentiment']= sentiments_negative
    df_twitter['Neutral_sentiment'] = sentiments_neutral
    df_twitter['Compound']          = sentiments_compound
    
    # list_reviews = df_googlemaps['Reviews'].tolist()
    
      
    # Creamos subset por idiomas [en,es,fr,de,it,pt,pl] en df_twitter
    df_twitter_en = df_twitter[df_twitter['Lang']=='en']
    df_twitter_es = df_twitter[df_twitter['Lang']=='es']
    df_twitter_fr = df_twitter[df_twitter['Lang']=='fr']
    df_twitter_de = df_twitter[df_twitter['Lang']=='de']
    df_twitter_it = df_twitter[df_twitter['Lang']=='it']
    df_twitter_pt = df_twitter[df_twitter['Lang']=='pt']
    df_twitter_pl = df_twitter[df_twitter['Lang']=='pl']
    
    
    #********CALCULO DE LOS 3 TWEETS MAS INFLUYENTES*************************************
    
    df_twitter['influence'] = df_twitter[['Likes', 'Replies', 'Retweets']].sum(axis=1)
    
    df_twitter_mx= df_twitter.sort_values(by =['influence'], ascending=[False], ignore_index=True)
    
    
    print(df_twitter_mx['Tweet'][0])
    print(df_twitter_mx['influence'][0])
    print(df_twitter_mx['Replies'][0])
    print(df_twitter_mx['Likes'][0])
    print(df_twitter_mx['Retweets'][0])
    
    
    
    print(df_twitter_mx['Positive_sentiment'][0])
    print(df_twitter_mx['Negative_sentiment'][0])
    print(df_twitter_mx['Neutral_sentiment'][0])
    print(df_twitter_mx['Compound'][0])
    
    print(df_twitter_mx['Tweet'][1])
    print(df_twitter_mx['influence'][1])
    print(df_twitter_mx['Replies'][1])
    print(df_twitter_mx['Likes'][1])
    print(df_twitter_mx['Retweets'][1])
    
    
    
    print(df_twitter_mx['Positive_sentiment'][1])
    print(df_twitter_mx['Negative_sentiment'][1])
    print(df_twitter_mx['Neutral_sentiment'][1])
    print(df_twitter_mx['Compound'][1])
    
    print(df_twitter_mx['Tweet'][2])
    print(df_twitter_mx['influence'][2])
    print(df_twitter_mx['Replies'][2])
    print(df_twitter_mx['Likes'][2])
    print(df_twitter_mx['Retweets'][2])
    
    
    
    print(df_twitter_mx['Positive_sentiment'][2])
    print(df_twitter_mx['Negative_sentiment'][2])
    print(df_twitter_mx['Neutral_sentiment'][2])
    print(df_twitter_mx['Compound'][2])
    
    print(df_twitter['Compound'].mean())
      #***************************************************************************
    
    neutro = 0
    positivo = 0
    negativo = 0
    
    for row in range(len(df_twitter)):
        if  df_twitter['Compound'][row] >= 0.5 :
        
          positivo = positivo + 1
        
        else: 
        
            if df_twitter['Compound'][row]  <= -0.5 :
            
                negativo = negativo + 1
            
            else: 
                neutro = neutro +1 
            
            pass
    
    porcentaje_positivo = positivo/(positivo + negativo + neutro)
    porcentaje_negativo = negativo/(positivo + negativo + neutro)
    porcentaje_neutro= neutro/(positivo + negativo + neutro)
    
    etiquetas = ['positive', 'negative', 'neutral']
    porcentas = [positivo, negativo, neutro]
    
    #FIGURA 2
    
    plt.pie(porcentas, labels = etiquetas, autopct='%1.1f%%', shadow=True, startangle=90) 
    
    
    
    plt.title("SENTIMENT ANALYSIS", 
      fontdict={'family': 'serif', 
        'color' : 'darkblue',
        'weight': 'bold',
        'size': 18})
    plt.legend()
    plt.show()
    
    print(porcentaje_positivo)
    print(porcentaje_negativo)
    print(porcentaje_neutro)
    
    
    df_twitter_en.reset_index(inplace=True, drop=False)
    df_twitter_es.reset_index(inplace=True, drop=False)
    df_twitter_fr.reset_index(inplace=True, drop=False)
    
    
    #FIGURA 2
    
    influence = []
    lista1 = []
    lista2 = []
    filtered_sentence = []
     
    fig, ax = plt.subplots()
    ax.set_ylabel('Nº Tweets')
    ax.set_title('Intent of tweets')
    plt.bar(etiquetas, porcentas)
    plt.show()
    
    for line in range(len(df_twitter_en)):
        sent_tokenize(df_twitter_en['Tweet'][line])
        stop_words = set(stopwords.words('english')) 
        len(stop_words)
        word_tokens = word_tokenize(df_twitter_en['Tweet'][line]) 
    
        for w in word_tokens: 
          if w not in stop_words: 
              filtered_sentence.append(w) 
    
    lista1.extend(filtered_sentence)
    
    x=0 
    
    
    
    for i in range(0, len(lista1)):
        if len(lista1[x]) >= 3:
            lista2.append(lista1[x])
        x=x+1
    
    
    numero = lista2.count("https")
    for x in range (0, numero):
        lista2.remove("https")
    
    fdist = nltk.FreqDist(lista2)
    
    fdist.tabulate(10, cumulative=False)
    
    #GRÁFICO 3
    
    plt.title("FRECUENCY OF ENGLISH WORDS", 
      fontdict={'family': 'serif', 
        'color' : 'darkblue',
        'weight': 'bold',
        'size': 18})
    
    fdist.plot(10, cumulative=False)
    
    #español
    
    lista3 = []
    filtered_sentence2 = []
    lista4 = []
    for line in range(len(df_twitter_es)):
    
        sent_tokenize(df_twitter_es['Tweet'][line])
        stop_words = set(stopwords.words('spanish')) 
        len(stop_words)
        word_tokens = word_tokenize(df_twitter_es['Tweet'][line]) 
    
    for w in word_tokens: 
      if w not in stop_words: 
          filtered_sentence2.append(w) 
    
    lista3.extend(filtered_sentence2)
    
    x=0 
    
    for i in range(0, len(lista3)):
        if len(lista3[x]) >= 3:
            lista4.append(lista3[x])
        x=x+1
    
    
    numero = lista4.count("https")
    for x in range (0, numero):
        lista4.remove("https")
    
    
    fdist = nltk.FreqDist(lista4)
    
    #GRÁFICO 4
    
    plt.title("FRECUENCY OF SPANISH WORDS", 
      fontdict={'family': 'serif', 
        'color' : 'darkblue',
        'weight': 'bold',
        'size': 18})
    
    
    fdist.tabulate(10, cumulative=False)
    
    fdist.plot(10, cumulative=False)
    
    
    #############################################################################
    
    ### CHI-SQUARED TEST ###
    from scipy.stats import chi2_contingency
    import seaborn as sns
    import matplotlib.pyplot as plt
    #%matplotlib inline #wrong sintax why?????
    
    
    #creacion de una nueva columna con la clasificacion del sentimiento
    df_twitter['Sent'] = 0
    
    
    #CHECK THE COMPOUND BINS FOR POS, NEG, AND NEU ARE OKAY
    #asignacion de valores a la columna de sentimiento
    for row in range(len(df_twitter)):
        if  df_twitter['Compound'][row] >= 0.5 :
        
          df_twitter['Sent'][row] = 'Positive'
        
        else: 
        
            if df_twitter['Compound'][row]  <= -0.5 :
            
                df_twitter['Sent'][row] = 'Negative'
            
            else: 
                df_twitter['Sent'][row] = 'Neutral'
    
    
    
    #subset utilizando unicamente los tweets en idiomas que nos interesan
    df_x = df_twitter[(df_twitter['Lang']=='en') 
            | (df_twitter['Lang']=='es') 
            | (df_twitter['Lang']=='fr') 
            | (df_twitter['Lang']=='pl')
            | (df_twitter['Lang']=='pt')]
    
    #contingency table para el chi-square test
    contingency= pd.crosstab(df_x['Lang'], df_x['Sent'])
    contingency
    #la misma tabla con %s
    contingency_pct = pd.crosstab(df_x['Lang'], df_x['Sent'], normalize='index')
    contingency_pct
    #plot de la distribucion
    plt.figure(figsize=(12,8)) 
    sns.heatmap(contingency, annot=True, cmap="YlGnBu") #NO FUNCIONA - 'sns' not defined?
    
    
    #chi-square test
    c, p, dof, expected = chi2_contingency(contingency)
    #p-value
    print(p) #p-value < 0.05 significa que, con un nivel de confianza del 95%, el senimiento no es independiente del idioma
    # conclusion: existen diferentes valoraciones de la app en diferentes paises/idiomas
    if p <= 0.05:
        print('There is evidence that opinions vary across countries')
    else: print('The opinion about'& x & ' is homogeneous across countries')
    
    
    ### SUBSETS STATS ###
    prueba = df_twitter[(df_twitter['Lang']=='es')].shape[0]
    prueba
    
    #media de compound por pais
    me = df_x[['Lang', 'Compound']].groupby(['Lang']).mean()
    me
    
    #tweets de cada sentimiento (prueba: este analisis ya lo tenemos)
    num = df_x[['Lang', 'Sent']].groupby(['Sent']).count()
    num
    
    #tweets de cada sentimiento por pais
    tab = pd.crosstab(df_x['Lang'], df_x['Sent'])
    tab
    
    #popularidad de los tweets segun sentimiento
    popxsent = df_x[['influence', 'Sent']].groupby(['Sent']).mean()
    popxsent
    
    
    ############################## Plot a map ######################################
    
    key = keys.oauth_maps()
    
    # # initialize Nominatim API
    # geolocator = Nominatim(user_agent="geoapiExercises")
    
    
    # city = []
    # state = []
    # country = []
    # zipcode = []
    
    
    # for row in range(len(df_googlemaps)):
    #     # Latitude & Longitude input
    #     Latitude = row['Latitude'].astype(str)
    #     Longitude = row['Longitud'].astype(str)
    
    #     location = geolocator.reverse(Latitude+","+Longitude)
      
    #     address = location.raw['address']
    #     city.append(address.get('city', ''))
    #     state.append(address.get('state', ''))
    #     country.append(address.get('country', ''))
    #     zipcode.append(address.get('postcode'))
    
    # df_googlemaps['City'] = city
    # df_googlemaps['State'] = state
    # df_googlemaps['Country'] = country
    # df_googlemaps['Zipcode'] = zipcode
    
    
    
    lat, lon = 0, 0
    bokeh_width, bokeh_height = 1000,800
    
    gmaps.configure(api_key=key["API_key"])
    df_googlemaps['Radius'] = df_googlemaps['Total_Ratings']/1
    
    def plot(lat, lng, zoom=2, map_type='roadmap'):
        gmap_options = GMapOptions(lat=lat, lng=lng, 
                    map_type=map_type, zoom=zoom)
    
        hover = HoverTool(
            tooltips = [
                ('Name', '@Name'),
                ('Rating', '@Rating{0.0} stars'), 
                ('Total_Ratings', '@Total_Ratings reviews'), 
                ]
        )
        p = gmap(key["API_key"], gmap_options, title='Mundo', 
          width=bokeh_width, height=bokeh_height,tools=[hover,'reset','wheel_zoom','pan'])
        
        source = ColumnDataSource(df_googlemaps)
        center = p.circle('Longitud', 'Latitud', size='Radius', alpha=0.5, color='red',source=source)
        show(p)
        return p
    
    p = plot(lat, lon)

#############################################################################
    
  
    
    
    
    # prueba = df_twitter[df_twitter['Tweet'].str.contains("trust")]
    # list_reviews = df_googlemaps['Reviews'].tolist()
    # for review in list_reviews:
    #     for comentary in review:
    #         print(comentary['author_name'])
        
    
    
    # prueba = sia.polarity_scores(df_twitter['Tweet'][0])['neg']
    
        
    # df_lang = df_twitter['Lang'].value_counts()
    
    # hist = df_lang.hist()  


        
    

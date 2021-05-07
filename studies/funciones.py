# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 18:33:02 2021

@author: Xabi
"""

def collectData(busqueda,pk):
    from . import keys
    import requests
    import json
    import sys, os
    from nltk.sentiment import SentimentIntensityAnalyzer
    # import nltk

    import pandas as pd
    import gmaps
    from . import keys

    from bokeh.io import show
    from bokeh.plotting import gmap
    from bokeh.models import GMapOptions
    from bokeh.models import ColumnDataSource
    from bokeh.models import HoverTool

    import numpy as np
    from geopy.geocoders import Nominatim
    import matplotlib.pyplot as plt

    import nltk

    from nltk import tokenize
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.probability import FreqDist

    import io
    import urllib, base64
    from .models import Estudio, Tweet, Review, Category
    error = ''

    try:
    
        print('\n\nComenzamos con el procesado\n\n')
        error = 'maps'
        ########################### Google Maps Data ##################################
        
        ##--------Variables and functions--------##
        
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
        
            search_url="https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input="+ required_params["input"]+ " " + country+"&inputtype=" + required_params["inputtype"]+"&fields="+ required_params["fields"]+"&key=" + required_params["api_key"]
            
            response=connect_to_endpoint(search_url)
            if json.loads(response.text)['status'] != "ZERO_RESULTS": 
                place_id = json.loads(response.text)['candidates'][0]['place_id']
                list_place_ids.append(place_id)
        
        list_place_ids = list(set(list_place_ids)) #elimina duplicados 
        
        
        ##--------Place Details--------##
        
        data_googlemaps = []
        required_params_details = {"fields": "name,geometry,rating,review,user_ratings_total",
                                    "api_key": key["API_key"]
                                    }
        for place_id in list_place_ids:
            
            search_url_details="https://maps.googleapis.com/maps/api/place/details/json?place_id="+ place_id +"&fields=" + required_params_details["fields"] + "&key=" + required_params_details["api_key"]
            
            response_details=connect_to_endpoint(search_url_details)
            if json.loads(response_details.text)['status'] == "OK":
                data_googlemaps.append(json.loads(response_details.text)['result'])
        
        # Eliminamos registros que no tengan la palabra deseada
        
        data_googlemaps = [item for item in data_googlemaps if busqueda in item['name'].lower()]
            
        error = 'twitter'
        ########################## Twitter data #####################################
        
        ##--------Variables and functions--------##
            
        keys_twitter = keys.oauth()
            
        bearer_token    = keys_twitter["bearer_token"]
        ntweets         = 100
        count           = 0 
        
        def create_headers(bearer_token):
            headers = {"Authorization": "Bearer {}".format(bearer_token)}
            return headers
        
        
        def connect_to_endpoint_twitter(url, headers):
            response = requests.request("GET", url, headers=headers)
            #print(response.status_code)
            if response.status_code != 200:
                raise Exception(response.status_code, response.text)
            return response.json()
        
        
        ##--------Twitter API Call--------##
        
        headers = create_headers(bearer_token)
        data_twitter = []
        autores = []
        
        while (count<1500):
            if count == 0:
                request_url     = "https://api.twitter.com/2/tweets/search/recent?query="+ busqueda + "&tweet.fields=" + "created_at,text,public_metrics,lang,geo"+"&max_results=" + str(ntweets) +"&expansions=author_id&user.fields=name,username,profile_image_url"
                json_response_twitter = connect_to_endpoint_twitter(request_url, headers)
                for tweet in json_response_twitter['data']:    
                    data_twitter.append(tweet)
                for author in json_response_twitter['includes']['users']:
                    autores.append(author)
                count += ntweets
                
                
            elif count < 1500:
                request_url     = "https://api.twitter.com/2/tweets/search/recent?query="+ busqueda + "&tweet.fields=" + "created_at,text,public_metrics,lang,geo"+ "&max_results=" + str(ntweets)+"&expansions=author_id&user.fields=name,username,profile_image_url" + "&next_token="+ json_response_twitter['meta']['next_token']
                json_response_twitter = connect_to_endpoint_twitter(request_url, headers)
                for tweet in json_response_twitter['data']:    
                    data_twitter.append(tweet)
                for author in json_response_twitter['includes']['users']:
                    autores.append(author)
                count += ntweets

        
        plt.switch_backend('agg')
        df_googlemaps= pd.DataFrame(data_googlemaps)
        df_twitter_v0= pd.DataFrame(data_twitter) 
        
        latitud = []
        longitud = []
        for row in range(len(df_googlemaps)):
            latitud.append(df_googlemaps['geometry'][row]['location']['lat'])
            longitud.append(df_googlemaps['geometry'][row]['location']['lng'])
        
        df_googlemaps['Latitud'] = latitud
        df_googlemaps['Longitud'] = longitud
        
        # Eliminamos colummnas innecesarias del dataframe y renombramos
        df_googlemaps.rename(columns={'name': 'Name',
                                    'rating': 'Rating',
                                    'reviews': 'Reviews',
                                    'user_ratings_total': 'Total_Ratings',
                                    },inplace=True)
        
        df_twitter_v0.rename(columns={ 'lang': 'Lang',
                                    'text': 'Tweet',
                                    'public_metrics.like_count': 'Likes',
                                    'public_metrics.quote_count': 'Quotes',
                                    'public_metrics.reply_count':'Replies',
                                    'public_metrics.retweet_count':'Retweets',
                                    'geo.place_id':'Place_id'
                                    },inplace=True)
        # try:
        #     df_googlemaps.drop(columns=['geometry.viewport.northeast.lat','geometry.viewport.northeast.lng','geometry.viewport.southwest.lat','geometry.viewport.southwest.lng'],axis=1,inplace=True)
        # except:    
        #     print('No google maps data')
            
        # df_twitter = df_twitter_v0.drop_duplicates('Tweet', keep="first")
        # df_twitter.reset_index(inplace=True, drop=False)
        
        likes = []
        rt = []
        replies = []
        for row in range(len(df_twitter_v0)):
            rt.append(df_twitter_v0['public_metrics'][row]['retweet_count'])
            likes.append(df_twitter_v0['public_metrics'][row]['like_count'])
            replies.append(df_twitter_v0['public_metrics'][row]['reply_count'])
            
        df_twitter_v0['Likes']     = likes
        df_twitter_v0['Retweets']  = rt
        df_twitter_v0['Replies']   = replies
        
        # Pasamos los tweets por la libreria NLTK
        sia = SentimentIntensityAnalyzer()
        sentiments_positive = []
        sentiments_negative = []
        sentiments_neutral = []
        sentiments_compound = []
        
        for row in range(len(df_twitter_v0)):
            sentiments_positive.append(sia.polarity_scores(df_twitter_v0['Tweet'][row])['pos'])
            sentiments_negative.append(sia.polarity_scores(df_twitter_v0['Tweet'][row])['neg'])
            sentiments_neutral.append(sia.polarity_scores(df_twitter_v0['Tweet'][row])['neu'])
            sentiments_compound.append(sia.polarity_scores(df_twitter_v0['Tweet'][row])['compound'])
        
        df_twitter_v0['Positive_sentiment']= sentiments_positive
        df_twitter_v0['Negative_sentiment']= sentiments_negative
        df_twitter_v0['Neutral_sentiment'] = sentiments_neutral
        df_twitter_v0['Compound']          = sentiments_compound
        
        # list_reviews = df_googlemaps['Reviews'].tolist()
        df_twitter = df_twitter_v0.drop_duplicates('Tweet', keep="first")   
        df_twitter.reset_index(drop=True, inplace=True)

        df_twitter['Author_name'] = "Anonimo"
        df_twitter['Author_username'] = "Anonimo"
        df_twitter['Author_image'] = "Not found"
        
        for row in range(len(df_twitter['author_id'])):
            for _id in range(len(autores)):
                if df_twitter['author_id'][row] == autores[_id]['id']:
                    df_twitter['Author_name'][row] = autores[_id]['name']
                    df_twitter['Author_username'][row] = autores[_id]['username']
                    df_twitter['Author_image'][row] = autores[_id]['profile_image_url']
                        
            
        # Creamos subset por idiomas [en,es,fr,de,it,pt,pl] en df_twitter
        df_twitter_en = df_twitter[df_twitter['Lang']=='en']
        df_twitter_es = df_twitter[df_twitter['Lang']=='es']
        # df_twitter_fr = df_twitter[df_twitter['Lang']=='fr']
        # df_twitter_de = df_twitter[df_twitter['Lang']=='de']
        # df_twitter_it = df_twitter[df_twitter['Lang']=='it']
        # df_twitter_pt = df_twitter[df_twitter['Lang']=='pt']
        # df_twitter_pl = df_twitter[df_twitter['Lang']=='pl']
        
        error='data'
        ############################## Plot a map ######################################
        
        key = keys.oauth_maps()  
        # initialize Nominatim API
        geolocator = Nominatim(user_agent="geoapiExercises")
        
        city = []
        state = []
        country = []
        zipcode = []
        
        for row in range(len(df_googlemaps)):
            # Latitude & Longitude input
            Latitude = str(df_googlemaps['Latitud'][row])
            Longitude = str(df_googlemaps['Longitud'][row])
            
            location = geolocator.reverse(Latitude+","+Longitude)
            
            address = location.raw['address']
            city.append(address.get('city', ''))
            state.append(address.get('state', ''))
            country.append(address.get('country', ''))
            zipcode.append(address.get('postcode'))
        
        df_googlemaps['City'] = city
        df_googlemaps['State'] = state
        df_googlemaps['Country'] = country
        df_googlemaps['Zipcode'] = zipcode
        
        Radius = []
        
        for row in range(len(df_googlemaps)):
            if df_googlemaps['City'][row] == '':
                df_googlemaps['City'][row] = df_googlemaps['State'][row]
        
            if df_googlemaps['Total_Ratings'][row]>=0 and df_googlemaps['Total_Ratings'][row] <10:
                pendiente=Radius.append(0.5*df_googlemaps['Total_Ratings'][row])
                Radius.append(pendiente)
            elif df_googlemaps['Total_Ratings'][row]>=10 and df_googlemaps['Total_Ratings'][row] <100:
                pendiente=(1/18)*df_googlemaps['Total_Ratings'][row]+4.44
                Radius.append(pendiente)
            elif df_googlemaps['Total_Ratings'][row]>=100 and df_googlemaps['Total_Ratings'][row] <1000:
                pendiente=(1/180)*df_googlemaps['Total_Ratings'][row]+9.44
                Radius.append(pendiente)
            elif df_googlemaps['Total_Ratings'][row]>=1000 and df_googlemaps['Total_Ratings'][row] <10000:
                pendiente=(1/1800)*df_googlemaps['Total_Ratings'][row]+14.44
                Radius.append(pendiente)
            elif df_googlemaps['Total_Ratings'][row] >=10000:
                pendiente=24
                Radius.append(pendiente)
                
        Radius = list(filter(None, Radius))    
        df_googlemaps['Radius'] = Radius        
        
        lat, lon = 0, 0
        bokeh_width, bokeh_height = 1000,800
        
        gmaps.configure(api_key=key["API_key"])
        
        def plot(lat, lng, zoom=2, map_type='roadmap'):
            gmap_options = GMapOptions(lat=lat, lng=lng, 
                                        map_type=map_type, zoom=zoom)
            
            hover = HoverTool(
                tooltips = [
                    ('Name', '@Name'),
                    ('City', '@City'),
                    ('Country', '@Country'),
                    ('Rating', '@Rating{0.0} stars'), 
                    ('Total_Ratings', '@Total_Ratings reviews'), 
                ]
            )
            p = gmap(key["API_key"], gmap_options, title='Mundo', 
                    width=bokeh_width, height=bokeh_height,tools=[hover,'reset','wheel_zoom','pan'])
            
            source = ColumnDataSource(df_googlemaps)
            center = p.circle('Longitud', 'Latitud', size='Radius', alpha=0.5, color='red',source=source)
            fig = plt.gcf()
            #convert graph into dtring buffer and then we convert 64 bit code into image
            buf = io.BytesIO()
            fig.savefig(buf,format='png')
            buf.seek(0)
            string = base64.b64encode(buf.read())
            uri_fig =  urllib.parse.quote(string)
            return uri_fig
        
        uri_fig = plot(lat, lon)
        
        # fig = plt.gcf()
        # #convert graph into dtring buffer and then we convert 64 bit code into image
        # buf = io.BytesIO()
        # fig.savefig(buf,format='png')
        # buf.seek(0)
        # string = base64.b64encode(buf.read())
        # uri =  urllib.parse.quote(string)
        # return uri
        

        #############################################################################
        
        #********CALCULO DE LOS 3 TWEETS MAS INFLUYENTES*******************************
        
        df_twitter['influence'] = df_twitter[['Likes', 'Replies', 'Retweets']].sum(axis=1)
        
        df_twitter_mx           = df_twitter.sort_values(by =['influence'], ascending=[False], ignore_index=True)
        
        df_twitter_3_most_important = df_twitter_mx[df_twitter_mx.index.isin([0,1,2])]
        
        #############################################################################
        
        
        #***************  % DE TWEETS POS/NEG/NEUTROS    ******************************
        
        percentage_positives    = (df_twitter[df_twitter['Compound']>0.5].count())['Compound']/(len(df_twitter))
        percentage_negatives    = (df_twitter[df_twitter['Compound']<-0.5].count())['Compound']/(len(df_twitter))
        percentage_neutrals     = 1-(percentage_positives+percentage_negatives)
        
        #Ploteamos en un PIE?
        etiquetas = ['Positive', 'Negative', 'Neutral']
        porcentajes = [percentage_positives, percentage_negatives, percentage_neutrals]
        explode = (0.1, 0.1, 0.1)
        colors = ["red", "salmon", "mistyrose"]
        
        plt.pie(porcentajes, labels = etiquetas, autopct='%1.2f%%', shadow=True, startangle=90, colors=colors,explode=explode) 
        
        plt.title("SENTIMENT ANALYSIS", 
                fontdict={'family': 'serif', 
                            'color' : 'darkred',
                            'weight': 'bold',
                            'size': 18})
        plt.legend()
        #plt.show()
        
        fig = plt.gcf()
        #convert graph into dtring buffer and then we convert 64 bit code into image
        buf = io.BytesIO()
        fig.savefig(buf,format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri_fig1 =  urllib.parse.quote(string)
        
        
        #Ploteado como barras y con numero de tweets
        
        colors = ["red", "salmon", "mistyrose"]
        ntweets = [percentage_positives*(len(df_twitter)), percentage_negatives*(len(df_twitter)), percentage_neutrals*(len(df_twitter))]
        
        fig, ax = plt.subplots()
        ax.set_xlabel('Nº Tweets')
        ax.set_ylabel('Sentiment')
        # ax.set_title('Intent of tweets')
        ax.barh(etiquetas, ntweets, color=colors)
        plt.title("Sentiment of tweets", 
                fontdict={'family': 'serif', 
                            'color' : 'darkred',
                            'weight': 'bold',
                            'size': 18})
        #plt.show()
        
        fig = plt.gcf()
        #convert graph into dtring buffer and then we convert 64 bit code into image
        buf = io.BytesIO()
        fig.savefig(buf,format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri_fig2 =  urllib.parse.quote(string)
        
        #############################################################################
        
        
        #***********  N tweets por idioma  *************************
        
        # De los idiomas con más de 30 tweets
        
        df_lang = pd.DataFrame(df_twitter['Lang'].value_counts())
        df_lang = df_lang[ df_lang.index != 'und' ]
        df_lang = df_lang[ df_lang['Lang'] >= 20 ]
        
        colors = ["darkred", "firebrick", "indianred", "lightcoral","salmon", "mistyrose"]
        
        from iso_language_codes import language
        
        languages = []
        for row in range(len(df_lang)):
            try:
                idioma = language(df_lang.index[row])
                languages.append(idioma['Name'])
            except:
                languages.append(df_lang.index[row].capitalize())
            
            
        fig, ax = plt.subplots()
        ax.set_ylabel('Nº Tweets')
        ax.set_xlabel('Languages')
        def autolabel(rects):
            for idx,rect in enumerate(bar_plot):
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                        df_lang['Lang'][idx],
                        ha='center', va='bottom', rotation=0, color='darkred',weight='bold')
        bar_plot  = ax.bar(languages, df_lang['Lang'], color=colors)
        autolabel(bar_plot)
        
        limit = max(df_lang['Lang'])
        plt.ylim(0,1.5*limit)
        
        plt.title("Tweets per language", 
                fontdict={'family': 'serif', 
                            'color' : 'darkred',
                            'weight': 'bold',
                            'size': 18})
        #plt.show()
        
        fig = plt.gcf()
        #convert graph into dtring buffer and then we convert 64 bit code into image
        buf = io.BytesIO()
        fig.savefig(buf,format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri_fig3 =  urllib.parse.quote(string)
        
        
        #############################################################################
        
        
        #***********  Palabras más repetidas  *************************
        
        df_twitter_en.reset_index(inplace=True, drop=False)
        df_twitter_es.reset_index(inplace=True, drop=False)
        # influence = []
        lista1 = []
        lista2 = []
        filtered_sentence = []
        
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
                            'color' : 'darkred',
                            'weight': 'bold',
                            'size': 18})
        fdist.plot(10, cumulative=False, color= 'darkred')
        
        fig = plt.gcf()
        #convert graph into dtring buffer and then we convert 64 bit code into image
        buf = io.BytesIO()
        fig.savefig(buf,format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri_fig4 =  urllib.parse.quote(string)
        
        # In spanish
        
        
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
                            'color' : 'darkred',
                            'weight': 'bold',
                            'size': 18})
        
        fdist.tabulate(10, cumulative=False)
        
        fdist.plot(10, cumulative=False, color= 'darkred')
        
        fig = plt.gcf()
        #convert graph into dtring buffer and then we convert 64 bit code into image
        buf = io.BytesIO()
        fig.savefig(buf,format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri_fig5 =  urllib.parse.quote(string)
        
        #############################################################################
        
        
        #*************  Media de rt,favs,replies de los pos,neg,neu  *******************
        
        df_positives    = df_twitter[df_twitter['Compound']>0.5]
        df_negatives    = df_twitter[df_twitter['Compound']<-0.5]
        df_neutral      = df_twitter[df_twitter['Compound']>=-0.5]
        df_neutral      = df_neutral[df_neutral['Compound']<=0.5]
        
        # medias = []
        rt = []
        fav = []
        reply = []
        
        rt.append(df_positives['Retweets'].mean())
        rt.append(df_negatives['Retweets'].mean())
        rt.append(df_neutral['Retweets'].mean())
        
        fav.append(df_positives['Likes'].mean())
        fav.append(df_negatives['Likes'].mean())
        fav.append(df_neutral['Likes'].mean())
        
        reply.append(df_positives['Replies'].mean())
        reply.append(df_negatives['Replies'].mean())
        reply.append(df_neutral['Replies'].mean())
        
        medias = [rt,fav,reply]
        
        colors = ["firebrick", "indianred", "lightcoral"]
        etiquetas = ['Positive', 'Negative', 'Neutral']
        
        
        X = np.arange(3)
        fig = plt.figure()
        ax = fig.add_axes([0,0,1,1])
        ax.bar(X - 0.25, medias[0], color = colors[0], width = 0.25, label='Retweets')
        ax.bar(X + 0.00, medias[1], color = colors[1], width = 0.25, label='Likes')
        ax.bar(X + 0.25 , medias[2], color = colors[2], width = 0.25, label='Replies')
        
        plt.xticks(X, ('Positive', 'Negative', 'Neutral'))
        ax.set_ylabel('Number of tweets')
        ax.set_xlabel('Sentiment')
        plt.legend()
        
        plt.title("Retweet,Likes and Reply counts", 
                fontdict={'family': 'serif', 
                            'color' : 'darkred',
                            'weight': 'bold',
                            'size': 18})
        plt.grid()
        #plt.show()
        
        fig = plt.gcf()
        #convert graph into dtring buffer and then we convert 64 bit code into image
        buf = io.BytesIO()
        fig.savefig(buf,format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri_fig6 =  urllib.parse.quote(string)
        
        #############################################################################
        
        
        #*************  Media de compound de los tweets  *******************
        
        # df_compound = df_twitter[df_twitter['Compound']>0.5]        
        
        df_compound = df_twitter[df_twitter['Lang'].isin(df_lang.index.tolist())]
        means = []
        for idioma in df_lang.index.tolist():
            mean = df_compound[df_compound['Lang']==idioma]['Compound'].mean()
            means.append(mean)
            
        fig, ax = plt.subplots()
        ax.set_ylabel('Compound mean')
        ax.set_xlabel('Languages')
            
        markerline, stemlines, baseline = plt.stem(languages, means, linefmt='salmon',markerfmt='or')
        markerline.set_markerfacecolor('darkred')
        plt.setp(baseline, 'color', 'darkred', 'linewidth', 2)
        
        plt.title("Compound mean by language", 
                fontdict={'family': 'serif', 
                            'color' : 'darkred',
                            'weight': 'bold',
                            'size': 18})
        #plt.show()
        
        fig = plt.gcf()
        #convert graph into dtring buffer and then we convert 64 bit code into image
        buf = io.BytesIO()
        fig.savefig(buf,format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri_fig7 =  urllib.parse.quote(string)
        
        #############################################################################
        
        
        #************************  CHI squared test ******************************
        
        from scipy.stats import chi2_contingency
        import seaborn as sns
        
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
        # if p <= 0.05:
        #     print('There is evidence that opinions vary across countries')
        # else: print('The opinion about'& x & ' is homogeneous across countries')
        
        
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
        
        fig = plt.gcf()
        #convert graph into dtring buffer and then we convert 64 bit code into image
        buf = io.BytesIO()
        fig.savefig(buf,format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri_fig8 =  urllib.parse.quote(string)
        
        #############################################################################
        
        
        #************************  Tweets por dia? ******************************
        
        df_time = df_twitter
        df_time['Year'] = 0
        df_time['Month'] = 0
        df_time['Day'] = 0
        
        for row in range(len(df_time)):
            df_time['Year'][row] = (str(df_time['created_at'][row])).split('-')[0]
            df_time['Month'][row]= (str(df_time['created_at'][row])).split('-')[1]
            df_time['Day'][row]  = ((str(df_time['created_at'][row])).split('-')[2]).split('T')[0]
        
            
        df_time = df_time.groupby(["Year","Month","Day"],as_index=False,sort=True)['id'].count()
        df_time['Date'] = df_time["Year"].map(str) + "-" + df_time["Month"].map(str) + "-" + df_time["Day"].map(str) 
        
        colors = ["darkred", "firebrick", "indianred", "lightcoral","salmon", "mistyrose"]
        
        dias = df_time['Date'].unique().tolist()
        tweets_dia = []
        for dia in dias: 
            tweets_dia.append(int(df_time[df_time['Date']==dia]['id'].to_string(index=False)))
        
        fig, ax = plt.subplots()
        ax.set_ylabel('Nº Tweets')
        ax.set_xlabel('Days')
        
        def autolabel(rects):
            for idx,rect in enumerate(bar_plot):
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                        tweets_dia[idx],
                        ha='center', va='bottom', rotation=0, color='darkred',weight='bold')
        
        bar_plot= ax.bar(dias, tweets_dia, color="salmon", width=1/len(dias))
        autolabel(bar_plot)
            
        limit = max(tweets_dia)
        plt.ylim(0,1.5*limit)
        
        plt.title("Tweets per day", 
                fontdict={'family': 'serif', 
                            'color' : 'darkred',
                            'weight': 'bold',
                            'size': 18})
        #plt.show()
        
        fig = plt.gcf()
        #convert graph into dtring buffer and then we convert 64 bit code into image
        buf = io.BytesIO()
        fig.savefig(buf,format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri_fig9 =  urllib.parse.quote(string)
    
        
        

        sen_predominante = ""

        if (percentage_negatives > percentage_neutrals + percentage_positives):
            sen_predominante = "negative"
        elif (percentage_neutrals > percentage_negatives + percentage_positives):
            sen_predominante = "neutral"
        elif (percentage_positives > percentage_negatives + percentage_neutrals):
            sen_predominante = "positive"

        data_obj = Estudio.objects.get(pk=pk)
        for x in range(3):
            tweet_obj = Tweet(text=df_twitter_3_most_important.loc[x, ['Tweet']].values[0],
                            created=df_twitter_3_most_important.loc[x, ['created_at']].values[0],
                            likes=df_twitter_3_most_important.loc[x, ['Likes']].values[0],
                            retweets=df_twitter_3_most_important.loc[x, ['Retweets']].values[0],
                            replies=df_twitter_3_most_important.loc[x, ['Replies']].values[0],
                            neg_sen=df_twitter_3_most_important.loc[x, ['Negative_sentiment']].values[0] * 100,
                            neu_sen=df_twitter_3_most_important.loc[x, ['Neutral_sentiment']].values[0] * 100,
                            pos_sen=df_twitter_3_most_important.loc[x, ['Positive_sentiment']].values[0] * 100,
                            username=df_twitter_3_most_important.loc[x, ['Author_name']].values[0],
                            picture=df_twitter_3_most_important.loc[x, ['Author_image']].values[0],
                            name=df_twitter_3_most_important.loc[x, ['Author_name']].values[0],
                            quotes=0, placeID=0)
            tweet_obj.save()
            data_obj.tweets.add(tweet_obj)
        error = ''
        Estudio.objects.filter(pk=pk).update(graph1=uri_fig1, graph2=uri_fig2, graph3=uri_fig3,
                                            graph4=uri_fig4, graph5=uri_fig5, graph6=uri_fig6, graph7=uri_fig7
                                            ,graph8=uri_fig8, graph9=uri_fig9, graph10=uri_fig,
                                            neg_sen=percentage_negatives
                                            ,neu_sen=percentage_neutrals
                                            ,pos_sen=percentage_positives
                                            , sen_predominant=sen_predominante
                                            , completed=True
                                            , success=True)

        print('\n\n\nPROCESAMIENTO TERMINADO EN EL BACKEND\n\n\n')
    
    except Exception as e:
        print('El error es: ',e)
        print(e.with_traceback)
        print("Oops!", sys.exc_info()[0], "occurred.")
        print('El error se ha dado en: ',error)
        data_obj = Estudio.objects.get(pk=pk)
        Estudio.objects.filter(pk=pk).update(completed=True, success=False, error= error)
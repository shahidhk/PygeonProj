from firebasic import add_event
from dateutil import parser
import urllib2
import ssl
import json
import bs4
import datetime
import random

CITIES = set([str(i.lower()) for i in json.loads(open("../../../TDS/Spiders/cities.json", 'r').read()).keys()])

def getHax():
    for i in CITIES:
        url = "https://www.hackathon.com/city/india/" + i
        url.replace(' ', '%20')
        print "LOG: Scraping city:", str(i)
        print "URL:", url
        content = ssl._create_unverified_context()
        resp = urllib2.urlopen(url, context = content)
        soup = bs4.BeautifulSoup(resp.read(), "html.parser")
        results = soup.findAll("div", {"class":"ht-eb-card"})
        for i in results:
            title = i.find("a", {"class":"ht-eb-card__title"})
            resp2 = urllib2.urlopen(title.attrs["href"], context = content)
            soup = bs4.BeautifulSoup(resp2.read(), 'html.parser')
            print soup.prettify()
            title = soup.h1.text
            organiser = soup.find("div", {"class":"event__organizer"}).a.text
            link = soup.findAll("a", {"class": "button large"})[1]['href']
            place = soup.findAll("div", {"class": "small-10 small-order-2 medium-order-1 columns"})[0].a.text
            dates = parser.parse(soup.findAll("div", {"class": "small-10 small-order-2 medium-order-1 columns"})[1].text.split("To")[0].split("From ")[1]) - datetime.datetime(1970, 1, 1, 0 ,0)
            dates = dates.total_seconds()
            desc = soup.find("div", {'class':'event-description__text'}).text
            print title
            print organiser
            print link
            print dates
            print desc
            print place

            event_dict = {
                'name': title,
                'epoch': dates,
                'link': link,
                'by': organiser,
                'date': dates,
                'description': desc}

            eid = title[:2] + str(random.sample(range(1,10000), 1)[0])
            add_event('Technology', 'Hackathons',
                      place, event_dict, eid)

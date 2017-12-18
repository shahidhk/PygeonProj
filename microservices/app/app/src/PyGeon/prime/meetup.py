from bs4 import BeautifulSoup as soup
from pprint import pprint
from firebasic import add_event
from data import cities_list
# from urllib2 import urlopen
# import re
# import pandas as pd
#
# url = 'https://www.meetup.com/find/events/tech/?allMeetups=false&radius=50&userFreeform=Chennai%2C+India&mcNam'
# s = soup(urlopen(url).read(), "lxml")
# from pytz import timezone
#
# ind = timezone('Asia/Kolkata')
#
# for container in s.select('.event-listing-container-li'):
#     try:
#         y, m, d = re.findall(
#             '.container-([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})', container.attrs['data-uniqselector'])[0]
#         timestamp = pd.Timestamp(str(d) + '-' + str(m) + '-' + str(y))
#         for events in container.select('.event-listing'):
#             org = events.select('.text--labelSecondary span')[0].text.strip()
#             event_name = events.select('.event')[0].text.strip()
#             attendee_count = events.select(
#                 '.attendee-count')[0].text.strip().split()[0]
#             x = pd.Timestamp(events.select('.text--secondary time')[0].text)
#             x = x.replace(year=int(y), month=int(m), day=int(d))
#             print(x, event_name)
#
#     except Exception as e:
#         print(e)
#
# import pytz
#
# [i for i in pytz.all_timezones if 'Kolkata' in i]
import time
import requests
import json
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from PLACES import PLACE
import datetime
"""
Scrapes meetup pages not more than 30 days old from India
"""
URL = "https://api.meetup.com"
geolocator = Nominatim()


def cities1():
    """
    :return: The cities in India Meetup
    """
    EXT = "/2/cities?&sign=true&photo-host=public&country=India&page=100"
    r = requests.get(URL + EXT)
    # print(r.text)
    response = json.loads(r.text)
    print(response)
    citys = []
    for city in response["results"]:
        citys.append([city["city"], city["lat"], city["lon"]])
    # print(citys)
    return citys
# cities()


catmap = {"Technology": 34,
          'Photography': 27}


def upcoming_events(category, evname):
    catnum = catmap[category]
    print ("================\n================")
    EXT = "/find/upcoming_events?&sign=true&photo-host=public&page=20&offset="
    """
    Loop throught the offset to get the latest events.
    Stop when you find an event that is already there in the event list
    """
    links = {}
    cities = []
    lat_lon = []
    # with open("cities.json", "r") as f:
    #     ff = json.loads(f.read())
    #     PLACE = ff.keys()
    for city in cities_list:
        print (city)
        try:
            location = geolocator.geocode(city, timeout=None)
            # lat_lon.append([location.latitude,location.longitude])
        except:
            print("Error: geocode failed on input %s with message %s")
            import time
            time.sleep(100)
        # final_url = URL + "/find/upcoming_events?&sign=true&text=photography&key=d1421476f3f654a755b2118c405c74&photo-host=public&lon=" + \
        #     str(location.longitude) + "&page=20&lat=" + \
        #     str(location.latitude) + "&offset="
        final_url2 = URL + "/find/upcoming_events?&sign=true&topic_category=" + str(catnum) + "&key=d1421476f3f654a755b2118c405c74&photo-host=public&lon=" + \
            str(location.longitude) + "&page=20&lat=" + \
            str(location.latitude) + "&offset="
        for i in range(5):
            r = requests.get(final_url2 + str(i))
            response = json.loads(r.text)
            # pprint(response)
            # print(response)
            if len(response["events"]) == 0:
                break
            else:
                for event in response["events"]:
                    name = event["name"]
                    if not 'local_date' in event or not 'venue' in event or not 'group' in event:
                        continue
                    date = event["local_date"]
                    chalu_date = date.split("-")
                    epoch = (datetime.datetime(
                        int(chalu_date[0]), int(chalu_date[1]), int(chalu_date[2]), 0, 0) - datetime.datetime(1970, 1, 1)).total_seconds()
                    time = event["time"]
                    link = event["link"]
                    city_ev = event[u"venue"]["city"]
                    description = ""
                    groupinfo = event['group']
                    if not 'urlname' in groupinfo:
                        continue
                    organiser = groupinfo['urlname']
                    if "description" in event:
                        desc = event["description"]
                        if len(desc) > 50:
                            desc = desc[:47] + '...'
                    else:
                        desc = name
                    if link in links:
                        break
                    else:
                        links[link] = 1

                    event_dict = {
                        'name': name,
                        'epoch': epoch,
                        'link': link,
                        'by': organiser,
                        'date': date,
                        'description': desc}
                    eid = event['id']

                    try:
                        add_event(category, evname,
                                  city, event_dict, eid)
                    except Exception as e:
                        print (e)
                    print (city)
        print(len(links))

        # for
# if __name__ == "__main__":
    # upcoming_events("Photography", 'Meetups')

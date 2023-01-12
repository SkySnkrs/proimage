import requests
import json
from colorama import init, Fore, Back, Style
import time 
import datetime
from urllib.parse import urlparse
import os
import glob
import argparse
import keyboard
from http.cookies import SimpleCookie
import urllib.parse
from twocaptcha import TwoCaptcha
from bs4 import BeautifulSoup


def colorama():
    init()
    # all available foreground colors
    FORES = [ Fore.BLACK, Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE ]
    # all available background colors
    BACKS = [ Back.BLACK, Back.RED, Back.GREEN, Back.YELLOW, Back.BLUE, Back.MAGENTA, Back.CYAN, Back.WHITE ]
    # brightness values
    BRIGHTNESS = [ Style.DIM, Style.NORMAL, Style.BRIGHT ]
    return FORES,BACKS,BRIGHTNESS

def print_with_color(s, color=Fore.WHITE, brightness=Style.NORMAL, **kwargs):
    print(f"{brightness}{color}{s}{Style.RESET_ALL}", **kwargs)

def getcookies():
    url = 'https://proimagesports.com/'
    
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }
    
    response = requests.get(url, headers=headers)
    
    cookies = response.cookies
    
    xsrftoken = response.cookies.get("XSRF-TOKEN")
    xsrf = urllib.parse.unquote(xsrftoken)
    
    print(xsrf)
    return headers, cookies, xsrf

    
def checkstock(headers):
    while True:
            url = 'https://proimagesports.com/check/quantity/64549'
            
            response = requests.get(url, headers=headers)
            
            response_data = response.json()
            qty = response_data['qty']
            
            if qty == 0:
                print('Out-Of-Stock')
                time.sleep(1)
            elif qty > 0:
                print('In-Stock:' + " " + str(response_data['qty']))
                break;


def addtocart(headers, cookies):
    #Add to Cart, Bypass Cart Goes To Checkout
    url = "https://proimagesports.com/buynow/64549"

    querystring = {"quantity":1}

    response = requests.request("GET", url, headers=headers, params=querystring, cookies=cookies)
    
    html_doc = response.text

    # Parse the HTML document using Beautiful Soup
    soup = BeautifulSoup(html_doc, 'html.parser')

    # Find the 'csrf-token' meta tag
    csrf_meta_tag = soup.find('meta', {'name': 'csrf-token'})
    
    # Extract the value of the 'content' attribute from the meta tag
    csrf_token = csrf_meta_tag['content']
   
    
    itemname_divclass = soup.find('div', {'class': 'item-name'})
    
    print("Carted->" + " " + itemname_divclass.text)
    
    
    return csrf_token, headers


def guestcheckout(headers, csrf_token, cookies):
    #Checkout As Guest
    url = 'https://proimagesports.com/checkout/setGuestSession'

    payload = {
        '_token':csrf_token,
        'email':'tristanm10@outlook.com',
        'account':'account_no'
    }

    headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "x-csrf-token": csrf_token,
    "x-requested-with": "XMLHttpRequest"
    }

    response = requests.post(url, data=payload, headers=headers, cookies=cookies)

    
    

def shipping(headers, csrf_token, cookies, xsrf):
    url = 'https://proimagesports.com/checkout/save-address'
    
    headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "x-csrf-token": csrf_token,
    "x-requested-with": "XMLHttpRequest",
    "x-xsrf-token": xsrf
    }
    
    payload = {
        "billing": {
            "address1": ["1910 Ridge Way"],
            "address2": [""],
            "use_for_shipping": True,
            "first_name": "tristan",
            "last_name": "martinez",
            "email": "skysnkrs@gmail.com",
            "country": "US",
            "state": "ID",
            "city": "MIDDLETON",
            "postcode": "83644",
            "phone": "2085509662",
            "twilio_sms": True
        },
        "shipping": {
            "address1": [""],
            "address2": [""]
        }
    }

    response = requests.post(url, json=payload, headers=headers, cookies=cookies)
    
    
    return headers


def shippingrate(headers, csrf_token, cookies, xsrf):
    url = 'https://proimagesports.com/checkout/shippingrate'
    
    headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "x-csrf-token": csrf_token,
    "x-requested-with": "XMLHttpRequest",
    "x-xsrf-token": xsrf
    }
    
    response = requests.get(url, headers=headers, cookies=cookies)
    
    response_json = response.json()
    
    first_key = list(response_json.keys())[0]

    # Get the value associated with the first key
    first_value = response_json[first_key]
    
    # Get the rates for the seller
    rates = first_value['rates']

    # Get the mpflatrate rate
    mpflatrate = rates['mpflatrate']

    # Get the rate details
    rate_details = mpflatrate['1']

    # Get the values and set them to variables
    price = rate_details['price']
    seller_id = rate_details['sellerId']
    rate_name = 'mpflatrate'

    
    return price, seller_id, rate_name
    

def chooserate(headers, csrf_token, cookies, xsrf, price, seller_id, rate_name):
    url = "https://proimagesports.com/checkout/save-shipping"

    payload = {
        "shipping_method": "mpmultishipping_mpmultishipping",
        "seller_shipping": {seller_id: [seller_id, "1", price]}
    }
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "x-csrf-token": csrf_token,
        "x-requested-with": "XMLHttpRequest",
        "x-xsrf-token": xsrf
    }

    response = requests.post(url, json=payload, headers=headers, cookies=cookies)


cardnumber = '4403933811892576'
expdatemonth = '10'
expdate1 = '27'
expdateyear = '20'+expdate1
expdate = expdatemonth+expdateyear

cvv = '204'
def card(csrf_token, cookies, cardnumber, cvv, expdate, expdatemonth, expdateyear):
    url = "https://api2.authorize.net/xml/v1/request.api"

    payload = {"securePaymentContainerRequest": {
        "merchantAuthentication": {
            "name": "7z99ujN6AC",
            "clientKey": "2p63epuC5JhfmEAGFB73SsqA2ne83ak4hZwVw7ENntBmZwG39g8JS9qEgJ59K5p8"
        },
        "data": {
            "type": "TOKEN",
            "id": "f7755c93-00d6-bd58-b226-8e37bddb0ebc",
            "token": {
                "cardNumber": cardnumber,
                "expirationDate": expdate,
                "cardCode": cvv
            }
        }
    }}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "content-type":"application/json; charset=UTF-8"
    }

    response = requests.post(url, json=payload, headers=headers, cookies=cookies)


    text = response.content.decode('utf-8-sig')

    # Load the JSON string into a dictionary
    data = json.loads(text)

    cardtoken = data['opaqueData']['dataValue']

    key = str(cardnumber)[-4:]
    key1 = str(cardnumber)[+4:]
  
    url = "https://proimagesports.com/checkout/sendtoken"

    payload = "_token=" + csrf_token + "&response%5BopaqueData%5D%5BdataDescriptor%5D=COMMON.ACCEPT.INAPP.PAYMENT&response%5BopaqueData%5D%5BdataValue%5D="+ cardtoken +"&response%5Bmessages%5D%5BresultCode%5D=Ok&response%5Bmessages%5D%5Bmessage%5D%5B0%5D%5Bcode%5D=I_WC_01&response%5Bmessages%5D%5Bmessage%5D%5B0%5D%5Btext%5D=Successful.&response%5BencryptedCardData%5D%5Bbin%5D="+key1+"%2B9&response%5BencryptedCardData%5D%5BexpDate%5D="+expdatemonth+"%2F"+expdateyear+"&response%5BencryptedCardData%5D%5BcardNumber%5D=XXXXXXXXXXXX"+key+"&result=true&cardId="
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "x-csrf-token": csrf_token,
        "x-requested-with": "XMLHttpRequest"
    }

    response = requests.post(url, data=payload, headers=headers, cookies=cookies)
    
    cookies = response.cookies
    
    
    return cookies
    
def checkout2(headers, csrf_token, cookies, xsrf):
    url = 'https://proimagesports.com/checkout/save-payment'
    
    payload = {
        "payment": 
            {"method": "mpauthorizenet"
        },
        'checkbox': 'on'
            }
        
    
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "x-csrf-token": csrf_token,
        "x-requested-with": "XMLHttpRequest",
        "x-xsrf-token": xsrf
    }
    

    response = requests.post(url, headers=headers, json=payload, cookies=cookies)
    
    
def finalpage(headers, csrf_token, cookies, xsrf):
    url = 'https://proimagesports.com/checkout/summary'
    
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "x-csrf-token": csrf_token,
        "x-requested-with": "XMLHttpRequest",
        "x-xsrf-token": xsrf
    }
    
    response = requests.get(url, headers=headers, cookies=cookies)
    
    
    print(response.text)
    
def saveorder(headers, csrf_token, cookies, xsrf):
    url = 'https://proimagesports.com/checkout/save-order'
    
    payload = {
        '_token':csrf_token
    }
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "x-csrf-token": csrf_token,
        "x-requested-with": "XMLHttpRequest",
        "x-xsrf-token": xsrf,
        'dnt': '1'
    }
    
    response = requests.post(url, headers=headers, json=payload, cookies=cookies)
    
    print(response.status_code)
  
    url = "https://www.facebook.com/tr"
    
    querystring = {"id":"274490659742640","ev":"SubscribedButtonClick","dl":"https://proimagesports.com/checkout/onepage","rl":"https://proimagesports.com/checkout/onepage","if":"true","ts":"1673557359176","cd\\[buttonFeatures\\]":"{\"classList\":\"btn common-btn mt-0 mb-5\",\"destination\":\"\",\"id\":\"checkout-place-order-button\",\"imageUrl\":\"linear-gradient(90deg, rgb(0, 63, 236) 0px, rgb(0, 126, 236))\",\"innerText\":\"PLACE ORDER\",\"numChildButtons\":0,\"tag\":\"button\",\"type\":\"button\",\"name\":\"\",\"value\":\"\"}","cd\\[buttonText\\]":"PLACE ORDER","cd\\[formFeatures\\]":"[]","cd\\[pageFeatures\\]":"{\"title\":\"    Checkout\\n\"}","cd\\[parameters\\]":"[]","sw":"1440","sh":"900","v":"2.9.92","r":"stable","ec":"7","o":"30","fbp":"fb.1.1673556900310.1292209738","it":"1673556991788","coo":"true","es":"automatic","tm":"3","rqm":"GET"}
    
    
    headers = {
        "accept": "image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76"
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    
    print(response.text)
      

def checkoutsuccess(headers, csrf_token, cookies, xsrf):
    url = 'https://proimagesports.com/checkout/success'
    
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }
    
    response = requests.get(url, headers=headers, cookies=cookies)
    
    
    


headers, cookies, xsrf = getcookies()
checkstock(headers)
csrf_token, headers = addtocart(headers, cookies)
guestcheckout(headers, csrf_token, cookies)   
headers = shipping(headers, csrf_token, cookies, xsrf)
price, seller_id, rate_name = shippingrate(headers, csrf_token, cookies, xsrf)
chooserate(headers, csrf_token, cookies, xsrf, price, seller_id, rate_name) 
cookies = card(csrf_token, cookies, cardnumber, cvv, expdate, expdatemonth, expdateyear)
checkout2(headers, csrf_token, cookies, xsrf)
finalpage(headers, csrf_token, cookies, xsrf)
saveorder(headers, csrf_token, cookies, xsrf)
checkoutsuccess(headers, csrf_token, cookies, xsrf)

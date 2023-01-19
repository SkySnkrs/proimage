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
from selenium import webdriver
import random
import string

id = "53a85471-bd60-a6ed-8d0d-519ed5b6c452"
random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=5))

# Append the random string to the end of the ID
new_id = id[:-5] + random_string


def profilecard():
    cardnumber = '4403933811892576'
    expdatemonth = '10'
    expdate1 = '27'
    expdateyear = '20'+expdate1
    expdate = expdatemonth+expdateyear
    cvv = '204'
    
    return cvv, expdate, expdate1, expdatemonth, expdateyear, cardnumber
cvv, expdate, expdate1, expdatemonth, expdateyear, cardnumber = profilecard()

def profileshipping():
    firstname = 'Tristan'
    lastname = 'Martinez'
    address = '1910 Ridge Way'
    address2 = ''
    country = 'US'
    state = 'ID'
    city = 'Middleton'
    postcode = '83644'
    phone = '2085509662'
    email = 'tristanm10@outlook.com'

    return firstname, lastname, address, address2, phone, city, state, country, postcode, email
firstname, lastname, address, address2, phone, city, state, country, postcode, email = profileshipping()

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
    session = requests.Session()
    while True:
        url = 'https://proimagesports.com/'
        
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        }
        
        response = session.get(url, headers=headers)
        
        if response.status_code == 200:
            cookies = response.cookies
            xsrftoken = response.cookies.get("XSRF-TOKEN")
            xsrf = urllib.parse.unquote(xsrftoken)
            break;
        else:
            time.sleep(1)
            print_with_color('Site Down... Retrying', Fore.RED, Style.BRIGHT)
    return xsrf, session
xsrf, session = getcookies()

def checkstock(session):
    while True:
            url = 'https://proimagesports.com/check/quantity/64547'
            
            headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            }
            
            response = session.get(url, headers=headers)
            
            response_data = response.json()
            qty = response_data['qty']
            
            if qty == 0:
                print_with_color('Out-Of-Stock', Fore.RED, Style.BRIGHT)
                time.sleep(1)
            elif qty > 0:
                print('In-Stock:', end=' ')
                print_with_color(str(response_data['qty']), Fore.GREEN, Style.BRIGHT)
                break;
    return session, headers
session, headers = checkstock(session)

def addtocart(headers, session):
    #Add to Cart, Bypass Cart Goes To Checkout
    while True:
        url = "https://proimagesports.com/buynow/64547"

        querystring = {"quantity":1}

        response = session.get(url, headers=headers, params=querystring)
        
        if response.status_code == 200:
            
            #cookies
            html_doc = response.text
            soup = BeautifulSoup(html_doc, 'html.parser')
            csrf_meta_tag = soup.find('meta', {'name': 'csrf-token'})
            csrf_token = csrf_meta_tag['content']
            itemname_divclass = soup.find('div', {'class': 'item-name'})
            

            if itemname_divclass == '':
                print_with_color('Cart Failed, Retrying...', Fore.RED, Style.BRIGHT)
                time.sleep(1)
            else:
                print('Carted:', end=' ')
                print_with_color(str(itemname_divclass.text), Fore.GREEN, Style.BRIGHT)
                break;
        else:
            print('Carting Failed, Retrying....', Fore.RED, Style.BRIGHT)
        
    return session, csrf_token
session, csrf_token = addtocart(headers, session)

def guestcheckout(headers, csrf_token, session):
    while True:
        #Checkout As Guest
        url = 'https://proimagesports.com/checkout/setGuestSession'

        payload = {
            '_token':csrf_token,
            'email':'tristanm10@outlook.com',
            'account':'account_no'
        }

        response = session.post(url, data=payload, headers=headers)

        if response.status_code == 200:
            print_with_color('Checking Out As Guest', Fore.GREEN, Style.BRIGHT)
            break;
        else:
            print_with_color('Failed Checkout Page, Retrying....', Fore.RED, Style.BRIGHT)
            time.sleep(1)  
    return session
session = guestcheckout(headers, csrf_token, session)

def shipping(headers, csrf_token, firstname, lastname, address, address2, phone, city, state, country, postcode, email, session):
    while True:
        url = 'https://proimagesports.com/checkout/save-address'
        
        headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "x-csrf-token": csrf_token,
        "x-requested-with": "XMLHttpRequest",
        "x-xsrf-token": xsrf
        }
        
        payload = {
            "billing": {
                "address1": [address],
                "address2": [address2],
                "use_for_shipping": False,
                "first_name": firstname,
                "last_name": lastname,
                "email": email,
                "country": country,
                "state": state,
                "city": city,
                "postcode": postcode,
                "phone": phone,
                "twilio_sms": True
            },
            "shipping": {
                "address1": [address],
                "address2": [address2],
                "first_name": firstname,
                "last_name": lastname,
                "email": email,
                "country": country,
                "state": state,
                "city": city,
                "postcode": postcode,
                "phone": phone,
            }
        }

        response = session.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print_with_color('Shipping Filled!', Fore.GREEN, Style.BRIGHT)
            break;
        else:
            print_with_color('Failed To Submit Shipping, Retrying...', Fore.RED, Style.BRIGHT)
            time.sleep(1)
    return headers, session
headers, session = shipping(headers, csrf_token, firstname, lastname, address, address2, phone, city, state, country, postcode, email, session)

def shippingrate(headers, csrf_token, session):
    while True:
        url = 'https://proimagesports.com/checkout/shippingrate'
        
        headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "x-csrf-token": csrf_token,
        }
        
        response = session.get(url, headers=headers)
        
        if response.status_code == 200:
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
            break;
        else:
            print_with_color('Failed Getting Shipping, Retrying...', Fore.RED, Style.BRIGHT)
            time.sleep(1)
    return price, seller_id, rate_name, session
price, seller_id, rate_name, session = shippingrate(headers, csrf_token, session)

def chooserate(headers, csrf_token, price, seller_id, rate_name, session):
    while True:
        url = "https://proimagesports.com/checkout/save-shipping"

        payload = {
            "shipping_method": "mpmultishipping_mpmultishipping",
            "seller_shipping": {seller_id: [rate_name, "1", price]}
        }
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "x-csrf-token": csrf_token,
        }

        response = session.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            print_with_color('Shipping Rate:'+' '+price+ ' ' + rate_name, Fore.GREEN, Style.BRIGHT)
            break;
        else:
            print_with_color('Failed To Submit Rate, Retrying...', Fore.RED, Style.BRIGHT)
            time.sleep(1)
    return session
session = chooserate(headers, csrf_token, price, seller_id, rate_name, session)

def card(cardnumber, cvv, expdate, new_id, session):
    while True:
        url = "https://api2.authorize.net/xml/v1/request.api"

        payload = {"securePaymentContainerRequest": {
            "merchantAuthentication": {
                "name": "7z99ujN6AC",
                "clientKey": "2p63epuC5JhfmEAGFB73SsqA2ne83ak4hZwVw7ENntBmZwG39g8JS9qEgJ59K5p8"
            },
            "data": {
                "type": "TOKEN",
                "id": new_id,
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

        response = session.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print_with_color('Payment Authorized', Fore.GREEN, Style.BRIGHT)
            text = response.content.decode('utf-8-sig')
            # Load the JSON string into a dictionary
            data = json.loads(text)
            cardtoken = data['opaqueData']['dataValue']
            key = str(cardnumber)[-4:]
            key1 = str(cardnumber)[:4]
            break;
        else:
            print_with_color('Failed To Authorize Payment, Retrying...', Fore.RED, Style.BRIGHT)
            time.sleep(1)
    return key, key1, cardtoken, session
key, key1, cardtoken, session = card(cardnumber, cvv, expdate, new_id, session)

def card2(csrf_token, expdatemonth, expdateyear, cardtoken, session):
    
    while True:
        url = "https://proimagesports.com/checkout/sendtoken"

        payload = "_token=" + csrf_token + "&response%5BopaqueData%5D%5BdataDescriptor%5D=COMMON.ACCEPT.INAPP.PAYMENT&response%5BopaqueData%5D%5BdataValue%5D="+ cardtoken +"&response%5Bmessages%5D%5BresultCode%5D=Ok&response%5Bmessages%5D%5Bmessage%5D%5B0%5D%5Bcode%5D=I_WC_01&response%5Bmessages%5D%5Bmessage%5D%5B0%5D%5Btext%5D=Successful.&response%5BencryptedCardData%5D%5Bbin%5D="+key1+"%2B9&response%5BencryptedCardData%5D%5BexpDate%5D="+expdatemonth+"%2F"+expdateyear+"&response%5BencryptedCardData%5D%5BcardNumber%5D=XXXXXXXXXXXX"+key+"&result=true&cardId="
        headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                "x-csrf-token": csrf_token,
                "x-requested-with": "XMLHttpRequest"
            }

        response = session.post(url, data=payload, headers=headers)
        
        if response.status_code == 200:
            print_with_color('Recieved Payment Token', Fore.GREEN, Style.BRIGHT)
            break;
        else:
            print_with_color('Failed To Process Payment', Fore.RED, Style.BRIGHT)
            time.sleep(1)
    return session
session = card2(csrf_token, expdatemonth, expdateyear, cardtoken, session)

def checkout2(headers, csrf_token, xsrf, session):
    print_with_color('Proccessing Payment...', Fore.GREEN, Style.BRIGHT)
    while True:
        url = 'https://proimagesports.com/checkout/save-payment'
            
        payload = {
                "payment": 
                    {"method": "mpauthorizenet"
                },
                    }
                
            
        headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                "x-csrf-token": csrf_token,
            }
            
        response = session.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print_with_color('Payment Processed', Fore.GREEN, Style.BRIGHT)
            break;
        else:
            print_with_color('Failed To Process Payment', Fore.RED, Style.BRIGHT)
            print(1)
    return session
session = checkout2(headers, csrf_token, xsrf, session)

def saveorder(headers, csrf_token, session):
    while True:
        url = 'https://proimagesports.com/checkout/save-order'
        
        payload = {
            '_token':csrf_token
        }
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "x-csrf-token": csrf_token,
        }
        
        response = session.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            print_with_color('Processing Order', Fore.GREEN, Style.BRIGHT)
            break;
        else:
            print_with_color('Failed To Process Order, Retrying...', Fore.RED, Style.BRIGHT)
            time.sleep(1)
    return session 
session = saveorder(headers, csrf_token, session)    

def charge(session):
    while True:
        url = "https://proimagesports.com/checkout/create/charge"

        headers = {
            "cookie":"proimage_session=eyJpdiI6IjdHVnZSQUVNRU5qcGlQSk0zclJxS2c9PSIsInZhbHVlIjoiMjRZcHFcL0oyZ3BsSXlcL1pISzhtbktwZ3dlZDZEMmZGbWZHSklvbmxYMlpETHVuU2M2eWFxMFJ0aFRuY1UxVGNiIiwibWFjIjoiYTZiZTk0MTk5NDE0Y2E1MDNhYWZmODdiYWRmZjdmZmUyOGY0ZDE5Zjg5ZmYyOWVmNGZkNjM3ZDM2MmFjZDczZCJ9",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }

        response = session.get(url, headers=headers)
        if response.status_code == 200:
            print_with_color('Finalizing Checkout...', Fore.GREEN, Style.BRIGHT)
            break;
        else:
            print_with_color('Failed To Checkout, Retrying...', Fore.RED, Style.BRIGHT)
            time.sleep(2.5)
    return session 
session = charge(session)


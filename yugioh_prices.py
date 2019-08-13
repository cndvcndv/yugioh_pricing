# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 21:50:32 2019

@author: cndvcndv
"""
import requests
from bs4 import BeautifulSoup
import string

letters = string.ascii_lowercase
with open("input.txt", 'r') as file:
    auto_correct = int(file.readlines()[0]) == 1

def get_card_info():
    cards = []
    with open("input.txt", 'r') as file:
        lines = file.readlines()
        for line in lines:
            if(len(line) > 5):
                card = {"name": "", "pack": "", "quantity": ""}
                card["name"], card["pack"], card["quantity"] = line.replace('\n', '').split(" | ")
                cards.append(card)
    return cards


def get_price(card_name, pack_name, try_correction):
    page_number = 1
    while True:
        url = "https://shop.tcgplayer.com/all/product/show?newSearch=false&IsProductNameExact=false&ProductName={}&orientation=list&PageNumber={}".format(card_name, page_number)
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        groups_ext = soup.find_all('span', class_="product__extended-field")
        prices = soup.find_all('dd')
        groups_act = []
        price = -1
        for group in groups_ext:
            if not "Rarity" in group.text:
                groups_act.append(group)
        for i in range(len(groups_act)):
            if pack_name in groups_act[i].text:
                price = float(prices[i].text.replace('$', ''))
        alert = soup.find('strong').text
        if "Oh no!" in alert or price != -1:
            break
        page_number += 1

    if try_correction:
        prediction = -1
        if price == -1:
            prediction = did_you_mean(card_name)
            print("{} was not found!".format(card_name))
        if prediction != -1:
            price = get_price(prediction, pack_name, False)
            print("{} is replaced by {}.\n".format(card_name, prediction))
            
    return price

def main():
    result = ""
    total_card = 0
    cards_found = 0
    total_price_cards = 0
    cards = get_card_info()
    for card in cards:
        unit_price = get_price(card["name"], card["pack"], auto_correct)
        if unit_price == -1:
            st = "{} not found!".format(card["name"])
        else:
            total_price = unit_price*int(card["quantity"])
            st = "{} | {} | {} | {} | {}".format(card["name"], card["pack"], card["quantity"], unit_price, total_price)
            cards_found += 1
            total_price_cards += total_price
        
        total_card += 1
        result += st + '\n'
    result += "\nTotal price | {}\n".format(round(total_price_cards*100)/100)
    result += "Total cards | {}\n".format(total_card)
    result += "Found cards | {}\n".format(cards_found)
    print(result)
    with open("output.txt", 'w+') as file:
        file.write(result)
    input("Press enter to quit...")

def letter_count(name):
    counts = [0]*len(letters)
    for l in name.replace(" ", "").lower():
        if l in letters:
            counts[letters.index(l)] += 1
    return counts

def did_you_mean(name):
    for i in range(len(name)):
        search_key = name[:i]
        url = "https://data.tcgplayer.com/autocomplete?q={}".format(search_key)
        query = requests.get(url).json()
#        matches = 0
        if len(query["products"]) == 1:
            return query["products"][0]["product-name"]
#        for suggestion in query["products"]:
#            if letter_count(suggestion["product-name"]) == letter_count(name):
#                matches += 1
#                result = suggestion["product-name"]
#        if matches == 1:
#            return result
    return -1        

if __name__ == '__main__':
    main()
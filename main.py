import requests
import telebot
import time
from bs4 import BeautifulSoup
import pickle
from googletrans import Translator
import re
import pandas


bot = telebot.TeleBot("732667528:AAF2LotMmuqEMJEehw0dqtyDv6auQQj1c3Q")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
#user_data = []
#calories_data = []
#with open("user_data.pkl", "wb") as pickle_file:
#    pickle.dump(user_data, pickle_file)
#with open("calories_data.txt", "wb") as pickle_file:
 #  pickle.dump(calories_data, pickle_file)
#with open("user_data.pkl", "wb") as pickle_file:
 #  pickle.dump(user_data, pickle_file)
with open("calories_data.pkl", "rb") as pickle_file:
    calories_data = pickle.load(pickle_file)
print(calories_data)
with open("user_data.pkl", "rb") as pickle_file:
    user_data = pickle.load(pickle_file)

with open("calories_data.txt", "wb") as pickle_file:
   pickle.dump(calories_data, pickle_file)

@bot.message_handler(commands=['get'])
def get(message):
    user_get_calories_for_today(message)


@bot.message_handler(commands=['add'])
def add(message):
    user_add_product(message)


@bot.message_handler(commands=['deletelast'])
def delete_last(message):
    user_delete_last_in_user_data(message)

@bot.message_handler(func=lambda m: True)
def user_search_calories(message):
    user_input_list = message.text.replace(" ", "").split(",")
    print(user_input_list)
    product_name = user_input_list[0]
    multiplier = if_user_entered_weight(message)
    if multiplier and multiplier > 10 < 1000:
        multiplier = multiplier * 0.01
    if '+' in product_name:
        user_find_calories_and_add_to_eaten(message, multiplier, product_name)
    else:
        user_find_calories(message, multiplier, product_name)


def if_user_entered_weight(message):
    user_input_list = message.text.replace(" ", "").split(",")
    print(user_input_list)
    if len(user_input_list) == 2:
        try:
            multiplier = float(user_input_list[1])
            return multiplier
        except: (EOFError)
        return


def user_delete_last_in_user_data(message):
    with open("user_data.pkl", "rb") as pickle_file:
        user_data = pickle.load(pickle_file)
    for i, name in enumerate(user_data):
        if message.chat.id in user_data[i]:
            del user_data[i][-1]
            with open("user_data.pkl", "wb") as pickle_file:
                pickle.dump(user_data, pickle_file)
            bot.send_message(message.chat.id, 'Общая калорийность за сегодня - ' + str(int(count_calories(message))) + ' кал.')


def product_find_calories(product_name):
    with open("calories_data.pkl", "rb") as pickle_file:
        calories_data = pickle.load(pickle_file)
        product_calories = search_in_pickle(product_name, calories_data)
    if product_calories:
        pass
    else:
        product_calories = search_in_google(product_name)
        if product_calories:
            product_calories = prepare_num(product_calories)
            calories_data.append([product_name, product_calories])
        else:
            product_calories = translate_in_google(product_name)
            if product_calories:
                product_calories = prepare_num(product_calories)
                calories_data.append([product_name, product_calories])
            else:
                pass
    with open("calories_data.pkl", "wb") as pickle_file:
        pickle.dump(calories_data, pickle_file)

    return product_calories


def count_calories(message):
    calories = 0
    with open("user_data.pkl", "rb") as pickle_file:
        user_data = pickle.load(pickle_file)
        for j, name in enumerate(user_data):
            if message.chat.id in user_data[j]:
                for i, value in enumerate(user_data[j]):
                    if i > 0:
                        calories += user_data[j][i]
    return calories


def search_in_pickle(product, calories_data):
    if calories_data is not None:
        for i in calories_data:
            for value in i:
                if value == product:
                    return i[1]


def search_in_google(text):
    quote_page = 'https://www.google.com.ua/search?q=' + text + '+калорийность'
    url = quote_page
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    result = soup.find('div', class_="Z0LcW an_fna")
    if result:
        result = result.text.replace(" кал", "")
    else:
        result = soup.find('span', class_="ILfuVd")
        if result:
            result = result.text.replace("100", ",").split(",")
            result = result[0]
            result = re.sub('[^0-9]', '', result)
    return result


def translate_in_google(text):
    translator = Translator()
    return search_in_google(translator.translate(text, dest='en', src='ru').text)


def prepare_text(text):
    text = (list(filter(None, re.split('\W|\d', text)))[0])
    return text.lower()


def prepare_num(num):
    if num:
        num = num.replace(",", ".")
        return int(pandas.to_numeric(num))
    else:
        return None


def user_add_product(message):
    created_list = message.text.replace("/add ", "").replace(" ", "").split(",")
    try:
        if (created_list[0]).isalpha() and int(created_list[1]):
            with open("calories_data.pkl", "rb") as pickle_file:
                calories_data = pickle.load(pickle_file)
            created_list[1] = int(created_list[1])
            calories_data.append(created_list)
            bot.send_message(message.chat.id, 'Добавлено:\n' + created_list[0] + ' с калорийностью в ' + str(created_list[1]) + ' кал.')
            with open("calories_data.pkl", "wb") as pickle_file:
                pickle.dump(calories_data, pickle_file)
        else:
            bot.send_message(message.chat.id,
                             'Ошибка. Соблюдайте структуру добавления. Если число калорийности не целое, десятые разделяются запятой: 47,3')
    except (ValueError, IndexError):
        bot.send_message(message.chat.id,
                         'Ошибка. Соблюдайте структуру добавления. Если число калорийности не целое, десятые разделяются запятой: 47,3')


def user_get_calories_for_today(message):
    calories_for_today = count_calories(message)
    if calories_for_today == 0:
        bot.send_message(message.chat.id, 'Вы пока ничего не ели.\nДля добавления продукта в список съеденого, просто поставьте перед ним +')
    else:
        bot.send_message(message.chat.id, 'Сегодня вы съели на ' + str(int(calories_for_today)) + ' кал.')


def user_find_calories(message, multiplier, product_name):
    product_name = product_name.replace(' ', '')
    product_name = prepare_text(product_name)
    product_calories = product_find_calories(product_name)
    if product_calories is not None:
        if multiplier is not None and multiplier > 0:
            product_calories = product_calories * multiplier
        bot.send_message(message.chat.id, str(int(product_calories)) + ' кал.')
    else:
        bot.send_message(message.chat.id, "Продукт не найден.\nДобавьте его, используя /add имя продукта, калорийность")


def user_find_calories_and_add_to_eaten(message, multiplier, product_name):
    product_name = product_name.replace('+', '').replace(' ', '')
    product_name = prepare_text(product_name)
    product_calories = product_find_calories(product_name)
    if product_calories is not None:
        if multiplier is not None and multiplier > 0:
            product_calories = product_calories * multiplier
        with open("user_data.pkl", "rb") as pickle_file:
            user_data = pickle.load(pickle_file)
        if data_in_user_data(user_data, message, product_calories) is None:
            user_data.append([message.chat.id, product_calories])
            print("else")
        print(user_data)
        with open("user_data.pkl", "wb") as pickle_file:
            pickle.dump(user_data, pickle_file)
        calories_for_today = count_calories(message)
        bot.send_message(message.chat.id,
                         str(int(product_calories)) + ' кал.\nКалорийность за день - ' + str(int(calories_for_today)) + ' кал.')
    else:
        bot.send_message(message.chat.id, "Продукт не найден.\nДобавьте его, используя /add имя продукта, калорийность")


def data_in_user_data(user_data, message, product_calories):
    for j, name in enumerate(user_data):
        if message.chat.id in user_data[j]:
            user_data[j].append(int(product_calories))
            return True


while True:
    bot.polling()
    time.sleep(15)


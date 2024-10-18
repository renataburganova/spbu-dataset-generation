import random
import tkinter as tk
from tkinter import ttk
import pandas as pd
import xml.etree.ElementTree as ET


store_names = [str(i) for i in open('stores.txt', 'r', encoding='utf-8').readlines()]
categories = [str(i) for i in open('categories.txt', 'r', encoding='utf-8').readlines()]

brands = {}
for line in open('brands.txt', 'r', encoding='utf-8'):
    line = line.replace('\n', '')
    categ, br = line.split(': ')
    brands[categ] = br.split(',')

coordinates_list = {}
for line in open('coordinates.txt', 'r', encoding='utf-8'):
    line = line.replace('\n', '')
    name, coords = line.split(': ')
    coordinates_list[name] = coords.split(',')


def get_coordinates(store):
    coords_format = 'Latitude:{latitude}, Longitude:{longitude}'

    store = store.strip()
    latitude, longitude = coordinates_list.get(store)

    coord = {
        'latitude': latitude,
        'longitude': longitude
    }

    return coords_format.format(**coord)



def gen_cost():
    return str(random.randint(1000, 60000))


def gen_quantity():
    return str(random.randint(5, 10))


def gen_card_number(pay_system, bank):
    card_number_format = '{num1} {num2} {num3} {num4}'

    # pay_system = random.choice(['Мир', 'MasterCard', 'Другая'])
    # bank = random.choice(['СберБанк', 'Т-Банк', 'Альфа Банк', 'Другой'])

    if pay_system == 'Мир':
        if bank == 'Т-Банк':
            num1, num2_1 = '2200', '70'
        elif bank == 'СберБанк':
            num1, num2_1 = '2202', '20'
        elif bank == 'Альфа Банк':
            num1, num2_1 = '2200', '15'
        else:
            num1, num2_1 = '2213', '19'
    elif pay_system == 'MasterCard':
        if bank == 'Т-Банк':
            num1, num2_1 = '5213', '24'
        elif bank == 'СберБанк':
            num1, num2_1 = '5536', '98'
        elif bank == 'Альфа Банк':
            num1, num2_1 = '5941', '24'
        else:
            num1, num2_1 = '5476', '24'
    else:
        if bank == 'Т-Банк':
            num1, num2_1 = '1213', '24'
        elif bank == 'СберБанк':
            num1, num2_1 = '1536', '98'
        elif bank == 'Альфа Банк':
            num1, num2_1 = '1941', '24'
        else:
            num1, num2_1 = '1476', '24'

    card_number = {
        'num1': num1,
        'num2': num2_1 + str(random.randint(10, 99)),
        'num3': str(random.randint(1000, 9999)),
        'num4': str(random.randint(1000, 9999))

    }

    return card_number_format.format(**card_number)


def gen_date():
    date_format = '{year}-{month}-{day}T{hour}:{minute}+{offset}'

    year = random.choice(['2020', '2021', '2022', '2023', '2024'])
    month = random.choice(['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'])
    if month in ['01', '03', '05', '07', '08', '10', '12']:
        day = str(random.randint(1, 31)).zfill(2)
    elif month == '02':
        if year in ['2020', '2024']:
            day = str(random.randint(1, 29)).zfill(2)
        else:
            day = str(random.randint(1, 28)).zfill(2)
    else:
        day = str(random.randint(1, 30)).zfill(2)

    hour = str(random.randint(10, 21))
    minute = str(random.randint(0, 59)).zfill(2)
    offset = '03:00'

    date = {
        'year': year,
        'month': month,
        'day': day,
        'hour': hour,
        'minute': minute,
        'offset': offset

    }

    return date_format.format(**date)

def get_weights():
    while True:
        try:
            pay_system_weights = list(map(int, input("Введите веса для платежных систем (Мир, MasterCard, Другая) через пробел: ").split()))
            bank_weights = list(map(int, input("Введите веса для банков (СберБанк, Т-Банк, Альфа Банк, Другой) через пробел: ").split()))

            if sum(pay_system_weights) != 100 or sum(bank_weights) != 100:
                raise ValueError("Сумма весов должна быть равна 100!")
            return pay_system_weights, bank_weights
        except ValueError as e:
            print(f"Ошибка: {e}. Попробуйте еще раз.")


def generate_bank_pay_system_combinations(size, pay_system_weights, bank_weights):
    pay_systems = ['Мир', 'MasterCard', 'Другая']
    banks = ['СберБанк', 'Т-Банк', 'Альфа Банк', 'Другой']

    combinations = []
    for i, pay_system_weight in enumerate(pay_system_weights):
        for j, bank_weight in enumerate(bank_weights):
            num_records = size * (pay_system_weight / 100) * (bank_weight / 100)
            combinations.extend([(pay_systems[i], banks[j])] * int(num_records))

    random.shuffle(combinations)

    return combinations


used_card_numbers = []


def gen_dataset(size, pay_system_weights, bank_weights):
    df = pd.DataFrame({
        'Название магазина': [],
        'Дата и время': [],
        'Координаты': [],
        'Категория': [],
        'Бренд': [],
        'Номер карточки': [],
        'Количество товаров': [],
        'Стоимость': []
    })

    combinations = generate_bank_pay_system_combinations(size, pay_system_weights, bank_weights)

    for pay_system, bank in combinations:
        store = random.choice(store_names)
        coordinates = get_coordinates(store)
        date = gen_date()
        category = random.choice(categories)
        brand = random.choice(brands.get(category.strip()))
        card_number = gen_card_number(pay_system, bank)
        quantity = gen_quantity()
        cost = gen_cost()

        while used_card_numbers.count(card_number) > 4:
            card_number = gen_card_number()
        used_card_numbers.append(card_number)

        df.loc[len(df.index)] = [
            str(store), str(date), str(coordinates),
            str(category), str(brand), str(card_number),
            str(quantity), str(cost)
        ]

    root = ET.Element("root")
    for _, row in df.iterrows():
        item = ET.SubElement(root, "item")
        for col in df.columns:
            child = ET.SubElement(item, col)
            child.text = str(row[col])

    tree = ET.ElementTree(root)
    tree.write("dataset.xml", encoding='utf-8', xml_declaration=True)
    return df


def display_table(root, dataframe):
    tree = ttk.Treeview(root)

    tree["columns"] = list(dataframe.columns)
    tree["show"] = "headings"

    for column in tree["columns"]:
        tree.heading(column, text=column)

    for _, row in dataframe.iterrows():
        tree.insert("", "end", values=list(row))

    tree.pack(expand=True, fill='both')


pay_system_weights, bank_weights = get_weights()

root = tk.Tk()
root.title("Генерация датасета")
root.geometry("400x200")

display_table(root, gen_dataset(50000, pay_system_weights, bank_weights))

root.mainloop()

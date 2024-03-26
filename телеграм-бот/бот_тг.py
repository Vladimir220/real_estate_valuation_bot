import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from secret import token
import joblib
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
import os
import time
import pandas as pd
import numpy as np
import warnings
from sklearn.preprocessing import StandardScaler
warnings.filterwarnings("ignore")
session = {}

pd.options.display.max_columns
# Set it to None to display all columns in the dataframe
pd.set_option('display.max_columns', None)


class Telegram_bot_session:
    address_columns = ['Улица', 'Дом', 'Строение'] 
    building_params_columns = ['Кол-во этажей', 'Тип здания', 'Высота потолков', 'Газ', 'Лифт', 'Мусоропровод', 'Год строительства', 'Ближайшая станция метро']
    apartment_params_columns = ['Площадь, м²', 'Кол-во комнат', 'Этаж']
    columns = ['Улица', 'Дом', 'Строение', 'Кол-во этажей', 'Тип здания', 'Высота потолков',  'Газ', 'Лифт', 
               'Мусоропровод', 'Год строительства', 'Ближайшая станция метро', 'Индекс станции', 'Площадь, м²', 'Кол-во комнат', 'Этаж']
    file_path = '.\\телеграм-бот\\Данные\\sales_processed.csv' 
    db = pd.read_csv(file_path, sep=',', index_col=False, usecols = columns).drop_duplicates()
    file_path = '.\\телеграм-бот\\Данные\\корректировки_на_метро.csv'
    subway_adjustments = pd.read_csv(file_path, sep=';', encoding='cp1251')

    @staticmethod
    def split_by_three(number):
        number = int(number)
        number_str = str(number)[::-1]
        result = ' '.join(number_str[i:i+3] for i in range(0, len(number_str), 3))[::-1]
        return result

    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.episode = ''
        self.next_input_data = ''
        self.extra_input_columns = []
        self.property = {}
        self.clear_session_data()
        Telegram_bot_session.db = Telegram_bot_session.db.applymap(lambda x: x.replace(',', '.') if isinstance(x, str) else x) 
        Telegram_bot_session.subway_adjustments['Наименование станции'] = Telegram_bot_session.subway_adjustments['Наименование станции'].str.title()

        
    def clear_session_data(self):
        self.property = {
            'Площадь, м²': np.NaN, 'Кол-во комнат': np.NaN, 'Этаж': np.NaN, 'Кол-во этажей': np.NaN, 'Высота потолков': np.NaN, 'Газ': np.NaN, 
            'Лифт': np.NaN, 'Мусоропровод': np.NaN, 'Год строительства': np.NaN, 'Индекс станции': np.NaN, 'Ближайшая станция метро': np.NaN, 'Тип здания': np.NaN, 'Улица': np.NaN, 'Дом': np.NaN, 
            'Строение': np.NaN
        }
    


    def preprocessing_input(self):
        buf = pd.DataFrame([self.property])
        buf = buf.applymap(lambda x: x.replace(',', '.') if isinstance(x, str) else x)
        buf['Мусоропровод'] = buf['Мусоропровод'].str.replace('Есть', '1')
        buf['Мусоропровод'] = buf['Мусоропровод'].str.replace('Нет', '0')
        buf['Мусоропровод'] = buf['Мусоропровод'].str.strip()
        buf['Лифт'] = buf['Лифт'].str.replace('Есть', '1')
        buf['Лифт'] = buf['Лифт'].str.replace('Нет', '0')
        buf['Лифт'] = buf['Лифт'].str.strip()
        buf['Газ'] = buf['Газ'].str.replace('Есть', '1')
        buf['Газ'] = buf['Газ'].str.replace('Нет', '0')
        buf['Газ'] = buf['Газ'].str.strip()
        

        X = buf.drop(columns=Telegram_bot_session.address_columns + ['Ближайшая станция метро'])
        print(X)
        
        X = pd.get_dummies(X, columns=['Тип здания'])

        all_building_types = ['Тип здания_Блочное', 'Тип здания_Деревянное', 'Тип здания_Кирпично-монолитное', 'Тип здания_Кирпичное', 'Тип здания_Монолитное', 'Тип здания_Панельное']
        # Определение добавленного столбца
        added_column = [col for col in X.columns if col in all_building_types]
        missing_columns = list(set(all_building_types) - set(added_column))
        additional_columns = pd.DataFrame(0, index=[0], columns=missing_columns)
        # Объединение датафреймов
        #X = pd.concat([X, additional_columns], axis=1)
        X[missing_columns] = additional_columns[missing_columns]
        #X = X.reindex(columns = ['Площадь, м²', 'Кол-во комнат', 'Этаж', 'Кол-во этажей', 'Высота потолков', 'Кол-во квартир', 'Год строительства', 'Индекс станции', 'Газ', 'Лифт', 'Мусоропровод', 'Тип здания_Блочное', 'Тип здания_Деревянное', 'Тип здания_Кирпично-монолитное', 'Тип здания_Кирпичное', 'Тип здания_Монолитное', 'Тип здания_Панельное'])
        X = X.reindex(columns = ['Площадь, м²', 'Кол-во комнат', 'Этаж', 'Кол-во этажей', 'Высота потолков', 'Год строительства', 'Индекс станции', 'Газ', 'Лифт', 'Мусоропровод', 'Тип здания_Блочное', 'Тип здания_Деревянное', 'Тип здания_Кирпично-монолитное', 'Тип здания_Кирпичное', 'Тип здания_Монолитное', 'Тип здания_Панельное'])

        X = X.astype(float)
        print(X)
        return X

    def market_price(self, isRentPrice = False):
        model = 0
        if isRentPrice:
            pass
        else:
            model = joblib.load('.\\телеграм-бот\\Данные\\cost_estimation_model.pkl')
        X = self.preprocessing_input()
        y_pred = model.predict(X)[0]
        print(y_pred)
        sum = y_pred * X.loc[0, 'Площадь, м²']
        return sum

    def scenario(self, chat_id, content = ''):       
        if self.episode == 'старт':
            self.clear_session_data()
            self.next_input_data = ''
            self.episode = 'выбор способа ввода хар-к дома'
            buttons = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text='Начать', callback_data='выбор способа ввода хар-к дома')]
                            ])
            bot.sendMessage(chat_id, 'Привет!\nЭтот бот поможет оценить стоимость вашей недвижимости.\nНажмите кнопку, чтобы начать работу с ботом.', reply_markup=buttons)
        elif self.episode == 'выбор способа ввода хар-к дома':
            self.clear_session_data()
            buttons = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text='Ввести самому', callback_data='ввод хар-к дома')],
                                [InlineKeyboardButton(text='Поискать в базе по адресу', callback_data='поиск хар-к дома')]
                            ])
            bot.sendMessage(chat_id, 'Для начала нужно ввести характеристики дома!\nМожете это ввести их вручную, либо мы можем поискать их в нашей базе.', reply_markup=buttons)
        elif self.episode == 'поиск хар-к дома':
            status = self.input(chat_id, content, isAddress=True)
            if status == 'ввод завершен':
                address = {key: self.property[key] for key in Telegram_bot_session.address_columns}
                bot.sendMessage(chat_id, 'Вы ввели следующие данные:\n' + self.output(address))
                found_building_params = self.building_search()
                if len(found_building_params) != 0:
                    valid_keys = [key for key, value in found_building_params.items() if not pd.isnull(value)]
                    self.property.update({key: found_building_params[key] for key in valid_keys})
                    bot.sendMessage(chat_id, f'Ура! Дом был найден базе! Характеристики дома:\n{self.output(found_building_params)}')
                    nan_keys = [key for key, value in found_building_params.items() if pd.isna(value)]
                    index = Telegram_bot_session.subway_adjustments.loc[Telegram_bot_session.subway_adjustments['Наименование станции'] == self.property['Ближайшая станция метро'], 'Индекс станции'].iloc[0]
                    self.property['Индекс станции'] = index
                    if len(nan_keys) != 0:
                        bot.sendMessage(chat_id, f'Следующие характеристики дома отсутствуют в базе:\n{nan_keys}\nИх нужно ввести в систему.')
                        self.extra_input_columns = nan_keys
                        self.episode = 'ввод хар-к дома'
                        self.scenario(chat_id)
                    else:
                        bot.sendMessage(chat_id, 'Теперь нужно ввести характеристики квартиры.')
                        self.episode = 'ввод хар-к квартиры'
                        self.scenario(chat_id)
                else:
                    bot.sendMessage(chat_id, 'Дом отсутствует в базе. Его параметры придется ввести вручную.')
                    self.episode = 'ввод хар-к дома'
                    self.scenario(chat_id)
        elif self.episode == 'ввод хар-к дома':
            status = ''
            if len(self.extra_input_columns) != 0:
                status = self.input(chat_id, content, columns = self.extra_input_columns)
            else:
                status = self.input(chat_id, content, isBuildParams = True)

            if status == 'ввод завершен':
                input_data = []
                if len(self.extra_input_columns) != 0:
                    input_data = {key: self.property[key] for key in self.extra_input_columns}
                else:
                    input_data = {key: self.property[key] for key in Telegram_bot_session.building_params_columns}
                self.extra_input_columns = []
                bot.sendMessage(chat_id, 'Вы ввели следующие данные:\n' + self.output(input_data))
                bot.sendMessage(chat_id, 'Теперь нужно ввести характеристики квартиры.')
                self.episode = 'ввод хар-к квартиры'
                self.scenario(chat_id)
        elif self.episode == 'ввод хар-к квартиры':
            status = self.input(chat_id, content, isApartParams = True)
            if status == 'ввод завершен':
                self.episode = 'выбор цели'
                input_data = {key: self.property[key] for key in Telegram_bot_session.apartment_params_columns}
                bot.sendMessage(chat_id, 'Вы ввели следующие данные:\n' + self.output(input_data))
                result = {key: self.property[key] for key in Telegram_bot_session.building_params_columns + Telegram_bot_session.apartment_params_columns}
                bot.sendMessage(chat_id, 'В результате оцениваемый объект содержит следующие характеристики:\n' + self.output(result))
                self.scenario(chat_id)
        elif self.episode == 'выбор цели':
            buttons = InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text='Текущая рыночная стоимость объекта', callback_data='рыночная стоимость')], 
                                [InlineKeyboardButton(text='Текущая рыночная стоимость аренды объекта', callback_data='рыночная стоимость аренды')],
                                [InlineKeyboardButton(text='Будущая рыночная стоимость объекта', callback_data='будущая рыночная стоимость')],
                                [InlineKeyboardButton(text='Будущая рыночная стоимость аренды объекта', callback_data='будущая рыночная стоимость аренды')],
                                [InlineKeyboardButton(text='Инвестиционная стоимость объекта', callback_data='инвестиционная стоимость')]
                            ])
            bot.sendMessage(chat_id, 'Выберите цель оценки.', reply_markup=buttons)
        elif self.episode == 'строения нет':
            self.episode = 'поиск хар-к дома'
            self.scenario(chat_id, np.NaN)
        elif self.episode == 'тип здания: панельное':
            self.episode = 'ввод хар-к дома'
            self.scenario(chat_id, 'Панельное')
        elif self.episode == 'тип здания: кирпичное':
            self.episode = 'ввод хар-к дома'
            self.scenario(chat_id, 'Кирпичное')
        elif self.episode == 'тип здания: блочное':
            self.episode = 'ввод хар-к дома'
            self.scenario(chat_id, 'Блочное')
        elif self.episode == 'тип здания: монолитное':
            self.episode = 'ввод хар-к дома'
            self.scenario(chat_id, 'Монолитное')
        elif self.episode == 'тип здания: кирпично-монолитное':
            self.episode = 'ввод хар-к дома'
            self.scenario(chat_id, 'Кирпично-монолитное')
        elif self.episode == 'газ: есть':
            self.episode = 'ввод хар-к дома'
            self.scenario(chat_id, 'Есть')
        elif self.episode == 'газ: нет':
            self.episode = 'ввод хар-к дома'
            self.scenario(chat_id, 'Нет')
        elif self.episode == 'лифт: есть':
            self.episode = 'ввод хар-к дома'
            self.scenario(chat_id, 'Есть')
        elif self.episode == 'лифт: нет':
            self.episode = 'ввод хар-к дома'
            self.scenario(chat_id, 'Нет')
        elif self.episode == 'мусоропровод: есть':
            self.episode = 'ввод хар-к дома'
            self.scenario(chat_id, 'Есть')
        elif self.episode == 'мусоропровод: нет':
            self.episode = 'ввод хар-к дома'
            self.scenario(chat_id, 'Нет')
        elif self.episode == 'ожидание кнопки':
            pass
        elif self.episode == 'рыночная стоимость':
            buttons = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Выбрать другую цель оценки', callback_data='выбор цели')],
                            [InlineKeyboardButton(text='Выбрать другой объект недвижимости', callback_data='выбор способа ввода хар-к дома')]
                        ])
            bot.sendMessage(chat_id, f'Рыночная стоимость объекта:\n{Telegram_bot_session.split_by_three(self.market_price())} рублей', reply_markup=buttons)
            bot.sendMessage(chat_id, f'Для завершения сессии нажмите /clear')
        elif self.episode == 'рыночная стоимость аренды':
            buttons = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Выбрать другую цель оценки', callback_data='выбор цели')],
                            [InlineKeyboardButton(text='Выбрать другой объект недвижимости', callback_data='выбор способа ввода хар-к дома')]
                        ])
            bot.sendMessage(chat_id, f'Рыночная стоимость аренды объекта:\n45800 рублей', reply_markup=buttons)
            bot.sendMessage(chat_id, f'Для завершения сессии нажмите /clear')
        elif self.episode == 'будущая рыночная стоимость':
            buttons = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Выбрать другую цель оценки', callback_data='выбор цели')],
                            [InlineKeyboardButton(text='Выбрать другой объект недвижимости', callback_data='выбор способа ввода хар-к дома')]
                        ])
            bot.sendMessage(chat_id, f'Будущая рыночная стоимость объекта:\n1400000 рублей', reply_markup=buttons)
            bot.sendMessage(chat_id, f'Для завершения сессии нажмите /clear')
        elif self.episode == 'будущая рыночная стоимость аренды':
            buttons = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Выбрать другую цель оценки', callback_data='выбор цели')],
                            [InlineKeyboardButton(text='Выбрать другой объект недвижимости', callback_data='выбор способа ввода хар-к дома')]
                        ])
            bot.sendMessage(chat_id, f'Будущая рыночная стоимость аренды объекта:\n51000 рублей', reply_markup=buttons)
            bot.sendMessage(chat_id, f'Для завершения сессии нажмите /clear')
        elif self.episode == 'инвестиционная стоимость':
            buttons = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Выбрать другую цель оценки', callback_data='выбор цели')],
                            [InlineKeyboardButton(text='Выбрать другой объект недвижимости', callback_data='выбор способа ввода хар-к дома')]
                        ])
            bot.sendMessage(chat_id, f'Инвестиционная стоимость аренды объекта:\n15200000 рублей', reply_markup=buttons)
            bot.sendMessage(chat_id, f'Для завершения сессии нажмите /clear')

    def input(self, chat_id, content = '', isAddress = False, isBuildParams = False, isApartParams = False, columns = []):
        isLastEntry = False
        if self.next_input_data == '':
            if isAddress:
                self.next_input_data = Telegram_bot_session.address_columns[0]
            elif isBuildParams:
                self.next_input_data = Telegram_bot_session.building_params_columns[0]
            elif isApartParams:
                self.next_input_data = Telegram_bot_session.apartment_params_columns[0]
            elif len(columns) != 0:
                self.next_input_data = columns[0]
            else:
                return -1
            # Тут добавляем ввод кнопками
            self.input_buttons(chat_id)
            self.input_tips(chat_id)
            return 'ввод продолжается'
        
        input_error = not self.input_validation(chat_id, content)
        if input_error:
            return -1
        self.property[self.next_input_data] = content

        if isAddress:
            if self.next_input_data in Telegram_bot_session.address_columns:
                index_of_next = Telegram_bot_session.address_columns.index(self.next_input_data) + 1
                if index_of_next < len(Telegram_bot_session.address_columns):
                    self.next_input_data = Telegram_bot_session.address_columns[index_of_next]
                else:
                    isLastEntry = True
            else:
                return -1
        elif isBuildParams:
            if self.next_input_data in Telegram_bot_session.building_params_columns:
                index_of_next = Telegram_bot_session.building_params_columns.index(self.next_input_data) + 1
                if index_of_next < len(Telegram_bot_session.building_params_columns):
                    self.next_input_data = Telegram_bot_session.building_params_columns[index_of_next]
                else:
                    isLastEntry = True
            else:
                return -1
        elif isApartParams:
            if self.next_input_data in Telegram_bot_session.apartment_params_columns:
                index_of_next = Telegram_bot_session.apartment_params_columns.index(self.next_input_data) + 1
                if index_of_next < len(Telegram_bot_session.apartment_params_columns):
                    self.next_input_data = Telegram_bot_session.apartment_params_columns[index_of_next]
                else:
                    isLastEntry = True
            else:
                return -1
        elif len(columns) != 0:
            if self.next_input_data in columns:
                index_of_next = columns.index(self.next_input_data) + 1
                if index_of_next < len(columns):
                    self.next_input_data = columns[index_of_next]
                else:
                    isLastEntry = True
            else:
                return -1
        else:
            return -1
        
        if isLastEntry:
            self.next_input_data = ''
            return 'ввод завершен'
        else:
            # Тут добавляем ввод кнопками
            self.input_buttons(chat_id)
            self.input_tips(chat_id)
            return 'ввод продолжается'

    def input_buttons(self, chat_id):
        if self.next_input_data == 'Строение':
            self.episode = 'ожидание кнопки'
            buttons = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Строения нет', callback_data='строения нет')]
                        ])
            bot.sendMessage(chat_id, f'Введите данные для поля "{self.next_input_data}".')
            bot.sendMessage(chat_id, 'Если в адресе дома нет строения, то нажмите на следующую кнопку:', reply_markup=buttons)
        elif self.next_input_data == 'Тип здания':
            self.episode = 'ожидание кнопки'
            buttons = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Панельное', callback_data='тип здания: панельное')],
                            [InlineKeyboardButton(text='Кирпичное', callback_data='тип здания: кирпичное')],
                            [InlineKeyboardButton(text='Блочное', callback_data='тип здания: блочное')],
                            [InlineKeyboardButton(text='Монолитное', callback_data='тип здания: монолитное')],
                            [InlineKeyboardButton(text='Кирпично-монолитное', callback_data='тип здания: кирпично-монолитное')]
                        ])
            bot.sendMessage(chat_id, 'Выберите тип здания объекта из следующих вариантов:', reply_markup=buttons)
        elif self.next_input_data == 'Газ':
            self.episode = 'ожидание кнопки'
            buttons = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Есть', callback_data='газ: есть')],
                            [InlineKeyboardButton(text='Нет', callback_data='газ: нет')]
                        ])
            bot.sendMessage(chat_id, 'Есть ли у объекта газ?', reply_markup=buttons)
        elif self.next_input_data == 'Лифт':
            self.episode = 'ожидание кнопки'
            buttons = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Есть', callback_data='лифт: есть')],
                            [InlineKeyboardButton(text='Нет', callback_data='лифт: нет')]
                        ])
            bot.sendMessage(chat_id, 'Есть ли у объекта лифт?', reply_markup=buttons)
        elif  self.next_input_data == 'Мусоропровод':
            self.episode = 'ожидание кнопки'
            buttons = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Есть', callback_data='мусоропровод: есть')],
                            [InlineKeyboardButton(text='Нет', callback_data='мусоропровод: нет')]
                        ])
            bot.sendMessage(chat_id, 'Есть ли у объекта мусоропровод?', reply_markup=buttons)
        else:
            bot.sendMessage(chat_id, f'Введите данные для поля "{self.next_input_data}".')

    def input_validation(self, chat_id, content):
        input_type = ''
        isError = False

        if isinstance(content, str):
            content.replace(',', '.')
            if content.isdigit():
                input_type = 'целое'
            elif content.replace('.', '', 1).isdigit():
                input_type = 'действительное'
            else:
                input_type = 'строка'
        elif isinstance(content, (int, float)):
            if np.isnan(content):
                    input_type = 'nan'

        current_type = []
        if self.next_input_data == 'Улица':
            current_type = ['строка']
        elif self.next_input_data == 'Дом':
            current_type = ['целое', 'строка']
        elif self.next_input_data == 'Строение':
            current_type = ['строка', 'целое', 'nan']
        elif self.next_input_data == 'Кол-во этажей':
            current_type = ['целое']
        elif self.next_input_data == 'Тип здания':
            current_type = ['строка']
        elif self.next_input_data == 'Высота потолков':
            current_type = ['целое', 'действительное']
        elif self.next_input_data == 'Кол-во квартир':
            current_type = ['целое']
        elif self.next_input_data == 'Газ':
            current_type = ['строка']
        elif self.next_input_data == 'Лифт':
            current_type = ['строка']
        elif self.next_input_data == 'Мусоропровод':
            current_type = ['строка']
        elif self.next_input_data == 'Год строительства':
            current_type = ['целое']
        elif self.next_input_data == 'Ближайшая станция метро':
            current_type = ['строка']
            content = content.title()
            index = 0
            try:
                index = Telegram_bot_session.subway_adjustments.loc[Telegram_bot_session.subway_adjustments['Наименование станции'] == content, 'Индекс станции'].iloc[0]
                self.property['Индекс станции'] = index
            except KeyError:
                bot.sendMessage(chat_id, f'Станция метро "{content}" не найдена в базе.')
        elif self.next_input_data == 'Площадь, м²':
            current_type = ['целое', 'действительное']
        elif self.next_input_data == 'Кол-во комнат':
            current_type = ['целое']
        elif self.next_input_data == 'Этаж':
            current_type = ['целое']


        if (input_type in current_type) and (not isError):
            return True
        else:
            bot.sendMessage(chat_id, f'Некоректный ввод для "{self.next_input_data}".\nВведите значение ещё раз.')
            return False
    
    def input_tips(self, chat_id):
        if self.next_input_data == 'Улица':
            bot.sendMessage(chat_id, f'Подсказка: ожидается только название улицы с заглавной буквы.\nПример: 2-я Бауманская')
        elif self.next_input_data == 'Дом':
            bot.sendMessage(chat_id, f'Подсказка: ожидается только целое число, либо дробь.\nПример: 9/23')
        elif self.next_input_data == 'Строение':
            bot.sendMessage(chat_id, f'Подсказка: ожидается только целое число.\nПример: 2')
        elif self.next_input_data == 'Кол-во этажей':
            bot.sendMessage(chat_id, f'Подсказка: ожидается только целое число.\nПример: 25')
        elif self.next_input_data == 'Высота потолков':
            bot.sendMessage(chat_id, f'Подсказка: ожидается только число; ожидается высота выраженная в метрах.\nПример: 123')
        elif self.next_input_data == 'Кол-во квартир':
            bot.sendMessage(chat_id, f'Подсказка: ожидается только целое число.\nПример: 123')
        elif self.next_input_data == 'Год строительства':
            bot.sendMessage(chat_id, f'Подсказка: ожидается только целое число.\nПример: 1985')
        elif self.next_input_data == 'Ближайшая станция метро':
            bot.sendMessage(chat_id, f'Подсказка: ожидается только название станции с заглавной буквы.\nПример: Выхино')
        elif self.next_input_data == 'Площадь, м²':
            bot.sendMessage(chat_id, f'Подсказка: ожидается только число; ожидается площадь выраженная в метрах квадратных.\nПример: 60')
        elif self.next_input_data == 'Кол-во комнат':
            bot.sendMessage(chat_id, f'Подсказка: ожидается только целое число.\nПример: 2')
        elif self.next_input_data == 'Этаж':
            bot.sendMessage(chat_id, f'Подсказка: ожидается только целое число.\nПример: 3')

    def output(self, row):
        return ",\n".join(f"{key}: {val}" for key, val in row.items())

    def building_search(self):

        address = {key: self.property[key] for key in ["Улица", "Дом", "Строение"]}
        res = []
        try:
            res = Telegram_bot_session.db.loc[(Telegram_bot_session.db["Улица"] == address["Улица"]) & 
                        (Telegram_bot_session.db["Дом"] == address["Дом"]) & 
                        ((Telegram_bot_session.db["Строение"] == address["Строение"]) | 
                        (pd.isna(Telegram_bot_session.db["Строение"]) & pd.isna(address["Строение"])))
                        ].loc[0, Telegram_bot_session.building_params_columns]
        except KeyError:
            res = []
        return res

def handle_callback(msg):
    query_id, chat_id, data = telepot.glance(msg, flavor='callback_query')
    if chat_id in session:
        session[chat_id].episode = data
        bot.answerCallbackQuery(query_id, text='Нажатие кнопки успешно!')
        session[chat_id].scenario(chat_id)

def handle_chat_message(msg):
    global session
    content_type, chat_type, chat_id = telepot.glance(msg)

    if not (chat_id in session):
        session[chat_id] = Telegram_bot_session(chat_id)

    if content_type == 'text':
        content = msg['text']
        if content == '/start':
            session[chat_id].episode = 'старт'
        elif content == '/clear':
            del session[chat_id]

    if chat_id in session:
        session[chat_id].scenario(chat_id, content)

# Запуск бота
bot = telepot.Bot(token)
MessageLoop(bot, {'chat': handle_chat_message,
                  'callback_query': handle_callback}).run_as_thread()

while True:
    time.sleep(4)

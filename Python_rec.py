from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from progress.bar import IncrementalBar
from easygui import *
import easygui as gui
import pandas as pd
import numpy as np
import sys

# максимальное увеличение размера массива отображения numpy для отображения easygui
np.set_printoptions(threshold=sys.maxsize)
# фрейм данных относительно большой, начальная загрузка займет около 30 секунд
# в зависимости от вашего компьютера, поэтому здесь уместна индикация загрузки
progress_bar = IncrementalBar('Loading Movie Database...', max=1)
for i in range(1):

    df_tags = pd.read_csv("tags.csv", usecols=[1, 2])
    df_movies = pd.read_csv("movies.csv")
    df_ratings = pd.read_csv("ratings.csv", usecols=[1, 2])
    # объединение столбцов из отдельных фреймов данных в новый фрейм
    df_1 = pd.merge(df_movies, df_ratings, on='movieId', how='outer')
    # заполнение значений NaN средним рейтингом
    df_1['rating'] = df_1['rating'].fillna(df_1['rating'].mean())
    # группирование строк df по среднему рейтингу фильма
    df_1 = pd.DataFrame(df_1.groupby('movieId')['rating'].mean().reset_index().round(1))
    # добавление столбцов title и genres в df
    df_1['title'] = df_movies['title']
    df_1['genres'] = df_movies['genres']
    progress_bar.next()
    # заполнение индикатора загрузки при успешной загрузке
progress_bar.finish()

def which_way():
    '''
    Эта функция, которая выполняется при запуске программы.
    Работает как перекресток, вы выбираете поиск фильмов по
    тегу или по жанру. По выбору пользователь переходит к следующему окну.
    '''
    # определение параметров easygui choicebox
    msg = "Choose an option:"
    title = "Main Menu"
    choices = ["Search recommended movies by genre:", "Search recommended movies by tag:"]
    fieldValues = choicebox(msg, title, choices)

    # переменная fieldValues - это пользовательский ввод, который возвращается из графического интерфейса
    # условный оператор, направляющий пользователя к следующему интерфейсу на основе ввода
    if fieldValues == "Search recommended movies by genre:":
        genre_entry()

    elif fieldValues == "Search recommended movies by tag:":
        tag_entry()

def field_check(msg, title, fieldNames):
    '''
    Эта функция проверяет отсутствие вводимых пользователем значений в multenterbox
    и возвращает пользовательский ввод как переменную fieldValues.

    Параметры:

    msg, title и fieldnames графического интерфейса multienterbox

    '''

    fieldValues = multenterbox(msg, title, fieldNames)

    # Цикл с условием, чтобы проверить,
    # что поля ввода не пусты
    while 1:
        if fieldValues is None: break
        errmsg = ""
        for i in range(len(fieldNames)):
            if fieldValues[i].strip() == "":
                errmsg += ('"%s" is a required field.\n\n' % fieldNames[i])
        if errmsg == "":
            break  # если пустых полей не найдено, перейти к следующему блоку кода
        # cохранить пользовательский ввода в виде списка в переменной fieldValues
        fieldValues = multenterbox(errmsg, title, fieldNames, fieldValues)

    return fieldValues

def tag_entry():
    '''
    Эта функция определяет параметры easygui multenterbox и вызывает
    field_check, если пользователь вводил значнеие,
    вызывает тест на подобие; если совпадение не найдено, пользователь возвращается
    в окно ввода
    '''

    # определение параметров easygui multenterbox
    msg = "Enter movie tag for example: world war 2 | brad pitt | documentary \nIf tag not found you will be returned to this window"
    title = 'Search by tag'
    fieldNames = ["Tag"]

    # вызов field_check() для проверки отсутствия пользовательского ввода и
    # сохранения вода как переменной fieldValues
    fieldValues = field_check(msg, title, fieldNames)

    # Если пользователь ввел значение, сохраняем его в fieldValues[0]
    if fieldValues != None:
        global user_input_2
        user_input_2 = fieldValues[0]

        # здесь мы вызываем функцию, которая в основном проверяет строку
        # на схожесть с другими строками. Когда пользователь нажимает кнопку отмены, он возвращается в главное меню
        similarity_test2(user_input_2)
    else:
        which_way()

def tag():
    '''
    Эта функция добавляет все совпадающие по тегам фильмы во фрейм данных pandas,
    изменяет фрейм данных для правильного отображения easygui, отбросив некоторые
    столбцы, сбрасывая индекс df, объединяя фреймы и сортируя элементы так,
    чтобы показывались фильмы с рейтингом >= 2.5. Она также преобразует столбцы df в списки
    и приводит их в порядок в массиве numpy для отображения easygui.
    '''

    # добавление тегов найденных фильмов как объекта фрейма
    final_1 = []
    for i in final_2:
        final_1.append(df_tags.loc[df_tags['tag'].isin(i)])

    # сброс индекса df, удаление столбца индекса, а также повторяющихся записей
    lst = final_1[0]
    lst = lst.reset_index()
    lst.drop('index', axis=1, inplace=True)
    lst = lst.drop_duplicates(subset='movieId')
    # слияние movieId с названиями и жанрами + удаление тега и идентификатора фильма
    df = pd.merge(lst, df_1, on='movieId', how='left')
    df.drop('tag', axis=1, inplace=True)
    df.drop('movieId', axis=1, inplace=True)
    # сортировка фильмов по рейтингам, отображение только фильмов с рейтингом выше или равным 2,5
    data = df.sort_values(by='rating', ascending=False)
    data = data[data['rating'] >= 2.5]
    heading = []  # добавление названий столбцов как первой строки фрейма данных для отображения easygui
    heading.insert(0, {'rating': 'Rating', 'title': '----------Title',
                       'genres': '----------Genre'})
    data = pd.concat([pd.DataFrame(heading), data], ignore_index=True, sort=True)

    # преобразование столбцов фрейма данных в списки
    rating = data['rating'].tolist()
    title = data['title'].tolist()
    genres = data['genres'].tolist()
    # составление массива numpy из списков столбцов dataframe для отображения easygui
    data = np.concatenate([np.array(i)[:, None] for i in [rating, title, genres]], axis=1)
    data = str(data).replace('[', '').replace(']', '')

    # отображение фильмов пользователю
    gui.codebox(msg='Movies filtered by tag returned from database:',
                text=(data), title='Movies')

    which_way()

def genre_entry():
    '''
    Эта функция определяет параметры easygui multenterbox
    и вызывает field_check, если пользователь что-то вводил,
    вызывается тест на подобие. Если совпадение не найдено, пользователь возвращается
    в то же окно
    '''
    # определение параметров easygui multenterbox
    msg = "Enter movie genre for example: mystery | action comedy | war \nIf genre not found you will be returned to this window"
    title = "Search by genre"
    fieldNames = ["Genre"]

    # вызов field_check() для проверки отсутствия пользовательского ввода и
    # сохранения ввода в fieldValues.
    fieldValues = field_check(msg, title, fieldNames)

    # Если пользовательский ввод не пуст, сохраняет его в переменной user_input
    if fieldValues != None:
        global user_input
        user_input = fieldValues[0]

        # здесь мы вызываем функцию, которая в основном проверяет строку
        # на подобие с другими строками. Если пользователь нажмет кнопку отмена, то он вернется в главное меню
        similarity_test1(user_input)
    else:
        which_way()

def genre():
    '''
    Эта функция добавляет все соответствующие жанру фильмы во фрейм pandas,
    изменяет фрейм для правильного отображения easygui, отбросив некоторые
    столбцы, сбрасывает индекс df, объединеняет фреймы и сортирует фильмы для отображения
    только фильмов с рейтингом >= 2.5. Она также преобразует столбцы конечного df в списки
    и приводит их в порядок в массиве numpy для отображения easygui.
    '''

    # добавление соответствующих жанру фильмов во фрейм.
    final_1 = []
    for i in final:
        final_1.append(df_movies.loc[df_movies['genres'].isin(i)])

    # сброс индекса df, удаление индекса столбцов и дубликатов записей
    lst = final_1[0]
    lst = lst.reset_index()
    lst.drop('index', axis=1, inplace=True)
    lst.drop('title', axis=1, inplace=True)
    lst.drop('genres', axis=1, inplace=True)
    lst = lst.drop_duplicates(subset='movieId')

    # объединение идентификатора фильма с названием, рейтингом и жанром + удаление индекса, названия и жанра
    df = pd.merge(lst, df_1, on='movieId', how='left')
    # сортировка по рейтингу, отображение только фильмов с рейтингом выше или равным 2,5
    data = df.sort_values(by='rating', ascending=False)
    data.drop('movieId', axis=1, inplace=True)
    data = data[data['rating'] >= 2.5]
    heading = []  # add column names as first dataframe row for easygui display
    heading.insert(0, {'rating': 'Rating', 'title': '----------Title',
                       'genres': '----------Genre'})
    data = pd.concat([pd.DataFrame(heading), data], ignore_index=True, sort=True)
    # преобразование столбцов фрейма данных в списки
    rating = data['rating'].tolist()
    title = data['title'].tolist()
    genres = data['genres'].tolist()

    # составление массива numpy из списков столбцов фрейма для отображения easygui
    data = np.concatenate([np.array(i)[:, None] for i in [rating, title, genres]], axis=1)
    data = str(data).replace('[', '').replace(']', '')

    # отображение фильмов пользователю
    gui.codebox(msg='Movies filtered by genre returned from database:',
                text=(data), title='Movies')

    which_way()

def similarity_test1(user_input):
    '''
    Эта функция проверяет схожесть строк путем сопоставления пользовательского ввода
    для жанров фильмов, совпадения > 90% сохраняется в переменной, которая
    затем передается функции жанра для сопоставления с базой данных и
    возврата в окно ввода, если совпадение не найдено
    '''
    # сохранение жанров фильмов в качестве тестовой базы и пользовательского ввода для тестирования
    genre_list = df_movies['genres'].unique()
    query = user_input
    choices = genre_list
    # here fuzzywuzzy does its magic to test for similarity
    output = process.extract(query, choices)

    # сохранение совпадений в переменной и их передача следующей функции
    global final
    final = [i for i in output if i[1] > 90]

    # если совпадений > 90%  не найдено, вернуть пользователя в окно жанра
    if final == []:
        genre_entry()
    else:
        genre()


def similarity_test2(user_input_2):
    '''
    Эта функция проверяет схожесть строк путем сопоставления пользовательского ввода
    в теги фильмов, совпадение > 90% сохраняется в переменной, которая
    затем передается в функцию тега для сопоставления базы данных и
    возврата в окно ввода, если совпадение не найдено
    '''
    # сохранение тега фильма в качестве тестовой базы и пользовательского ввода для тестирования
    tag_list = df_tags['tag'].unique()
    query = user_input_2
    choices = tag_list
    output = process.extract(query, choices)

    # сохранение возвращенных совпадений в переменной и их передача следующей функции
    global final_2
    final_2 = [i for i in output if i[1] > 90]

    # если совпадение> 90% не найдено, возврат в окно ввода
    if final_2 == []:
        tag_entry()
    else:
        tag()

if __name__ == '__main__':
    which_way()
from aiogram import types
from loader import dp
import random

max_count = 150
total = 0
new_game = False
duel = []
first = 0
current = 0


@dp.message_handler(commands=['start', 'старт'])
async def mes_start(message: types.Message):
    global new_game
    name = message.from_user.first_name
    if not new_game:
        await message.answer(f'Привет, {name}! Давай поиграем в конфеты.\n\n'
                             f'Выбери количество конфет: '
                             f'напиши /set и через пробел количество конфет (по умолчанию конфет 150),\n\n'
                             f'а потом нажми /new_game\n'
                             f'или /duel и id противника для игры вдвоем.')
        print(message.from_user.id)
    else:  # добавлена возможность сброса начатой игры по команде /start
        new_game = False
        await message.answer(f'Ну что, {name}, начинаем играть заново.\n\n'
                             f'Выбери количество конфет: '
                             f'напиши /set и через пробел количество конфет,\n\n'
                             f'а потом нажми /new_game\n'
                             f'Или /duel и id противника для игры вдвоем.\n\n/rules - здесь правила\n')


@dp.message_handler(commands=['rules'])  # добавлено описание правил
async def mes_rules(message: types.Message):
    await message.answer('На столе лежит заданное количество конфет.\n'
                         'Играют два игрока, делая ход по очереди.\n'
                         'Первый ход определяется жеребьёвкой.\n'
                         'За один ход можно забрать не более чем 28 конфет.\n'
                         'Все конфеты противника достаются сделавшему последний ход.')


@dp.message_handler(commands=['new_game'])
async def mes_new_game(message: types.Message):
    global new_game
    global total
    global max_count
    new_game = True
    total = max_count
    await message.answer(f'Игра началась, на столе {total} конфет.')
    await lot(message)  # выбор игрока, делающего первый ход, вынесен в отдельную функцию


@dp.message_handler(commands=['duel'])
async def mes_duel(message: types.Message):
    global new_game
    global total
    global max_count
    global duel
    global current
    global first
    try:  # добавлена проверка, если после команды /duel не будет введен id или введены не цифры
        duel.append(int(message.from_user.id))
        duel.append(int(message.text.split()[1]))
        player = duel[0]  # переменной player присвоено значение duel[0]
        enemy = duel[1]  # переменной enemy присвоено значение duel[1]
        total = max_count
        first = random.randint(0, 1)
        if first:
            await dp.bot.send_message(player, f'Игра началась. На столе {total} конфет. Первый ход за тобой. '
                                              'Бери конфеты')  # duel[0] заменена переменной player
            await dp.bot.send_message(enemy, f'Игра началась. На столе {total} конфет. '
                                             f'Первый ход за твоим противником. '
                                             'А ты жди своего хода')  # duel[1] заменена переменной enemy
        else:
            await dp.bot.send_message(enemy, f'Игра началась. На столе {total} конфет. Первый ход за тобой. '
                                             'Бери конфеты')  # вместо duel[1] переменная enemy
            await dp.bot.send_message(player, f'Игра началась. На столе {total} конфет. '
                                              f'Первый ход за твоим противником. '
                                              'А ты жди своего хода')  # duel[0] заменена переменной player
        current = player if first else enemy  # duel[0] и duel[1] заменены на переменные player и enemy
        new_game = True
    except:
        await message.answer(f'{message.from_user.first_name}, нужен id соперника, '
                             f'а то непонятно, с кем хочешь играть.')


@dp.message_handler(commands=['set'])
async def mes_set(message: types.Message):
    global max_count
    global new_game
    name = message.from_user.first_name
    try:  # добавлена проверка, чтобы при вводе команды /set без указания числа не вылетала ошибка: IndexError
        count = message.text.split()[1]
        if not new_game:
            if count.isdigit():
                max_count = int(count)
                await message.answer(f'Конфет теперь будет {max_count}')
            else:
                await message.answer(f'{name}, напиши цифрами')
        else:
            await message.answer(f'{name}, нельзя менять правила во время игры')
    except IndexError:
        if new_game:  # добавлено условие, чтобы не выводилось сообщение, что Конфет будет ..., если игра уже началась
            await message.answer(f'{name}, нельзя менять правила во время игры. Бери уже конфеты.'
                                 f'Или жди своего хода')
        else:
            await message.answer(f'Конфет будет {max_count}, начинаем /new_game ?')


@dp.message_handler()
async def mes_take_candy(message: types.Message):
    global total
    global new_game
    global max_count
    global duel
    name = message.from_user.first_name
    count = message.text  # все вхождения message.text в функцию заменены переменной count
    if len(duel) == 0:
        if new_game:
            if count.isdigit() and 0 < int(count) < 29:
                total -= int(count)
                if total <= 0:
                    await message.answer('Ты забрал последние конфеты и победил!')
                    new_game = False
                else:
                    await message.answer(f'Ты взял(а) {count} конфет. На столе осталось {total} конфет.')
                    await bot_turn(message)
            else:
                await message.answer(f'{name}, надо указать ЧИСЛО от 1 до 28.')
    else:
        if current == int(message.from_user.id):
            if new_game:
                if count.isdigit() and 0 < int(count) < 29:
                    total -= int(count)
                    if total <= 0:
                        await message.answer('Ты забрал последние конфеты и победил! Поиграем еще? /start')
                        await dp.bot.send_message(enemy_id(), 'К сожалению, ты проиграл, '
                                                              'твой противник оказался хитрее'
                                                              'Поиграем еще? /start')
                        new_game = False
                    else:
                        await message.answer(f'Ты взял {count} конфет. На столе осталось {total} конфет. '
                                             f'Теперь подожди, когда сделает ход твой противник')
                        await dp.bot.send_message(enemy_id(), f'Твой противник взял {count} конфет. '
                                                              f'На столе осталось ровно {total}. '
                                                              f'Теперь твой ход, бери конфеты.')
                        switch_players()
                else:
                    await message.answer(f'{name}, надо указать ЧИСЛО от 1 до 28.')


async def bot_turn(message: types.Message):
    global total
    global new_game
    # bot_take = 0 - здесь можно не объявлять переменную bot_take
    if 0 < total < 29:
        bot_take = total
        total -= bot_take
        await message.answer(f'Candy-бот взял {bot_take} конфет. '
                             f'На столе осталось {total} конфет и Candy-бот одержал победу!')
        new_game = False
    else:
        reminder = total % 29
        bot_take = reminder if reminder != 0 else 28
        total -= bot_take
        await message.answer(f'Candy-бот взял {bot_take} конфет. На столе осталось {total} конфет.')


def switch_players():
    global duel
    global current
    if current == duel[0]:
        current = duel[1]
    else:
        current = duel[0]


def enemy_id():
    global duel
    global current
    if current == duel[0]:
        return duel[1]
    else:
        return duel[0]


async def lot(message):
    global first
    if first:
        await message.answer(f'Первый ход достался тебе, {message.from_user.first_name}. Бери конфеты')
    else:
        await message.answer('Первый ход достается Candy-боту')
        await bot_turn(message)

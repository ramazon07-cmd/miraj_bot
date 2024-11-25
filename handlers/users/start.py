import requests
from datetime import datetime
import pytz
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from keyboards.default.newkeyboards import menu, menu_rus
from keyboards.default.orderkeyboards import ordbut, delevery, checkbutton, comback, location, number, \
    ordbut_rus, number_rus, delevery_rus, checkbutton_rus, location_rus, comback_rus
from keyboards.inline.admin import adminbut
from keyboards.inline.lang import langs
from keyboards.inline.mycallbak import ordcallback
from keyboards.inline.utils import my_callback
from data.config import ADMINS
from loader import dp
from save import save_user, Create_order
from states.orderState import OrderData, RegOrderData
from utils.location import get_address_from_coords
from data.config import ADDRES

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


users = dict()


def get_lang_code(user_lang):
    return 'ru' if user_lang == 'rus' else 'uz'


@dp.message_handler(Command('start'))
async def show_menu1(message: Message):
    users[message.from_user.id] = dict()
    if message.from_user.id in ADMINS:
        await dp.bot.send_message(message.chat.id, "<b>Assalomu alaykum! Admin botga xush kelibsiz.</b>", reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
    await dp.bot.send_message(message.chat.id, "Miraj Restaurant Botga xush kelibsiz!", reply_markup=ReplyKeyboardRemove())
    await dp.bot.send_message(message.chat.id, "Tilni tanlang | Выберите язык", reply_markup=langs)
    if save_user(message) == 201:
        join = datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%Y-%m-%d, %H:%M')
        for admin in ADMINS:
            txt = f"Yangi foydalanuvchi qo'shildi:\n" \
                f"<b>Vaqti:</b> {join}\n" \
                f"<b>User:</b> <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
            await dp.bot.send_message(admin, txt, parse_mode='HTML')


@dp.callback_query_handler(text=['uzb', 'rus'])
async def myorder(call: CallbackQuery):
    await dp.bot.delete_message(call.message.chat.id, call.message.message_id)
    if call.data == 'uzb':
        users[call.from_user.id]['lang'] = 'uzb'
        await dp.bot.send_message(call.message.chat.id, f"Assalomu alaykum {call.from_user.full_name}.",
                                  reply_markup=menu)
    elif call.data == 'rus':
        users[call.from_user.id]['lang'] = 'rus'
        await dp.bot.send_message(call.message.chat.id, f"Привет {call.from_user.full_name}.",
                                  reply_markup=menu_rus)


@dp.message_handler(CommandStart(), state=OrderData)
async def show_menu2(message: Message, state: FSMContext):
    await state.finish()
    lang = users[message.from_user.id].get('lang', '-')
    if lang == 'rus':
        await message.answer(f"Привет {message.from_user.full_name}.", reply_markup=menu_rus)
    else:
        await message.answer(f"Assalomu alaykum {message.from_user.full_name}.", reply_markup=menu)


@dp.message_handler(CommandStart(), state=RegOrderData)
async def show_menu3(message: Message, state: FSMContext):
    await state.finish()
    lang = users[message.from_user.id].get('lang', '-')
    if lang == 'rus':
        await message.answer(f"Привет {message.from_user.full_name}", reply_markup=menu_rus)
    else:
        await message.answer(f"Assalomu alaykum {message.from_user.full_name}", reply_markup=menu)


@dp.message_handler(text=['🍔 Buyurtma berish', '🍔 Заказать'])
async def show_menu4(message: Message):
    try:
        lang = users[message.from_user.id].get('lang', '-')
        lang_code = get_lang_code(lang)
        data = requests.get(f'{ADDRES}category/?lang={lang_code}').json()
        but = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, )
        but.add(*(KeyboardButton(text=str(num['title'])) for num in data))
        but.add(KeyboardButton(text='🏠 Bosh menyu'), KeyboardButton(text='⬅️ Orqaga'))

        but_rus = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, )
        but_rus.add(*(KeyboardButton(text=str(num['title'])) for num in data))
        but_rus.add(KeyboardButton(text='🏠 Главное меню'), KeyboardButton(text='⬅️ Назад'))
        try:
            if lang == 'rus':
                await message.answer('Категории', reply_markup=but_rus)
            else:
                await message.answer('Kategoriyalar', reply_markup=but)
            await OrderData.category.set()
        except:
            pass
    except Exception:
        pass


@dp.message_handler(text=['📦 Buyurtmalarim', '📦 Мои заказы'])
async def Order(message: Message):
    keyboard = types.InlineKeyboardMarkup()
    data = requests.get(f'{ADDRES}order/{message.from_user.id}/').json()
    lang = users[message.from_user.id].get('lang', '-')
    try:
        if data:
            if data['page_number'] != data['count'] and data['page_number'] == 1:
                keyboard.add(types.InlineKeyboardButton(f"{data['page_number']} / {data['count']}", callback_data='0'),
                             types.InlineKeyboardButton('➡️',
                                                        callback_data=ordcallback.new(num=data['page_number'] + 1)))
            elif data['page_number'] != data['count'] and data['page_number'] != 1:
                keyboard.add(
                    types.InlineKeyboardButton('⬅️', callback_data=ordcallback.new(num=data['page_number'] - 1)),
                    types.InlineKeyboardButton(f"{data['page_number']} / {data['count']}", callback_data='0'),
                    types.InlineKeyboardButton('➡️', callback_data=ordcallback.new(num=data['page_number'] + 1)))
            elif data['count'] == 1:
                keyboard.add(types.InlineKeyboardButton(f"{data['page_number']} / {data['count']}", callback_data='0'))
            elif data['page_number'] == data['count']:
                keyboard.add(
                    types.InlineKeyboardButton('⬅️', callback_data=ordcallback.new(num=data['page_number'] - 1)),
                    types.InlineKeyboardButton(f"{data['page_number']} / {data['count']}", callback_data='0'))

            if lang == 'rus':
                await message.answer(f'ID: #{data["results"][0]["id"]}A\n'
                                     f'Время: {data["results"][0]["created_at"]}\n'
                                     f'Телефон: {data["results"][0]["number"]}\n'
                                     f'Расходы: {data["results"][0]["price"]}\n'
                                     f'\nУсловие: {data["results"][0]["order"]}',
                                     reply_markup=keyboard)

            else:
                await message.answer(f'ID: #{data["results"][0]["id"]}A\n'
                                     f'Vaqti: {data["results"][0]["created_at"]}\n'
                                     f'Telefon: {data["results"][0]["number"]}\n'
                                     f'Narxi: {data["results"][0]["price"]}\n'
                                     f'\nHolati: {data["results"][0]["order"]}',
                                     reply_markup=keyboard)

    except:
        if lang == 'rus':
            await message.answer('У вас нет заказов')
        else:
            await message.answer('Sizda buyurtmalar yo\'q')


@dp.callback_query_handler(ordcallback.filter())
async def myorder(call: CallbackQuery, callback_data: dict):
    data = requests.get(f'{ADDRES}order/{call.from_user.id}/?page={callback_data.get("num")}').json()
    keyboard = types.InlineKeyboardMarkup()

    if data:
        try:
            if data['page_number'] == 1:
                keyboard.add(types.InlineKeyboardButton(f"{data['page_number']} / {data['count']}", callback_data='0'),
                             types.InlineKeyboardButton('➡️',
                                                        callback_data=ordcallback.new(num=data['page_number'] + 1)))
            elif data['page_number'] != data['count'] and data['page_number'] != 1:
                keyboard.add(
                    types.InlineKeyboardButton('⬅️', callback_data=ordcallback.new(num=data['page_number'] - 1)),
                    types.InlineKeyboardButton(f"{data['page_number']} / {data['count']}", callback_data='0'),
                    types.InlineKeyboardButton('➡️', callback_data=ordcallback.new(num=data['page_number'] + 1)))

            elif data['page_number'] == data['count']:
                keyboard.add(
                    types.InlineKeyboardButton('⬅️', callback_data=ordcallback.new(num=data['page_number'] - 1)),
                    types.InlineKeyboardButton(f"{data['page_number']} / {data['count']}", callback_data='0'))
            lang = users[call.from_user.id].get('lang', '-')
            if lang == 'rus':
                await dp.bot.edit_message_text(text=f'ID: #{data["results"][0]["id"]}A\n'
                                                    f'Время: {data["results"][0]["created_at"]}\n'
                                                    f'Телефон: {data["results"][0]["number"]}\n'
                                                    f'Расходы: {data["results"][0]["price"]}\n'
                                                    f'\nУсловие: {data["results"][0]["order"]}',
                                               chat_id=call.message.chat.id,
                                               message_id=call.message.message_id, reply_markup=keyboard)

            else:
                await dp.bot.edit_message_text(text=f'ID: #{data["results"][0]["id"]}A\n'
                                                    f'Vaqti: {data["results"][0]["created_at"]}\n'
                                                    f'Telefon: {data["results"][0]["number"]}\n'
                                                    f'Narxi: {data["results"][0]["price"]}\n'
                                                    f'\nHolati: {data["results"][0]["order"]}',
                                               chat_id=call.message.chat.id,
                                               message_id=call.message.message_id, reply_markup=keyboard)
        except:
            pass
    else:
        await call.answer('Sizda buyurtmalar yo\'q | У вас нет заказов')


@dp.message_handler(text=['⚙ Настройки', '⚙ Sozlamalar'])
async def settings(message: Message):
    lang = users[message.from_user.id].get('lang', '-')
    if lang == 'rus':
        await message.answer("Выберите язык", reply_markup=langs)
    else:
        await message.answer("Tilni tanlang", reply_markup=langs)


@dp.message_handler(text=['🛒 Korzina', '🛒 Корзина'])
async def show_menu6(message: Message):
    but_uz = types.InlineKeyboardMarkup(row_width=1)
    but_ru = types.InlineKeyboardMarkup(row_width=1)
    data = requests.get(f'{ADDRES}korzina/list/{message.from_user.id}').json()
    x = 0
    txt = '🛒Savatdagi mahsulotlarni tekshirib kiyin `Rasmiylashtirish` ni bosing!!!\n\n'
    txt_rus = '🛒После проверки товаров в корзине нажмите «Оформить заказ»!!!\n\n'

    for i in data:
        price_int = int(i["price"])
        count_int = int(i["count"])
        total_price = price_int * count_int
        
        txt += f'🔹<b>{i["product"]}</b>\n' \
            f'{count_int} x {price_int} = {total_price:,} \n\n'.replace(',', ' ')
        x += total_price
        
        txt_rus += f'🔹<b>{i["product"]}</b>\n' \
                f'{count_int} x {price_int} = {total_price:,} \n\n'.replace(',', ' ')

    txt += f"<b>Umumiy:</b> {x:,} so'm".replace(',', ' ')
    txt_rus += f"<b>Общий:</b> {x:,} сум".replace(',', ' ')
    but_uz.row(*(types.InlineKeyboardButton(f'✖️{i["product"]}',
                                            callback_data=my_callback.new(item=f'id_{i["id"]}')) for i in data))
    but_uz.add(types.InlineKeyboardButton('♻️Tozalash', callback_data=my_callback.new(item='clear')))
    but_uz.add(types.InlineKeyboardButton('✅ Rasmiylashtirish', callback_data=my_callback.new(item='order')))

    but_ru.row(*(types.InlineKeyboardButton(f'✖️{i["product"]}',
                                            callback_data=my_callback.new(item=f'id_{i["id"]}')) for i in data))
    but_ru.add(types.InlineKeyboardButton('♻️Уборка', callback_data=my_callback.new(item='clear')))
    but_ru.add(types.InlineKeyboardButton('✅ Регистрация', callback_data=my_callback.new(item='order')))

    if data:
        lang = users[message.from_user.id].get('lang', '-')
        if lang == 'rus':
            await message.answer(txt_rus, reply_markup=but_ru, parse_mode='HTML')
        else:
            await message.answer(txt, reply_markup=but_uz, parse_mode='HTML')
    else:
        lang = users[message.from_user.id].get('lang', '-')
        lang_code = get_lang_code(lang)
        data = requests.get(f'{ADDRES}category/?lang={lang_code}').json()
        but = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, )
        but.add(*(KeyboardButton(text=str(num['title'])) for num in data))
        but.add(KeyboardButton(text='🏠 Bosh menyu'), KeyboardButton(text='⬅️ Orqaga'))

        but_rus = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, )
        but_rus.add(*(KeyboardButton(text=str(num['title'])) for num in data))
        but_rus.add(KeyboardButton(text='🏠 Главное меню'), KeyboardButton(text='⬅️ Назад'))
        if lang == 'rus':
            await message.answer('Корзина пуста, выберите товары и добавьте их в корзину', reply_markup=but_rus,
                                 reply=True)
        else:
            await message.answer('Korzina bo\'sh, Mahsulotlarni tanlang va korzinaga qo\'shing', reply_markup=but,
                                 reply=True)
        await OrderData.category.set()


@dp.callback_query_handler(my_callback.filter(item='clear'))
async def korzinaclear(call: CallbackQuery, callback_data: dict):
    requests.get(url=f'{ADDRES}korzina/clear/{call.from_user.id}')

    lang = users[call.from_user.id].get('lang', '-')
    if lang == 'rus':
        await dp.bot.edit_message_text(text='🛒 Корзина очищена', chat_id=call.message.chat.id,
                                       message_id=call.message.message_id)
    else:
        await dp.bot.edit_message_text(text='🛒 Korzina tozalandi', chat_id=call.message.chat.id,
                                       message_id=call.message.message_id)


@dp.callback_query_handler(my_callback.filter(item='order'))
async def order(call: CallbackQuery, callback_data: dict):
    data = requests.get(f'{ADDRES}korzina/list/{call.from_user.id}').json()
    if data:
        await dp.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        lang = users[call.from_user.id].get('lang', '-')
        if lang == 'rus':
            await dp.bot.send_message(chat_id=call.message.chat.id, text='Выберите тип оплаты', reply_markup=ordbut_rus)
        else:
            await dp.bot.send_message(chat_id=call.message.chat.id, text='To`lov turini tanlang', reply_markup=ordbut)
        await RegOrderData.pay.set()
    else:
        lang = users[call.from_user.id].get('lang', '-')
        if lang == 'rus':
            await call.answer(text="Корзина пуста", show_alert=True)
        else:
            await call.answer(text="Korzina bo'sh", show_alert=True)


@dp.callback_query_handler(my_callback.filter())
async def korzina(call: CallbackQuery, callback_data: dict):
    pk = callback_data.get('item').split('_')[1]
    requests.delete(url=f'{ADDRES}korzina/delete/{pk}')
    but_uz = types.InlineKeyboardMarkup(row_width=3, )
    but_ru = types.InlineKeyboardMarkup(row_width=3, )
    data = requests.get(f'{ADDRES}korzina/list/{call.from_user.id}').json()
    x = 0
    txt = '🛒Savatdagi mahsulotlarni tekshirib kiyin `Rasmiylashtirish` ni bosing!!!\n\n'
    txt_rus = '🛒После проверки товаров в корзине нажмите «Оформить заказ»!!!\n\n'

    for i in data:
        price_int = int(i["price"])
        count_int = int(i["count"])
        total_price = price_int * count_int
        
        txt += f'🔹<b>{i["product"]}</b>\n' \
            f'{count_int} x {price_int} = {total_price:,} \n\n'.replace(',', ' ')
        x += total_price
        
        txt_rus += f'🔹<b>{i["product"]}</b>\n' \
                f'{count_int} x {price_int} = {total_price:,} \n\n'.replace(',', ' ')

    txt += f"<b>Umumiy:</b> {x:,} so'm".replace(',', ' ')
    txt_rus += f"<b>Общий:</b> {x:,} сум".replace(',', ' ')
    but_uz.row(*(types.InlineKeyboardButton(f'✖️{i["product"]}',
                                            callback_data=my_callback.new(item=f'id_{i["id"]}')) for i in data))
    but_uz.add(types.InlineKeyboardButton('♻️Tozalash', callback_data=my_callback.new(item='clear')))
    but_uz.add(types.InlineKeyboardButton('✅ Rasmiylashtirish', callback_data=my_callback.new(item='order')))

    but_ru.row(*(types.InlineKeyboardButton(f'✖️{i["product"]}',
                                            callback_data=my_callback.new(item=f'id_{i["id"]}')) for i in data))
    but_ru.add(types.InlineKeyboardButton('♻️Уборка', callback_data=my_callback.new(item='clear')))
    but_ru.add(types.InlineKeyboardButton('✅ Регистрация', callback_data=my_callback.new(item='order')))
    try:
        lang = users[call.from_user.id].get('lang', '-')
        if lang == 'rus':
            await dp.bot.edit_message_text(text=txt_rus, chat_id=call.message.chat.id,
                                           message_id=call.message.message_id, reply_markup=but_ru)
        else:
            await dp.bot.edit_message_text(text=txt, chat_id=call.message.chat.id,
                                           message_id=call.message.message_id, reply_markup=but_uz)

    except:
        lang = users[call.from_user.id].get('lang', '-')
        if lang == 'rus':
            await dp.bot.edit_message_text(text='Корзина пуста, выберите товары и добавьте их в корзину',
                                           chat_id=call.message.chat.id,
                                           message_id=call.message.message_id, reply_markup=but_ru)
        else:
            await dp.bot.edit_message_text(text='Korzina bo\'sh, Mahsulotlarni tanlang va korzinaga qo\'shing',
                                           chat_id=call.message.chat.id,
                                           message_id=call.message.message_id, reply_markup=but_uz)
        await OrderData.category.set()


@dp.message_handler(state=RegOrderData.pay)
async def regorder(message: Message, state: FSMContext):
    lang = users[message.from_user.id].get('lang', '-')
    if message.text == '⬅️ Orqaga' or message.text == '⬅️ Назад':
        if lang == 'rus':
            await message.answer('🏠 Главное меню', reply_markup=menu_rus)
        else:
            await message.answer('🏠 Bosh menu', reply_markup=menu)
        await state.finish()

    elif message.text == '💳 Click':
        await state.update_data(
            {"pay": message.text}
        )

        if lang == 'rus':
            await message.answer('Отправьте или введите свой номер телефона Пример: +998940938189',
                                 reply_markup=number_rus)
        else:
            await message.answer('Telefon raqamingizni yuboring yoki kiriting Misol: +998940938189',
                                 reply_markup=number)
        await RegOrderData.number.set()

    elif message.text == '💵 Naqd' or message.text == '💵 Наличные':
        await state.update_data(
            {"pay": message.text}
        )
        if lang == 'rus':
            await message.answer('Отправьте или введите свой номер телефона Пример: +998940938189',
                                 reply_markup=number_rus)
        else:
            await message.answer('Telefon raqamingizni yuboring yoki kiriting Misol: +998940938189',
                                 reply_markup=number)

        await RegOrderData.number.set()


@dp.message_handler(state=RegOrderData.number)
@dp.message_handler(content_types='contact', state=RegOrderData.number)
async def regordernum(message: Message, state: FSMContext):
    lang = users[message.from_user.id].get('lang', '-')

    if message.text == '⬅️ Orqaga' or message.text == '⬅️ Назад':
        if lang == 'rus':
            await message.answer('Отправить тип платежа', reply_markup=ordbut_rus)
        else:
            await message.answer('To`lov turini yuboring', reply_markup=ordbut)
        await RegOrderData.pay.set()

    elif message.contact.phone_number:
        await state.update_data(
            {"number": message.contact.phone_number}
        )
        if lang == 'rus':
            await message.answer('Выберите тип доставки', reply_markup=delevery_rus)
        else:
            await message.answer('Yetkazib berish turini tanlang', reply_markup=delevery)
        await RegOrderData.delivery.set()
    elif len(message.text) == 12 or len(message.text) == 13:
        await state.update_data(
            {"number": message.text}
        )
        if lang == 'rus':
            await message.answer('Выберите тип доставки', reply_markup=delevery_rus)
        else:
            await message.answer('Yetkazib berish turini tanlang', reply_markup=delevery)
        await RegOrderData.delivery.set()
    else:
        if lang == 'rus':
            await message.answer("Номер ошибки!", reply_markup=number_rus)
        else:
            await message.answer("Номер ошибки!", reply_markup=number)
        await RegOrderData.number.set()


@dp.message_handler(state=RegOrderData.delivery)
async def regorder2(message: Message, state: FSMContext):
    lang = users[message.from_user.id].get('lang', '-')
    data = requests.get(f'{ADDRES}korzina/list/{message.from_user.id}').json()
    txt = ''
    txt_rus = ''
    x = 0

    for i in data:
        price_int = int(i["price"])
        count_int = int(i["count"])
        total_price = price_int * count_int
        
        txt += f'<b>{i["product"]}</b>\n' \
            f'{count_int} x {price_int} = {total_price:,}\n'.replace(',', ' ')
        
        txt_rus += f'<b>{i["product"]}</b>\n' \
                f'{count_int} x {price_int} = {total_price:,}\n'.replace(',', ' ')
        
        x += total_price
    txt += f"<b>Umumiy:</b> {x:,} so'm".replace(',', ' ')
    txt_rus += f"<b>Общий:</b> {x:,} сум".replace(',', ' ')
    if message.text == '⬅️ Orqaga' or message.text == '⬅️ Назад':
        if lang == 'rus':
            await message.answer('Отправьте или введите свой номер телефона Пример: +998940938189',
                                 reply_markup=number_rus)
        else:
            await message.answer('Telefon raqamingizni yuboring yoki kiriting Misol: +998940938189',
                                 reply_markup=number)
        await RegOrderData.number.set()
    elif message.text == '🏫 Olib ketish' or message.text == '🏫 Самовывоз':
        await state.update_data(
            {"delevery": message.text}
        )
        data = await state.get_data()
        pay = data.get("pay")
        delever = data.get("delevery")
        text = f"<b>Sizning buyurtmangiz</b>\nNomer:{data.get('number')}\nTo'lov:{pay}\nYetkazib berish:{delever}"
        text_rus = f"<b>Твоя очередь</b>\nНомер:{data.get('number')}\nОплата:{pay}\nДоставка:{delever}"
        if lang == 'rus':
            await message.answer(f'{text_rus}\n\n{txt_rus},', reply_markup=checkbutton_rus)
        else:
            await message.answer(f'{text}\n\n{txt},', reply_markup=checkbutton)
        await RegOrderData.location.set()
    elif message.text == '🛵 Yetkazib berish' or message.text == '🛵 Доставка':
        await state.update_data(
            {"delevery": message.text}
        )
        if lang == 'rus':
            await message.answer(f'Введите адрес, отправьте текст или Локатцию', reply_markup=location_rus)
        else:
            await message.answer(f'Manzilni kiriting, tekst yoki lokatsiya yuboring', reply_markup=location)
        await RegOrderData.location.set()


@dp.message_handler(content_types='location', state=RegOrderData.location)
@dp.message_handler(content_types='text', state=RegOrderData.location)
async def regorder2(message: Message, state: FSMContext):
    data = requests.get(f'{ADDRES}korzina/list/{message.from_user.id}').json()
    date = datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%Y-%m-%d, %H:%M')
    lang = users[message.from_user.id].get('lang', '-')
    if message.text == '⬅️ Orqaga' or message.text == '⬅️ Назад':
        if lang == 'rus':
            await message.answer('Выберите тип доставки', reply_markup=delevery_rus)
        else:
            await message.answer('Yetkazib berish turini tanlang', reply_markup=delevery)

        await RegOrderData.delivery.set()

    elif message.text == '✅ Buyurtmani tasdiqlash' or message.text == '✅ Подтвердить заказ':
        if lang == 'rus':
            await message.answer("Заказ принят! Мы скоро с Вами свяжемся", reply_markup=menu_rus)
        else:
            await message.answer("Buyurtma qabul qilindi! Tez orada siz bilan bog'lanamiz", reply_markup=menu)
        txt = ''
        x = 0
        product = ''
        price = 0

        for i in data:
            price_int = int(i["price"])
            count_int = int(i["count"])
            total_price = price_int * count_int
            
            txt += f'<b>{i["product"]}</b>\n' \
                f'{count_int} x {price_int} = {total_price:,}\n'.replace(',', ' ')
            
            x += total_price
            product += f'{i["product"]}: {count_int} x {price_int} = {total_price:,}, '.replace(',', ' ')
            price += total_price

        txt += f"<b>Umumiy:</b> {x:,} so'm".replace(',', ' ')
        db = await state.get_data()
        pay = db.get("pay")
        num = db.get("number")
        delever = db.get("delevery")
        com = ''
        address = ''
        if db.get("comment"):
            com += f'\n<b>Izoh</b>: {db.get("comment")}'
        res = Create_order(product, price, address, num, message.from_user.id)
        text = f"<b>Yangi buyurtma {date}</b>\n\nID: #{res[1]}A\n" \
               f"<b>User: </b> <a href='tg://user?id={message.from_user.id}'>" \
               f"{message.from_user.first_name} @{message.from_user.username} </a>\n" \
               f"Nomer: <a href='tel:{num}'>{num}</a>\nTo'lov:{pay}\nYetkazib berish:{delever}\n{com}\n{txt}"
        if db.get("address"):
            address = db.get("address")
            text = f"<b>Yangi buyurtma  {date}</b>\n\nID: #{res[1]}A\n<b>User: </b><a href='tg://user?id={message.from_user.id}'>" \
                   f"{message.from_user.first_name} @{message.from_user.username} </a>\n" \
                   f"Nomer: {num}\nTo'lov: {pay}\n" \
                   f"Yetkazib berish: {delever}\nManzil: {db.get('address')}\n{com}\n{txt}"

        for admin in ADMINS:
            if db.get("latitude") and db.get("longitude"):
                await dp.bot.send_location(admin, latitude=db.get("latitude"), longitude=db.get("longitude"))
            await dp.bot.send_message(admin, text, parse_mode='HTML',
                                      reply_markup=adminbut(chat_id=message.from_user.id,
                                                            lang=lang, id=res[1])
                                      )
        await state.finish()

    elif message.text == '❌ Bekor qilish' or message.text == '❌ Отмена':
        if lang == 'rus':
            await message.answer("Заказ отменен", reply_markup=menu_rus)
        else:
            await message.answer("Buyurtma bekor qilindi", reply_markup=menu)
        await state.finish()

    elif message.text == '💬 Buyurtmaga kommentariy' or message.text == '💬 Комментарий к заказу':
        if lang == 'rus':
            await message.answer("Введите комментарий", reply_markup=comback_rus)
        else:
            await message.answer("Izoh kiriting", reply_markup=comback)
        await RegOrderData.comment.set()

    elif message.location:
        address = get_address_from_coords(f"{message.location.longitude}, {message.location.latitude},")
        await state.update_data(
            {
                "address": address,
                "longitude": message.location.longitude,
                "latitude": message.location.latitude,
            }
        )
        txt = ''
        txt_rus = ''
        x = 0

        for i in data:
            price_int = int(i["price"])
            count_int = int(i["count"])
            total_price = price_int * count_int
            
            txt += f'<b>{i["product"]}</b>\n' \
                f'{count_int} x {price_int} = {total_price:,}\n'.replace(',', ' ')
            
            txt_rus += f'<b>{i["product"]}</b>\n' \
                    f'{count_int} x {price_int} = {total_price:,}\n'.replace(',', ' ')
            
            x += total_price

        txt += f"<b>Umumiy:</b> {x:,} so'm".replace(',', ' ')
        txt_rus += f"<b>Общий:</b> {x:,} сум".replace(',', ' ')
        data = await state.get_data()
        pay = data.get("pay")
        num = data.get("number")
        delever = data.get("delevery")
        text = f"<b>Sizning buyurtmangiz</b>\nNomer:{num}\nTo'lov:{pay}\nYetkazib berish:{delever}\nManzil:{address}"
        text_rus = f"<b>Ваш заказ</b>\nНомер:{num}\nоплата:{pay}\nДоставка:{delever}\nРасположение:{address}"
        if lang == 'rus':
            await message.answer(f'{text_rus}\n\n{txt_rus},', reply_markup=checkbutton_rus)
        else:
            await message.answer(f'{text}\n\n{txt},', reply_markup=checkbutton)
        await RegOrderData.location.set()

    else:
        await state.update_data(
            {"address": message.text}
        )
        txt = ''
        txt_rus = ''
        x = 0

        for i in data:
            price_int = int(i["price"])
            count_int = int(i["count"])
            total_price = price_int * count_int
            
            txt += f'<b>{i["product"]}</b>\n' \
                f'{count_int} x {price_int} = {total_price:,}\n'.replace(',', ' ')
            
            txt_rus += f'<b>{i["product"]}</b>\n' \
                    f'{count_int} x {price_int} = {total_price:,}\n'.replace(',', ' ')
            
            x += total_price

        txt += f"<b>Umumiy:</b> {x:,} so'm".replace(',', ' ')
        txt_rus += f"<b>Общий:</b> {x:,} сум".replace(',', ' ')
        data = await state.get_data()
        pay = data.get("pay")
        num = data.get("number")
        delever = data.get("delevery")
        address = data.get("address")
        text = f"<b>Sizning buyurtmangiz</b>\nNomer:{num}\nTo'lov:{pay}\nYetkazib berish:{delever}\nManzil:{address}"
        text_rus = f"<b>Ваш заказ</b>\nНомер:{num}\nоплата:{pay}\nДоставка:{delever}\nРасположение:{address}"
        if lang == 'rus':
            await message.answer(f'{text_rus}\n\n{txt_rus},', reply_markup=checkbutton_rus)
        else:
            await message.answer(f'{text}\n\n{txt},', reply_markup=checkbutton)
        await RegOrderData.location.set()


@dp.message_handler(state=RegOrderData.comment)
async def regorder3(message: Message, state: FSMContext):
    lang = users[message.from_user.id].get('lang', '-')
    data = requests.get(f'{ADDRES}korzina/list/{message.from_user.id}').json()
    txt = ''
    txt_rus = ''
    x = 0

    for i in data:
        price_int = int(i["price"])
        count_int = int(i["count"])
        total_price = price_int * count_int
        
        txt += f'<b>{i["product"]}</b>\n' \
            f'{count_int} x {price_int} = {total_price:,}\n'.replace(',', ' ')
        
        txt_rus += f'<b>{i["product"]}</b>\n' \
                f'{count_int} x {price_int} = {total_price:,}\n'.replace(',', ' ')
        
        x += total_price

    txt += f"<b>Umumiy:</b> {x:,} so'm".replace(',', ' ')
    txt_rus += f"<b>Общий:</b> {x:,} сум".replace(',', ' ')
    data = await state.get_data()
    pay = data.get("pay")
    delever = data.get("delevery")
    text = f"<b>Sizning buyurtmangiz</b>\nNomer:{data.get('number')}\nTo'lov:{pay}\nYetkazib berish:{delever}\n"
    text_rus = f"<b>Ваш заказ</b>\nНомер:{data.get('number')}\nоплата:{pay}\nДоставка:{delever}"
    if data.get("address"):
        text = f"<b>Sizning buyurtmangiz</b>\nNomer:{data.get('number')}\nTo'lov:{pay}\nYetkazib berish:{delever}\nManzil:{data.get('address')}\n"
        text_rus = f"<b>Ваш заказ</b>\nНомер:{data.get('number')}\nоплата:{pay}\nДоставка:{delever}Адрес:{data.get('address')}\n"

    if message.text == '⬅️ Orqaga' or message.text == '⬅️ Назад':
        if lang == 'rus':
            await message.answer(f'{text_rus}\n{txt_rus},', reply_markup=checkbutton_rus)
        else:
            await message.answer(f'{text}\n{txt},', reply_markup=checkbutton)
        await RegOrderData.location.set()
    else:
        await state.update_data(
            {"comment": message.text}
        )
        if lang == 'rus':
            await message.answer(f'{text_rus}\n<b>Примечание</b>: {message.text}\n\n{txt_rus}',
                                 reply_markup=checkbutton_rus)
        else:
            await message.answer(f'{text}\n<b>Izoh</b>: {message.text}\n\n{txt}', reply_markup=checkbutton)
        await RegOrderData.confirm.set()


@dp.message_handler(content_types='text', state=RegOrderData.confirm)
async def regorder4(message: Message, state: FSMContext):
    lang = users[message.from_user.id].get('lang', '-')
    data = requests.get(f'{ADDRES}korzina/list/{message.from_user.id}').json()
    date = datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%Y-%m-%d, %H:%M')
    if message.text == '⬅️ Orqaga' or message.text == '⬅️ Назад':
        if lang == 'rus':
            await message.answer('Выберите тип доставки', reply_markup=delevery_rus)
        else:
            await message.answer('Yetkazib berish turini tanlang', reply_markup=delevery)
        await RegOrderData.delivery.set()

    elif message.text == '✅ Buyurtmani tasdiqlash' or message.text == '✅ Подтвердить заказ':
        if lang == 'rus':
            await message.answer("Заказ принят! Мы скоро с Вами свяжемся", reply_markup=menu_rus)
        else:
            await message.answer("Buyurtma qabul qilindi! Tez orada siz bilan bog'lanamiz", reply_markup=menu)
        txt = ''
        x = 0
        product = ''
        price = 0

        for i in data:
            price_int = int(i["price"])
            count_int = int(i["count"])
            total_price = price_int * count_int
            
            txt += f'<b>{i["product"]}</b>\n' \
                f'{count_int} x {price_int} = {total_price:,}\n'.replace(',', ' ')
            
            x += total_price
            
            product += f'{i["product"]}: ' \
                    f'{count_int} x {price_int} = {total_price:,}, '.replace(',', ' ')
            
            price += total_price

        txt += f"<b>Umumiy:</b> {x:,} so'm".replace(',', ' ')
        db = await state.get_data()
        pay = db.get("pay")
        num = db.get("number")
        delever = db.get("delevery")
        com = ''
        address = ''
        res = Create_order(product, price, address, num, message.from_user.id)
        if db.get("comment"):
            com += f'<b>Izoh</b>: {db.get("comment")}'
        text = f"<b>Yangi buyurtma {date}</b>\n\nID: #{res[1]}A\n<b>User: </b> <a href='tg://user?id={message.from_user.id}'>" \
               f"{message.from_user.first_name} @{message.from_user.username} </a>\n" \
               f"Nomer: <a href='tel:{num}'>{num}</a>\nTo'lov:{pay}\nYetkazib berish:{delever}\n{com}\n{txt}"
        if db.get("address"):
            address = db.get("address")
            text = f"<b>Yangi buyurtma {date}</b>\n\nID:#{res[1]}A\n<b>User: </b><a href='tg://user?id={message.from_user.id}'>" \
                   f"{message.from_user.first_name} @{message.from_user.username} </a>\n" \
                   f"Nomer: {num}\nTo'lov: {pay}\n" \
                   f"Yetkazib berish: {delever}\nManzil: {db.get('address')}\n\n{com}\n\n{txt}"

        for admin in ADMINS:
            if db.get("latitude") and db.get("longitude"):
                await dp.bot.send_location(admin, latitude=db.get("latitude"), longitude=db.get("longitude"))
            await dp.bot.send_message(admin, text, parse_mode='HTML',
                                      reply_markup=adminbut(chat_id=message.from_user.id,
                                                            lang=lang, id=res[1]))

        await state.finish()

    elif message.text == '❌ Bekor qilish' or message.text == '❌ Отмена':
        if lang == 'rus':
            await message.answer("Заказ отменен", reply_markup=menu_rus)
        else:
            await message.answer("Buyurtma bekor qilindi", reply_markup=menu)
        await state.finish()

    elif message.text == '💬 Buyurtmaga kommentariy' or message.text == '💬 Комментарий к заказу':
        if lang == 'rus':
            await message.answer("Введите комментарий", reply_markup=comback_rus)
        else:
            await message.answer("Izoh kiriting", reply_markup=comback)
        await RegOrderData.comment.set()

import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from keyboards.default.mahsulotSoni import mah_miqdori, mah_miqdori_rus
from keyboards.default.newkeyboards import menu, menu_rus
from states.orderState import OrderData
from loader import dp, bot
from save import save_korzina
from handlers.users.start import users
from data.config import ADDRES


def get_lang_code(user_lang):
    return 'ru' if user_lang == 'rus' else 'uz'


def generate_menu_buttons(lang, categories):
    buttons = [KeyboardButton(text=item['title']) for item in categories]
    buttons.append(KeyboardButton(text='🏠 Главное меню' if lang == 'rus' else '🏠 Bosh menyu'))
    buttons.append(KeyboardButton(text='⬅️ Назад' if lang == 'rus' else '⬅️ Orqaga'))
    return buttons


@dp.message_handler(state=OrderData.category)
async def products(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_lang = users[user_id].get('lang', '-')

    if message.text in ['🏠 Bosh menyu', '🏠 Главное меню']:
        reply_markup = menu_rus if user_lang == 'rus' else menu
        await message.answer(message.text, reply_markup=reply_markup)
        await state.finish()
        return

    if message.text in ['⬅️ Orqaga', '⬅️ Назад']:
        reply_markup = menu_rus if user_lang == 'rus' else menu
        await message.answer(message.text, reply_markup=reply_markup)
        await state.finish()
        return

    try:
        lang_code = get_lang_code(user_lang)
        response = requests.get(f'{ADDRES}category/{message.text}/?lang={lang_code}')
        data = response.json()

        if data:
            buttons = generate_menu_buttons(user_lang, data)
            reply_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(*buttons)
            
            await bot.send_chat_action(message.chat.id, 'typing')
            await message.answer('Продукты' if user_lang == 'rus' else 'Mahsulotlar', reply_markup=reply_markup)
            await OrderData.products.set()
    except Exception as e:
        await message.answer(f"Error fetching category details: {e}")


@dp.message_handler(state=OrderData.products)
async def products_detail(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_lang = users[user_id].get('lang', '-')
    lang_code = get_lang_code(user_lang)

    if message.text in ['🏠 Bosh menyu', '🏠 Главное меню']:
        reply_markup = menu_rus if user_lang == 'rus' else menu
        await message.answer(message.text, reply_markup=reply_markup)
        await state.finish()
        return

    if message.text in ['⬅️ Orqaga', '⬅️ Назад']:
        try:
            category_data = requests.get(f'{ADDRES}category/?lang={lang_code}').json()
            buttons = generate_menu_buttons(user_lang, category_data)
            reply_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add(*buttons)
            await message.answer('Категории' if user_lang == 'rus' else 'Categories', reply_markup=reply_markup)
            await OrderData.category.set()
        except Exception as e:
            await message.answer(f"Error fetching categories: {e}")
        return

    try:
        detail_prod = requests.get(f'{ADDRES}product/?q={message.text}&lang={lang_code}').json()
        for product in detail_prod:
            if message.text == product['title']:
                await message.answer_photo(photo=product['image'], caption=f"{product['title']}\n{product['description']}\n{product['price']:,}")
                quantity_markup = mah_miqdori_rus if user_lang == 'rus' else mah_miqdori
                await message.answer('Выберите или введите сумму' if user_lang == 'rus' else 'Miqdorini tanlang yoki kiriting', reply_markup=quantity_markup)
                await OrderData.detail.set()
                await state.update_data({"title": product['title'], "price": product['price']})
                return
    except Exception as e:
        await message.answer(f"Error fetching product details: {e}")


@dp.message_handler(state=OrderData.detail)
async def products_detail(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_lang = users[user_id].get('lang', '-')

    if message.text in ['🏠 Bosh menyu', '🏠 Главное меню', '🛒 Korzina', '🛒 Корзина']:
        reply_markup = menu_rus if user_lang == 'rus' else menu
        await message.answer(message.text, reply_markup=reply_markup)
        await state.finish()
        return

    try:
        quantity = int(message.text)
        lang_code = get_lang_code(user_lang)
        category_data = requests.get(f'{ADDRES}category/?lang={lang_code}').json()
        buttons = generate_menu_buttons(user_lang, category_data)
        reply_markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add(*buttons)
        
        data = await state.get_data()
        save_korzina(message, data.get("title"), data.get("price"), message.text)
        await message.answer('Товар добавлен в корзину, что нибудь еще?' if user_lang == 'rus' else 'Mahsulot savatchaga qoshildi, davom etamizmi?', reply_markup=reply_markup)
        await OrderData.category.set()
    except ValueError:
        pass

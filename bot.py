import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from menu import MENU


# =========================
# НАСТРОЙКИ
# =========================

import os

TOKEN = os.getenv("BOT_TOKEN")

GROUP_ID = -5127411007
ADMIN_ID = 457315827

BOT_USERNAME = "zakaz_sls_bot"

# Скидка 40%
DISCOUNT_PERCENT = 40


bot = Bot(token=TOKEN)
dp = Dispatcher()


# =========================
# РАСЧЁТ ЦЕНЫ СО СКИДКОЙ
# =========================

def discounted_price(price):

    if price is None:
        return None

    return round(
        price * (100 - DISCOUNT_PERCENT) / 100
    )


# =========================
# ДАННЫЕ ЗАКАЗА
# =========================

common_order = []

pending_users = {}


# =========================
# КНОПКИ ДЛЯ ГРУППЫ
# =========================

def group_order_menu():

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="🛒 Сделать заказ",
                    url=f"https://t.me/{BOT_USERNAME}?start=order"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🛒 Общая корзина",
                    callback_data="group_common_order"
                )
            ]

        ]
    )

    return keyboard


# =========================
# ГЛАВНОЕ МЕНЮ
# =========================

def main_menu():

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="🎁 Подарочные сертификаты",
                    callback_data="category_certificate"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🍳 Завтраки",
                    callback_data="category_breakfast"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🌯 Лава'Шаурма",
                    callback_data="category_shaurma"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🌯 Мини-шаурма",
                    callback_data="category_mini_shaurma"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🍔 Лава'Бургеры",
                    callback_data="category_burger"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🌭 Лава'Доги",
                    callback_data="category_dog"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🫓 Роти",
                    callback_data="category_roti"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🥗 Салаты",
                    callback_data="category_salad"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🍽 Обеды",
                    callback_data="category_lunch"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🍟 Фри",
                    callback_data="category_fries"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🧃 Фирменные морсы",
                    callback_data="category_morse"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🥤 Холодные напитки",
                    callback_data="category_drinks"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🛒 Мой заказ",
                    callback_data="my_order"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🛒 Общая корзина",
                    callback_data="common_order"
                )
            ]
        ]
    )

    return keyboard


# =========================
# /START
# =========================

@dp.message(CommandStart())
async def start(message: Message):

    # -------------------------
    # ЕСЛИ /START НАПИСАЛИ В ГРУППЕ
    # -------------------------

    if message.chat.type != "private":

        await message.answer(
            "🌯 НАЛАВАШЕ\n\n"
            "Чтобы сделать заказ, нажмите кнопку ниже:",
            reply_markup=group_order_menu()
        )

        return


    # -------------------------
    # ЛИЧНЫЙ ЧАТ С БОТОМ
    # -------------------------

    user_id = message.from_user.id

    print(
        f"👤 Пользователь открыл бота: "
        f"{message.from_user.full_name} "
        f"(ID: {user_id})"
    )


    # -------------------------
    # ПРОВЕРЯЕМ УЧАСТИЕ В ГРУППЕ
    # -------------------------

    try:

        member = await bot.get_chat_member(
            chat_id=GROUP_ID,
            user_id=user_id
        )

        if member.status not in [
            "member",
            "administrator",
            "creator"
        ]:

            await message.answer(
                "❌ Чтобы пользоваться ботом, "
                "сначала вступите в группу "
                "«НАЛАВАШЕ ЗАКАЗ SLS»."
            )

            return


    except Exception as error:

        print(
            "❌ Ошибка проверки участника:"
        )

        print(error)

        await message.answer(
            "❌ Не удалось проверить ваше "
            "участие в группе."
        )

        return


    # -------------------------
    # ПОКАЗЫВАЕМ МЕНЮ
    # -------------------------

    await message.answer(
        "🌯 НАЛАВАШЕ\n\n"
        "Выберите категорию:",
        reply_markup=main_menu()
    )


# =========================
# КАТЕГОРИИ
# =========================

@dp.callback_query(
    F.data.startswith("category_")
)
async def category(
    callback: CallbackQuery
):

    category_id = callback.data.replace(
        "category_",
        ""
    )

    category_data = MENU.get(
        category_id
    )

    if not category_data:

        await callback.answer(
            "Категория не найдена"
        )

        return


    buttons = []


    for index, product in enumerate(
        category_data["products"]
    ):

        if product["price"] is None:

            price_text = "цена уточняется"

        else:

            regular_price = product["price"]

            sale_price = discounted_price(
                regular_price
            )

            price_text = (
                f"{regular_price} ₽ "
                f"🔥 {sale_price} ₽ (-40%)"
            )


        buttons.append(
            [
                InlineKeyboardButton(
                    text=(
                        f"{product['name']} — "
                        f"{price_text}"
                    ),
                    callback_data=(
                        f"product_"
                        f"{category_id}_"
                        f"{index}"
                    )
                )
            ]
        )


    buttons.append(
        [
            InlineKeyboardButton(
                text="◀️ Назад в меню",
                callback_data="back_to_menu"
            )
        ]
    )


    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


    await callback.message.edit_text(
        f"{category_data['name']}\n\n"
        "Выберите блюдо:",
        reply_markup=keyboard
    )


    await callback.answer()


# =========================
# ДОБАВЛЕНИЕ ТОВАРА
# =========================

@dp.callback_query(
    F.data.startswith("product_")
)
async def add_product(
    callback: CallbackQuery
):

    print(
        "НАЖАТО БЛЮДО:",
        callback.data
    )


    parts = callback.data.split("_")


    if len(parts) < 3:

        await callback.answer(
            "❌ Ошибка данных товара"
        )

        return


    category_id = "_".join(
        parts[1:-1]
    )


    try:

        product_index = int(
            parts[-1]
        )

    except ValueError:

        await callback.answer(
            "❌ Ошибка индекса товара"
        )

        return


    print(
        "Категория:",
        category_id
    )

    print(
        "Индекс блюда:",
        product_index
    )


    category_data = MENU.get(
        category_id
    )


    if not category_data:

        await callback.answer(
            "❌ Категория не найдена"
        )

        return


    if (
        product_index < 0
        or
        product_index >= len(
            category_data["products"]
        )
    ):

        await callback.answer(
            "❌ Блюдо не найдено"
        )

        return


    product = category_data[
        "products"
    ][product_index]


    print(
        "Найдено блюдо:",
        product
    )


    if product["price"] is None:

        await callback.answer(
            "⚠️ Цена этого товара "
            "пока не указана"
        )

        return


    # -------------------------
    # ЦЕНЫ
    # -------------------------

    regular_price = product["price"]

    sale_price = discounted_price(
        regular_price
    )


    user_name = (
        callback.from_user.full_name
    )

    user_id = (
        callback.from_user.id
    )


    existing_item = None


    for item in common_order:

        if (
            item["user_id"] == user_id
            and
            item["product"]
            == product["name"]
        ):

            existing_item = item

            break


    if existing_item:

        existing_item["quantity"] += 1

    else:

        common_order.append(
            {
                "user_id": user_id,
                "user": user_name,
                "product": product["name"],

                # Сохраняем обычную цену
                "regular_price": regular_price,

                # В заказе используем скидочную цену
                "price": sale_price,

                "quantity": 1
            }
        )


    print(
        "ОБЩИЙ ЗАКАЗ:",
        common_order
    )


    await callback.answer(
        "✅ Добавлено"
    )


    await callback.message.answer(
        "✅ Добавлено!\n\n"
        f"{product['name']}\n"
        f"Обычная цена: {regular_price} ₽\n"
        f"🔥 Цена со скидкой 40%: {sale_price} ₽"
    )


# =========================
# НАЗАД В МЕНЮ
# =========================

@dp.callback_query(
    F.data == "back_to_menu"
)
async def back_to_menu(
    callback: CallbackQuery
):

    await callback.message.edit_text(
        "🌯 НАЛАВАШЕ\n\n"
        "Выберите категорию:",
        reply_markup=main_menu()
    )

    await callback.answer()


# =========================
# МОЙ ЗАКАЗ
# =========================

@dp.callback_query(
    F.data == "my_order"
)
async def show_my_order(
    callback: CallbackQuery
):

    user_id = (
        callback.from_user.id
    )


    my_order = []


    for index, item in enumerate(
        common_order
    ):

        if item["user_id"] == user_id:

            my_order.append(
                (index, item)
            )


    print(
        "МОЙ ЗАКАЗ:",
        my_order
    )


    if not my_order:

        text = (
            "🛒 МОЙ ЗАКАЗ\n\n"
            "У вас пока нет товаров."
        )


        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="◀️ Назад в меню",
                        callback_data="back_to_menu"
                    )
                ]
            ]
        )


    else:

        text = (
            "🛒 МОЙ ЗАКАЗ\n\n"
        )


        total = 0

        buttons = []


        for index, item in my_order:

            item_total = (
                item["price"]
                *
                item["quantity"]
            )


            text += (
                f"{item['product']} "
                f"× {item['quantity']} "
                f"— {item_total} ₽\n"
            )

            text += (
                f"🔥 скидка 40%\n\n"
            )


            total += item_total


            buttons.append(
                [
                    InlineKeyboardButton(
                        text="➖",
                        callback_data=(
                            f"my_minus_{index}"
                        )
                    ),

                    InlineKeyboardButton(
                        text=str(
                            item["quantity"]
                        ),
                        callback_data="nothing"
                    ),

                    InlineKeyboardButton(
                        text="➕",
                        callback_data=(
                            f"my_plus_{index}"
                        )
                    )
                ]
            )


        text += (
            f"💰 Итого со скидкой: {total} ₽"
        )


        buttons.append(
            [
                InlineKeyboardButton(
                    text=(
                        "✅ Оформить мой заказ"
                    ),
                    callback_data=(
                        "create_order"
                    )
                )
            ]
        )


        buttons.append(
            [
                InlineKeyboardButton(
                    text="◀️ Назад в меню",
                    callback_data="back_to_menu"
                )
            ]
        )


        keyboard = InlineKeyboardMarkup(
            inline_keyboard=buttons
        )


    await callback.message.edit_text(
        text,
        reply_markup=keyboard
    )


    await callback.answer()


# =========================
# ПУСТАЯ КНОПКА КОЛИЧЕСТВА
# =========================

@dp.callback_query(
    F.data == "nothing"
)
async def nothing(
    callback: CallbackQuery
):

    await callback.answer()


# =========================
# МОЙ ПЛЮС
# =========================

@dp.callback_query(
    F.data.startswith("my_plus_")
)
async def my_plus_product(
    callback: CallbackQuery
):

    print(
        "🔥 MY PLUS:",
        callback.data
    )


    index = int(
        callback.data.replace(
            "my_plus_",
            ""
        )
    )


    if index >= len(common_order):

        await callback.answer(
            "Товар не найден"
        )

        return


    item = common_order[index]


    if (
        item["user_id"]
        != callback.from_user.id
    ):

        await callback.answer(
            "❌ Это не ваш товар"
        )

        return


    item["quantity"] += 1


    await show_my_order(
        callback
    )


# =========================
# МОЙ МИНУС
# =========================

@dp.callback_query(
    F.data.startswith("my_minus_")
)
async def my_minus_product(
    callback: CallbackQuery
):

    print(
        "🔥 MY MINUS:",
        callback.data
    )


    index = int(
        callback.data.replace(
            "my_minus_",
            ""
        )
    )


    if index >= len(common_order):

        await callback.answer(
            "Товар не найден"
        )

        return


    item = common_order[index]


    if (
        item["user_id"]
        != callback.from_user.id
    ):

        await callback.answer(
            "❌ Это не ваш товар"
        )

        return


    item["quantity"] -= 1


    if item["quantity"] <= 0:

        common_order.pop(index)


    await show_my_order(
        callback
    )


# =========================
# ОБЩАЯ КОРЗИНА В ЛИЧНОМ ЧАТЕ
# =========================

@dp.callback_query(
    F.data == "common_order"
)
async def show_common_order(
    callback: CallbackQuery
):

    if not common_order:

        text = (
            "🛒 ОБЩАЯ КОРЗИНА\n\n"
            "Пока заказ пуст."
        )


        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="◀️ Назад в меню",
                        callback_data="back_to_menu"
                    )
                ]
            ]
        )


    else:

        text = (
            "🛒 ОБЩАЯ КОРЗИНА\n\n"
        )


        total = 0


        for item in common_order:

            item_total = (
                item["price"]
                *
                item["quantity"]
            )


            text += (
                f"👤 {item['user']}\n"
                f"{item['product']} × "
                f"{item['quantity']} — "
                f"{item_total} ₽\n\n"
            )


            total += item_total


        text += (
            f"💰 Итого со скидкой: {total} ₽"
        )


        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="◀️ Назад",
                        callback_data="back_to_menu"
                    )
                ]
            ]
        )


    await callback.message.edit_text(
        text,
        reply_markup=keyboard
    )


    await callback.answer()


# =========================
# ОБЩАЯ КОРЗИНА В ГРУППЕ
# =========================

@dp.callback_query(
    F.data == "group_common_order"
)
async def group_common_order(
    callback: CallbackQuery
):

    if callback.message.chat.id != GROUP_ID:

        await callback.answer(
            "❌ Эта кнопка предназначена для группы"
        )

        return


    if not common_order:

        await callback.message.answer(
            "🛒 ОБЩАЯ КОРЗИНА\n\n"
            "Пока заказ пуст."
        )

        await callback.answer(
            "Корзина пока пустая"
        )

        return


    text = (
        "🛒 ОБЩАЯ КОРЗИНА\n\n"
    )


    total = 0


    for item in common_order:

        item_total = (
            item["price"]
            *
            item["quantity"]
        )


        text += (
            f"👤 {item['user']}\n"
            f"🍽 {item['product']}\n"
            f"Количество: {item['quantity']}\n"
            f"💰 {item_total} ₽\n\n"
        )


        total += item_total


    text += (
        "━━━━━━━━━━━━━━\n"
        f"💰 ИТОГО со скидкой: {total} ₽"
    )


    await callback.message.answer(
        text
    )


    await callback.answer(
        "🛒 Общая корзина"
    )


# =========================
# ИЗМЕНЕНИЕ ОБЩЕГО ЗАКАЗА
# =========================

async def show_order_after_change(
    callback: CallbackQuery
):

    await show_my_order(
        callback
    )


# =========================
# ОБЩИЙ ПЛЮС
# =========================

@dp.callback_query(
    F.data.startswith("plus_")
)
async def plus_product(
    callback: CallbackQuery
):

    index = int(
        callback.data.replace(
            "plus_",
            ""
        )
    )


    if index >= len(common_order):

        await callback.answer(
            "Товар не найден"
        )

        return


    item = common_order[index]


    if (
        item["user_id"]
        != callback.from_user.id
    ):

        await callback.answer(
            "❌ Это не ваш товар"
        )

        return


    item["quantity"] += 1


    await show_my_order(
        callback
    )


# =========================
# ОБЩИЙ МИНУС
# =========================

@dp.callback_query(
    F.data.startswith("minus_")
)
async def minus_product(
    callback: CallbackQuery
):

    index = int(
        callback.data.replace(
            "minus_",
            ""
        )
    )


    if index >= len(common_order):

        await callback.answer(
            "Товар не найден"
        )

        return


    item = common_order[index]


    if (
        item["user_id"]
        != callback.from_user.id
    ):

        await callback.answer(
            "❌ Это не ваш товар"
        )

        return


    item["quantity"] -= 1


    if item["quantity"] <= 0:

        common_order.pop(index)


    await show_my_order(
        callback
    )


# =========================
# ОФОРМЛЕНИЕ ОБЩЕГО ЗАКАЗА
# =========================

@dp.callback_query(
    F.data == "create_order"
)
async def create_order(
    callback: CallbackQuery
):

    print(
        "🔥 CREATE ORDER СРАБОТАЛ"
    )


    user_id = (
        callback.from_user.id
    )

    user_name = (
        callback.from_user.full_name
    )


    # -------------------------
    # ИЩЕМ ТОВАРЫ ЭТОГО ПОЛЬЗОВАТЕЛЯ
    # -------------------------

    user_items = []


    for item in common_order:

        if item["user_id"] == user_id:

            user_items.append(item)


    if not user_items:

        await callback.answer(
            "❌ У вас нет товаров"
        )

        return


    # -------------------------
    # СОЗДАЁМ СООБЩЕНИЕ ДЛЯ ГРУППЫ
    # -------------------------

    group_text = (
        "🛒 НОВОЕ ПОПОЛНЕНИЕ "
        "ОБЩЕЙ КОРЗИНЫ\n\n"
        f"👤 {user_name}\n"
    )


    user_total = 0


    for item in user_items:

        item_total = (
            item["price"]
            *
            item["quantity"]
        )


        group_text += (
            f"• {item['product']} "
            f"× {item['quantity']} "
            f"— {item_total} ₽\n"
        )


        user_total += item_total


    group_text += (
        f"\n🔥 Цена со скидкой 40%\n"
        f"💰 Добавлено на: "
        f"{user_total} ₽"
    )


    # -------------------------
    # ОТПРАВЛЯЕМ В ГРУППУ
    # -------------------------

    try:

        await bot.send_message(
            chat_id=GROUP_ID,
            text=group_text
        )


        print(
            "✅ УВЕДОМЛЕНИЕ ОТПРАВЛЕНО В ГРУППУ"
        )


    except Exception as error:

        print(
            "❌ ОШИБКА ОТПРАВКИ В ГРУППУ:"
        )

        print(error)


    # -------------------------
    # ЗАПОМИНАЕМ УЧАСТНИКОВ
    # -------------------------

    pending_users.clear()


    for item in common_order:

        pending_users[
            item["user_id"]
        ] = item["user"]


    # -------------------------
    # ФОРМИРУЕМ ЗАКАЗ ДЛЯ АДМИНА
    # -------------------------

    text = (
        "📋 НОВЫЙ ОБЩИЙ ЗАКАЗ\n\n"
    )


    total = 0
    current_user_id = None


    for item in common_order:

        if (
            item["user_id"]
            != current_user_id
        ):

            current_user_id = (
                item["user_id"]
            )

            text += (
                f"👤 {item['user']}\n"
            )


        item_total = (
            item["price"]
            *
            item["quantity"]
        )


        text += (
            f"• {item['product']} "
            f"× {item['quantity']} "
            f"— {item_total} ₽\n"
        )


        total += item_total


    text += (
        "\n🔥 Все цены со скидкой 40%\n"
        f"💰 ИТОГО: {total} ₽"
    )


    # -------------------------
    # КНОПКИ АДМИНА
    # -------------------------

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Принять заказ",
                    callback_data=(
                        "admin_accept_order"
                    )
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отклонить заказ",
                    callback_data=(
                        "admin_reject_order"
                    )
                )
            ]
        ]
    )


    # -------------------------
    # ОТПРАВЛЯЕМ АДМИНУ
    # -------------------------

    try:

        await bot.send_message(
            chat_id=ADMIN_ID,
            text=text,
            reply_markup=keyboard
        )


        print(
            "✅ СООБЩЕНИЕ АДМИНУ ОТПРАВЛЕНО"
        )


    except Exception as error:

        print(
            "❌ ОШИБКА ОТПРАВКИ АДМИНУ:"
        )

        print(error)


        await callback.answer(
            "❌ Не удалось отправить "
            "заказ администратору"
        )

        return


    # -------------------------
    # ОТВЕТ ПОЛЬЗОВАТЕЛЮ
    # -------------------------

    await callback.message.answer(
        "✅ Ваш заказ добавлен "
        "в общую корзину!\n\n"
        "Участники группы увидели, "
        "что вы добавили товары."
    )


    await callback.answer(
        "✅ Заказ добавлен"
    )


# =========================
# АДМИН — ПРИНЯТЬ
# =========================

@dp.callback_query(
    F.data == "admin_accept_order"
)
async def admin_accept_order(
    callback: CallbackQuery
):

    if (
        callback.from_user.id
        != ADMIN_ID
    ):

        await callback.answer(
            "❌ У вас нет доступа"
        )

        return


    await callback.message.edit_text(
        callback.message.text
        +
        "\n\n✅ ЗАКАЗ ПРИНЯТ"
    )


    # -------------------------
    # УВЕДОМЛЕНИЕ В ГРУППУ
    # -------------------------

    try:

        await bot.send_message(
            chat_id=GROUP_ID,
            text=(
                "🎉 ОБЩИЙ ЗАКАЗ ПРИНЯТ!\n\n"
                "Заказ передан в работу."
            )
        )

    except Exception as error:

        print(
            "❌ Ошибка отправки "
            "уведомления в группу:"
        )

        print(error)


    # -------------------------
    # ОЧИЩАЕМ КОРЗИНУ
    # -------------------------

    common_order.clear()

    pending_users.clear()


    print(
        "🧹 ОБЩАЯ КОРЗИНА ОЧИЩЕНА"
    )


    await callback.answer(
        "Заказ принят"
    )


# =========================
# АДМИН — ОТКЛОНИТЬ
# =========================

@dp.callback_query(
    F.data == "admin_reject_order"
)
async def admin_reject_order(
    callback: CallbackQuery
):

    if (
        callback.from_user.id
        != ADMIN_ID
    ):

        await callback.answer(
            "❌ У вас нет доступа"
        )

        return


    await callback.message.edit_text(
        callback.message.text
        +
        "\n\n❌ ЗАКАЗ ОТКЛОНЁН"
    )


    # -------------------------
    # УВЕДОМЛЕНИЕ В ГРУППУ
    # -------------------------

    try:

        await bot.send_message(
            chat_id=GROUP_ID,
            text=(
                "❌ ОБЩИЙ ЗАКАЗ ОТКЛОНЁН.\n\n"
                "Необходимо оформить заказ заново."
            )
        )

    except Exception as error:

        print(
            "❌ Ошибка отправки "
            "уведомления в группу:"
        )

        print(error)


    await callback.answer(
        "Заказ отклонён"
    )


# =========================
# ЗАПУСК
# =========================

async def main():

    print(
        "🤖 Бот запущен"
    )

    await dp.start_polling(
        bot
    )


if __name__ == "__main__":

    asyncio.run(main())
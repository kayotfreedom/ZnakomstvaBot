import time

print('[START] Version: 1.1')

import asyncio
import logging
import random

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, Message



from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder, KeyboardButton, InlineKeyboardButton

from database import *
from settings import *

from aiogram.filters.callback_data import CallbackData



logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)
router = Router()


class AdminState(StatesGroup):
    waiting_for_user_id_add_stars = State()
    waiting_for_stars_amount_add = State()
    waiting_for_user_id_remove_stars = State()
    waiting_for_stars_amount_remove = State()
    waiting_for_mailing_text = State()
    waiting_for_channel_id_add = State()
    waiting_for_channel_id_delete = State()
    waiting_for_promocode_activation = State()
    waiting_for_promo_details_add = State()
    waiting_for_promocode_delete = State()
    waiting_for_user_blocked = State()

class UserState(StatesGroup):
    waiting_for_user_name = State()
    waiting_for_user_age = State()
    waiting_for_user_about_info = State()
    waiting_for_user_interesi = State()


def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🔎Искать собеседника")
    builder.button(text="🗄️Профиль")
    builder.row(
        KeyboardButton(text="✨VIP-функции")
    )
    builder.row(
        KeyboardButton(text="❓Помощь")
    )
    return builder.as_markup(resize_keyboard=True)


@router.message(StateFilter(UserState.waiting_for_user_name))
async def process_add_user_name(message: types.Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await bot.send_message(message.chat.id, "<b>Введите ваш возраст:</b>", parse_mode='HTML')
    await state.set_state(UserState.waiting_for_user_age)

@router.message(StateFilter(UserState.waiting_for_user_age))
async def process_add_user_age(message: types.Message, state: FSMContext):
    await state.update_data(user_age=message.text)
    await bot.send_message(message.chat.id, "<b>Введите информацию о себе:</b>", parse_mode='HTML')
    await state.set_state(UserState.waiting_for_user_about_info)

@router.message(StateFilter(UserState.waiting_for_user_about_info))
async def process_add_stars_user_id(message: types.Message, state: FSMContext):
    await state.update_data(user_about_info=message.text)
    await bot.send_message(message.chat.id, "<b>Введите ваши интересы:</b>", parse_mode='HTML')
    await state.set_state(UserState.waiting_for_user_interesi)

@router.message(StateFilter(UserState.waiting_for_user_interesi))
async def set_user_info(message: types.Message, state: FSMContext):
    data = await state.get_data()
    interesi = message.text
    name = data.get("user_name")
    age = data.get("user_age")
    about_info = data.get("user_about_info")



@router.message(StateFilter(AdminState.waiting_for_user_id_add_stars))
async def process_add_stars_user_id(message: types.Message, state: FSMContext):
    await state.update_data(user_id_add_stars=message.text)
    await bot.send_message(message.chat.id, "<b>Введите количество звезд для добавления:</b>", parse_mode='HTML')
    await state.set_state(AdminState.waiting_for_stars_amount_add)

@router.message(StateFilter(AdminState.waiting_for_stars_amount_add))
async def process_add_stars_amount(message: types.Message, state: FSMContext):
    try:
        stars = int(message.text)
        data = await state.get_data()
        user_id = int(data.get("user_id_add_stars"))
        increment_stars(user_id, stars)
        await bot.send_message(message.chat.id, f"<b>✅ {stars} звезд успешно добавлено пользователю с ID {user_id}</b>", parse_mode='HTML')
        await bot.send_message(user_id, f"✅ Администратор добавил вам {stars} звезд!", parse_mode='HTML')
    except ValueError:
        await bot.send_message(message.chat.id, "<b>❌ Неверный формат. Пожалуйста, введите число.</b>", parse_mode='HTML')
    except TypeError:
        await bot.send_message(message.chat.id, "<b>❌ Неверный формат ID.</b>", parse_mode='HTML')
    await state.clear()

@router.message(StateFilter(AdminState.waiting_for_user_id_remove_stars))
async def process_remove_stars_user_id(message: types.Message, state: FSMContext):
    await state.update_data(user_id_remove_stars=message.text)
    await bot.send_message(message.chat.id, "<b>Введите количество звезд для удаления:</b>", parse_mode='HTML')
    await state.set_state(AdminState.waiting_for_stars_amount_remove)

@router.message(StateFilter(AdminState.waiting_for_stars_amount_remove))
async def process_remove_stars_amount(message: types.Message, state: FSMContext):
    try:
        stars = int(message.text)
        data = await state.get_data()
        user_id = int(data.get("user_id_add_stars"))
        deincrement_stars(user_id, stars)
        await bot.send_message(message.chat.id, "<b>✅ Звезды успешно удалены!</b>", parse_mode='HTML')
    except ValueError:
        await bot.send_message(message.chat.id, "<b>❌ Неверный формат. Пожалуйста, введите число.</b>", parse_mode='HTML')
    except TypeError:
        await bot.send_message(message.chat.id, "<b>❌ Неверный формат ID.</b>", parse_mode='HTML')
    await state.clear()

@router.message(StateFilter(AdminState.waiting_for_mailing_text))
async def process_mailing_text(message: types.Message, state: FSMContext):
    text = message.text
    users = get_users()
    counter = 0

    for user in users:
        user_id = user[0]
        ref_link = f"\n\nПерешли ссылку всем своим друзьям — https://t.me/{ (await bot.me()).username }?start={user_id}"
        full_text = f"{text}{ref_link}"

        try:
            counter += 1
            await bot.send_message(user_id, f"<b>{full_text}</b>", parse_mode='HTML')
            print(f"[РАССЫЛКА] Отправлено: {user_id}")
        except Exception as e:
            print(f"[РАССЫЛКА] Не отправлено: {user_id}")

    await bot.send_message(message.chat.id, f"<b>✅ Рассылка успешно отправлена!\n\nОтправлено: {counter}/{str(len(users))} пользователю</b>", parse_mode='HTML')
    await state.clear()

@router.message(StateFilter(AdminState.waiting_for_channel_id_add))
async def process_add_channel_id(message: types.Message, state: FSMContext):
    try:
        channel_id_to_add = int(message.text)
        if channel_id_to_add not in channel_ids:
            channel_ids.append(channel_id_to_add)
            await bot.send_message(message.chat.id, "<b>✅ Канал успешно добавлен!</b>", parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id, "<b>⚠️ Этот канал уже есть в списке.</b>", parse_mode='HTML')
    except ValueError:
        await bot.send_message(message.chat.id, "<b>❌ Некорректный ID канала!</b>", parse_mode='HTML')
    await state.clear()

@router.message(StateFilter(AdminState.waiting_for_channel_id_delete))
async def process_delete_channel_id(message: types.Message, state: FSMContext):
    try:
        channel_id_to_delete = int(message.text)
        if channel_id_to_delete in channel_ids:
            channel_ids.remove(channel_id_to_delete)
            await bot.send_message(message.chat.id, "<b>✅ Канал успешно удален!</b>", parse_mode='HTML')
        else:
            await bot.send_message(message.chat.id, "<b>❌ Канал не найден!</b>", parse_mode='HTML')
    except ValueError:
        await bot.send_message(message.chat.id, "<b>❌ Некорректный ID канала!</b>", parse_mode='HTML')
    await state.clear()

@router.message(StateFilter(AdminState.waiting_for_promocode_activation))
async def process_promocode_activation(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    promocode = message.text
    success, result = use_promocode(promocode, user_id)
    if success:
        await bot.send_message(message.chat.id, f"<b>✅ Промокод успешно активирован!\nВам начислено {result} ⭐️</b>", parse_mode='HTML')
    else:
        await bot.send_message(message.chat.id, f"<b>❌ Ошибка: {result}</b>", parse_mode='HTML')
    await state.clear()

@router.message(StateFilter(AdminState.waiting_for_promo_details_add))
async def process_add_promo_details(message: types.Message, state: FSMContext):
    try:
        promocode, stars_str, uses_str = message.text.split(",")
        stars = int(stars_str.strip())
        uses = int(uses_str.strip())
        add_promocode(promocode.strip(), stars, uses)
        await bot.send_message(message.chat.id, "<b>✅ Промокод успешно добавлен!</b>", parse_mode='HTML')
    except ValueError:
        await bot.send_message(message.chat.id, "<b>❌ Некорректный ввод! Введите промокод, количество звезд, количество использований через запятую.</b>", parse_mode='HTML')
    await state.clear()

@router.message(StateFilter(AdminState.waiting_for_promocode_delete))
async def process_delete_promo(message: types.Message, state: FSMContext):
    try:
        promocode = message.text.strip()
        deactivate_promocode(promocode)
        await bot.send_message(message.chat.id, "<b>✅ Промокод успешно удален!</b>", parse_mode='HTML')
    except ValueError:
        await bot.send_message(message.chat.id, "<b>❌ Некорректный ввод!</b>", parse_mode='HTML')
    await state.clear()


@router.message(CommandStart())
async def handle_start(message: types.Message, bot: Bot):
    args = message.text.split()
    user_id = message.from_user.id
    username = message.from_user.username or f"User{user_id}"
    ref_link = f"https://t.me/{ (await bot.me()).username }?start={user_id}"


    builder = InlineKeyboardBuilder()
    builder.button(text="Поделиться ссылкой", url=f"https://t.me/share/url?url={ref_link}")
    markup = builder.as_markup()

    start_command = BotCommand(command='start', description='♻️ Перезапустить бота')
    await bot.set_my_commands([start_command])
    await bot.set_chat_menu_button(
        chat_id=message.chat.id,
        menu_button=types.MenuButtonCommands()
    )

    if not user_exists(user_id):
        referral_id = None
        if len(channel_ids) > 0:
            if await check_subscription(user_id, channel_ids, bot):
                return
        if len(args) > 1 and args[1].isdigit():
            referral_id = int(args[1])
            if user_exists(referral_id):
                await bot.send_message(referral_id, f"<b>☑️ По вашей реферальной ссылке перешел новый пользователь: {user_id}.\n\nНа ваш баланс зачислено +3⭐️\n\nПерешли ссылку — {ref_link}</b>", parse_mode='HTML')
                await bot.send_message(admins, text=f"Новый пользователь! рефер: {referral_id}, пользователь: {user_id}", parse_mode='HTML')
                increment_referrals(referral_id)
                increment_stars(referral_id, 3)
        add_user(user_id, username, 'None', 'None', 'None', 0)
        add_vip_user(user_id, username, 'None', 'None', 'None', 0)
        add_pre_user(user_id, username, 'None', 'None', 'None', 0)
        add_podbor(user_id, username, 0, obmen_message_id="None")
        await bot.send_message(user_id, "⭐", reply_markup=get_podpiska_keyboard())
        await bot.send_message(user_id, f"<b>✨ Добро пожаловать!\n\nЭто бот для анонимных знакомств!\nНе теряй времени жми кнопки и общайся!</b>", parse_mode='HTML')
    else:
        if len(channel_ids) > 0:
            if await check_subscription(user_id, channel_ids, bot):
                return
        await bot.send_message(user_id, "⭐", reply_markup=get_main_keyboard())
        await bot.send_message(user_id, f"<b>✨ Добро пожаловать!\n\nЭто бот для анонимных знакомств!\nНе теряй времени жми кнопки и общайся!</b>", parse_mode='HTML', reply_markup=markup)

@router.message(Command("admin"))
async def adminpanel_command(message: types.Message, bot: Bot):
    if message.from_user.id in admins:
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="⭐️ Выдать звезды", callback_data="add_stars"),
            InlineKeyboardButton(text="⭐️ Снять звезды", callback_data="remove_stars")
        )
        builder.row(
            InlineKeyboardButton(text="📨 Рассылка", callback_data="mailing")
        )
        builder.row(
            InlineKeyboardButton(text="📚 Добавить канал", callback_data="add_channel"),
            InlineKeyboardButton(text="🚫 Удалить канал", callback_data='delete_channel')
        )
        builder.row(
            InlineKeyboardButton(text="📨 Рассылка 0 реф", callback_data='mailing_zero_refs')
        )
        builder.row(
            InlineKeyboardButton(text="🎁 Добавить промокод", callback_data='add_promo_code'),
            InlineKeyboardButton(text="🚫 Удалить промокод", callback_data='remove_promo_code')
        )
        markup = builder.as_markup()
        await bot.send_message(message.chat.id, f"<b>📊 Админ-панель\n\n👥 Пользователей: {get_user_count()}\n💸 Выплачено: {get_total_withdrawn()} ⭐️</b>", parse_mode='HTML', reply_markup=markup)

@router.message()
async def handle_reply_buttons(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    ref_link = f"https://t.me/{ (await bot.me()).username }?start={user_id}"
    if message.text == "🔎Искать собеседника":
        try:
            user_data = get_podbor(user_id)
            user_standart_data = get_user(user_id)
            user_vip = get_vip_user(user_id)
            user_pre = get_pre_user(user_id)
            users_data = get_podbor_status_1(1)
            if user_data:
                # Vip
                vip = user_vip[0]
                vip_about_info = user_vip[3]
                vip_name = user_vip[5]
                vip_interesi = user_vip[4]
                vip_age = user_vip[6]
                # Pre
                pre = user_pre[0]
                pre_about_info = user_pre[3]
                pre_name = user_pre[5]
                pre_interesi = user_pre[4]
                pre_age = user_pre[6]
                # Podbor
                status = user_data[2]
                id_obmen_message = user_data[3]
                users = users_data[0]
                users_interesi = users_data[4]
                # Standart user
                user_about_info = user_standart_data[5]
                user_interesi = user_standart_data[6]
                user_name = user_standart_data[7]
                user_age = user_standart_data[8]
                if vip == 1:
                    if not user_about_info == 'None':
                        if not user_interesi == 'None':
                            if not user_name == 'None':
                                if not user_age == 'None':
                                    await bot.send_message(user_id, text="🔎Подбираем вам собеседника")
                                    sobes = random.choice(users)





        except ValueError as e:
            await bot.send_message(user_id, text=f"🚫Error🚫\n\n<blockquote>{e}</blockquote>\n\nНе спешите сообщать об ошибке, эта ошибка была автоматически отправлена администратору!", parse_mode='HTML')
            await bot.send_message(admins, text=f"Была перехвачена ошибка:\n<blockquote>{e}</blockquote>\n\nРешите эту проблему!")
    else:
        if len(channel_ids) > 0:
            if await check_subscription(user_id, channel_ids, bot):
                return
    if message.text == "Получить звезды":
        await bot.send_message(user_id, text="Подпишитесь на спонсоров для получения доступа к боту")
    if message.text == "💸 Вывести звёзды":
        user_data = get_user(user_id)
        if user_data:
            stars = user_data[2]
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="15 ⭐️", callback_data="15"),
                InlineKeyboardButton(text="25 ⭐️", callback_data="25")
            )
            builder.row(
                InlineKeyboardButton(text="50 ⭐️", callback_data="50"),
                InlineKeyboardButton(text="100 ⭐️", callback_data="100")
            )
            builder.row(
                InlineKeyboardButton(text="150 ⭐️", callback_data="150"),
                InlineKeyboardButton(text="350 ⭐️", callback_data="350")
            )
            builder.row(
                InlineKeyboardButton(text="500 ⭐️", callback_data="500")
            )
            withdraw_stars_markup = builder.as_markup()
            await bot.send_message(message.chat.id, f"<b>У тебя на счету: {stars}\n\n(По всем вопросам - @ABTOSOUND)\n\nВыбери сколько звезд хочешь получить:</b>", parse_mode='HTML', reply_markup=withdraw_stars_markup)
    else:
        if len(channel_ids) > 0:
            if await check_subscription(user_id, channel_ids, bot):
                return
    if message.text == "🤑 Мой баланс":
        user_data = get_user(user_id)
        builder = InlineKeyboardBuilder()
        builder.button(text="🎁 Активировать промокод", callback_data="promocode")
        builder.button(text="NFT чат", url="https://t.me/PABEL_DUP0V")
        builder.row(
            InlineKeyboardButton(text="BotNet", callback_data="botnet")
        )
        markup_profile = builder.as_markup()
        if user_data:
            count_refs = user_data[3]
            withdrawed = user_data[5]
            stars = user_data[2]
            await bot.send_message(user_id, f'<b>У тебя на счету: {stars} ⭐️\nВыведено звезд: {withdrawed} ⭐️\nПриглашенных пользователей: {count_refs}\n\n🔗 Ваша ссылка - {ref_link}</b>', parse_mode='HTML', reply_markup=markup_profile)
        else:
            await bot.send_message(user_id, "<b>❌ Ваш профиль не найден. Используйте /start для регистрации.</b>", parse_mode='HTML')
    else:
        if len(channel_ids) > 0:
            if await check_subscription(user_id, channel_ids, bot):
                return
    if message.text == "💰 Задания":
        await bot.send_message(user_id, "<b>🎯 На данный момент нет доступных заданий!\n\nВозвращайся позже!</b>",parse_mode='HTML')
    else:
        if len(channel_ids) > 0:
            if await check_subscription(user_id, channel_ids, bot):
                return
    if message.text == "Помощь":
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="Не засчитали реферала", callback_data="ne_zaschitali_referala")
        )
        builder.row(
            InlineKeyboardButton(text="Не вывелись звезды", callback_data="ne_viveli_zvezdi")
        )
        builder.row(
            InlineKeyboardButton(text="Написать в поддержку", url="https://t.me/ABTOSOUND")
        )
        help_markup = builder.as_markup()
        await bot.send_message(user_id, text="Выберите подходящие варианты, если не нашли свою проблему напишите в поддержку!", reply_markup=help_markup)

@router.callback_query()
async def handle_stars_callback(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    user_id = call.from_user.id
    username = call.from_user.username
    user_data = get_user(user_id)
    if call.data == 'set_znach':
        await bot.send_message(user_id, text="Введите имя которое хотите видеть в профиле:")
        await state.set_state()
    if call.data == "ne_viveli_zvezdi":
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="Написать в поддержку", url="https://t.me/ABTOSOUND")
        )
        markup = builder.as_markup()
        await bot.send_message(user_id, text="Не вывелись звезды?\n\n1.Проверьте достаточно ли у вас звезд на балансе для вывода\n2.Напишите в поддержку если вы уверены что вы сделали все правильно", reply_markup=markup)
    if call.data == "ne_zaschitali_referala":
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="Написать в поддержку", url="https://t.me/ABTOSOUND")
        )
        markup = builder.as_markup()
        await bot.send_message(user_id, text="Не засчитали реферала?\n\n1.Проверьте зашел ли он по ВАШЕЙ реферальной ссылке, запустил бота, подписался на всех спонсоров - если это не сделано реферал не засчитается!\n2.Если реферал был в боте то не засчитается!\n3.Если все условия выполнены, но вам не зачислили реферала, то нажмите кнопку ниже и сообщите это администратору", reply_markup=markup)
    if user_data:
        stars = user_data[2]
        if call.data in ['15', '25', '50', '100', '150', '350', '500']:
            if int(call.data) > stars:
                await bot.answer_callback_query(call.id, "❌ У вас недостаточно звезд для вывода!", show_alert=True)
            else:
                await bot.answer_callback_query(call.id, "✅ Заявка на вывод звезд успешно отправлена!", show_alert=True)
                withdraw_stars(user_id, int(call.data))
                for admin in admins:
                    await bot.send_message(admin, f"<b>✅ Cоздан запрос на вывод\n\n👤 Пользователь @{username} | {user_id} \n💫 Количество: <code>{int(call.data)}</code>⭐️ </b>", parse_mode='HTML')
    if call.data == "add_stars":
        await bot.send_message(user_id, "<b>Введите ID пользователя:</b>", parse_mode='HTML')
        await state.set_state(AdminState.waiting_for_user_id_add_stars)
    if call.data == "remove_stars":
        await bot.send_message(user_id, "<b>Введите ID пользователя:</b>", parse_mode='HTML')
        await state.set_state(AdminState.waiting_for_user_id_remove_stars)
    if call.data == "mailing":
        await bot.send_message(user_id, "<b>Введите текст для рассылки:</b>", parse_mode='HTML')
        await state.set_state(AdminState.waiting_for_mailing_text)
    if call.data == "add_channel":
        await bot.send_message(user_id, "<b>Введите ID канала:</b>", parse_mode='HTML')
        await state.set_state(AdminState.waiting_for_channel_id_add)
    if call.data == 'delete_channel':
        await bot.send_message(user_id, "<b>Введите ID канала:</b>", parse_mode='HTML')
        await state.set_state(AdminState.waiting_for_channel_id_delete)
    if call.data == 'mailing_zero_refs':
        text = "⁉️🤨Мы заметили, что вы не пригласили ни 1 друга!\n\nПерешли ссылку своим друзьям, а также по чатам, 3 ⭐️ за 1 приглашенного⤵️"
        users = get_user_zero_referrals()

        for user in users:
            user_id = user[0]
            ref_link = f"\n\nТвоя персональная ссылка — https://t.me/{ (await bot.me()).username }?start={user_id}"
            full_text = f"{text}{ref_link}"

            try:
                await bot.send_message(user_id, f"<b>{full_text}</b>", parse_mode='HTML')
                print(f"[РАССЫЛКА 1.0] Отправлено: {user_id}")
            except Exception as e:
                print(f"[РАССЫЛКА 1.0] Не отправлено: {user_id}")

        await bot.send_message(call.message.chat.id, "<b>✅ Рассылка успешно отправлена!</b>", parse_mode='HTML')
    if call.data == "check_subs":
        if await check_subscription(user_id, channel_ids, bot):
            await bot.send_message(user_id, "<b>⚠️ Подпишитесь на каналы, чтобы продолжить!</b>", parse_mode='HTML')
        else:
            reff_link = f"https://t.me/{ (await bot.me()).username }?start={user_id}"
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(text="Поделиться ссылкой", url="https://t.me/share/url?url=" + reff_link)
            )
            markup = builder.as_markup()
            await bot.send_message(user_id, "⭐", reply_markup=get_main_keyboard())
            await bot.send_message(user_id, f"<b>✨ Добро пожаловать!\n\nРаспространяй свою ссылку и получи 3 ⭐️ телеграма за 1 приглашенного друга\n\n🔗 Ваша ссылка - {reff_link}</b>", parse_mode='HTML', reply_markup=markup)
    if call.data == "promocode":
        await bot.send_message(user_id, "<b>🎄 Введите промокод:</b>", parse_mode='HTML')
        await state.set_state(AdminState.waiting_for_promocode_activation)
    if call.data == "add_promo_code":
        await bot.send_message(user_id, "<b>Введите промокод, количество звезд, количество использований через запятую:</b>", parse_mode='HTML')
        await state.set_state(AdminState.waiting_for_promo_details_add)
    if call.data == "delete_promo_code":
        await bot.send_message(user_id, "<b>Введите промокод:</b>", parse_mode='HTML')
        await state.set_state(AdminState.waiting_for_promocode_delete)
    await call.answer()

async def check_subscription(user_id, channel_ids, bot: Bot):
    if not channel_ids:
        return True

    builder = InlineKeyboardBuilder()
    show_join_button = False
    for channel_id in channel_ids:
        try:
            chat_member = await bot.get_chat_member(channel_id, user_id)
            if chat_member.status not in ['member', 'administrator', 'creator', 'restricted']:
                invite_link = (await bot.create_chat_invite_link(channel_id, member_limit=1)).invite_link
                builder.button(text="Подписаться", url=invite_link)
                show_join_button = True
        except Exception as e:
            print(f"Ошибка при проверке подписки: {e}")
            await bot.send_message(user_id, "Ошибка при проверке подписки. Пожалуйста, попробуйте позже.")
            return False

    if show_join_button:
        builder.row(
            InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_subs")
        )
        markup = builder.as_markup()
        await bot.send_message(user_id, "<b>👋🏻 Добро пожаловать\n\nПодпишитесь на каналы, чтобы продолжить!</b>", parse_mode='HTML', reply_markup=markup)
        return True

    return False








dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    executor.start_polling(dp, skip_updates=True)
### --- ИМПОРТ БИБЛИОТЕК, "РЕГИСТРАЦИИ БОТА", ОБЪЯВЛЕНИЕ ПЕРЕМЕННЫХ И ПОЛУЧЕНИЯ ИМЯ ПОЛЬЗОВАТЕЛЯ --- ###

# Импорт необходимых библиотек
import asyncio          # Асинхронное программирование
import logging          # Логирование для отладки
import os              # Работа с операционной системой (переменные окружения)
from aiogram import Bot, Dispatcher, types, F  # Основные компоненты aiogram
from aiogram.filters.command import Command    # Фильтр для команд
from aiogram.utils.keyboard import InlineKeyboardBuilder  # Создание inline клавиатур
import random          # Генерация случайных чисел

# Настройка логирования для отладки
# Устанавливаем уровень логирования INFO для вывода информационных сообщений
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  # Создаем логгер для текущего модуля

# Получаем токен из переменных окружения
# Сначала пытаемся получить из переменной окружения BOT_TOKEN, если нет - используем тестовый токен
TOKEN = os.getenv("BOT_TOKEN") or '8325400636:AAEfcbUyJqUpsvphbx86NmSrEeH_HkDi7LY'
# Проверяем, что токен существует
if not TOKEN:
    raise ValueError("Токен бота не найден! Установите переменную окружения BOT_TOKEN")

# Создаем экземпляры бота и диспетчера
# Bot - основной класс для взаимодействия с Telegram API
# Dispatcher - маршрутизатор сообщений и обработчиков
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Глобальные переменные для хранения данных
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # Числа для математических примеров
signs = ("+", "-", "*", "/")           # Математические операции

# Кортеж с правилами русского языка
russian_rules = (
    "Безударные гласные в корне — проверяются ударением: вода — вОды, сады — сАд.", 
    "Парные звонкие и глухие согласные в конце слова и перед глухими — проверяются подбором однокоренного слова: дуб — дубы, пруд — прудик.",
    "Непроизносимые согласные — проверяются подбором слова, где звук слышен: звёздный — звезда, честный — честь.",
    "Правописание приставок на -з/-с: без-/бес-, воз-/вос-, из-/ис- — зависит от последующего согласного (звонкий/глухой).",
    "Правописание приставок пре-/при-: при- — близость, присоединение, неполнота действия (приехать, приклеить, приоткрыть); пре- — высшая степень, «очень» или как пере- (прекрасный, преградить).",
    "Чередующиеся гласные в корне (-гор/-гар, -клон/-клан, -раст/-рос и др.) — пишутся по правилу, а не по слуху: загар, наклонение, выращенный.", 
    "Правописание -Н- и -НН- в суффиксах причастий и отглагольных прилагательных: -Н- — краткие формы, несов. вид без приставки (жареный картофель); -НН- — полные формы, приставка, зависимые слова (жаренный на сковороде картофель).",
    "Правописание -О-/-Е- после шипящих и Ц: под ударением — О (шОрох, крыжОвник), без ударения — Е (жЕлудь, цЕпочка), исключения: крыжовник, шорох, капюшон.", 
    "Правописание Ь после шипящих: в существительных жен. рода — ночь, мышь, в глаголах 2-го лица ед. ч. — пишешь, молчишь,в инфинитиве — беречь, стричь.",
    "Правописание безударных окончаний имён существительных, прилагательных, глаголов — определяется склонением/спряжением: в лесу (1 скл.), в степи (3 скл.), красивого (муж. р.), красивой (жен. р.).", 
    "Запятая при однородных членах предложения, соединённых интонацией перечисления или союзами и, да (=и), или, либо: Я купил хлеб, молоко и сыр.",
    "Запятая перед союзами А, НО, ЗАТО, ОДНАКО, ДА (=но) между простыми предложениями в составе сложного: Я хотел пойти, но пошёл дождь.", 
    "Запятая при деепричастном обороте (с деепричастием): Гуляя по парку, он вспомнил детство.",
    "Запятая при причастном обороте (если он стоит после определяемого слова): Книга, прочитанная мной, была интересной.", 
    "Запятая при вводных словах и конструкциях: К сожалению, я не смогу прийти.",
    "Тире между подлежащим и сказуемым, если они выражены существительными в именительном падеже: Он — мой друг. (Но: Он мой друг — без тире, если нет паузы.)", 
    "Согласование подлежащего и сказуемого в роде, числе и лице: Мама читает. Дети играют. Мы идём.",
    "Управление — правильный выбор падежа при глаголах и предлогах: думать о чём? — о будущем (П.п.), ждать кого? — друга (В.п.).", 
    "Спряжение глаголов: 1 спряжение — -ешь, -ет, -ем, -ете, -ут/-ют (писать — пишешь), 2 спряжение — -ишь, -ит, -им, -ите, -ат/-ят (носить — носишь). Исключения: брить, стелить, гнать, держать, дышать, слышать, видеть, ненавидеть, обидеть, вертеть, смотреть, зависеть, терпеть.",
    "Различие частиц НЕ и НИ: НЕ — отрицание (не идёт, не красивый), НИ — усиление отрицания или в составе устойчивых выражений (ни за что, ни тот ни другой, кто бы ни пришёл)."
)

# Словари для хранения состояния пользователей и сообщений
user_state = {}        # Хранит текущее состояние каждого пользователя (примеры)
user_messages = {}     # Хранит ID сообщений для последующего удаления

# Кортежи с фразами для продолжения
more_math = ("Нужен еще пример? Держи", "Подогнал для тебя еще один пример", "Вот ещё один пример")
more_russian = ("Нужено еще правило? Держи", "Подогнал для тебя еще одино правило", "Вот ещё одино правило")

def get_user_name(user: types.User) -> str:
    """
    Получает имя пользователя для персонализации общения
    
    Args:
        user (types.User): Объект пользователя Telegram
        
    Returns:
        str: Имя пользователя (first_name, username или "Пользователь")
    """
    if user.first_name:
        return user.first_name          # Возвращаем имя пользователя
    elif user.username:
        return f"@{user.username}"      # Возвращаем username с @
    else:
        return "Пользователь"           # Стандартное имя, если ничего нет

def safe_delete_message(chat_id: int, message_id: int):
    """
    Безопасное удаление сообщения с обработкой ошибок
    
    Args:
        chat_id (int): ID чата
        message_id (int): ID сообщения для удаления
        
    Returns:
        function: Асинхронная функция для удаления сообщения
    """
    async def _delete():
        try:
            # Проверяем, что message_id существует
            if message_id:
                await bot.delete_message(chat_id, message_id)  # Удаляем сообщение
                logger.info(f"Сообщение {message_id} успешно удалено")  # Логируем успех
        except Exception as e:
            # Логируем ошибку, но не прерываем выполнение
            logger.warning(f"Не удалось удалить сообщение {message_id}: {e}")
    return _delete()

### --- ХЭНДЛЕРЫ ДЛЯ СТАРТА И ВЫХОДА В МЕНЮ --- ###

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    """
    Обработчик команды /start - приветствие и показ главного меню
    
    Args:
        message (types.Message): Сообщение от пользователя
    """
    user_name = get_user_name(message.from_user)  # Получаем имя пользователя
    
    # Создаем inline клавиатуру с двумя кнопками
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Тренировать примеры",           # Текст кнопки
        callback_data="math")                 # Callback данные
    )
    builder.add(types.InlineKeyboardButton(
        text="Повторить правила русского языка",
        callback_data="russian")
    )
    
    # Отправляем приветственное сообщение с клавиатурой
    sent_message = await message.answer(
        f"Привет, {user_name}! Я твой цифровой бот помощник, и помогу тебе разобраться с твоими проблемами! Начнем!",
        reply_markup=builder.as_markup()      # Добавляем клавиатуру
    )

    # Сохраняем ID сообщения меню для последующего удаления
    user_messages[message.from_user.id] = {'menu_message_id': sent_message.message_id}

@dp.callback_query(F.data == "exit")
async def exit_handler(callback: types.CallbackQuery):
    """
    Обработчик кнопки "Выйти" - возврат в главное меню
    
    Args:
        callback (types.CallbackQuery): Callback запрос от пользователя
    """
    user_name = get_user_name(callback.from_user)  # Получаем имя пользователя
    chat_id = callback.message.chat.id             # Получаем ID чата

    # Удаляем все сообщения пользователя
    if callback.from_user.id in user_messages:
        user_msg_data = user_messages[callback.from_user.id].copy()  # Копируем данные
        
        # Определяем порядок удаления сообщений (от новых к старым)
        message_keys = [
            'skip_buttons_message_id',    # Сначала кнопки пропустить/выйти
            'buttons_message_id',         # Затем кнопки еще пример/выйти
            'answer_message_id',          # Ответ пользователя
            'example_message_id',         # Пример
            'instruction_message_id',     # Инструкция
            'explanation_message_id',     # Объяснение
            'error_message_id',           # Сообщения об ошибках
            'russianrule_message_id',     # Правило русского
            'russian_message_id',         # Сообщение о правилах
            'menu_message_id'             # Меню
        ]
        
        # Удаляем сообщения в обратном порядке
        for key in message_keys:
            message_id = user_msg_data.get(key)
            if message_id:
                await safe_delete_message(chat_id, message_id)
        
        # Очищаем данные пользователя
        user_messages.pop(callback.from_user.id, None)
    
    # Показываем новое меню
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Тренировать примеры",
        callback_data="math")
    )
    builder.add(types.InlineKeyboardButton(
        text="Повторить правила русского языка",
        callback_data="russian")
    )
    
    # Отправляем новое приветственное сообщение
    sent_message = await callback.message.answer(
        f"Привет, {user_name}! Я твой цифровой бот помощник, и помогу тебе разобраться с твоими проблемами! Начнем!",
        reply_markup=builder.as_markup()
    )

    # Сохраняем ID нового меню
    user_messages[callback.from_user.id] = {'menu_message_id': sent_message.message_id}
    await callback.answer()  # Подтверждаем callback

### --- ХЭНДЛЕРЫ ДЛЯ ВСЕГО, ЧТО СВЯЗАНО С МАТЕМАТИЧЕСКИМИ ПРИМЕРАМИ --- ###

@dp.callback_query(F.data == "math")
async def math_handler(callback: types.CallbackQuery):
    """
    Обработчик выбора математики - генерация примера
    
    Args:
        callback (types.CallbackQuery): Callback запрос от пользователя
    """
    user_name = get_user_name(callback.from_user)  # Получаем имя пользователя
    chat_id = callback.message.chat.id             # Получаем ID чата

    # Удаляем меню, если оно есть
    if callback.from_user.id in user_messages:
        menu_message_id = user_messages[callback.from_user.id].get('menu_message_id')
        if menu_message_id:
            await safe_delete_message(chat_id, menu_message_id)
    
    # Генерируем случайный математический пример
    num1 = random.choice(numbers)     # Первое число
    sign = random.choice(signs)       # Знак операции
    num2 = random.choice(numbers)     # Второе число
    
    # Обработка деления на ноль
    if sign == "/":
        while num2 == 0:              # Пока второе число равно нулю
            num2 = random.choice(numbers)  # Генерируем новое число

    # Сохраняем состояние пользователя (текущий пример)
    user_state[callback.from_user.id] = {
        'num1': num1,
        'sign': sign,
        'num2': num2
    }

    # Создаем клавиатуру с кнопками пропустить и выйти
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Пропустить пример",
        callback_data="skip_example")
    )
    builder.add(types.InlineKeyboardButton(
        text="Выйти",
        callback_data="exit")
    )

    # Отправляем сообщения с примером и инструкцией
    explanation_msg = await callback.message.answer(f"{user_name}, хочешь повторить примеры по математике? Держи один.")
    instruction_msg = await callback.message.answer("Если при делении выйдет длинная десятичная дробь, округляй ее до сотых")
    buttons_msg = await callback.message.answer("Если станет сложно решить пример, можешь его пропустить его, или выйти", reply_markup=builder.as_markup())
    example_msg = await callback.message.answer(f"{num1} {sign} {num2}")
    
    # Сохраняем ID всех отправленных сообщений для последующего удаления
    user_messages[callback.from_user.id] = {
        'explanation_message_id': explanation_msg.message_id,
        'instruction_message_id': instruction_msg.message_id,
        'example_message_id': example_msg.message_id,
        'skip_buttons_message_id': buttons_msg.message_id
    }
    
    await callback.answer()  # Подтверждаем callback

@dp.callback_query(F.data == "skip_example")
async def skip_example_handler(callback: types.CallbackQuery):
    """
    Обработчик кнопки "Пропустить пример" - переход к следующему примеру
    
    Args:
        callback (types.CallbackQuery): Callback запрос от пользователя
    """
    chat_id = callback.message.chat.id  # Получаем ID чата
    
    # Удаляем сообщение с кнопками пропустить/выйти
    if callback.from_user.id in user_messages:
        skip_message_id = user_messages[callback.from_user.id].get('skip_buttons_message_id')
        if skip_message_id:
            await safe_delete_message(chat_id, skip_message_id)
    
    # Переходим к генерации следующего примера
    await more_math_handler(callback)

@dp.message()
async def math_answer_handler(message: types.Message):
    """
    Обработчик текстовых сообщений - проверка ответов на примеры
    
    Args:
        message (types.Message): Сообщение от пользователя
    """
    user_name = get_user_name(message.from_user)  # Получаем имя пользователя
    chat_id = message.chat.id                     # Получаем ID чата
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Еще пример",
        callback_data="more_math")
    )
    builder.add(types.InlineKeyboardButton(
        text="Выйти",
        callback_data="exit")
    )

    user_id = message.from_user.id  # Получаем ID пользователя
    
    # Проверяем, есть ли у пользователя активный пример
    if user_id not in user_state:
        await message.answer("Сначала запроси пример через кнопку 'Тренировать примеры'.")
        return

    # Получаем данные текущего примера
    data = user_state[user_id]
    num1 = data['num1']
    sign = data['sign']
    num2 = data['num2']

    # Вычисляем правильный ответ
    if sign == "+":
        realy_answer = num1 + num2
    elif sign == "-":
        realy_answer = num1 - num2
    elif sign == "*":
        realy_answer = num1 * num2
    elif sign == "/":
        realy_answer = round(num1 / num2, 2)  # Округляем до сотых

    # Проверяем ответ пользователя
    try:
        # Преобразуем текст в число (поддерживаем как точку, так и запятую как десятичный разделитель)
        user_answer = float(message.text.replace(',', '.'))  
    except ValueError:
        # Если введено не число, отправляем сообщение об ошибке
        # Удаляем предыдущее сообщение об ошибке, если оно есть
        if user_id in user_messages:
            error_message_id = user_messages[user_id].get('error_message_id')
            if error_message_id:
                await safe_delete_message(chat_id, error_message_id)
        
        error_msg = await message.answer("Пожалуйста, введи числовой ответ.")
        
        # Сохраняем ID сообщения об ошибке
        if user_id in user_messages:
            user_messages[user_id]['error_message_id'] = error_msg.message_id
        else:
            user_messages[user_id] = {'error_message_id': error_msg.message_id}
        return

    # Сохраняем ID сообщения пользователя
    if user_id in user_messages:
        user_messages[user_id]['answer_message_id'] = message.message_id
    else:
        user_messages[user_id] = {'answer_message_id': message.message_id}

    # Удаляем сообщения об ошибках и кнопки пропуска
    if user_id in user_messages:
        # Удаляем сообщение об ошибке
        error_message_id = user_messages[user_id].get('error_message_id')
        if error_message_id:
            await safe_delete_message(chat_id, error_message_id)
            user_messages[user_id].pop('error_message_id', None)

        # Удаляем кнопки пропустить/выйти
        skip_buttons_id = user_messages[user_id].get('skip_buttons_message_id')
        if skip_buttons_id:
            await safe_delete_message(chat_id, skip_buttons_id)
            user_messages[user_id].pop('skip_buttons_message_id', None)

    # Формируем ответ в зависимости от правильности ответа
    if abs(user_answer - realy_answer) < 1e-2:  # Сравнение с учетом погрешности
        response_text = f"Правильно, {user_name}! Ответ был: {realy_answer}"
    else:
        response_text = f"Неправильно, {user_name}. Правильный ответ: {realy_answer}"
    
    # Отправляем результат проверки с кнопками
    buttons_msg = await message.answer(response_text, reply_markup=builder.as_markup())
    
    # Сохраняем ID сообщения с кнопками
    if user_id in user_messages:
        user_messages[user_id]['buttons_message_id'] = buttons_msg.message_id
    else:
        user_messages[user_id] = {'buttons_message_id': buttons_msg.message_id}

    # Удаляем состояние пользователя (пример решен)
    user_state.pop(user_id, None)

@dp.callback_query(F.data == "more_math")
async def more_math_handler(callback: types.CallbackQuery):
    """
    Обработчик кнопки "Еще пример" - генерация нового математического примера
    
    Args:
        callback (types.CallbackQuery): Callback запрос от пользователя
    """
    user_name = get_user_name(callback.from_user)  # Получаем имя пользователя
    chat_id = callback.message.chat.id             # Получаем ID чата

    # Удаляем предыдущие сообщения
    if callback.from_user.id in user_messages:
        user_msg_data = user_messages[callback.from_user.id]
        
        # Определяем порядок удаления сообщений
        message_keys = [
            'skip_buttons_message_id',
            'buttons_message_id',
            'answer_message_id',
            'example_message_id',
            'instruction_message_id',
            'explanation_message_id',
            'error_message_id'
        ]
        
        # Удаляем сообщения в правильном порядке
        for key in message_keys:
            message_id = user_msg_data.get(key)
            if message_id:
                await safe_delete_message(chat_id, message_id)
    
    # Генерируем новый пример
    num1 = random.choice(numbers)     # Первое число
    sign = random.choice(signs)       # Знак операции
    num2 = random.choice(numbers)     # Второе число
    
    # Обработка деления на ноль
    if sign == "/":
        while num2 == 0:
            num2 = random.choice(numbers)

    # Сохраняем состояние пользователя (новый пример)
    user_state[callback.from_user.id] = {
        'num1': num1,
        'sign': sign,
        'num2': num2
    }

    # Создаем клавиатуру с кнопками
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Пропустить пример",
        callback_data="skip_example")
    )
    builder.add(types.InlineKeyboardButton(
        text="Выйти",
        callback_data="exit")
    )

    # Отправляем сообщения с новым примером
    explanation_msg = await callback.message.answer(f"{user_name}, {random.choice(more_math).lower()}")
    instruction_msg = await callback.message.answer("Если при делении выйдет длинная десятичная дробь, округляй ее до сотых")
    buttons_msg = await callback.message.answer("Если станет сложно решить пример, можешь его пропустить его, или выйти", reply_markup=builder.as_markup())
    example_msg = await callback.message.answer(f"{num1} {sign} {num2}")
    
    # Обновляем ID сообщений
    user_messages[callback.from_user.id] = {
        'explanation_message_id': explanation_msg.message_id,
        'instruction_message_id': instruction_msg.message_id,
        'example_message_id': example_msg.message_id,
        'skip_buttons_message_id': buttons_msg.message_id
    }
    
    await callback.answer()  # Подтверждаем callback

### --- ХЭНДЛЕРЫ ДЛЯ ВСЕГО, ЧТО СВЯЗАНО С ПРАВИЛАМИ РУССКОГО ЯЗЫКА --- ###

@dp.callback_query(F.data == "russian")
async def russian_handler(callback: types.CallbackQuery):
    """
    Обработчик выбора русского языка - показ правила
    
    Args:
        callback (types.CallbackQuery): Callback запрос от пользователя
    """
    # Создаем клавиатуру с кнопками
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Еще одно правило",
        callback_data="more_russian")
    )
    builder.add(types.InlineKeyboardButton(
        text="Выйти",
        callback_data="exit")
    )

    user_name = get_user_name(callback.from_user)  # Получаем имя пользователя
    chat_id = callback.message.chat.id             # Получаем ID чата

    # Удаляем меню, если оно есть
    if callback.from_user.id in user_messages:
        menu_message_id = user_messages[callback.from_user.id].get('menu_message_id')
        if menu_message_id:
            await safe_delete_message(chat_id, menu_message_id)

    # Отправляем сообщения с правилом
    russian_msg = await callback.message.answer(f"{user_name}, хочешь повторить правила русского языка? Держи одно.")
    russianrule_msg = await callback.message.answer(random.choice(russian_rules), reply_markup=builder.as_markup())

    # Сохраняем ID сообщений
    user_messages[callback.from_user.id] = {
        'russian_message_id': russian_msg.message_id,
        'russianrule_message_id': russianrule_msg.message_id
    }

    await callback.answer()  # Подтверждаем callback

@dp.callback_query(F.data == "more_russian")
async def morerussian_handler(callback: types.CallbackQuery):
    """
    Обработчик кнопки "Еще одно правило" - показ нового правила
    
    Args:
        callback (types.CallbackQuery): Callback запрос от пользователя
    """
    # Создаем клавиатуру с кнопками
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Еще одно правило",
        callback_data="more_russian")
    )
    builder.add(types.InlineKeyboardButton(
        text="Выйти",
        callback_data="exit")
    )

    user_name = get_user_name(callback.from_user)  # Получаем имя пользователя
    chat_id = callback.message.chat.id             # Получаем ID чата

    # Удаляем предыдущие сообщения
    if callback.from_user.id in user_messages:
        # Удаляем предыдущее сообщение с приветствием
        russian_message_id = user_messages[callback.from_user.id].get('russian_message_id')
        if russian_message_id:
            await safe_delete_message(chat_id, russian_message_id)
            
        # Удаляем предыдущее сообщение с правилом
        russianrule_message_id = user_messages[callback.from_user.id].get('russianrule_message_id')
        if russianrule_message_id:
            await safe_delete_message(chat_id, russianrule_message_id)

    # Отправляем новые сообщения с правилом
    russian_msg = await callback.message.answer(f"{user_name}, {random.choice(more_russian).lower()}")
    russianrule_msg = await callback.message.answer(random.choice(russian_rules), reply_markup=builder.as_markup())

    # Обновляем ID сообщений
    user_messages[callback.from_user.id] = {
        'russian_message_id': russian_msg.message_id,
        'russianrule_message_id': russianrule_msg.message_id
    }

    await callback.answer()  # Подтверждаем callback

### --- ЗАПУСК ПРОЕКТА --- ###

async def main():
    """
    Основная функция запуска бота
    """
    # Запускаем polling (опрос Telegram API на наличие новых сообщений)
    await dp.start_polling(bot)

# Запуск бота
if __name__ == "__main__":
    # Запускаем асинхронную функцию main
    asyncio.run(main())
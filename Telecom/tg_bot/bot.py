import joblib
import pandas as pd

# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram import Router

model = joblib.load('model.pkl')
scaler = joblib.load('scaler.pkl')
columns = joblib.load('columns_list.pkl')
# print(columns)

API_TOKEN = '8204293895:AAFKf7k51HSiFq97XuavYm589HfY7-7YQhs'
# Создание объектов
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

class Form(StatesGroup):
    # снижение оттока
    tenure = State()
    monthly_charges = State()
    contract = State()
    # повышение оттока
    total_charges = State()
    internet_service = State()
    streaming = State()
    payment_method = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    # tenure
    await state.set_state(Form.tenure)
    await message.answer("Сколько месяцев клиент с компанией (tenure):")

@router.message(Form.tenure)
async def tenure(message: Message, state: FSMContext):
    try:
        await state.update_data(tenure=float(message.text))
    except ValueError:
        await message.answer('Введите корректное число')
        return
    # monthly_charges
    await state.set_state(Form.monthly_charges)
    await message.answer("Ежемесячные платежи:")

@router.message(Form.monthly_charges)
async def monthly_charges(message: Message, state: FSMContext):
    try:
        await state.update_data(monthly_charges=float(message.text))
    except ValueError:
        await message.answer('Введите корректное число')
        return

    # contract
    contract_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Month-to-month")],
            [KeyboardButton(text="One year")],
            [KeyboardButton(text="Two year")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await state.set_state(Form.contract)
    await message.answer("Выберите тип контракта:", reply_markup=contract_kb)

@router.message(Form.contract)
async def contract(message: Message, state: FSMContext):
    if message.text not in ["Month-to-month", "One year", "Two year"]:
        await message.answer("выберите нужный вариант")
        return
    await state.update_data(contract=message.text)

    # total_charges
    await state.set_state(Form.total_charges)
    await message.answer("Общая сумма платежей (TotalCharges):")

@router.message(Form.total_charges)
async def total_charges(message: Message, state: FSMContext):
    try:
        await state.update_data(total_charges=float(message.text))
    except ValueError:
        await message.answer('Введите корректное число')
        return

    # internet_service
    internet_service_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="DSL")],
            [KeyboardButton(text="Fiber optic")],
            [KeyboardButton(text="No internet service")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await state.set_state(Form.internet_service)
    await message.answer("Выберите тип интернет-сервиса:", reply_markup=internet_service_kb)

@router.message(Form.internet_service)
async def internet_service(message: Message, state: FSMContext):
    mapping = {
        "DSL": "DSL",
        "Fiber optic": "Fiber optic",
        "No internet service": "No"
    }

    if message.text not in mapping:
        await message.answer("выберите нужный вариант")
        return
    await state.update_data(internet_service=mapping[message.text])

    # steaming
    streaming_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Только TV")],
            [KeyboardButton(text="Только Movies")],
            [KeyboardButton(text="TV + Movies")],
            [KeyboardButton(text="Нет стриминга")]
            ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await state.set_state(Form.streaming)
    await message.answer(
        "Используется ли стриминг сервисы?",
        reply_markup=streaming_kb
    )

@router.message(Form.streaming)
async def streaming_tv(message: Message, state: FSMContext):
    mapping = {
        "Только TV": ("Yes", "No"),
        "Только Movies": ("No", "Yes"),
        "TV + Movies": ("Yes", "Yes"),
        "Нет стриминга": ("No", "No")
    }

    if message.text not in mapping:
        await message.answer("выберите нужный вариант")
        return

    tv, movies = mapping[message.text]
    await state.update_data(streaming_tv=tv, streaming_movies=movies)

    # payment_method
    payment_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Electronic check")],
            [KeyboardButton(text="Mailed check")],
            [KeyboardButton(text="Bank transfer (automatic)")],
            [KeyboardButton(text="Credit card (automatic)")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await state.set_state(Form.payment_method)
    await message.answer("Способ оплаты:", reply_markup=payment_kb)

@router.message(Form.payment_method)
async def payment_method(message: Message, state: FSMContext):
    answers = [
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)"]
    if message.text not in answers:
        await message.answer("выберите нужный вариант")
        return
    await state.update_data(payment_method=message.text)

    data = await state.get_data()
    await state.clear()
    df = pd.DataFrame([data])
    df_encoded = pd.get_dummies(df)

    # доп колонки с обучения
    for col in columns:
        if col not in df_encoded.columns:
            df_encoded[col] = 0

    df_encoded = df_encoded[columns]

    # scale
    X_scaled = scaler.transform(df_encoded)

    # predict
    proba = model.predict_proba(X_scaled)[0][1]
    percent = round(proba * 100, 2)

# print(df_encoded.head())

    # Итог
    risk = "высокий" if percent >= 50 else "низкий" # для красоты

    await message.answer(
        f"*Вероятность оттока клиента:* {percent}%\n"
        f"Уровень риска: *{risk}*"
        f"\n\nДля нового ввода данных нажмите /start",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode=ParseMode.MARKDOWN
    )

dp.include_router(router)

if __name__ == "__main__":
    import asyncio
    async def main():
        await dp.start_polling(bot)
    asyncio.run(main())
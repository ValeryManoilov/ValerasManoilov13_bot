from Config import Config
from aiogram.bot import Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio

storage = MemoryStorage()
bot = Bot(Config.BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)

class History(StatesGroup):
    first_vote = State()
    second_vote = State()
    end = State()

def get_kb() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup()
    keyboard.add(
        KeyboardButton('Пойти направо'),
        KeyboardButton('Пойти налево')
    )
    return keyboard

@dp.message_handler(commands=['start'])
async def cmd_start(message: Message):
    await message.answer('Это игра с разными концовками, введи => /start_game')
    await History.first_vote.set()

@dp.message_handler(state=History.first_vote)
async def answer_q1(message: Message):
    await message.answer(text='Развилка. Выбери путь:', reply_markup=get_kb())
    await History.second_vote.set()

@dp.message_handler(state=History.second_vote)
async def answer_q2(message: Message,state=FSMContext):
    await message.answer(text='Еще одна развилка. Выбери путь:', reply_markup=get_kb())
    answer = message.text
    async with state.proxy() as data:
        data['answer1'] = answer
    await History.end.set()

@dp.message_handler(state=History.end)
async def end(message: Message, state: FSMContext):
    answer = message.text
    async with state.proxy() as data:
        data['answer2'] = answer

    data = await state.get_data()
    answer1 = data.get('answer1')
    answer2 = data.get('answer2')
    print(answer1, answer2)
    if answer1 == 'Пойти направо':
        if answer2 == 'Пойти направо':
            await message.answer('Тебе не повезло, тебя съел дракон\nПопробуй еще раз => /start', reply_markup=ReplyKeyboardRemove())
        elif answer2 == 'Пойти налево':
            await message.answer('Ты еле спасся из лап дракона\nПопробуй еще раз => /start', reply_markup=ReplyKeyboardRemove())
    elif answer1 == 'Пойти налево':
        if answer2 == 'Пойти направо':
            await message.answer('Ты нашел сундук золота, поздравляю!', reply_markup=ReplyKeyboardRemove())
        elif answer2 == 'Пойти налево':
            await message.answer('Ты наткнулся на ловушку и склеил ласты\nПопробуй еще раз => /start', reply_markup=ReplyKeyboardRemove())


    await state.finish()
        
@dp.message_handler(commands=['close_game'])
async def close_game(message: Message):
    await message.answer(text='Игра закрыта\nЧтобы начать игру, нажми => /start', reply_markup=ReplyKeyboardRemove())



async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
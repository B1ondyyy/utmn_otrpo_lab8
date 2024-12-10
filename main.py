import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from smtplib import SMTP_SSL
from email.mime.text import MIMEText


class EmailBot:
    def __init__(self, tg_token, smtp_email, smtp_password):
        self.tg_token = tg_token
        self.smtp_email = smtp_email
        self.smtp_password = smtp_password
        self.user_data = {}
        self.bot = Bot(token=self.tg_token)
        self.dispatcher = Dispatcher()

    async def send_email(self, recipient, message):
        """Отправляет сообщение на указанный email через SMTP Яндекса."""
        try:
            with SMTP_SSL("smtp.yandex.ru", 465) as server:
                server.login(self.smtp_email, self.smtp_password)
                email_message = MIMEText(message, "plain")
                email_message["Subject"] = "Сообщение от Telegram-бота"
                email_message["From"] = self.smtp_email
                email_message["To"] = recipient
                server.sendmail(self.smtp_email, recipient, email_message.as_string())
            return "Письмо успешно отправлено!"
        except Exception as e:
            return f"Ошибка при отправке письма: {e}"

    async def handle_start(self, message: types.Message):
        """Обработчик команды /start."""
        await message.answer("Привет! Пожалуйста, укажи свой email для отправки сообщения.")
        self.user_data[message.from_user.id] = {}

    async def handle_email(self, message: types.Message):
        """Обработчик ввода email."""
        user_id = message.from_user.id
        email = message.text.strip()
        if "@" in email and "." in email:
            self.user_data[user_id]["email"] = email
            await message.answer("Email принят! Теперь введи текст сообщения.")
        else:
            await message.answer("Неверный email. Попробуй еще раз.")

    async def handle_message(self, message: types.Message):
        """Обработчик текста сообщения."""
        user_id = message.from_user.id
        if "email" in self.user_data.get(user_id, {}):
            text = message.text.strip()
            recipient = self.user_data[user_id]["email"]
            result = await self.send_email(recipient, text)
            await message.answer(result)
            await message.answer("Если хочешь отправить еще одно письмо, просто укажи новый email.")
            self.user_data[user_id] = {}
        else:
            await message.answer("Сначала укажи email, чтобы отправить сообщение.")

    async def run(self):
        """Запуск бота."""
        self.dispatcher.message.register(self.handle_start, Command("start"))
        self.dispatcher.message.register(self.handle_email, lambda msg: "@" in msg.text and "." in msg.text)
        self.dispatcher.message.register(self.handle_message)

        await self.bot.delete_webhook(drop_pending_updates=True)
        print("Бот запущен!")
        await self.dispatcher.start_polling(self.bot)


async def main():
    # Ввод данных для запуска бота
    print("Настройка бота:")
    tg_token = input("Введите токен Telegram-бота: ").strip()
    smtp_email = input("Введите SMTP email: ").strip()
    smtp_password = input("Введите SMTP пароль: ").strip()

    # Создание и запуск бота
    email_bot = EmailBot(tg_token, smtp_email, smtp_password)
    await email_bot.run()


if __name__ == "__main__":
    asyncio.run(main())
from telethon import events
from .core import build_reply
from .utils import extract_context
from .log import load_log, save_log

def register_handlers(client, group_id):
    @client.on(events.NewMessage(chats=group_id))
    async def handler(event):
        text = event.raw_text.strip()
        lines = text.split("\n")
        if len(lines) < 5:
            return

        context = extract_context(lines)
        log = load_log()
        phone = context.get("phone")

        if phone in log:
            return

        decision = decide_action(context)
        action = decision["action"]
        reply = decision["reply"]

        try:
            if action == "message" and context.get("username"):
                await client.send_message(context["username"], reply)
            elif action == "message_by_phone":
                entity = await client.get_input_entity(phone)
                await client.send_message(entity, reply)
            else:
                print("Ожидание или неполные данные. Ответ не отправлен.")
                return


            log[phone] = True
            save_log(log)
        except Exception as e:
            print(f"[Ошибка отправки]: {e}")

@client.on(events.NewMessage(incoming=True))
async def on_response(event):
    sender = await event.get_sender()
    message_text = event.raw_text.lower().strip()

    # Простой фильтр: реагируем только на личные ответы (не группы)
    if event.is_private:
        # Простейшая логика — ответ содержит согласие
        if message_text in ["да", "+", "конечно", "согласен", "верно", "готов"]:
            await event.reply("Супер! Для знакомства давай проведем небольшой созвон, чтобы я мог немного рассказать тебе о работе.\nПодскажи, пожалуйста, актуальный ли у тебя номер телефона — если всё верно, я наберу тебя в течение минуты. Мой номер будет начинаться на +1.")
        else:
            await event.reply("Спасибо за ответ! Можешь уточнить, ты готов к короткому звонку или предпочитаешь пока переписку?")
            

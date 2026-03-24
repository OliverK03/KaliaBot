from telegram import Update
from telegram.ext import ContextTypes
from config.settings import BOT_USERNAME


# Response Handler
async def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'kalia' in processed:
        return 'juo lissää'
    if 'kalja' in processed:
        return 'opettelee kirjottaa'
    # varsinkin mutterille
    if 'hoploppi' in processed:
        return 'ei oo mikää vitun hoploppi!'
    
    return 'juo kaliaaa'
    
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type in ('group', 'supergroup'):
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = await handle_response(new_text)
        else:
            return
        
    else:
        response: str = await handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)
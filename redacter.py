import asyncio
import os
import time

import dotenv
from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import clear
from prompt_toolkit.validation import Validator
from telethon import TelegramClient

if not dotenv.load_dotenv():
    raise RuntimeError('Could not load .env file')

APP_ID = int(os.getenv('APP_ID'))
API_HASH = str(os.getenv('API_HASH'))

client = TelegramClient('anon', APP_ID, API_HASH)

ps = PromptSession()

page_size = 10
page = 0

class PageValidator(Validator):
    def __init__(self, count):
        self.count = count

    def validate(self, document):
        global page
        text = document.text
        if text == 'n':
            if page*page_size+page_size < self.count:
                page += 1
        elif text == 'p':
            if page > 0:
                page -= 1
        elif not text.strip().isdigit():
            with open('tmp.txt', 'w') as f:
                f.write(f'text {text} {text.isdigit()} {text in list(range(page_size))}')
            raise ValueError('Please enter a number or n/p')


NL = '\n'

async def prompt_app():

    print("Getting chats...")
    chats = await client.get_dialogs()

    while True:
        content = f'''Here are your chats ({page * page_size}-{page * page_size + page_size}):

{(lambda x: NL.join(f'{i}: {y.name}' for i, y in enumerate(x)))(chats[page * page_size:page * page_size + page_size])}

Page {page} of {len(chats) // page_size}
n: next page
p: previous page
{len(chats)} chats total

Select a chat: '''
        clear()
        chat_index = await ps.prompt_async(
            content,
            validator=PageValidator(len(chats)),
            validate_while_typing=False
        )
        if chat_index.isdigit():
            break
    chat = chats[int(chat_index)]

    await ps.prompt_async(f'You selected {chat.name}. Press enter to continue, or Ctrl-C to exit...', validator=Validator.from_callable(lambda x: x == '', error_message='Please press enter to continue...'))
    message_count = int(await ps.prompt_async('How many messages to delete? (0 for all) [0]: ', validator=Validator.from_callable(lambda x: x.isdigit() or not x, error_message='Please enter a number')) or 0)

    print(f'Getting {message_count if message_count else "all"} messages from {chat.name}...')
    kwargs = {
        'from_user': 'me'
    }
    if message_count:
        kwargs['limit'] = message_count

    delete_requests = []
    async for message in client.iter_messages(chat.id, **kwargs):
        print(f'{message.date}: {message.message if message.message else "[media or other content]"}')
        delete_requests.append(message.delete())
    print(f'You are about to delete {len(delete_requests)} messages.')
    res = await ps.prompt_async('Continue? [y/N]: ', validator=Validator.from_callable(lambda x: x.lower() in ['y', 'n', ''], error_message='Please enter y or n'))
    if res.lower() != 'y':
        print('Aborting...')
        for req in delete_requests:
            req.close()
        return
    print(f'Deleting {len(delete_requests)} messages...')
    # If there are more than 100 messages, we need to delete them in batches of 100
    if len(delete_requests) > 100:
        print('Deleting in batches of 100...')
        for i in range(0, len(delete_requests), 100):
            await asyncio.gather(*delete_requests[i:min(i+100, len(delete_requests))])
            print(f'Deleted {min(i+100, len(delete_requests))} messages...')
            await asyncio.sleep(0.5)
    else:
        await asyncio.gather(*delete_requests)
    print('Done!')


def main():
    with client:
        client.loop.run_until_complete(prompt_app())


if __name__ == '__main__':
    main()

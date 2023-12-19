# TelethonRedacter

A simple script to delete sent messages from a Telegram chat using [Telethon](https://github.com/LonamiWebs/Telethon)

## Prerequisites

- Python 3 (Only tested with Python 3.9.2)

## Usage

1. Create a `.env` file with the following contents:
    ```
    APP_ID=<your api id>
    API_HASH=<your api hash>
    ```
    You can get your app id and api hash from [here](https://my.telegram.org/apps).

2. Install the requirements: `pip install -r requirements.txt`
3. Run the script: `python redacter.py`
4. The first time you run the script, it will ask you to enter your phone number and the code you received on Telegram. This will get automatically saved to `anon.session` so you don't have to enter it again.
5. A paged list of your chats will be shown. Select the chat you want to delete messages from. You can use n/p to navigate between pages.
6. Enter the amount of messages you want to delete. The messages will be ordered from earliest to latest and a preview of the message will be shown before deleting it. You can enter `0` to delete all messages.
7. The script will start deleting the messages. This action cannot be undone.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
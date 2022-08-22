# ✉️📮 - PostCardBot - 📬🏠

> `PostCardBot` is a Telegram bot, that provided simple postcard serivce for Telegram users. Select postcard and share with your friedns. Easy right? 😉


## **Running PostCardBot**

### Step 1: **Create Telegram bot 🤖**
1. Create Telegram bot using [Telegram BotFather](https://telegram.me/botfather).
2. Save bot token.

### Step 2: **Download PostCardBot 💾**
1. Clone repository to your local machine.
```bash
git clone git@github.com:backostech/PostCardBot.git
```
2. Change directory to `PostCardBot`
```bash
cd PostCardBot
```

### Step 3: **Install requirements 🔩**
1. Install [Python](https://www.python.org/downloads/).
2. Install required packages.
```bash
pip install -r requirements.txt
```
> If you want to install PostCardBot on virtualenv, run  `pip install -e .`

### Step 4: **Prepare PostCardBot configuration 🔩**
1. Rename .env.sample to .env
```bash
mv .env.sample .env
```
2. Write your bot token in .env file next to API_TOKEN= and save it.
```ini
# .env file

API_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
```

### Step 5: **Configure Database 🗄**
1. Create MongoDB cluster from [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. Create dns link to MongoDB cluster.
3. Write dns link to database in .env file next to `DATABASE_URL`= and save it.
```ini
# .env file

DATABASE_URL=mongodb+srv://user:<password>@cluster0-xxxx.mongodb.net/database
```
4. Write your database name in .env file next to `DATABASE_NAME=` and save it.
```ini
# .env file

DATABASE_NAME=postcardbot
```

### Step 5: **Configure logging 📋**
1. Create log directory called `logs` in parent directory (back one level).
```bash
mkdir ../logs
```
2. Write log file name in .env file next to `LOG_FILE_NAME=` and save it.
```ini
# .env file

LOG_FILE_NAME=postcardbot.log
```
4. Write your notifier name in .env file next to NOTIFIER= and save it (for example: `NOTIFIER=gmail`).
```ini
# .env file

NOTIFIER=gmail
```
4. Write your notifier email in .env file next to `NOTIFIER_EMAIL=` and save it.
```ini
# .env file

NOFIER_EMAIL=example@mail.com
````
5. Write your notifier password in .env file next to `NOTIFIER_PASSWORD=` and save it.
```ini
# .env file

NOTIFIER_PASSWORD=examplepassword
```
6. Write your notification recipient email in .env file next to `NOTIFICATION_RECIPIENT=` and save it.
```ini
# .env file

NOTIFICATION_RECIPIENT=recipientemail@mail.com
```

> **Note:** Minimum configuration must look like this:
```ini
# .env file

API_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
DATABASE_URL=mongodb+srv://user:<password>@cluster0-xxxx.mongodb.net/database
DATABASE_NAME=postcardbot
LOG_FILE_NAME=postcardbot.log
NOTIFIER=gmail
NOFIER_EMAIL=example@mail.com
NOTIFIER_PASSWORD=examplepassword
NOTIFICATION_RECIPIENT=recipientemail@mail.com
```

### Step 6: **Run PostCardBot 🚀**
1. Run PostCardBot.
```bash
python3 -m PostCardBot
```

### **Available configuration options 🔧**
- `API_TOKEN` - Telegram bot token.
- `DATABASE_URL` - MongoDB dns link.
- `DATABASE_NAME` - MongoDB database name.
- `LOG_FILE_NAME` - Log file name.
- `NOTIFIER` - Notifier name.
- `NOTIFIER_EMAIL` - Notifier email.
- `NOTIFIER_PASSWORD` - Notifier password.
- `NOTIFICATION_RECIPIENT` - Notification recipient email.
- `LOG_ROTATION_SIZE` - Log rotation size.
- `DATABASE_SELECTION_TIMEOUT` - Database selection timeout. Default: 10 seconds.

## **License**
<!-- Apache -->
<a href="https://www.apache.org/licenses/LICENSE-2.0">Apache License 2.0" </a>


## **Brought to you by**

<p align="center">
  <img width="150" height="150" src="https://www.backostech.com/wp-content/uploads/2022/08/cropped-BackosLogo.png">
  <h1 align="center"><a href="https://backostech.com">𝔹𝕒𝕔𝕜𝕠𝕤 𝕋𝕖𝕔𝕙𝕟𝕠𝕝𝕠𝕘𝕚𝕖𝕤</a></h1>

  ```
                                                ᴀ ᴛᴇᴄʜ ʏᴏᴜ ᴄᴀɴ ᴛʀᴜsᴛ
  ```
</p>


Build with [aiogram](https://github.com/aiogram/aiogram).

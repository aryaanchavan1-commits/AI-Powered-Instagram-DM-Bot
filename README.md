# AI-Powered Instagram DM Bot

A fully-featured Instagram DM automation bot with AI-powered replies using Groq API, built with Streamlit for an easy-to-use web interface.

## Features

- 🔐 **User Authentication**: Secure login system with password hashing
- 📱 **Instagram Login**: Full Instagram integration with 2FA and captcha handling
- 🤖 **AI-Powered Replies**: Uses Groq API (Llama 3) for intelligent message responses
- 💬 **Message Storage**: All conversations saved to `user_messages.json`
- 📊 **Dashboard**: Beautiful Streamlit interface for managing everything
- ⚙️ **Customizable Settings**: Language, default messages, auto-reply toggle
- 📜 **History Tracking**: Complete history of all bot activities
- 👥 **Group Message Support**: Option to reply to group messages
- 🔄 **Real-time Monitoring**: Live bot status and conversation tracking

## Installation

### Prerequisites

- Python 3.8 or higher
- Groq API key (Get from https://console.groq.com/)

### Step 1: Clone the repository

```bash
git clone https://github.com/aryaanchavan1-commits/AI-Powered-Instagram-DM-Bot.git
cd AI-Powered-Instagram-DM-Bot
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set up environment variables

Copy the example environment file and add your Groq API key:

```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:

```
GROQ_API_KEY=your_actual_groq_api_key_here
```

### Step 4: Run the application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Usage

### First Time Setup

1. **Register**: Create a new account using the Register tab
2. **Login**: Login with your credentials
3. **Configure Instagram**: Go to "Instagram Login" and enter your Instagram credentials
4. **Set Groq API Key**: Go to "Settings" and enter your Groq API key
5. **Configure Bot**: Set your preferred language, default message, and other settings
6. **Start Bot**: Go to "Bot Control" and click "Start Bot"

### Dashboard Overview

- **Dashboard**: View bot status, recent activity, and statistics
- **Instagram Login**: Connect/disconnect your Instagram account
- **Settings**: Configure Groq API, language, default messages, and more
- **Messages**: View all saved conversations and AI replies
- **History**: Complete history of all bot activities
- **Bot Control**: Start/stop the bot and monitor its status

### Settings Explained

- **Groq API Key**: Your API key from Groq for AI-powered replies
- **Language**: The language the AI will use for replies
- **Default Message**: A fixed message to send instead of AI-generated replies (leave empty for AI)
- **Auto Reply**: Enable/disable automatic replies
- **Group Messages**: Enable/disable replies to group messages

### Handling 2FA and Captchas

The bot automatically handles:
- **2FA**: When Instagram requires two-factor authentication, you'll be prompted to enter the verification code
- **Captchas**: If Instagram shows a captcha, you'll need to complete it manually in your browser

## File Structure

```
AI-Powered-Instagram-DM-Bot/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .env                     # Your environment variables (create this)
├── config.json              # Legacy configuration file
├── user_messages.json       # Message storage (auto-created)
├── users.json               # User database (auto-created)
├── wezaxy/
│   ├── __init__.py
│   ├── groq_ai.py          # Groq API integration
│   ├── message_storage.py  # Message storage system
│   ├── user_db.py          # User database management
│   ├── login.py            # Instagram login with 2FA support
│   ├── sendmessage.py      # Message sending functionality
│   ├── ai.py               # Legacy AI module
│   ├── test.py             # Legacy test module
│   └── Authorization.json  # Instagram auth token storage
├── proxies.txt              # Proxy list (optional)
├── README.md               # This file
└── LICENSE                 # License file
```

## API Keys

### Groq API Key

1. Go to https://console.groq.com/
2. Create an account or login
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file or in the Settings page

## Troubleshooting

### Bot not responding

1. Check if Instagram is connected (Dashboard shows status)
2. Verify Groq API key is set correctly
3. Check bot status in Bot Control page
4. Review History for any error messages

### Instagram login fails

1. Verify your Instagram credentials are correct
2. If 2FA is enabled, enter the verification code when prompted
3. If captcha appears, complete it in your browser
4. Try again after a few minutes if rate limited

### Messages not being saved

1. Check if `user_messages.json` file exists
2. Verify file permissions
3. Check History for any error messages

## Security Notes

- Passwords are hashed using bcrypt
- Instagram credentials are stored locally
- API keys are stored in environment variables
- All data is stored locally on your machine

## Legal Disclaimer

This bot is for educational purposes only. Use it responsibly and in accordance with Instagram's Terms of Service. The developers are not responsible for any misuse or account restrictions.

## Support

For issues and questions, please check the troubleshooting section or create an issue in the repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## contact

Instagram = codieryan_version

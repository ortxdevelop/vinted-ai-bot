# Vinted AI Telegram Bot

A Telegram bot that automates **searching and filtering items on Vinted** with:
- 🔎 On-demand and scheduled searches  
- 🤖 AI-based clothing recognition (FastAI Vision)  
- 💬 Telegram integration for instant alerts  
- 📂 JSON-based storage of seen items and schedules

---

## Demo
![demo-gif](https://github.com/user-attachments/assets/4ba99247-2a08-4afe-86c1-a61e7d5bb1a5)

---

## Features
- **Telegram commands**:
  - `/search` start a manual search
  - `/settime HH:MM ...` set schedule times
  - `/clear` clear the seen items list
- **Keyboard shortcuts** for easy interaction (`🔎Search`, `🗑️Clear seen.json`, `🕑Set schedule`)
- **Scheduled searches** with automatic checks
- **AI-powered filtering** with a custom FastAI model
- **Persistent storage** of seen items and schedules
- **Access control**: only allowed users can trigger main actions
- **Bypass Vinted blocks**: Unlike direct `requests` (which often return 403 Forbidden), this bot uses a real browser session with your logged-in account to reliably fetch items
---
## Tech Overview

### Highlights
- 💬 **Telegram Bot Automation**: On-demand and scheduled searches
- 🌐 **Robust Data Access**: Reliable scraping and API calls from Vinted
- 🕵️ **Selenium Integration**: Uses undetected_chromedriver for stealth sessions
- 📡 **HTTP Requests**: Fetches JSON data efficiently
- 🤖 **AI Clothing Detection**: FastAI model for image classification
- 💾 **Persistence**: Stores user and schedule data in JSON
  
### Tech Stack
- 🐍 [Python 3.10+](https://www.python.org/)
- 💬 [Aiogram](https://docs.aiogram.dev/) - Telegram bot framework  
- 🌐 [Selenium](https://www.selenium.dev/) + [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) - bypass anti-bot  
- 🤖 [FastAI](https://docs.fast.ai) - vision model for clothing recognition  
- 📡 [Requests](https://docs.python-requests.org/) - API calls  

---

## Setup

To use this bot, you need to set up your environment, Chrome profile, and Vinted account session

### 1. Clone the repository and install dependencies

```bash
git clone https://github.com/ortxdevelop/vinted-ai-bot.git
cd vinted-ai-bot
pip install -r requirements.txt
```

### 2. Configure your Chrome profile

The bot uses undetected_chromedriver with your Chrome profile to stay logged in to Vinted.

- Open Chrome and create a new profile (or use an existing one).
- Set it up in config file, e.g.: `CHROME_PROFILE = r'--user-data-dir=C:\Users\user\AppData\Local\Google\Chrome\User Data\Profile x'`

- Run script `account.py` and log in into your Vinted account.

### 3. Set all constants in `config.py` file

### 4. Run the `main.py` script
```bash
python main.py
```
---

## Training the AI Model

The bot uses a custom **FastAI vision model** to recognize specific types of clothing.  
You can train (or retrain) the model on your own dataset.

### 1. Prepare your dataset
- Create a folder called `dataset/`
- Inside, create subfolders for each class (e.g. `big_pony`, `other`)
- Put images in the corresponding folders:
```
dataset/
├── big_pony/
│ ├── img1.jpg
│ ├── img2.jpg
├── other/
├── img1.jpg
├── img2.jpg
```
### 2. Train the model
Run the training script:

```bash
python train.py
```
**This will:**
- Build a FastAI DataBlock with augmentation and normalization
- Train a `ResNet34` backbone with transfer learning
- Use both fine-tuning of the head and full unfreezing of the model
- Apply TTA (Test-Time Augmentation) for evaluation
- Save the trained model as `big_pony_model.pkl`

### 3. Using the trained model

The exported model (`big_pony_model.pkl`) is used by the bot to classify clothing items fetched from Vinted.
Place the file in the project root or specify the path in your bot configuration

---

## Contact
Created by [ortxdevelop](https://github.com/ortxdevelop)  
For questions or support, please open an issue on GitHub

---

**Thank you for checking out this project!** 👾

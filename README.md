# Discord-Bulk-Message-Cleaner
Project Discription
Discord Bulk Message Deleter

A modern, fast, and user-friendly desktop application built with Python and Tkinter for searching and bulk deleting your messages across Discord servers and Direct Messages (DMs).
✨ Features

    Custom Dark Theme UI: Custom-built Tkinter interface designed to match Discord's native dark palette.

    Server & Channel Bulk Cleaning: Target specific servers and select individual text/announcement channels to clean.

    Direct Messages (DMs) Cleaning: Search and delete messages across single and group DMs.

    Adaptive Rate Limiting: Smart API back-off and acceleration to handle Discord's rate limits safely.

    Real-time Progress Tracker: Animated progress bar, deletion counter, speed tracker, and estimated time remaining (ETA).

    Detailed Logs: Live feed showing message content snippets, success checks, and failure warnings.

🛠️ Prerequisites

    Python 3.8 or higher installed on your system.

    Required Python libraries (requests, Pillow).

🚀 Getting Started
1. Clone the Repository
Bash

git clone https://github.com/your-username/Discord-Bulk-Message-Cleaner.git
cd Discord-Bulk-Message-Cleaner

2. Install Dependencies

Install the required packages using pip:
Bash

pip install requests pillow

3. Run the Application
Bash

python discord_cleaner.py

🔑 How to Get Your Discord Token

To log into the app, you will need your Discord account User Token[cite: 1].

    Open Discord in your web browser (discord.com/app)[cite: 1].

    Press F12 (or Ctrl + Shift + I) to open Developer Tools[cite: 1].

    Go to the Network tab, then press Ctrl + R to reload[cite: 1].

    Click any network request on the list and navigate to the Headers tab[cite: 1].

    Scroll down to find Authorization: and copy the string value[cite: 1].

    Paste the token into the application login screen[cite: 1].

    🔒 Security Notice:
    Never share your token with anyone[cite: 1]! Your token gives full access to your account[cite: 1]. The token is only used locally by this application to interact directly with Discord's API[cite: 1].

📖 How to Use

    Log In: Paste your user token and click Log In[cite: 1].

    Select Target:

        Servers Tab: Choose a server, then check the channels you wish to scan[cite: 1].

        Direct Messages Tab: Check the DMs or group chats you want to clean[cite: 1].

    Scan: Click 🔍 Scan Selected to fetch your sent messages[cite: 1].

    Delete: Review the found message count and click 🗑️ Delete All Found[cite: 1].

⚠️ Disclaimer & Terms of Service Notice

Using self-bots or automated user-token scripts interacts with Discord's API outside official bot endpoints. Use this tool responsibly. The developer assumes no responsibility for any account restrictions, rate limits, or bans resulting from the misuse of this tool.
📜 License

This project is licensed under the MIT License — see the LICENSE file for details.

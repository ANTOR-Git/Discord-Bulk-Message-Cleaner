# Discord Bulk Message Deleter

A modern, fast, and user-friendly desktop application for searching and bulk deleting your messages across Discord servers and Direct Messages (DMs).


[![Download Button](https://img.shields.io/badge/Direct_Download-Click_Here-success?style=for-the-badge&logo=github)](https://github.com/ANTOR-Git/Discord-Bulk-Message-Cleaner/releases/latest)
---

## ✨ Features

* **Custom Dark Theme UI**: Custom-built interface designed to match Discord's native dark palette.
* **Server & Channel Bulk Cleaning**: Target specific servers and select individual text/announcement channels to clean.
* **Direct Messages (DMs) Cleaning**: Search and delete messages across single and group DMs.
* **Adaptive Rate Limiting**: Smart API back-off and acceleration to handle Discord's rate limits safely.
* **Real-time Progress Tracker**: Animated progress bar, deletion counter, speed tracker, and estimated time remaining (ETA).
* **Detailed Logs**: Live feed showing message content snippets, success checks, and failure warnings.

---

## 🚀 Getting Started

1. Go to the **[Releases](../../releases)** section on the right side of this repository.
2. Download the latest `.exe` file (e.g., `Discord-Bulk-Message-Cleaner.exe`).
3. Double-click the file to launch the application — **no installation or Python required!**

---

## 🔑 How to Get Your Discord Token

To log into the app, you will need your Discord account User Token.

1. Open Discord in your web browser ([discord.com/app](https://discord.com/app)).
2. Press `F12` (or `Ctrl + Shift + I`) to open Developer Tools.
3. Go to the **Network** tab, then press `Ctrl + R` to reload.
4. Click any network request on the list and navigate to the **Headers** tab.
5. Scroll down to find `Authorization:` and copy the string value.
6. Paste the token into the application login screen.

> **🔒 Security Notice:**
> Never share your token with anyone! Your token gives full access to your account. The token is only used locally by this application to interact directly with Discord's API.

---

## 📖 How to Use

1. **Log In**: Paste your user token and click **Log In**.
2. **Select Target**:
   * **Servers Tab**: Choose a server, then check the channels you wish to scan.
   * **Direct Messages Tab**: Check the DMs or group chats you want to clean.
3. **Scan**: Click **🔍 Scan Selected** to fetch your sent messages.
4. **Delete**: Review the found message count and click **🗑️ Delete All Found**.

---

## ⚠️ Disclaimer & Terms of Service Notice

Using self-bots or automated user-token scripts interacts with Discord's API outside official bot endpoints. Use this tool responsibly. The developer assumes no responsibility for any account restrictions, rate limits, or bans resulting from the misuse of this tool.

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

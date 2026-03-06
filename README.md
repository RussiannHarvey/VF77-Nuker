VF77 Nuker
<p align="center"> <img src="https://img.shields.io/badge/Python-3.8%2B-blue"> <img src="https://img.shields.io/badge/Discord%20API-v10-brightgreen"> <img src="https://img.shields.io/badge/Async-aiohttp-orange"> <img src="https://img.shields.io/badge/License-MIT-red"> </p><p align="center"> <b>A high‑speed, asynchronous Discord server nuker with a stylish CLI interface.<br> Designed for maximum performance and ease of use.</b> </p>
🔥 Features
24 destructive commands – ban, kick, unban, channel/role nuking, webhook spam, mass DM, server settings, and more.

Fully asynchronous – powered by aiohttp and asyncio for lightning‑fast requests.

Smart rate‑limit handling – automatically respects Discord’s rate limits and retries when needed.

Parallel execution – fine‑tuned concurrency for each command to avoid hitting limits.

Webhook spammer – creates webhooks on every text channel and spams messages in parallel.

Proxy support – optional proxy rotation (HTTP/HTTPS/SOCKS) to bypass IP‑based restrictions.

Beautiful ASCII banner – eye‑catching gradient design.

Clean console output – colour‑coded logs (green for success, red for failure) with timestamps.

Optimised TCP connector – DNS caching, connection reuse, and high concurrency settings.

🛠️ Available Commands
Command	Description
01	Ban all members (except the bot)
02	Kick all members (except the bot)
03	Unban everyone
04	Create text channels
05	Create voice channels
06	Create categories
07	Delete all channels
08	Create new roles
09	Display server information
10	Mass‑ping (send messages to random text channels)
11	Rename all channels
12	Grant administrator permissions to the @everyone role
13	Rename all members
14	Delete all emojis
15	Delete all stickers
16	Delete vanity URL
17	Webhook spammer (creates webhooks on every text channel and sends bulk messages)
18	Change server name
19	Delete all invites
20	Pause all invites
21	Disable auto‑moderation
22	Disable community features
23	Enable community features
0x90	Full server nuke (ban all → delete all channels → create 200 channels → spam 2000 messages)
0	Shut down the program
📋 Requirements
Python 3.8 or higher

Required packages:

aiohttp

colorama

aiohttp_socks (optional, for SOCKS5 proxy support)

Install them with:

bash
pip install aiohttp colorama aiohttp_socks
🚀 Installation & Usage
Clone or download this repository.

Install dependencies (see above).

Run the script:

bash
python vf77.py
Choose whether to enable proxies (optional – you need a proxies.txt file).

Enter your bot token and the target guild ID.

Select a command from the menu by typing its number (e.g., 01, 17, 0x90).

⚠️ The bot must have the necessary permissions in the target server (e.g., Ban Members, Manage Channels, Manage Roles, etc.) depending on the command.

🔧 Proxy Support (Optional)
To use proxies, create a file named proxies.txt in the same directory, with one proxy per line in any of these formats:

text
http://user:pass@ip:port
http://ip:port
socks5://user:pass@ip:port
socks5://ip:port
socks4://ip:port
When prompted, answer y to enable proxy mode. VF77 will rotate proxies automatically and mark failed ones.

📦 Compiling to EXE (Windows)
To create a standalone Windows executable (no Python required), use PyInstaller:

bash
pip install pyinstaller
pyinstaller --onefile --console --name "VF77_Nuker" vf77.py
The executable will be placed in the dist folder.

Note: Some antivirus programs may flag the generated .exe as a false positive due to its network activity. This is normal for tools that send many HTTP requests.

⚠️ Disclaimer
This tool is intended for educational purposes only.

Using it against servers you do not own is strictly prohibited and violates Discord's Terms of Service.

The author is not responsible for any misuse or damage caused by this program.

📄 License
This project is open source under the MIT License.
Feel free to modify, distribute, and use it within the bounds of the law and Discord's ToS.

💬 Support & Contributions
Found a bug? Want a new feature? Open an issue or submit a pull request.
All contributions are welcome!
discord username : russianharvey

<p align="center"> Made with ❤️ by <b>RussianHarvey</b> </p>

<img width="1395" height="693" alt="Screenshot 2026-03-07 004929" src="https://github.com/user-attachments/assets/4b44523d-0807-432e-9bc9-7199c85eacab" />

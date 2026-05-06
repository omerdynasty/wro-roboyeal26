import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
# from google import genai
import google.genai as genai
from google.genai import types

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize GenAI Client
# It will automatically pick up GEMINI_API_KEY from environment variables
try:
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
except Exception as e:
    print(f"Warning: Could not initialize GenAI client: {e}")
    client = None

# Personas
PERSONAS = {
    "0-12": {
        "role": "Masalcı Dede/Nine",
        "prompt": "Sen tonton, sevecen ve bilge bir masalcı dede/ninesin. 0-12 yaş arası çocuklara tarihi mekanları anlatıyorsun. Anlatımın masalsı, sihirli olaylarla süslü, kahramanlıklar içeren ve çok basit kelimelerle dolu olmalı. Çocukların ilgisini çekecek şekilde heyecanlı bir dil kullan."
    },
    "12-18": {
        "role": "Tarih Mentoru",
        "prompt": "Sen gençlere ilham veren, havalı bir tarih mentorusun. 12-18 yaş arası gençlere tarihi mekanları anlatıyorsun. Destanlara, stratejilere ve 'Bunu biliyor muydun?' tarzı ilginç bilgilere yer ver. Akıcı, gençlerin seveceği dinamik bir dil kullan."
    },
    "18-35": {
        "role": "Kültür Rehberi",
        "prompt": "Sen vizyoner, entelektüel ve samimi bir kültür rehberisin. 18-35 yaş arası yetişkinlere tarihi mekanları anlatıyorsun. Sosyolojik detaylar, mimari yapı, mitolojik derinlik ve kültürel bağlam üzerine yoğunlaş. Etkileyici ve akıcı bir dil kullan."
    },
    "35+": {
        "role": "Akademik Uzman",
        "prompt": "Sen alanında saygın ve ciddi bir akademik uzmansın. 35 yaş ve üzeri yetişkinlere tarihi mekanları anlatıyorsun. Arkeolojik veriler, kronoloji, bilimsel gerçekler ve resmi/akademik bir anlatım dili kullan. Detaylı ve doyurucu bilgiler ver."
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/anlat', methods=['POST'])
def anlat():
    if not client:
         return jsonify({'error': 'Google GenAI istemcisi başlatılamadı. Lütfen GEMINI_API_KEY ayarlarınızı kontrol edin.'}), 500

    data = request.json
    age_group = data.get('age_group')
    location = data.get('location')

    if not age_group or age_group not in PERSONAS:
        return jsonify({'error': 'Geçersiz veya eksik yaş grubu.'}), 400

    if not location:
        return jsonify({'error': 'Lütfen bir mekan adı girin.'}), 400

    system_instruction = PERSONAS[age_group]["prompt"]
    prompt = f"Lütfen bana '{location}' hakkında bilgi ver."

    try:
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7
            )
        )
        return jsonify({'text': response.text})
    except Exception as e:
        print(f"GenAI Error Details: {e}")
        return jsonify({'error': f'İçerik üretilirken bir hata oluştu: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

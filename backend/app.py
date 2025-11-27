from flask import Flask, request, jsonify
from .profile import Profile
from . import algorithm

app = Flask(__name__)

@app.route('/get-council', methods=['POST'])
def get_council():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Необхідно надати JSON з даними заявника (application_data)."}), 400
    
    # підготовка даних до передачі в метод form_council()
    amount = data.get('amount', 5)  
    key = data.get('key', 0)
    specialty = data.get('specialty_id', "01.01.01")
    keywords = data.get('keywords', [])

    app_profile = Profile("application-profile", specialty, keywords)

    try:
        council = algorithm.form_council(app_profile, amount, key=key)
        res_list = [cand.orcid for cand in council]
        return jsonify({"orcid_list": res_list}), 200
    except Exception as e:
        # обробка помилок
        print(f"Помилка під час обробки запиту: {e}")
        return jsonify({"error": "Внутрішня помилка сервера.", "details": str(e)}), 500

if __name__ == '__main__':
    # запуск сервера на локальному хості та порту 5000
    app.run(debug=True, port=5000)
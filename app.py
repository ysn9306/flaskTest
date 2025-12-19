from flask import Flask, render_template, request
from bmi import BMICalculator
from db import Database
import os

app = Flask(__name__)

# DB는 필요할 때만 생성
def get_db():
    return Database()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        weight = float(request.form['weight'])
        height = float(request.form['height'])

        if weight <= 0 or height <= 0:
            return render_template('index.html', error="체중과 신장은 양수여야 합니다.")

        calculator = BMICalculator(weight, height)
        result = calculator.get_result()

        # DB 저장 (실패해도 페이지는 뜨게)
        try:
            db = get_db()
            db.save_bmi_record(weight, height, result["bmi"], result["category"])
            db.close()
        except Exception as e:
            print("DB 저장 실패:", e)

        return render_template(
            'result.html',
            bmi=result["bmi"],
            category=result["category"],
            weight=weight,
            height=height
        )

    except ValueError:
        return render_template('index.html', error="유효한 숫자를 입력해주세요.")

@app.route('/history')
def history():
    try:
        db = get_db()
        records = db.get_bmi_records(10)
        db.close()
    except Exception as e:
        print("DB 조회 실패:", e)
        records = []

    return render_template('history.html', records=records)

# ❌ app.run 제거 (Cloudtype는 gunicorn 사용)

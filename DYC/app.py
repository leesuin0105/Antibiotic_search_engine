from flask import Flask, render_template, request, jsonify, url_for, redirect
import pandas as pd
import random

app = Flask(__name__)

# 엑셀 파일 로드 (데이터프레임으로 변환)
file_path = "D:/Programming/Jupyter/02.data/데청캠/진단명리스트.csv"
df = pd.read_csv(file_path)

# 엑셀 파일 로드 (약품 정보 데이터프레임으로 변환)
medicine_file_path = r"D:/Programming/Jupyter/02.data/데청캠/약순위.xlsx"
medicine_df = pd.read_excel(medicine_file_path)

# 퀴즈 데이터를 저장할 리스트
quiz_data = []

# 데이터프레임을 불러옵니다.
quiz_data_df = pd.read_excel(r"D:/Programming/Jupyter/02.data/데청캠/퀴즈정리데이터.xlsx")

# 중복 데이터 제거
quiz_data_df = quiz_data_df.drop_duplicates()

def generate_random_quiz():
    # 데이터프레임에서 무작위로 하나의 행 선택
    random_row = quiz_data_df.sample(1)
    
    # 질문 및 정답 생성
    category = random.choice(['약품명', '진단명(한국어)', '성분명'])  # 랜덤으로 문제 유형 선택
    
    if category == '약품명':
        diagnosis_korean = random_row['진단명(한국어)'].values[0]  # 진단명(한국어)을 가져옵니다.
        question_text = f"다음 [{diagnosis_korean}]에 해당하는 약품명을 선택하세요: "
        question_value = random_row['약품명'].values[0]
        options = [question_value]
        
        # 랜덤하게 3개의 오답 추가 (오답은 약품명으로)
        while len(options) < 4:
            random_option = random.choice(quiz_data_df['약품명'].unique())
            
            if random_option != question_value and random_option not in options:
                options.append(random_option)
    
    elif category == '진단명(한국어)':
        diagnosis_korean1 = random_row['증상 키워드'].values[0]  #증상 키워드
        question_text = f"[{diagnosis_korean1}]에 해당하는 진단명을 선택하세요:"
        question_value = random_row['진단명(한국어)'].values[0]
        options = [question_value]
        
        # 랜덤하게 3개의 오답 추가 (오답은 진단명(한국어)로)
        while len(options) < 4:
            random_option = random.choice(quiz_data_df['진단명(한국어)'].unique())
            
            if random_option != question_value and random_option not in options:
                options.append(random_option)
    
    elif category == '성분명':
        diagnosis_korean2 = random_row['약품명'].values[0]  # 진단명(한국어)을 가져옵니다.
        question_text = f"다음 [{diagnosis_korean2}]에 해당하는 성분명을 선택하세요:"
        question_value = random_row['성분명'].values[0]
        options = [question_value]
        
        # 랜덤하게 3개의 오답 추가 (오답은 성분명으로)
        while len(options) < 4:
            random_option = random.choice(quiz_data_df['성분명'].unique())
            
            if random_option != question_value and random_option not in options:
                options.append(random_option)
    
    random.shuffle(options)  # 옵션을 섞습니다.
    
    # 정답 옵션의 인덱스 찾기
    correct_index = options.index(question_value)
    
    question = f"{question_text}"  # 문제 형식 수정
    
    return question, options, correct_index

# 초기 퀴즈 데이터 생성
for _ in range(100):  # 100개의 초기 퀴즈를 생성합니다. (원하는 개수로 수정 가능)
    quiz_data.append(generate_random_quiz())

# 현재 퀴즈 인덱스를 추적합니다.
current_quiz_index = 0

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search', methods=['POST'])
def search():
    search_symptom = request.form['symptom']

    filtered_data = df[df['증상 키워드'].str.contains(search_symptom, case=False, na=False)]

    diagnosis_korean_with_count = filtered_data[['진단명(한국어)', '카운트']]
    diagnosis_korean_with_count_json = diagnosis_korean_with_count.to_dict(orient='records')

    return jsonify(diagnosis_korean_with_count_json)

@app.route('/result')
def result():
    diagnosis = request.args.get('diagnosis')

    filtered_data = df[df['증상 키워드'].str.contains(diagnosis, case=False, na=False)]

    diagnosis_results = filtered_data[['진단명(한국어)', '카운트']].to_dict(orient='records')

    return render_template('result.html', diagnosis=diagnosis, diagnosis_results=diagnosis_results)

@app.route('/medicine/<diagnosis>')
def show_medicine(diagnosis):
    result = medicine_df[medicine_df['진단명(한국어)'] == diagnosis]
    
    medicine_results = result[['진단명(한국어)', '약품명', '개수']].to_dict(orient='records')

    return render_template('medicine.html', diagnosis=diagnosis, medicine_results=medicine_results)

@app.route('/quiz')
def quiz():
    global current_quiz_index
    num_questions_to_show = 4  # 4개의 문제를 보여줍니다.
    
    if current_quiz_index + num_questions_to_show <= len(quiz_data):
        current_quizzes = quiz_data[current_quiz_index:current_quiz_index + num_questions_to_show]
    else:
        # 수정: 새로운 문제 생성하여 quiz_data에 추가
        for _ in range(num_questions_to_show):
            quiz_data.append(generate_random_quiz())
        current_quizzes = quiz_data[current_quiz_index:]
    
    # 현재 퀴즈 인덱스가 퀴즈 데이터 길이를 초과하면 홈 페이지로 이동
    if current_quiz_index >= len(quiz_data):
        return redirect('/')  # 마지막 퀴즈면 홈 페이지로 이동
    
    feedback = ""  # 초기 피드백 초기화
    
    # 문제와 옵션 생성
    questions = []
    for current_quiz in current_quizzes:
        question_text = current_quiz[0]
        options = [(index, option) for index, option in enumerate(current_quiz[1])]
        questions.append((question_text, options))
    
    return render_template('quiz.html', questions=questions, current_quiz_index=current_quiz_index, feedback=feedback)

@app.route('/check_answer', methods=['POST'])
def check_answer():
    global current_quiz_index
    user_answer = int(request.form['answer'])
    correct_index = int(request.form['correct_index'])

    if user_answer == correct_index:
        feedback = "정답입니다!"
    else:
        feedback = "틀렸습니다. 정답은 %d번입니다." % (correct_index + 1)

    # 현재 퀴즈 가져오기
    num_questions_to_show = 4  # 4개의 문제를 보여줍니다.
    if current_quiz_index + num_questions_to_show <= len(quiz_data):
        current_quizzes = quiz_data[current_quiz_index:current_quiz_index + num_questions_to_show]
    else:
        current_quizzes = quiz_data[current_quiz_index:]
    
    # 현재 퀴즈 인덱스가 퀴즈 데이터 길이를 초과하면 홈 페이지로 이동
    if current_quiz_index >= len(quiz_data):
        return redirect('/')  # 마지막 퀴즈면 홈 페이지로 이동
    
    # 문제와 옵션 생성
    questions = []
    for current_quiz in current_quizzes:
        question_text = current_quiz[0]
        options = [(index, option) for index, option in enumerate(current_quiz[1])]
        questions.append((question_text, options))

    return render_template('quiz.html', questions=questions, current_quiz_index=current_quiz_index, feedback=feedback)

@app.route('/next')
def next_quiz():
    global current_quiz_index
    if current_quiz_index < len(quiz_data) - 1:
        current_quiz_index += 1
    return redirect('/quiz')

@app.route('/prev')
def prev_quiz():
    global current_quiz_index
    if current_quiz_index > 0:
        current_quiz_index -= 1
    return redirect('/quiz')

if __name__ == '__main__':
    app.run(debug=True)

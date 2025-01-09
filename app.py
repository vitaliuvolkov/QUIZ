from flask import Flask, render_template, request, redirect, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

from questions import questions

conn = sqlite3.connect('quiz_results.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS results
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                score INTEGER)''')
conn.commit()
conn.close()

def get_score():
    conn = sqlite3.connect('quiz_results.db')
    cursor = conn.cursor()
    data = []

    cursor.execute("SELECT name, score FROM results ORDER BY score DESC")
    for row in cursor.fetchall():
        name = row[0]
        score = row[1]
        _data = {'name': name, 'score': score}
        data.append(_data)

    conn.close()
    return data

def set_score():
    conn = sqlite3.connect('quiz_results.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO results (name, score) VALUES (?, ?)", (session.get('username'), session.get('score')))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html', data=get_score())

@app.route('/quiz', methods=['POST', 'GET'])
def quiz():
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            session['username'] = username
            session['category'] = 'Викторина'
            session['score'] = 0
            session['question_index'] = 0
            return redirect('/question')
    return redirect('/')

@app.route('/question', methods=['GET', 'POST'])
def question():
    category = 'Викторина'
    score = session.get('score')
    question_index = session.get('question_index')

    if category and score is not None and question_index is not None:
        if request.method == 'POST':
            user_answer = request.form.get('answer')
            if user_answer and user_answer == questions[category][question_index]['answer']:
                session['score'] += 1

            session['question_index'] += 1
            if session['question_index'] < len(questions[category]):
                return redirect('/question')
            else:
                return redirect('/result')

        current_question = questions[category][question_index]
        return render_template('quiz.html', category=category, question=current_question, index=question_index + 1, total=len(questions[category]))

    return redirect('/')

@app.route('/result')
def result():
    username = session.get('username')
    category = session.get('category')
    score = session.get('score')
    if username and score is not None:
        set_score()
        return render_template('result.html', username=username, score=score, total=len(questions[category]))
    return redirect('/')
if __name__ == '__main__':
    app.run(debug=True)

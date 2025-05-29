from flask import Flask, request, jsonify, render_template
import psycopg2
import requests
import pandas as pd

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname='DndEnemyDB',
        user='postgres',
        password='123',
        host='localhost',
        port='5432'
    )
    return conn

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/api/enemy', methods=['POST'])
def get_enemy():
    data = request.json
    features = data.get('features')[0]

    response = requests.post('http://127.0.0.1:8000/predict', json={
        'features': [features]
    })
    
    enemy_names = response.json()
    enemy_name1 = enemy_names[0].get('label')
    enemy_name2 = enemy_names[1].get('label')
    enemy_name3 = enemy_names[2].get('label')

    df = pd.read_csv('dnd_monsters.csv')
    def get_monster_link(monster_name):
        monster_name_link = "not found"
        for index, row in df.iterrows():
            if row['name'] == monster_name:
                print(row['name'])
                monster_name_link = row["url"]
                break
        return monster_name_link

    enemy_link1 = get_monster_link(enemy_name1)
    enemy_link2 = get_monster_link(enemy_name2)
    enemy_link3 = get_monster_link(enemy_name3)

    legendary = bool(features[3])
    can_fly = bool(features[10])
    can_swim = bool(features[11])

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO requestsdata (size_value, ac, hp, legendary, str, dex, con, int, wis, cha, can_fly, can_swim, enemy_name, enemy_name2, enemy_name3, request_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)',
                (features[0], features[1], features[2], legendary, features[4], features[5], features[6], features[7], features[8], features[9], can_fly, can_swim, enemy_name1, enemy_name2, enemy_name3))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'enemy_name1': enemy_name1, 'enemy_name2': enemy_name2, 'enemy_name3': enemy_name3,
                    'enemy_link1': enemy_link1, 'enemy_link2': enemy_link2, 'enemy_link3': enemy_link3
    })

if __name__ == '__main__':
    app.run(debug=True)
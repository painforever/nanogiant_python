from flask import Flask
from flask import request

import mysql.connector
import sys
sys.path.append(".")
from nlp import TopicGenerator

#flask run

app = Flask(__name__)
cnx = mysql.connector.connect(user='root', password='adminadmin', host='127.0.0.1', database='nanogiant_nlp_development')
model = TopicGenerator()
RecordCount = 1000

@app.route("/topics")
def topics():
    cursor = cnx.cursor()
    query = ("SELECT * from feed_backs LIMIT {record_count}".format(record_count=RecordCount))
    cursor.execute(query)
    feed_backs = []
    for (row) in cursor:
        feed_backs.append(row[4])

    sentences = model.generate_topic_sentences(model.make_topics(feed_backs))
    return {'result': sentences}

@app.route("/positive_feedbacks")
def positive_feedbacks():
    cursor = cnx.cursor()
    query = ("SELECT * from feed_backs LIMIT {record_count}".format(record_count=RecordCount))
    cursor.execute(query)
    result = []
    count = 0
    for (row) in cursor:
        try:
            res = model.analyzer.polarity_scores(row[4])
            if res['pos'] > res['neg'] and res['compound'] > 0:
                result.append({'feedback': row[4], 'scores': res})
                count += 1
        except:
            continue
    return {'count': count, 'result': result}

@app.route("/negative_feedbacks")
def nagetive_feedbacks():
    cursor = cnx.cursor()
    query = ("SELECT * from feed_backs LIMIT {record_count}".format(record_count=RecordCount))
    cursor.execute(query)
    result = []
    count = 0
    for (row) in cursor:
        try:
            res = model.analyzer.polarity_scores(row[4])
            if res['pos'] < res['neg'] and res['compound'] < 0:
                result.append({'feedback': row[4], 'scores': res})
                count += 1
        except:
            continue
    return {'count': count, 'result': result}


@app.route("/topic_details")
def topic_details():
    word = request.args.get("word")
    cursor = cnx.cursor()
    query = ("SELECT * from feed_backs WHERE content LIKE '%{word}%' LIMIT {record_count}".format(word=word, record_count=RecordCount))
    cursor.execute(query)
    result = []
    count = 0
    for (row) in cursor:
        try:
            res = model.analyzer.polarity_scores(row[4])
            row_hash = {'feedback': row[4], 'score': row[5], 'thumbs_up_count': row[6]}
            # if res['pos'] < res['neg'] and res['compound'] < 0:
            #     row_hash['type'] = 'negative'
            #     result.append(row_hash)
            # if res['pos'] > res['neg'] and res['compound'] > 0:
            #     row_hash['type'] = 'positive'
            #     result.append(row_hash)
            row_hash['type'] = model.sentiment_helper(res)
            result.append(row_hash)
            count += 1
        except:
            continue
    return {'count': count, 'result': result}


@app.route("/charts")
def charts():
    cursor = cnx.cursor()
    query = ("SELECT * from feed_backs LIMIT {record_count}".format(record_count=RecordCount))
    cursor.execute(query)
    bar_chart_hash = {'positive': 0, 'negative': 0, 'neutral': 0}
    word_count_chart_hash = {}
    feed_backs = []
    for (row) in cursor:
        #for word count chart
        feed_backs.append(row[4])
        try:
            res = model.analyzer.polarity_scores(row[4])
            bar_chart_hash[model.sentiment_helper(res)] += 1
        except:
            continue


    sentences = model.generate_topic_sentences(model.make_topics(feed_backs))
    for sentence in sentences:
        arr = sentence.split(',')
        for word in arr:
            word_count_chart_hash[word.strip()] = word_count_chart_hash.get(word.strip(), 0) + 1

    return {'result': {'bar_chart_hash': bar_chart_hash, 'pie_chart_hash': word_count_chart_hash}}

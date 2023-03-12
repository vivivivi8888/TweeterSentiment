from flask import Flask, jsonify, request
import psycopg2
from DAL.TweetDAL import TweetDAL
screen_name = ['elonmusk', 'BarackObama', 'cathiedwood']
column_name = ['tweet_id', 'created_at', 'author_id', 'text', 'conversation_id', 'conversation_txt', 'retweet_count',
               'reply_count', 'like_count', 'quote_count', 'sentiment_score']

app = Flask('twitter_server')
tweetDAL = TweetDAL()

@app.route('/accounts', methods=['GET'])
def get_accounts():
    return jsonify({"account_name": screen_name})

@app.route('/tweets', methods=['GET'])
def get_tweets():
    user_id = request.args.get('tweet_handle')
    tweet_raw = tweetDAL.fetch_all()
    result = {}
    result['tweets'] = []
    for row in tweet_raw:
        if row[2] == user_id:
            row_dict = dict(zip(column_name, row))
            result['tweets'].append(row_dict)

    return jsonify(result)


@app.route('/sentiment', methods=['GET'])
def get_sentiment():
    user_id = request.args.get('tweet_handle')
    tweet_raw = tweetDAL.fetch_all()
    all_stats = {}

    all_stats['retweet_ratio'] = []
    all_stats['reply_ratio'] = []
    all_stats['like_ratio'] = []
    all_stats['sentiment_score'] = []
    all_stats['comprehensive_senti'] = []

    for row in tweet_raw:
        if row[2] == user_id:
            all_stats['retweet_ratio'].append(row[6] / row[9])
            all_stats['reply_ratio'].append(row[7] / row[9])
            all_stats['like_ratio'].append(row[8] / row[9])
            all_stats['sentiment_score'].append(float(row[10][3]))
            all_stats['comprehensive_senti'].append((sum([row[6], row[7], row[8]])/3/row[9])*float(row[10][3]))

    res = {}
    res['number_of_tweets']=len(tweet_raw)
    res['retweet_ratio'] = sum(all_stats['retweet_ratio'])/len(all_stats['retweet_ratio'])
    res['reply_ratio'] = sum(all_stats['reply_ratio'])/len(all_stats['reply_ratio'])
    res['like_ratio'] = sum(all_stats['like_ratio'])/len(all_stats['like_ratio'])
    res['sentiment_score'] = sum(all_stats['sentiment_score'])/len(all_stats['sentiment_score'])
    res['comprehensive_senti'] = sum(all_stats['comprehensive_senti'])/len(all_stats['comprehensive_senti'])
    if res['sentiment_score'] < -0.5:
        res['comment'] = 'Negative'
    elif res['sentiment_score'] > 0.5:
        res['comment'] = 'Positive'
    else:
        res['comment'] = 'Neutral'


    return jsonify(res)





if __name__ == '__main__':
    app.run(debug=True)
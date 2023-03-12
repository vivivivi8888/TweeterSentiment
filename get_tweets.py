import tweepy
import datetime
from datetime import timezone
import psycopg2
import emoji
import re
from DAL.TweetDAL import TweetDAL
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


#########################################################   upload all tweets to input data list  #########################################################
class TweetSentimentClient:

    def __init__(self):
        print(tweepy.__version__)
        bearer_token = "{Your Twitter bearer Token}"
        self.client = tweepy.Client(bearer_token)

        self.start_t_str = datetime.datetime(2023, 2, 1, 0, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ")
        screen_name = ['elonmusk', 'BarackObama', 'cathiedwood']
        self.id_list = []
        ### get user_id of target users
        for name in screen_name:
            res = client.get_user(username=name)
            self.id_list.append(res.data.id)

        self.analyzer = SentimentIntensityAnalyzer()
        self.tweet_dal = TweetDAL()


    def handle_twitter_text(self, original_text):

        tunned_text = emoji.demojize(original_text)
        tunned_text = re.sub(r'@\w+', '', tunned_text)

        return tunned_text


    def get_text_sentiment(self, sentence):
        ####################      sentiment analysis       #####################
        ########      input data is tweet context and quote context      #########
        vs = self.analyzer.polarity_scores(sentence)
        return [str(vs['neg']), str(vs['neu']), str(vs['pos']), str(vs['compound'])]


    def Update_Input_Data(self, response, input_data):

        conversation_id = [tweet.conversation_id for tweet in response.data]
        conversation_tweet = self.client.get_tweets(ids=conversation_id, tweet_fields=['created_at', 'author_id'])
        conv_dict = {}
        for tweet in conversation_tweet.data:
            conv_dict[tweet.id] = self.handle_twitter_text(tweet.text)

        for tweet in response.data:
            if tweet.conversation_id in conv_dict:
                conv_text = conv_dict[tweet.conversation_id]
            else:
                conv_text = ''
            tweet_text = self.handle_twitter_text(tweet.text)
            sentiment_score = self.get_text_sentiment(tweet_text + ' ' + conv_text)
            one_line = [tweet.id, tweet.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"), tweet.author_id, tweet_text,
                        tweet.conversation_id, conv_text, tweet.public_metrics['retweet_count'],
                        tweet.public_metrics['reply_count'], tweet.public_metrics['like_count'],
                        tweet.public_metrics['impression_count'], sentiment_score]
            input_data.append(one_line)

        return input_data


    def Update_Input_Data_Next_Token(self, next_token, response, input_data, user_id):
        while next_token:
            print(next_token)
            input_data = self.Update_Input_Data(response, input_data)

            response = client.get_users_tweets(user_id, start_time=self.start_t_str,
                                               tweet_fields=['context_annotations', 'created_at', 'public_metrics',
                                                             'author_id', 'conversation_id'],
                                               pagination_token=next_token, max_results=100)

            if 'next_token' in response.meta:
                next_token = response.meta['next_token']
            else:
                break

        return input_data


    def get_new_tweet_data(self):
        input_data = []
        for user_id in self.id_list:
            print(user_id)
            response = self.client.get_users_tweets(
                user_id,
                start_time=self.start_t_str,
                tweet_fields=['context_annotations', 'created_at', 'public_metrics', 'author_id','conversation_id'],
                max_results=100
            )
            if 'next_token' in response.meta:
                next_token = response.meta['next_token']
                input_data = self.Update_Input_Data_Next_Token(next_token, response, input_data, user_id)
            else:
                input_data = self.Update_Input_Data(response, input_data)

        self.tweet_dal.insert(input_data)

    def get_tweet_replies(self, tweet_id, tweet_handle):
        replies=[]

        query = f'to:{tweet_handle}'
        resp = self.client.search_recent_tweets(query=query, max_results=100)
        replies_list = resp.data
        next_token = resp.meta['next_token']
        while next_token:
            resp = self.client.search_recent_tweets(query=query, max_results=100, next_token=next_token)
            replies_list.extend(resp.data)
            next_token = resp.meta['next_token']

        for reply in replies_list:
            # if reply.in_reply_to_user_id:
            #     print(reply.data)
            if reply.in_reply_to_user_id == tweet_id:
                replies.append(reply)

        return replies

CREATE TABLE IF NOT EXISTS tweepy.tweet
(
    tweet_id character varying COLLATE pg_catalog."default" NOT NULL,
    created_at character varying COLLATE pg_catalog."default" NOT NULL,
    author_id character varying COLLATE pg_catalog."default",
    text character varying COLLATE pg_catalog."default",
    conversation_id character varying COLLATE pg_catalog."default",
    conversation_txt character varying COLLATE pg_catalog."default",
    retweet_count integer,
    reply_count integer,
    like_count integer,
    quote_count integer,
    sentiment_score character varying[] COLLATE pg_catalog."default",
    CONSTRAINT tweet_pkey PRIMARY KEY (tweet_id)
)
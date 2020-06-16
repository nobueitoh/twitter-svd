import configparser
import twitter
import logging
import json

def main():
    config = configparser.ConfigParser()
    config.read('cfg.ini')
    logging.debug('connecting to twitter')
    default = config['DEFAULT']
    api = twitter.Api(consumer_key=default['consumer_key'],
            consumer_secret=default['consumer_secret'],
            access_token_key=default['access_token_key'],
            access_token_secret=default['access_token_secret'])
    logging.debug('connected')
    for line in api.GetStreamFilter(
            track=['python'],
            languages=['en']):
        try:
            logging.debug(line['text'])
        except KeyError:
            pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()

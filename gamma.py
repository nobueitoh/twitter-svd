
from sklearn.cluster import Birch, MiniBatchKMeans
from sklearn.feature_extraction.text import HashingVectorizer
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
import twitter, configparser, logging
from collections import deque
try:
    import cPickle as pickle
except ImportError:
    logging.warning("couldn't find cPickle")
    import pickle

def preprocess(text):
    tok = TweetTokenizer(reduce_len=True)
    return [i for i in tok.tokenize(text) if i not in stopwords.words()]

def main():
    vec = HashingVectorizer(tokenizer=preprocess, ngram_range=(3,3), analyzer='word')
    clu = Birch(n_clusters=3)
    #clu = MiniBatchKMeans(n_clusters=2)

    config = configparser.ConfigParser()
    config.read('cfg.ini')
    config = config['DEFAULT']
    api = twitter.Api(consumer_key=config['consumer_key'],
            consumer_secret=config['consumer_secret'],
            access_token_key=config['access_token_key'],
            access_token_secret=config['access_token_secret'])
    queue = deque(maxlen=50)
    for n, line in enumerate(api.GetStreamFilter(
            track=['pokemon','dark souls', 'darksouls', 'sonic', 'hedgehog'], languages=['en'])):
        if n > 1000000:
            break
        elif len(queue) != 50:
            try:
                queue.append(line['text'])
                logging.warning("%s", line['text'])
            except KeyError:
                pass
        else:
            try:
                v = vec.transform(queue)
                clu = clu.partial_fit(v)
                logging.warning('TESTING\n.\n.\n.\n.')
                logging.warning("%s, %s, %s", n, clu.predict(v[-1]), queue[-1])
            except KeyError:
                pass
            queue.clear()

    pickle.dump(clu, open('cluster_model.pkl', 'w'))

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    main()

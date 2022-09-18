import tweepy
import time
import requests
from bs4 import BeautifulSoup
from transformers import *
from itertools import islice
import os, dotenv
from datetime import datetime

currentTime = datetime.now().time()
givenTimePreRangeMorning = datetime.strptime("09:00AM", "%I:%M%p").time()
givenTimePostRangeMorning = datetime.strptime("09:20AM", "%I:%M%p").time()
givenTimePreRangeEvening = datetime.strptime("06:00PM", "%I:%M%p").time()
givenTimePostRangeEvening = datetime.strptime("06:20PM", "%I:%M%p").time()


def get_var_value(filename="/Users/parambhatia/News/varstore.dat"):
    with open(filename, "a+") as f:
        f.seek(0)
        val = int(f.read() or 0) + 1
        f.seek(0)
        f.truncate()
        f.write(str(val))
        return val
def set_var_value(filename="/Users/parambhatia/News/varstore.dat"):
    with open(filename, "a+") as f:
        f.seek(0)
        f.truncate()
        f.write(str(1))
    with open("/Users/parambhatia/News/data.txt", 'r+') as f:
        f.truncate(0)

if(currentTime >= givenTimePreRangeMorning and currentTime < givenTimePostRangeMorning):
    set_var_value()
if(currentTime >= givenTimePreRangeEvening and currentTime < givenTimePostRangeEvening):
    set_var_value()

global counterExecute
counterExecute = int(get_var_value())
print("The current article count is :" + " " + str(counterExecute))

if(counterExecute >=27):
    set_var_value()
    print()
    print('---------------------------')
    print()
    with open("/Users/parambhatia/News/data.txt", "r+") as file:
        lines = file.readlines()
        print(lines)
    file.close()
    set_var_value()




print("This script has been run {} times.".format(str(counterExecute)))

dotenv.load_dotenv()
consumerKey = os.environ["CONSUMER_KEY"]
consumerSecret = os.environ["CONSUMER_SECRET"]
accessToken = os.environ["ACCESS_TOKEN"]
accessTokenSecret = os.environ["SECRET_ACCESS_TOKEN"]


auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
auth.set_access_token(accessToken, accessTokenSecret)
api = tweepy.API(auth)



def get_paraphrased_sentences(model, tokenizer, sentence, num_return_sequences=5, num_beams=5):
    # tokenize the text to be form of a list of token IDs
    inputs = tokenizer([sentence], truncation=True, padding="longest", return_tensors="pt")
    # generate the paraphrased sentences
    outputs = model.generate(
        **inputs,
        num_beams=num_beams,
        num_return_sequences=num_return_sequences,
    )
    # decode the generated sentences using the tokenizer to get them back to text
    return tokenizer.batch_decode(outputs, skip_special_tokens=True)

def printNews():
    response = requests.get('http://feeds.bbci.co.uk/news/rss.xml?edition=uk')
    try:
        soup = BeautifulSoup(response.content, features='xml')
    except Exception as E:
        print("lol")
    items = soup.findAll('item')
    news_articles = []
    i = 0
    for item in items:
        if(i<36):
            news_item = {}
            news_item['title'] = item.title.text
            news_item['description'] = item.description.text
            news_item['link'] = item.link.text
            news_item['pubDate'] = item.pubDate.text
            news_articles.append(news_item)
            i += 1
    return news_articles

def job():
    global counterExecute
    if(counterExecute == 1):
        newsStack = printNews()
        print(len(newsStack))
        model = PegasusForConditionalGeneration.from_pretrained("tuner007/pegasus_paraphrase")
        tokenizer = PegasusTokenizerFast.from_pretrained("tuner007/pegasus_paraphrase")
        with open("/Users/parambhatia/News/data.txt", 'w') as file:
            for words in newsStack:
                amendedSentence = get_paraphrased_sentences(model, tokenizer, words['title'], num_beams=10, num_return_sequences=1)
                headline = f'"{amendedSentence[0]}"'
                source = "Source : " + words['link']
                final_string = headline + "\n" + source
                print(final_string)
                file.write("%s\n" % final_string)
        file.close()
    with open("/Users/parambhatia/News/data.txt", "r+") as file:
        head = list(islice(file, 2))
        print("the current headline is:")
        print(head)
        print("Hope you enjoyed reading that headline")
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        api.update_status(head[0] + head[1] + "- " + current_time)
    file.close()
    with open("/Users/parambhatia/News/data.txt", "r+") as file:
        lines = file.readlines()
        file.seek(0)
        file.truncate()
        file.writelines(lines[2:])
    file.close()

job()

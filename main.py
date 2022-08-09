# TODO:
# - Nothing right now!
import feedparser
import os

from flask import Flask, send_from_directory, redirect, url_for
from importlib.metadata import entry_points
from jinja2 import Environment, FileSystemLoader
from pprint import pprint
from threading import Thread

app = Flask(__name__, static_folder='./html')


# Update the settings here in order to add more feeds
settings = {
    'kubernetes-blog': 'https://kubernetes.io/feed.xml',
    'azure-blog': 'https://azurecomcdn.azureedge.net/en-us/blog/feed/',
    'cncf': 'https://www.cncf.io/feed',
    'stefanstranger': 'https://stefanstranger.github.io/feed.xml',
    'danielhaxx': 'https://daniel.haxx.se/blog/feed/'
}

env = Environment(
    loader=FileSystemLoader(['templates'])
)

index_tpl = env.get_template('index.html.j2')
slug_tpl = env.get_template('slug.html.j2')

with open('html/index.html', 'w') as index_fh:
    index_fh.write(index_tpl.render(slugs=settings.keys()))

def worker_func():
    """
        Start a thread to fetch and render rss feeds
    """
    thr = Thread(target=fetch_and_render, args=[settings])
    thr.start()
    return thr

def fetch_and_render(settings:dict):
    print("Updating feed...")
    feeds = settings.copy()
    for slug, feed in settings.items():
        content = list()
        newsfeed = feedparser.parse(feed)
        entries = newsfeed.entries
        for article in entries:
            content.append({
                'title': article.title,
                'published': article.published,
                'link': article.link
            })
        feeds[slug] = content
        with open(f'html/{slug}.html', 'w') as slug_fh:
            slug_fh.write(slug_tpl.render(slugs=feeds.keys(), rss_feed=content))

@app.route('/', methods=['GET'])
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<feed>', methods=['GET'])
def load_feed(feed):
    return send_from_directory(app.static_folder, feed)

@app.route('/refresh', methods=['POST'])
def refresh_content():
    worker_func()
    return redirect(url_for('.index')) 

worker_func()
app.run("0.0.0.0")

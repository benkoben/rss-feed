# TODO:
# - Create a refresh button
# - Error handling for the following
# {'bozo': True, 'entries': [], 'feed': {}, 'headers': {}, 'bozo_exception': URLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:997)'))}
# {'bozo': True, 'entries': [], 'feed': {}, 'headers': {}, 'bozo_exception': URLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self signed certificate in certificate chain (_ssl.c:997)'))}
# {'bozo': True, 'entries': [], 'feed': {}, 'headers': {}, 'bozo_exception': URLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:997)'))}
# {'bozo': True, 'entries': [], 'feed': {}, 'headers': {}, 'bozo_exception': URLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:997)'))}
# {'bozo': True, 'entries': [], 'feed': {}, 'headers': {}, 'bozo_exception': URLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:997)'))}

from importlib.metadata import entry_points
import feedparser
from pprint import pprint
from jinja2 import Environment, FileSystemLoader
from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder='./html')

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
    settings[slug] = content
    print(newsfeed)
    with open(f'html/{slug}.html', 'w') as slug_fh:
        slug_fh.write(slug_tpl.render(slugs=settings.keys(), rss_feed=content))

@app.route('/', methods=['GET'])
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<feed>', methods=['GET'])
def feed(feed):
    return send_from_directory(app.static_folder, feed)

app.run("0.0.0.0")

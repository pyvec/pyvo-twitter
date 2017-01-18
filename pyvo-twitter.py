import sys
import os.path
from os.path import join
from datetime import datetime
import random

import json
import tweepy
import click
import git
from git import Repo
from jinja2 import Template
from pyvodb.load import get_db as pyvodb_get_db, load_from_directory
from pyvodb.tables import Event, City, Venue

import config

access_token = None

PHRASES = open("phrases.txt", encoding="utf-8").read().strip().split('\n')

def get_api():
    """ Log in to Twitter and get the API object. """
    if os.path.isfile("access_token.json"):
        with open("access_token.json", encoding="utf-8") as f:
            access_token = json.load(f)
        
        auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
        auth.set_access_token(access_token['key'], access_token['secret'])
        try:
            api = tweepy.API(auth)
            api.me()
        except tweepy.error.TweepError as ex:
            print("Failed to authorize: {}".format(ex))
            print("Please re-run `authorize`.")
            sys.exit(1)
    else:
        print("No access_token.json present.")
        print("Please run `authorize`.")
        sys.exit(1)
        
    return api

def get_db():
    """ 
        Update and return the Pyvo events database, initializing
        it if it's not present.
    """
    if os.path.exists(config.data_dir):
        repo = Repo(config.data_dir)
        repo.remotes.origin.pull()
    else:
        repo = Repo.clone_from(config.data_repo_url, config.data_dir)
    return pyvodb_get_db(config.data_dir)

def get_events(date):
    """ Get the Pyvo events on a single day """
    db = get_db()
    query = db.query(Event).filter(Event.year == date.year, Event.month == date.month, Event.day == date.day)
    return query.all()
    

@click.group()
def main():
    """
        Announce Pyvo meetups on Twitter, automatically!
    """
    pass

@main.command()
def authorize():
    """
        Interactively authorize on Twitter.
    """
    if not (config.consumer_key and config.consumer_secret):
        print("A Twitter consumer key and consumer secret is necessary.")
        sys.exit(1)
    auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
    authorization_url = auth.get_authorization_url()

    print("Please authorize the pyvo-twitter application at:")
    print(" {}".format(authorization_url))
    pin = input("PIN: ")

    auth.get_access_token(pin)

    access_token = {"key": auth.access_token, "secret": auth.access_token_secret}
    with open("access_token.json", "w", encoding="utf-8") as f:
        json.dump(access_token, f)

    get_api()
    print("Authorization successful.")

@main.command("tweet-next")
@click.option('--dry', is_flag=True, default=False, required=False, help="Do not tweet, print instead")
@click.option('--is-test', is_flag=True, default=False, required=False, help="Note that this tweet is a test")
def announce_next(dry, is_test):
    """
        Make a test tweet with the upcoming event.
    """
    db = get_db()
    event = db.query(Event).filter(Event.date >= datetime.today()).first()

    if is_test:
        text = "Toto je testovací tweet zapomocí pyvo-twitter! 🐍🐍🐍\n"
    else:
        text = ""
    if event:
        text += "🐍🍺 Příští akce bude {event.name} dne {event.day}. {event.month}.!".format(event=event)
        if event.links:
            text += "\n{}".format(event.links[0].url)
    else:
        text += "🐍🍺 Příští akce ještě nebyla ohlášena! 😨"
    if not dry:
        api = get_api()
        api.update_status(text)
    else:
        print(text)
    

@main.command("tweet-today")
@click.option('--date', required=False, help="Pretend it's another day")
@click.option('--dry', is_flag=True, default=False, required=False, help="Do not tweet, print instead")
def announce_today(date, dry):
    """
        Make the relevant tweets for today.
        
        This command will announce the Pyvo events that are happening.
        Intended to be run from a cronjob once a day, e.g. at midday.
    """
    tweets = []
    
    if date:
        date = datetime.strptime(date, '%Y-%m-%d')
    else:
        date = datetime.today()
    
    events = get_events(date)
    for event in events:
        text = Template(random.choice(PHRASES)).render(event=event)
        if event.links:
            text += "\n{}".format(event.links[0].url)
        tweets.append(text)
    
    if not dry:
        api = get_api()
        for tweet in tweets:
            api.update_status(tweet)
    else:
        for tweet in tweets:
            print(tweet)

if __name__ == '__main__':
    main()

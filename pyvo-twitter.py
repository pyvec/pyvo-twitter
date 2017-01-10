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
from pyvodb.load import get_db, load_from_directory
from pyvodb.tables import Event, City, Venue

import config

access_token = None

PHRASES = open("phrases.txt").read().strip().split('\n')

def get_api():
    if os.path.isfile("access_token.json"):
        with open("access_token.json") as f:
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

def update_data():
    if os.path.exists(config.data_dir):
        repo = Repo(config.data_dir)
        repo.remotes.origin.pull()
    else:
        repo = Repo.clone_from(config.data_repo_url, config.data_dir)

def get_events(date):
    db = get_db(config.data_dir)
    query = db.query(Event).filter(Event.year == date.year, Event.month == date.month, Event.day == date.day)
    return query.all()
    

@click.group()
def main():
    pass

@main.command()
def authorize():
    """
        Interactively authorize on Twitter.
    """
    auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
    authorization_url = auth.get_authorization_url()

    print("Please authorize the pyvo-twitter application at:")
    print(" {}".format(authorization_url))
    pin = input("PIN: ")

    auth.get_access_token(pin)

    access_token = {"key": auth.access_token, "secret": auth.access_token_secret}
    with open("access_token.json", "w") as f:
        json.dump(access_token, f)

    get_api()
    print("Authorization successful.")

@main.command()
@click.option('--date', required=False, help="Pretend it's another day")
@click.option('--dry', is_flag=True, default=False, required=False, help="Do not tweet, print instead")
def tweet(date, dry):
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
    update_data()
    
    events = get_events(date)
    for event in events:
        text = random.choice(PHRASES).format(event=event)
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

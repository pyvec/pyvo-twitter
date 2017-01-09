import sys
import os.path

import json
import tweepy
import click

import config

access_token = None

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

@click.group()
def main():
    pass

@main.command()
def authorize():
    """
        Interactively authorize the pyvo-twitter application on Twitter.
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
def tweet():
    api = get_api()
    api.update_status("test")

if __name__ == '__main__':
    main()

# pyvo-twitter

`pyvo-twitter` is a single-purpose script for announcing Pyvo meetups on Twitter, because some of can use the reminder.  It draws data from [pyvo-data](https://github.com/pyvec/pyvo-data) using [pyvodb](https://github.com/pyvec/pyvodb/).

## Setting up

Setting up pyvo-twitter has been made as painless as possible.  First, clone the repo and set up the virtualenv.

```
    git clone https://github.com/Sanqui/pyvo-twitter
    cd pyvo-twitter
    virtualenv --python=python3 env
    source env/bin/activate
    pip install -r requirements.txt
```

Next, copy `config.py.example` to `config.py`.

To access the API and send automated tweets, Twitter requires having an
application registered.  You can either make a new one, or ask
[Sanqui](https://github.com/sanqui/) for the *official* pyvo-twitter keys.
Either way, fill these out in `config.py`.

Finally, you'll need to authenticate pyvo-twitter to tweet under the desired
Twitter account.  Running `python pyvo-twitter.py authorize` should walk you
through this.

To make a test tweet after having set up, you can run

```
    python pyvo-twitter.py tweet-next --is-test
```

This will announce the date of the next Pyvo event (and note that the tweet
is a test).  The tweet can be deleted the standard way if you so wish.

## Automatic run

If all looks well, it's time to set up automatic tweeting.

To faciliate automatic tweeting, `pyvo-twitter` has a `tweet-today`
command.  This command will tweet out if there is an event planned for today,
otherwise, it will do nothing.  (You can pass the `--dry` parameter to
see what would be tweeted.)

You can set up the `tweet-today` command to run daily at a desired time (e.g.,
at midday) using cron.  This is an example cronjob line, replacing [PATH] with the absolute path to pyvo-twitter:

```
    0 12 * * *  cd [PATH]/ && [PATH]/env/bin/python [PATH]/pyvo-twitter.py tweet-today
```

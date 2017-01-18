# pyvo-twitter

`pyvo-twitter` is a single-purpose script for announcing Pyvo meetups on Twitter, because some of can use the reminder.  It draws data from [pyvo-data](https://github.com/pyvec/pyvo-data) using [pyvodb](https://github.com/pyvec/pyvodb/).

## Setting up

Setting up pyvo-twitter has been made as painless as possible.  First, clone the repo and set up the virtualenv.

```
    git clone https://github.com/pyvec/pyvo-twitter.git
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

## Current deployment on rosti.cz

`pyvo-twitter` runs on the Roští.cz server alongside `pyvo.cz`.  It's set up in `/srv/pyvo-twitter`, cloned from `https://github.com/pyvec/pyvo-twitter.git`.

The current setup has a POSIX locale.  This breaks things (see PEP 538).  The virtualenv in `/srv/pyvo-twitter/env/` is set up to switch to utf-8 in `/src/pyvo-twitter/env/bin/activate`:

```
    export LC_ALL=C.UTF-8
    export LANG=C.UTF-8
```

The cron has to be set up according to [rosti.cz docs on cron](https://docs.rosti.cz/tools/cron/) (which isn't too complicated).

The cron command is set up to change the locale as well, and also pull the repository.

```
    30 15 * * * export LC_ALL=C.UTF-8; export LANG=C.UTF-8; cd /srv/pyvo-twitter/ && ( git pull origin master --quiet; /srv/pyvo-twitter/env/bin/python /srv/pyvo-twitter/pyvo-twitter.py tweet-today )
```

If necessary, @Sanqui and @encukou have access.

## License
`pyvo-twitter` is under the MIT license.

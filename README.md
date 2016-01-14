# Slack Gamebot

A gamebot for slack.  Supports

* Leaderboards
* Stats
* Smack Talking

Written in python2/django 1.9

# How to:

1. Get your slack API token
    * go to *https://your_teamname.slack.com/apps/manage/custom-integrations*
    * Click *bots*
    * Click *Add Configuration*.
    * Choose a username (I recommend *gamebot*).  Press "Add Bot Integration" 
    * Copy your bot's API key.
    * Customize your bots picture or name (optional). Press "Save Integration"

2. On command line (replace `<YOUR-API-KEY>` with the API key you copied above):

```
git clone https://github.com/owocki/slack_gamebot.git
cd slack_gamebot
echo API_TOKEN = "<YOUR-API-KEY>" > slackbot_settings.py
pip install -r requirements.txt
./manage.py migrate
./manage.py run_bot
```

3. Invite your gamebot to channel.
4. Start interacting with commands like `gamebot help`.


# Looks like this:

<img src='http://bits.owocki.com/1g2K0G3s450v/Screen%20Recording%202015-12-27%20at%2007.12%20AM.gif' />

<!-- Google Analytics --> 
<img src='https://ga-beacon.appspot.com/UA-1014419-15/owocki/slack_gamebot' style='width:1px; height:1px;' >

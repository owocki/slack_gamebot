# Slack Gamebot

A gamebot for Slack, written in python2 and utilzing Django
1.9. Gamebot has support for leaderboards, stats, and smack talking;
it covers all the bases.

## Setup:

- Get your slack API token:

    * go to *https://your_teamname.slack.com/apps/manage/custom-integrations*
    * Click *bots*
    * Click *Add Configuration*.
    * Choose a username (I recommend *gamebot*).  Press "Add Bot Integration" 
    * Copy your bot's API key.
    * Customize your bots picture or name (optional). Press "Save Integration"

- On command line (replace `<YOUR-API-KEY>` with the API key you copied above):

```
git clone https://github.com/owocki/slack_gamebot.git
cd slack_gamebot
echo API_TOKEN = "<YOUR-API-KEY>" > slackbot_settings.py
pip install --ignore-installed -r requirements.txt
./manage.py migrate
./manage.py run_bot
```
- Invite your gamebot to a channel.
- Start interacting with commands like `gamebot help`.

## Looks like this:

<img src='http://bits.owocki.com/1g2K0G3s450v/Screen%20Recording%202015-12-27%20at%2007.12%20AM.gif' />

## Creates ELO rankings and charts like this:

<img src='http://bits.owocki.com/102w2P0J231M/Image%202016-03-30%20at%2010.13.30%20AM.png' />


<!-- Google Analytics --> 
<img src='https://ga-beacon.appspot.com/UA-1014419-15/owocki/slack_gamebot' style='width:1px; height:1px;' >

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from history.models import Game, Tag, Season
from datetime import datetime, date
from collections import Counter
from elo import rate_1vs1


class Command(BaseCommand):
    help = 'Runs slackbot'

    def handle(self, *args, **options):
        from slackbot.bot import respond_to
        from slackbot.bot import listen_to
        from slackbot.bot import Bot
        import re 
        begin_elo_at = 1000

        def _get_elo(gamename):
            #get games from ORM
            games = Game.objects.filter(gamename=gamename).order_by('created_on')

            #instantiate rankings object
            rankings = {}
            for game in games:
                rankings[game.winner] = begin_elo_at
                rankings[game.loser] = begin_elo_at

            #build actual rankings
            for game in games:
                new_rankings = rate_1vs1(rankings[game.winner],rankings[game.loser])
                rankings[game.winner] = new_rankings[0]
                rankings[game.loser] = new_rankings[1]

            for player in rankings:
                rankings[player] = int(round(rankings[player],0))

            return rankings

        def _get_elo_graph(gamename):
            #setup plotly
            import random
            import plotly.plotly as py
            import plotly.graph_objs as go
            py.sign_in('slack_gamebot', 'e07cmetnop')

            #get games from ORM
            games = Game.objects.filter(gamename=gamename).order_by('created_on')

            #instantiate rankings object
            rankings = {}
            tracing = {}
            for game in games:
                tracing[game.winner] = begin_elo_at
                tracing[game.loser] = begin_elo_at
                rankings[game.winner] = begin_elo_at
                rankings[game.loser] = begin_elo_at

            x_axis = [game.created_on for game in games] + [ timezone.now() + timezone.timedelta(hours=6) ]

            #setup history object
            rankings_history = rankings.copy()
            for player in rankings_history.keys():
                rankings_history[player] = []

            #build traces
            for game in games:
                new_rankings = rate_1vs1(rankings[game.winner],rankings[game.loser])
                rankings[game.winner] = new_rankings[0]
                rankings[game.loser] = new_rankings[1]
                for player in tracing.keys():
                    rankings_history[player] =  rankings_history[player] + [rankings[player]]

            #add todays ranking
            for player in tracing.keys():
                rankings_history[player] =  rankings_history[player] + [rankings_history[player][-1]]

            traces = []
            # Create traces
            for player in tracing.keys():
                traces = traces + [ go.Scatter(
                    x = x_axis,
                    y = rankings_history[player],
                    mode = 'lines',
                    name = player
                ) ]

            # Plot!
            url = ""
            try:
                url = py.plot(traces, filename='python-datetime',auto_open=False,xTitle='Dates',yTitle='ELO Rankings',title='Leaderboard history for ' + gamename) + ".png?" + str(random.random())
            except Exception:
                pass

            return url

        def _get_user_username(message,opponentname):
            if opponentname.find('>') > 0:
                opp_userid = opponentname.replace('@','').replace('<','').replace('>','')
                opponentname = '@' + str(message.channel._client.users[opp_userid][u'name'])
            else:
                opponentname = opponentname if opponentname.find('@') != -1 else '@' + opponentname
            return opponentname

        def get_gif(type):
            if type == 'challenge':
                gifs = ['http://media0.giphy.com/media/DaNgLGo1xefu0/200.gif','http://media2.giphy.com/media/HbkT5F5CiRD3O/200.gif','http://media4.giphy.com/media/10mRi3yn0TVjGw/200.gif','http://media0.giphy.com/media/lcezaVyxCMMqQ/200.gif','http://media2.giphy.com/media/zp0nsdaiKMP4s/200.gif','http://media1.giphy.com/media/rYAr8hOdPqUqk/200.gif','http://media1.giphy.com/media/QDMBetxJ8YDvy/200.gif','http://media1.giphy.com/media/ozhDtzrmemc0w/200.gif','http://media1.giphy.com/media/rhV4HrtcNkgW4/200.gif','http://media0.giphy.com/media/dW073LLVqyUH6/200.gif','http://media2.giphy.com/media/peM7G1oWYgahW/200.gif','http://media2.giphy.com/media/E8GWazqt84V1u/200.gif','http://media2.giphy.com/media/qX3CivVQbEwo/200.gif','http://media1.giphy.com/media/Xmhz0vejtVhp6/200.gif','http://media4.giphy.com/media/CTeW3X1txg556/200.gif','http://media3.giphy.com/media/T6wZ2b32ZRORW/200.gif','http://media3.giphy.com/media/R7IYpzLLMBomk/200.gif','http://media3.giphy.com/media/DeoY3iC6VLBHG/200.gif','https://media1.giphy.com/media/l0NwKRRtGFjT9k6Q0/200.gif','https://media4.giphy.com/media/q7dp7xY7sHGCs/200.gif','https://media4.giphy.com/media/T6cP9jEs04fbW/200.gif','https://media3.giphy.com/media/xTcnT1NyU61Fpk75WU/200.gif','https://media0.giphy.com/media/Z6gwIJr7CPoqI/200.gif','https://media3.giphy.com/media/Z0Umc2aJY64XS/200.gif','https://media2.giphy.com/media/Ndy3hL4v1miMo/200.gif','https://media1.giphy.com/media/14dspyNocVyBwI/200.gif','https://media2.giphy.com/media/26tPoKcKX13IejXt6/200.gif','https://media4.giphy.com/media/lD08EuqQjc1K8/200.gif','https://media0.giphy.com/media/xTiTnCdwS6XsosHHyM/200.gif','https://media4.giphy.com/media/vdLRwjtIZ7g3K/200.gif','https://media0.giphy.com/media/VNGBU36a1vhwA/200.gif','https://media0.giphy.com/media/xTiTnin6Dlh2VGMbo4/200.gif','https://media2.giphy.com/media/phuTWDjfoXYcw/200.gif','https://media1.giphy.com/media/12TZCBBU3tFPY4/200.gif','https://media4.giphy.com/media/l7IwVljx8wgSc/200.gif','https://media0.giphy.com/media/3o85xJm1Rh6pISHhks/200.gif','https://media1.giphy.com/media/3oEdv73lmCG5GGiWxa/200.gif','https://media2.giphy.com/media/3oEdv3V0pwSlsKkKGs/200.gif','https://media3.giphy.com/media/gw3zMXiPDkOyVBsc/200.gif','https://media2.giphy.com/media/3o85xHHfQ1NiRfocCc/200.gif','https://media4.giphy.com/media/3o85xLA0jpUO3LlIc0/200.gif','https://media1.giphy.com/media/Ux15Wjv9kDRFm/200.gif','https://media1.giphy.com/media/1391lvKWNyuc9i/200.gif'] 
            elif type == 'taunt':
                gifs = ['https://media1.giphy.com/media/l0GRkpk8mcWhekrVC/200.gif' ,'https://media4.giphy.com/media/l41lKvLqu2xcYX8ly/200.gif' ,'https://media1.giphy.com/media/3o85xvq7HFBjnX3VBK/200.gif' ,'https://media2.giphy.com/media/tG4q5t4gdepjy/200.gif' ,'https://media4.giphy.com/media/YE5RrQAC1g7xm/200.gif' ,'https://media0.giphy.com/media/BFw86Be9MSWNa/200.gif' ,'https://media3.giphy.com/media/wp8DE7gpQKre0/200.gif' ,'https://media4.giphy.com/media/14wAFFW4x09qgw/200.gif' ,'https://media3.giphy.com/media/7Q8wiXGmhbXO0/200.gif' ,'https://media2.giphy.com/media/tvC9faYbQrHlS/200.gif' ,'https://media4.giphy.com/media/fCOYq0wyKeWZy/200.gif' ,'https://media0.giphy.com/media/136ttE0X1uWmsM/200.gif' ,'https://media0.giphy.com/media/86VV3ZYT1owDu/200.gif' ,'https://media0.giphy.com/media/rg22G4omR08lW/200.gif' ,'https://media0.giphy.com/media/u1hqtTKoTWVHi/200.gif' ,'https://media3.giphy.com/media/ETKSOS0KOgljO/200.gif' ,'https://media1.giphy.com/media/N4iJYIkzuIn6g/200.gif' ,'https://media4.giphy.com/media/pK1xYb8ftQZdm/200.gif' ,'https://media2.giphy.com/media/qGgu8qGWbPMkg/200.gif' ,'https://media3.giphy.com/media/FenUXhxrhGLle/200.gif' ,'https://media1.giphy.com/media/LByI6Ze8GWZKo/200.gif' ,'https://media1.giphy.com/media/uLHj9dmluha8M/200.gif' ,'https://media0.giphy.com/media/SpdOR2xwYzvYk/200.gif' ,'https://media3.giphy.com/media/kOlwMOrqkBQ6A/200.gif' ,'https://media3.giphy.com/media/WgvO9zb96dVx6/200.gif','https://media1.giphy.com/media/cnczob1SfXevK/200.gif','https://media1.giphy.com/media/HgRlGFapLl92U/200.gif','https://media3.giphy.com/media/ZOW5uliTiHwLS/200.gif','https://media0.giphy.com/media/jXAfNZqbmaEb6/200.gif','https://media2.giphy.com/media/LOpsoo3yRDHbi/200.gif','https://media1.giphy.com/media/11UV14XPbGFyCc/200.gif','https://media4.giphy.com/media/KqFsOCQZweNhK/200.gif','https://media4.giphy.com/media/qN7NZR3Q5R2mY/200.gif','https://media3.giphy.com/media/qraiyjvXXP2oM/200.gif','https://media4.giphy.com/media/VzbN9gupkkXp6/200.gif','https://media2.giphy.com/media/Qr4JSl1M86qLC/200.gif','https://media3.giphy.com/media/h38BLEj9QOx0I/200.gif','https://media0.giphy.com/media/BJMIzBe8OZyWQ/200.gif','https://media3.giphy.com/media/RSzvGBuoQRlp6/200.gif'] 
            elif type == 'winorloss':
                gifs = ['https://media1.giphy.com/media/Vs6ASalhnbomk/200.gif','https://media4.giphy.com/media/k4dmtQafDuhDG/200.gif','https://media4.giphy.com/media/6gyuq0k9zIcBG/200.gif','https://media1.giphy.com/media/11IPXDbYmRRNwk/200.gif','https://media1.giphy.com/media/13t2Pa6WECl8je/200.gif','https://media3.giphy.com/media/aHJ6uCT5aMcPS/200.gif','https://media0.giphy.com/media/s2pfpFIc6CDlu/200.gif','https://media1.giphy.com/media/11IPXDbYmRRNwk/200.gif','https://media4.giphy.com/media/M0yDGzfdQQOcg/200.gif','https://media3.giphy.com/media/YJ6TmsrR4rjOg/200.gif','https://media3.giphy.com/media/Mp19UE9GMARKE/200.gif','https://media1.giphy.com/media/fdgOAnZS81CRq/200.gif','https://media3.giphy.com/media/OetNQSs0jO7Kw/200.gif']
            else:
                gifs = ['http://media.tumblr.com/0e07ec60ce9b5f8019e7e98510e3e86e/tumblr_inline_mvq3ol2lHr1qahu1s.gif','http://38.media.tumblr.com/tumblr_ls933rtrAa1r3v6f2o1_500.gif','http://media.tumblr.com/ee3d490720837f2728e8de52094e1413/tumblr_inline_mknw21r56j1qz4rgp.gif','http://25.media.tumblr.com/ec131b67c3a55dcb99fa5e4ef5f3599b/tumblr_mmst60zClN1rhhrvto1_500.gif','http://31.media.tumblr.com/eb9e90aff682182d613737b9072f8e41/tumblr_mgo892vhpu1rk6n1go1_500.gif','http://media.tumblr.com/tumblr_mdicgvDPim1qh8ujs.gif','http://31.media.tumblr.com/f86af9c670404254ae22ab900a4c51f1/tumblr_mypy1toyaL1sgrpsuo1_500.gif','http://33.media.tumblr.com/aebeb686a640493b512c8999881d1fb5/tumblr_njzrzaICmG1s3h43ko1_500.gif','http://24.media.tumblr.com/209fafb786577f6556c8b49c1c8112e4/tumblr_mlqov0OsUf1rch0b8o1_500.gif','https://media2.giphy.com/media/l0NwIoO8LN6Pr3Ety/200.gif','https://media1.giphy.com/media/sNWGEbc5Jzp4c/200.gif','https://media3.giphy.com/media/l41m5FCBtcRpH4Djq/200.gif','https://media4.giphy.com/media/A4HCrFVdbxZpS/200.gif','https://media3.giphy.com/media/14g4EHIdeENmda/200.gif','https://media0.giphy.com/media/SF7kg7hOePkkg/200.gif','https://media3.giphy.com/media/e2wFIvRQ71MaI/200.gif','https://media2.giphy.com/media/iMlzhPDCJ7bQA/200.gif','https://media3.giphy.com/media/DTdI3KKdS8TBK/200.gif','https://media4.giphy.com/media/10h8kjAyPnGRsA/200.gif','https://media2.giphy.com/media/XKcxxxW2e075e/200.gif','https://media0.giphy.com/media/80QhlBqHx1DMs/200.gif','https://media3.giphy.com/media/14unPQFbyCdq2A/200.gif','https://media4.giphy.com/media/jgelsNvS6tYFG/200.gif','https://media1.giphy.com/media/PentDub5eQnu0/200.gif','https://media4.giphy.com/media/rCciDdJY8aTvO/200.gif','https://media2.giphy.com/media/JVC7ZSJEEpYgU/200.gif','https://media4.giphy.com/media/ef0ZKzcEPOBhK/200.gif','https://media0.giphy.com/media/kaDYxHzwxVlBK/200.gif','https://media2.giphy.com/media/MsC2pXWAPUqru/200.gif','https://media3.giphy.com/media/11nI3aybdZ9EA0/200.gif','https://media1.giphy.com/media/iGMQJxHoi9iDK/200.gif','https://media3.giphy.com/media/OYlmWQVEuM6yc/200.gif','https://media4.giphy.com/media/U90QBiNwIuV0c/200.gif']

            import random
            gifurl = random.choice (gifs)
            return gifurl

        @listen_to('^help', re.IGNORECASE)
        @listen_to('^gamebot help', re.IGNORECASE)
        @listen_to('^gb help', re.IGNORECASE)
        def help(message):
            help_message="Hello! I am a gamebot for tracking game statistics.  Here's how to use me: \n\n"+\
                " _Play_: \n" +\
                "    `challenge <@opponent> <gamename>` -- challenges @opponent to a friendly game of <gamename> \n" +\
                "    `accept <@opponent> <gamename>` -- accepts a challenge \n" +\
                "    `won <@opponent> <gamename>` -- records a win for you against @opponent \n" +\
                "    `lost <@opponent> <gamename>` -- records a loss for you against @opponent \n" +\
                "    `predict <@opponent> <gamename>` -- predict the outcome of a game between you and @opponent \n" +\
                "    `taunt <@opponent> ` -- taunt @opponent \n\n" +\
                "    Wins and losses can also be #tagged to record how things went down, e.g. `won @owocki chess #time`. Up to 5 tags can be added.\n\n" +\
                " _Stats_: \n" +\
                "    `gamebot leaderboard <gamename>` -- displays this seasons leaderboard for <gamename>\n" +\
                "    `gamebot alltime leaderboard <gamename>` -- displays the all time leaderboard for <gamename>\n" +\
                "    `gamebot history <gamename>` -- displays history for <gamename>\n\n" +\
                "    `gamebot season <gamename>` -- displays season information for <gamename>\n\n" +\
                " _About_: \n" +\
                "    `gamebot list-games` -- lists all game types that I'm keeping track of\n" +\
                "    `gamebot list-tags <gamename>` -- lists all tags associated with a specific <gamename>\n" +\
                "    `gamebot help` -- displays help menu (this thing)\n" +\
                "    `gamebot version` -- displays my software version\n\n" +\
                " You may also use the handy shortcut `gb <command>`, if you're too tired from being a champion to type `gamebot`" +\
                " " 
            message.send(help_message)


        @listen_to('^version', re.IGNORECASE)
        @listen_to('^gamebot version', re.IGNORECASE)
        @listen_to('^gb version', re.IGNORECASE)
        def version(message):
            help_message="Version 0.4 \n\n"+\
                " Version history \n" +\
                " * `0.4` -- #tags for games, more commands, cleanup output \n" +\
                " * `0.3` -- new gifs, strip() gamename input \n" +\
                " * `0.2` -- ELO, leaderboards, plotly graphs\n" +\
                " * `0.1` -- MVP \n" +\
                "More info @ https://github.com/owocki/slack_gamebot " 
            message.reply(help_message)

        def get_active_season(gamename,seasoned):
            try:
                active_season = Season.objects.get(gamename=gamename,active=True)
            except Exception as e:
                active_season = Season.objects.create(gamename=gamename,start_on = datetime.now(),active = True)
                active_season.save()

            if seasoned:
                range_start_date = active_season.start_on
            else:
                active_season = None
                range_start_date = date(2000, 1, 1)

            return active_season, range_start_date

        @listen_to('^gamebot alltime leaderboard (.*)',re.IGNORECASE)
        @listen_to('^gb alltime leaderboard (.*)', re.IGNORECASE)
        @listen_to('^alltime leaderboard (.*)',re.IGNORECASE)
        def unseasoned_leaderboard(message,gamename):
            return _leaderboard(message,gamename,False)

        @listen_to('^gamebot leaderboard (.*)',re.IGNORECASE)
        @listen_to('^gb leaderboard (.*)', re.IGNORECASE)
        @listen_to('^leaderboard (.*)',re.IGNORECASE)
        def seasoned_leaderboard(message,gamename):
            return _leaderboard(message,gamename,True)

        def _leaderboard(message,gamename,seasoned=False):
            #input sanitization
            gamename = gamename.strip()

            STATS_SIZE_LIMIT = 1000

            active_season , range_start_date = get_active_season(gamename,seasoned)

            games = Game.objects.filter(created_on__gt=range_start_date,gamename=gamename)
            if not games.count():
                message.send("No stats found for this game type {}.".format( "this season" if active_season is not None else "" ))

            players = list(set(list(games.values_list('winner',flat=True).distinct()) + list(games.values_list('loser',flat=True).distinct())))
            stats_by_user = {}
            elo_rankings = _get_elo(gamename)

            for player in players:
                stats_by_user[player] = { 'name': player, 'elo': elo_rankings[player], 'wins' : 0, 'losses': 0, 'total': 0 }

            for game in games.order_by('-created_on')[:STATS_SIZE_LIMIT]:
                stats_by_user[game.winner]['wins']+=1
                stats_by_user[game.winner]['total']+=1
                stats_by_user[game.loser]['losses']+=1
                stats_by_user[game.loser]['total']+=1

            for player in stats_by_user:
                stats_by_user[player]['win_pct'] =  round(stats_by_user[player]['wins'] * 1.0 / stats_by_user[player]['total'],2)*100

            stats_by_user = sorted(stats_by_user.items(), key=lambda x: -1 * x[1]['elo'])

            season_str = "All time" if active_season is None else "This season"
            stats_str = "\n ".join([  " * {}({}): {}/{} ({}%)".format(stats[1]['name'],stats[1]['elo'],stats[1]['wins'],stats[1]['losses'],stats[1]['win_pct'])  for stats in stats_by_user ])
            stats_str = "{} seaderboard for {}: \n\n{}\n{}".format(season_str, gamename, stats_str,_get_elo_graph(gamename))
            message.send(stats_str)

        @listen_to('^season (.*)',re.IGNORECASE)
        @listen_to('^gamebot season (.*)',re.IGNORECASE)
        @listen_to('^gb season (.*)',re.IGNORECASE)
        def season(message,gamename):
            #input sanitization
            gamename = gamename.strip()

            #close current season
            active_season, start_on = get_active_season(gamename,True)

            #msg back to users
            msg_str = "{} is active. \nUse `gamebot end season {}` to end this season.".format(active_season, gamename)
            message.send(msg_str)


        @listen_to('^end season (.*)',re.IGNORECASE)
        @listen_to('^gamebot end season (.*)',re.IGNORECASE)
        @listen_to('^gb end season (.*)',re.IGNORECASE)
        def end_season(message,gamename):
            #input sanitization
            gamename = gamename.strip()

            #close current season
            active_season, start_on = get_active_season(gamename,True)
            active_season.end_on = datetime.now()
            active_season.active = False
            active_season.save()

            #start new season
            new_season = Season.objects.create(gamename=gamename,start_on = datetime.now(),active=True)

            #msg back to users
            msg_str = "{} ended.\n\n {} opened".format(active_season,new_season)
            message.send(msg_str)


        @listen_to('^history (.*)',re.IGNORECASE)
        @listen_to('^gamebot history (.*)',re.IGNORECASE)
        @listen_to('^gb history (.*)',re.IGNORECASE)
        def history(message,gamename):
            #input sanitization
            gamename = gamename.strip()

            HISTORY_SIZE_LIMIT = 10
            history_str = "\n".join(list( [ "* " + str(game) for game in Game.objects.filter(gamename=gamename).order_by('-created_on')[:HISTORY_SIZE_LIMIT] ]  ))
            if history_str:
                history_str = "History for last {} {} games: \n\n{}".format(str(HISTORY_SIZE_LIMIT),gamename,history_str)
                message.send(history_str )
            else:
                message.send('No history found for {}'.format(gamename))

        @listen_to('^challenge (.*) (.*)',re.IGNORECASE)
        def challenge(message,opponentname,gamename):
             #input sanitization
            gamename = gamename.strip()

           #setup
            sender = "@" + message.channel._client.users[message.body['user']][u'name']
            opponentname = _get_user_username(message,opponentname)

            #body
            accept_message = "accept {} {}".format(sender,gamename)
            gifurl = get_gif('challenge')

            #send response
            this_message = "{}, {} challenged you to {}. accept like this: `{}` \n\n{}".format(opponentname,sender,gamename,accept_message,gifurl)
            message.send(this_message)

        @listen_to('^taunt (.*)',re.IGNORECASE)
        def taunt(message,opponentname):

            #setup
            sender = "@" + message.channel._client.users[message.body['user']][u'name']
            opponentname = _get_user_username(message,opponentname)

            #body
            gifurl = get_gif('taunt')

            #send response
            this_message = "{}, {} taunted you {}".format(opponentname,sender,gifurl)
            message.send(this_message)

        @listen_to('^predict (.*) (.*)',re.IGNORECASE)
        def predict(message,opponentname,gamename,seasoned=False):
            _predict(message,opponentname,gamename,True)
            _predict(message,opponentname,gamename,False)

        def _predict(message,opponentname,gamename,seasoned=False):
            #input sanitization
            gamename = gamename.strip()

            #setup
            sender = "@" + message.channel._client.users[message.body['user']][u'name']
            opponentname = _get_user_username(message,opponentname)
            active_season , range_start_date = get_active_season(gamename,seasoned)
            
            #body
            games = list(Game.objects.filter(created_on__gt=range_start_date,gamename=gamename,winner=sender,loser=opponentname))+list(Game.objects.filter(created_on__gt=range_start_date,gamename=gamename,winner=opponentname,loser=sender)) 
            if not games:
                message.send("No {} games found between {} and {}".format(gamename,sender,opponentname))
                return;
                
            stats_by_user = {}

            stats_for_sender = { 'wins' : 0, 'losses': 0, 'total': 0 }
            list_tags = []
            for game in games:
                tags = Tag.objects.filter(game=game).values_list('tag', flat=True)
                if len(tags) > 0:
                    for tag in Tag.objects.filter(game=game).values_list('tag', flat=True):
                        list_tags.append(tag)
                if game.winner == sender:
                    stats_for_sender['wins'] = stats_for_sender['wins'] + 1 
                    stats_for_sender['total'] = stats_for_sender['total'] + 1 
                else:
                    stats_for_sender['losses'] = stats_for_sender['losses'] + 1 
                    stats_for_sender['total'] = stats_for_sender['total'] + 1 

            win_pct = round(stats_for_sender['wins'] * 1.0 / stats_for_sender['total'],2)*100  
            common_tag = Counter(list_tags).most_common()
            season_str = "*all time*" if active_season is None else "*this season*"
            if not common_tag:
                this_message = "{} total {} games played between {} and {} {}. \n{} is {}% likely to win next game"\
                               .format(stats_for_sender['total'],gamename,sender,opponentname,season_str,sender,win_pct)
                message.send(this_message)
            else:                
                most_probable_tag = common_tag[0][0]
                #send response
                this_message = "{} total {} games played between {} and {}. \n{} is {}% likely to win next game by #{}"\
                               .format(stats_for_sender['total'],gamename,sender,opponentname,season_str,sender,win_pct,most_probable_tag)
                message.send(this_message)


        @listen_to('^accept (.*) (.*)',re.IGNORECASE)
        def accepted(message,opponentname,gamename):
            #input sanitization
            gamename = gamename.strip()

            #setup
            sender = "@" + message.channel._client.users[message.body['user']][u'name']
            opponentname = _get_user_username(message,opponentname)

            #body
            gifurl = get_gif('accepted')

            #send response
            this_message = "{}, {} accepted your challenge to {} \n\n{}".format(opponentname,sender,gamename,gifurl)
            message.send(this_message)


        def parseTags(message, opponentname, gamename):
            if " " in opponentname:
                if "#" not in gamename:
                    strings = opponentname.split(" ")
                    if len(strings) > 5:
                        message.send("That message is too long; I can't quite parse it :confused:")
                        return False
                    tags = ""
                    for x in range(2, len(strings)):
                        tags += "#" + strings[x] + " "
                    tags += "#" + gamename
                    message.reply("Did you mean `won {} {} {}`? I'm a bit confused...".format(strings[0], strings[1], tags))
                    return False
                # Ignore 'games' that are actually tags
                if "#" in gamename:
                    return False
            return True                


        @listen_to('won (.*) (.*)$',re.IGNORECASE)
        @listen_to('won (.*) (.*) #(.*)$',re.IGNORECASE)        
        @listen_to('won (.*) (.*) #(.*) #(.*)$',re.IGNORECASE)
        @listen_to('won (.*) (.*) #(.*) #(.*) #(.*)$',re.IGNORECASE)
        @listen_to('won (.*) (.*) #(.*) #(.*) #(.*) #(.*)$',re.IGNORECASE)
        @listen_to('won (.*) (.*) #(.*) #(.*) #(.*) #(.*) #(.*)$',re.IGNORECASE)
        @listen_to('win (.*) (.*)$',re.IGNORECASE)
        @listen_to('win (.*) (.*) #(.*)$',re.IGNORECASE)        
        @listen_to('win (.*) (.*) #(.*) #(.*)$',re.IGNORECASE)
        @listen_to('win (.*) (.*) #(.*) #(.*) #(.*)$',re.IGNORECASE)
        @listen_to('win (.*) (.*) #(.*) #(.*) #(.*) #(.*)$',re.IGNORECASE)
        @listen_to('win (.*) (.*) #(.*) #(.*) #(.*) #(.*) #(.*)$',re.IGNORECASE)
        def won(*arg):
            message = arg[0]
            opponentname = arg[1]
            gamename = arg[2]
            #input sanitization
            gamename = gamename.strip()
            if parseTags(message, opponentname, gamename) == False:
                return 

            #setup
            sender = "@" + message.channel._client.users[message.body['user']][u'name']
            opponentname = _get_user_username(message,opponentname)

            winner_old_elo = 1000
            loser_old_elo = 1000
            if gamename == "chess":
                elo_rankings = _get_elo(gamename)
                if sender in elo_rankings:
                    winner_old_elo = elo_rankings[sender]
                if opponentname in elo_rankings:
                    loser_old_elo = elo_rankings[opponentname]

            #body
            newgame = Game.objects.create(winner=sender,loser=opponentname,gamename=gamename,created_on=datetime.now(),modified_on=datetime.now())

            # Create tags for game
            if len(arg) > 3:
                for x in range(3, len(arg)):
                    Tag.objects.create(tag=arg[x], game=newgame)

            #send response
            message.send("#win recorded \n")
            if gamename == "chess":
                elo_rankings = _get_elo(gamename)
                winner_elo_diff = elo_rankings[sender] - winner_old_elo
                loser_elo_diff = elo_rankings[opponentname] - loser_old_elo
                message.send(":arrow_up: {}'s new elo: {} (+{})\n:arrow_down: {}'s new elo: {} ({})\n"\
                             .format(sender, elo_rankings[sender], winner_elo_diff, \
                                     opponentname, elo_rankings[opponentname], loser_elo_diff))


        @listen_to('lost (.*) (.*)$',re.IGNORECASE)
        @listen_to('lost (.*) (.*) #(.*)$',re.IGNORECASE)        
        @listen_to('lost (.*) (.*) #(.*) #(.*)$',re.IGNORECASE)
        @listen_to('lost (.*) (.*) #(.*) #(.*) #(.*)$',re.IGNORECASE)
        @listen_to('lost (.*) (.*) #(.*) #(.*) #(.*) #(.*)$',re.IGNORECASE)
        @listen_to('lost (.*) (.*) #(.*) #(.*) #(.*) #(.*) #(.*)$',re.IGNORECASE)
        @listen_to('loss (.*) (.*)$',re.IGNORECASE)
        @listen_to('loss (.*) (.*) #(.*)$',re.IGNORECASE)        
        @listen_to('loss (.*) (.*) #(.*) #(.*)$',re.IGNORECASE)
        @listen_to('loss (.*) (.*) #(.*) #(.*) #(.*)$',re.IGNORECASE)
        @listen_to('loss (.*) (.*) #(.*) #(.*) #(.*) #(.*)$',re.IGNORECASE)
        @listen_to('loss (.*) (.*) #(.*) #(.*) #(.*) #(.*) #(.*)$',re.IGNORECASE)
        def loss(*arg):
            message = arg[0]
            opponentname = arg[1]
            gamename = arg[2]
            #input sanitization
            gamename = gamename.strip()
            if parseTags(message, opponentname, gamename) == False:
                return 

            sender = "@" + message.channel._client.users[message.body['user']][u'name']
            opponentname = _get_user_username(message,opponentname)

            winner_old_elo = 1000
            loser_old_elo = 1000
            if gamename == "chess":
                elo_rankings = _get_elo(gamename)
                if sender in elo_rankings:
                    winner_old_elo = elo_rankings[opponentname]
                if opponentname in elo_rankings:
                    loser_old_elo = elo_rankings[sender]
            #body
            newgame = Game.objects.create(winner=opponentname,loser=sender,gamename=gamename,created_on=datetime.now(),modified_on=datetime.now())

            # Create tags for game
            if len(arg) > 3:
                for x in range(3, len(arg)):
                    Tag.objects.create(tag=arg[x], game=newgame)

            #send response
            message.send("#loss recorded \n")
            if gamename == "chess":
                elo_rankings = _get_elo(gamename)
                winner_elo_diff = elo_rankings[opponentname] - winner_old_elo
                loser_elo_diff = elo_rankings[sender] - loser_old_elo
                message.send(":arrow_up: {}'s new elo: {} (+{})\n:arrow_down: {}'s new elo: {} ({})\n"\
                             .format(opponentname, elo_rankings[opponentname], winner_elo_diff, \
                                     sender, elo_rankings[sender], loser_elo_diff))


        @listen_to('^gamebot list-games$',re.IGNORECASE)
        @listen_to('^gb list-games$',re.IGNORECASE)
        def listGames(message):
            list_message = ""
            for name in Game.objects.values_list('gamename', flat=True).distinct():
                list_message += "- {}\n".format(name)

            if list_message == "": 
                message.send("You haven't played anything yet...")
            else:
                message.send("Here are the games that I'm keeping track of:")
                message.send(list_message)


        @listen_to('^gamebot list-tags (.*)$',re.IGNORECASE)
        @listen_to('^gb list-tags (.*)$',re.IGNORECASE)
        def listTags(message,gamename):
            gamename = gamename.strip()
            if Game.objects.filter(gamename=gamename).count() == 0:
                message.send("You haven't played any games of {} yet :anguished:".format(gamename))
                return

            # Kind of messy, but it works!
            list_tags = []
            list_message = ""
            games = Game.objects.filter(gamename=gamename)
            for game in games:
                for tag in Tag.objects.filter(game=game).values_list('tag', flat=True).distinct():
                    list_tags.append(tag)
            for name in list(set(list_tags)):
                list_message += "#{}\n".format(name)

            if not list_tags:
                message.send("There are no tagged games of {} :neutral_face:".format(gamename))
            else:
                message.send("Here are the tags currently used in {}:".format(gamename))
                message.send(list_message)


        #validation helpers
        @listen_to('^history$',re.IGNORECASE)
        @listen_to('^gamebot history$',re.IGNORECASE)
        @listen_to('^gamebot list-tags$', re.IGNORECASE)
        @listen_to('^gb history$',re.IGNORECASE)
        @listen_to('^gb list-tags$', re.IGNORECASE)
        def error_history(message):
            message.reply('Please specify a gametype.')

        @listen_to('^challenge$',re.IGNORECASE)
        @listen_to('^accept$',re.IGNORECASE)
        @listen_to('^win$',re.IGNORECASE)
        @listen_to('^won$',re.IGNORECASE)
        @listen_to('^lost$',re.IGNORECASE)
        @listen_to('^loss$',re.IGNORECASE)
        def error_history_2(message):
            message.reply('Please specify a gametype and an opponent handle.')

        @listen_to('^challenge (.*)$',re.IGNORECASE)
        @listen_to('^accept (.*)$',re.IGNORECASE)
        @listen_to('^win (.*)$',re.IGNORECASE)
        @listen_to('^won (.*)$',re.IGNORECASE)
        @listen_to('^lost (.*)$',re.IGNORECASE)
        @listen_to('^loss (.*)$',re.IGNORECASE)
        def error_history_3(message,next_arg):
            #message.reply('Please specify both a gametype and an opponent handle.')
            pass

        def main():
            bot = Bot()
            bot.run()

        main()

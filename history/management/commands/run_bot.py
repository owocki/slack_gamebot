from django.core.management.base import BaseCommand, CommandError
from history.models import Game
from datetime import datetime
from elo import rate_1vs1


class Command(BaseCommand):
    help = 'Runs slackbot'

    def handle(self, *args, **options):
        from slackbot.bot import respond_to
        from slackbot.bot import listen_to
        from slackbot.bot import Bot
        import re 

        def _get_elo(gamename):
            #get games from ORM
            games = Game.objects.filter(gamename=gamename).order_by('created_on')

            #instantiate rankings object
            begin_elo_at = 1000
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

        def _get_user_username(message,opponentname):
            if opponentname.find('>') > 0:
                opp_userid = opponentname.replace('@','').replace('<','').replace('>','')
                opponentname = '@' + str(message.channel._client.users[opp_userid][u'name'])
            else:
                opponentname = opponentname if opponentname.find('@') != -1 else '@' + opponentname
            return opponentname

        def get_gif(type):
            if type == 'challenge':
                gifs = ['http://media0.giphy.com/media/DaNgLGo1xefu0/200.gif','http://media2.giphy.com/media/HbkT5F5CiRD3O/200.gif','http://media4.giphy.com/media/10mRi3yn0TVjGw/200.gif','http://media0.giphy.com/media/lcezaVyxCMMqQ/200.gif','http://media2.giphy.com/media/zp0nsdaiKMP4s/200.gif','http://media1.giphy.com/media/rYAr8hOdPqUqk/200.gif','http://media1.giphy.com/media/QDMBetxJ8YDvy/200.gif','http://media1.giphy.com/media/ozhDtzrmemc0w/200.gif','http://media1.giphy.com/media/rhV4HrtcNkgW4/200.gif','http://media0.giphy.com/media/dW073LLVqyUH6/200.gif','http://media2.giphy.com/media/peM7G1oWYgahW/200.gif','http://media2.giphy.com/media/E8GWazqt84V1u/200.gif','http://media2.giphy.com/media/qX3CivVQbEwo/200.gif','http://media1.giphy.com/media/Xmhz0vejtVhp6/200.gif','http://media4.giphy.com/media/CTeW3X1txg556/200.gif','http://media3.giphy.com/media/T6wZ2b32ZRORW/200.gif','http://media3.giphy.com/media/R7IYpzLLMBomk/200.gif','http://media3.giphy.com/media/DeoY3iC6VLBHG/200.gif'] 
            elif type == 'taunt':
                gifs = ['https://media1.giphy.com/media/l0GRkpk8mcWhekrVC/200.gif' ,'https://media4.giphy.com/media/l41lKvLqu2xcYX8ly/200.gif' ,'https://media1.giphy.com/media/3o85xvq7HFBjnX3VBK/200.gif' ,'https://media2.giphy.com/media/tG4q5t4gdepjy/200.gif' ,'https://media4.giphy.com/media/YE5RrQAC1g7xm/200.gif' ,'https://media0.giphy.com/media/BFw86Be9MSWNa/200.gif' ,'https://media3.giphy.com/media/wp8DE7gpQKre0/200.gif' ,'https://media4.giphy.com/media/14wAFFW4x09qgw/200.gif' ,'https://media3.giphy.com/media/7Q8wiXGmhbXO0/200.gif' ,'https://media2.giphy.com/media/tvC9faYbQrHlS/200.gif' ,'https://media4.giphy.com/media/fCOYq0wyKeWZy/200.gif' ,'https://media0.giphy.com/media/136ttE0X1uWmsM/200.gif' ,'https://media0.giphy.com/media/86VV3ZYT1owDu/200.gif' ,'https://media0.giphy.com/media/rg22G4omR08lW/200.gif' ,'https://media0.giphy.com/media/u1hqtTKoTWVHi/200.gif' ,'https://media3.giphy.com/media/ETKSOS0KOgljO/200.gif' ,'https://media1.giphy.com/media/N4iJYIkzuIn6g/200.gif' ,'https://media4.giphy.com/media/pK1xYb8ftQZdm/200.gif' ,'https://media2.giphy.com/media/qGgu8qGWbPMkg/200.gif' ,'https://media3.giphy.com/media/FenUXhxrhGLle/200.gif' ,'https://media1.giphy.com/media/LByI6Ze8GWZKo/200.gif' ,'https://media1.giphy.com/media/uLHj9dmluha8M/200.gif' ,'https://media0.giphy.com/media/SpdOR2xwYzvYk/200.gif' ,'https://media3.giphy.com/media/kOlwMOrqkBQ6A/200.gif' ,'https://media3.giphy.com/media/WgvO9zb96dVx6/200.gif'] 
            else:
                gifs = ['http://media.tumblr.com/0e07ec60ce9b5f8019e7e98510e3e86e/tumblr_inline_mvq3ol2lHr1qahu1s.gif','http://38.media.tumblr.com/tumblr_ls933rtrAa1r3v6f2o1_500.gif','http://media.tumblr.com/ee3d490720837f2728e8de52094e1413/tumblr_inline_mknw21r56j1qz4rgp.gif','http://25.media.tumblr.com/ec131b67c3a55dcb99fa5e4ef5f3599b/tumblr_mmst60zClN1rhhrvto1_500.gif','http://31.media.tumblr.com/eb9e90aff682182d613737b9072f8e41/tumblr_mgo892vhpu1rk6n1go1_500.gif','http://media.tumblr.com/tumblr_mdicgvDPim1qh8ujs.gif','http://31.media.tumblr.com/f86af9c670404254ae22ab900a4c51f1/tumblr_mypy1toyaL1sgrpsuo1_500.gif','http://33.media.tumblr.com/aebeb686a640493b512c8999881d1fb5/tumblr_njzrzaICmG1s3h43ko1_500.gif','http://24.media.tumblr.com/209fafb786577f6556c8b49c1c8112e4/tumblr_mlqov0OsUf1rch0b8o1_500.gif']

            import random
            gifurl = random.choice (gifs)
            return gifurl

        @listen_to('^help', re.IGNORECASE)
        @listen_to('^gamebot help', re.IGNORECASE)
        def help(message):
            help_message="I am a gamebot for tracking game statistics.  Here's how to use me: \n\n"+\
                " Playing: \n" +\
                " * `challenge <@opponent> <gamename>` -- challenges an opponent \n" +\
                " * `accept <@opponent> <gamename>` -- accepts challenge \n" +\
                " * `won <@opponent> <gamename>` -- records a win against @opponent \n" +\
                " * `lost <@opponent> <gamename>` -- records a loss against @opponent \n" +\
                " * `predict <@opponent> <gamename>` -- predict the outcome of a game against @opponent \n" +\
                " Stats: \n" +\
                " * `gamebot leaderboard <gamename>` -- displays a leaderboard\n" +\
                " * `gamebot history <gamename>` -- displays history for game\n" +\
                " Help: \n" +\
                " * `gamebot help` -- displays help menu\n" +\
                " " 
            message.reply(help_message)

        @listen_to('^gamebot leaderboard (.*)',re.IGNORECASE)
        @listen_to('^leaderboard (.*)',re.IGNORECASE)
        def leaderboard(message,gamename):
            STATS_SIZE_LIMIT = 1000

            if not Game.objects.filter(gamename=gamename).count():
                message.send("No stats found for this game type.")

            players = list(set(list(Game.objects.filter(gamename=gamename).values_list('winner',flat=True).distinct()) + list(Game.objects.filter(gamename=gamename).values_list('loser',flat=True).distinct())))
            stats_by_user = {}
            elo_rankings = _get_elo(gamename)

            for player in players:
                stats_by_user[player] = { 'name': player, 'elo': elo_rankings[player], 'wins' : 0, 'losses': 0, 'total': 0 }

            for game in Game.objects.filter(gamename=gamename).order_by('-created_on')[:STATS_SIZE_LIMIT]:
                stats_by_user[game.winner]['wins']+=1
                stats_by_user[game.winner]['total']+=1
                stats_by_user[game.loser]['losses']+=1
                stats_by_user[game.loser]['total']+=1

            for player in stats_by_user:
                stats_by_user[player]['win_pct'] =  round(stats_by_user[player]['wins'] * 1.0 / stats_by_user[player]['total'],2)*100

            stats_by_user = sorted(stats_by_user.items(), key=lambda x: -1 * x[1]['elo'])

            stats_str = "\n ".join([  " * {}({}): {}/{} ({}%)".format(stats[1]['name'],stats[1]['elo'],stats[1]['wins'],stats[1]['losses'],stats[1]['win_pct'])  for stats in stats_by_user ])
            stats_str = "Stats for {}: \n\n{}".format(gamename, stats_str)
            message.send(stats_str)

        @listen_to('^history (.*)',re.IGNORECASE)
        @listen_to('^gamebot history (.*)',re.IGNORECASE)
        def history(message,gamename):
            HISTORY_SIZE_LIMIT = 10
            history_str = "\n".join(list( [ "* " + str(game) for game in Game.objects.filter(gamename=gamename).order_by('-created_on')[:HISTORY_SIZE_LIMIT] ]  ))
            if history_str:
                history_str = "History for last {} {} games: \n\n{}".format(str(HISTORY_SIZE_LIMIT),gamename,history_str)
                message.send(history_str )
            else:
                message.send('No history found for {}'.format(gamename))

        @listen_to('^challenge (.*) (.*)',re.IGNORECASE)
        def challenge(message,opponentname,gamename):
            #setup
            sender = "@" + message.channel._client.users[message.body['user']][u'name']
            opponentname = _get_user_username(message,opponentname)

            #body
            accept_message = "accept {} {}".format(sender,gamename)
            gifurl = get_gif('challenge')

            #send response
            this_message = "{}, {} challenged you to a game of {}. accept like this: `{}` \n\n{}".format(opponentname,sender,gamename,accept_message,gifurl)
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
        def predict(message,opponentname,gamename):
            #setup
            sender = "@" + message.channel._client.users[message.body['user']][u'name']
            opponentname = _get_user_username(message,opponentname)
            
            #body
            games = list(Game.objects.filter(gamename=gamename,winner=sender,loser=opponentname))+list(Game.objects.filter(gamename=gamename,winner=opponentname,loser=sender)) 
            if not games:
                message.send("No {} games found between {} and {}".format(gamename,sender,opponentname))
                return;
                
            stats_by_user = {}

            stats_for_sender = { 'wins' : 0, 'losses': 0, 'total': 0 }
            for game in games:
                if game.winner == sender:
                    stats_for_sender['wins'] = stats_for_sender['wins'] + 1 
                    stats_for_sender['total'] = stats_for_sender['total'] + 1 
                else:
                    stats_for_sender['losses'] = stats_for_sender['losses'] + 1 
                    stats_for_sender['total'] = stats_for_sender['total'] + 1 

            #send response
            win_pct = round(stats_for_sender['wins'] * 1.0 / stats_for_sender['total'],2)*100
            this_message = "{} total {} games played between {} vs {}.  {} is {}% likely to win next game".format(stats_for_sender['total'],gamename,sender,opponentname,sender,win_pct)
            message.send(this_message)

        @listen_to('^accept (.*) (.*)',re.IGNORECASE)
        def accepted(message,opponentname,gamename):
            #setup
            sender = "@" + message.channel._client.users[message.body['user']][u'name']
            opponentname = _get_user_username(message,opponentname)

            #body
            gifurl = get_gif('accepted')

            #send response
            this_message = "{}, {} accepted your challenge to a game of {} \n\n{}".format(opponentname,sender,gamename,gifurl)
            message.send(this_message)

        @listen_to('^won (.*) (.*)',re.IGNORECASE)
        @listen_to('^win (.*) (.*)',re.IGNORECASE)
        def won(message,opponentname,gamename):
            #setup
            sender = "@" + message.channel._client.users[message.body['user']][u'name']
            opponentname = _get_user_username(message,opponentname)

            #body
            Game.objects.create(winner=sender,loser=opponentname,gamename=gamename,created_on=datetime.now(),modified_on=datetime.now())

            #send response
            message.send("#win recorded")

        @listen_to('^lost (.*) (.*)',re.IGNORECASE)
        @listen_to('^loss (.*) (.*)',re.IGNORECASE)
        def loss(message,opponentname,gamename):
            sender = "@" + message.channel._client.users[message.body['user']][u'name']
            opponentname = _get_user_username(message,opponentname)
            
            #body
            Game.objects.create(winner=opponentname,loser=sender,gamename=gamename,created_on=datetime.now(),modified_on=datetime.now())

            #send response
            message.send("#loss recorded")

        #validation helpers
        @listen_to('^stats$',re.IGNORECASE)
        @listen_to('^history$',re.IGNORECASE)
        @listen_to('^gamebot stats$',re.IGNORECASE)
        @listen_to('^gamebot history$',re.IGNORECASE)
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
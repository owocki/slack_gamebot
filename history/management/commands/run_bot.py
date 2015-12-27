from django.core.management.base import BaseCommand, CommandError
from history.models import Game
from datetime import datetime

class Command(BaseCommand):
    help = 'Runs slackbot'

    def handle(self, *args, **options):
        from slackbot.bot import respond_to
        from slackbot.bot import listen_to
        from slackbot.bot import Bot
        import re 

        def get_gif(type):
            if type == 'challenge':
                gifs = ['http://media0.giphy.com/media/DaNgLGo1xefu0/200.gif','http://media2.giphy.com/media/HbkT5F5CiRD3O/200.gif','http://media4.giphy.com/media/10mRi3yn0TVjGw/200.gif','http://media0.giphy.com/media/lcezaVyxCMMqQ/200.gif','http://media2.giphy.com/media/zp0nsdaiKMP4s/200.gif','http://media1.giphy.com/media/rYAr8hOdPqUqk/200.gif','http://media1.giphy.com/media/QDMBetxJ8YDvy/200.gif','http://media1.giphy.com/media/ozhDtzrmemc0w/200.gif','http://media1.giphy.com/media/rhV4HrtcNkgW4/200.gif','http://media0.giphy.com/media/dW073LLVqyUH6/200.gif','http://media2.giphy.com/media/peM7G1oWYgahW/200.gif','http://media2.giphy.com/media/E8GWazqt84V1u/200.gif','http://media2.giphy.com/media/qX3CivVQbEwo/200.gif','http://media1.giphy.com/media/Xmhz0vejtVhp6/200.gif','http://media4.giphy.com/media/CTeW3X1txg556/200.gif','http://media3.giphy.com/media/T6wZ2b32ZRORW/200.gif','http://media3.giphy.com/media/R7IYpzLLMBomk/200.gif','http://media3.giphy.com/media/DeoY3iC6VLBHG/200.gif'] 
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
                " Stats: \n" +\
                " * `gamebot leaderboard <gamename>` -- displays a leaderboard\n" +\
                " * `gamebot history <gamename>` -- displays history for game\n" +\
                " Help: \n" +\
                " * `gamebot help` -- displays help menu\n" +\
                " " 
            message.reply(help_message)

        @listen_to('^gamebot leaderboard ([@a-zA-z0-9]*)',re.IGNORECASE)
        @listen_to('^leaderboard ([@a-zA-z0-9]*)',re.IGNORECASE)
        def leaderboard(message,gamename):
            STATS_SIZE_LIMIT = 1000

            if not Game.objects.filter(gamename=gamename).count():
                message.send("No stats found for this game type.")

            players = list(set(list(Game.objects.filter(gamename=gamename).values_list('winner',flat=True).distinct()) + list(Game.objects.filter(gamename=gamename).values_list('loser',flat=True).distinct())))
            stats_by_user = {}

            for player in players:
                stats_by_user[player] = { 'name': player, 'wins' : 0, 'losses': 0, 'total': 0 }

            for game in Game.objects.filter(gamename=gamename).order_by('-created_on')[:STATS_SIZE_LIMIT]:
                stats_by_user[game.winner]['wins']+=1
                stats_by_user[game.winner]['total']+=1
                stats_by_user[game.loser]['losses']+=1
                stats_by_user[game.loser]['total']+=1

            for player in stats_by_user:
                stats_by_user[player]['win_pct'] =  round(stats_by_user[player]['wins'] * 1.0 / stats_by_user[player]['total'],2)*100

            stats_by_user = sorted(stats_by_user.items(), key=lambda x: -1 * x[1]['win_pct'])

            stats_str = "\n ".join([  " * {}: {}/{} ({}%)".format(stats[1]['name'],stats[1]['wins'],stats[1]['losses'],stats[1]['win_pct'])  for stats in stats_by_user ])
            stats_str = "Stats for {}: \n\n{}".format(gamename, stats_str)
            message.send(stats_str)

        @listen_to('^history ([@a-zA-z0-9]*)',re.IGNORECASE)
        @listen_to('^gamebot history ([@a-zA-z0-9]*)',re.IGNORECASE)
        def challenge(message,gamename):
            HISTORY_SIZE_LIMIT = 10
            history_str = "\n".join(list( [ "* " + str(game) for game in Game.objects.filter(gamename=gamename).order_by('-created_on')[:HISTORY_SIZE_LIMIT] ]  ))
            if history_str:
                history_str = "History for last {} {} games: \n\n{}".format(str(HISTORY_SIZE_LIMIT),gamename,history_str)
                message.send(history_str )
            else:
                message.send('No history found for {}'.format(gamename))

        @listen_to('^challenge ([@a-zA-z0-9]*) ([@a-zA-z0-9]*)',re.IGNORECASE)
        def challenge(message,opponentname,gamename):
            #setup
            sender = "@" + message.channel._client.users[message.body['user']][u'name']
            opponentname = opponentname if opponentname.find('@') != -1 else '@' + opponentname

            #body
            accept_message = "accept {} {}".format(sender,gamename)
            gifurl = get_gif('challenge')

            #send response
            this_message = "{}, {} challenged you to a game of {}. accept like this: `{}` \n\n{}".format(opponentname,sender,gamename,accept_message,gifurl)
            message.send(this_message)

        @listen_to('^accept ([@a-zA-z0-9]*) ([@a-zA-z0-9]*)',re.IGNORECASE)
        def accepted(message,opponentname,gamename):
            #setup
            sender = "@" + message.channel._client.users[message.body['user']][u'name']
            opponentname = opponentname if opponentname.find('@') != -1 else '@' + opponentname

            #body
            gifurl = get_gif('accepted')

            #send response
            this_message = "{}, {} accepted your challenge to a game of {} \n\n{}".format(opponentname,sender,gamename,gifurl)
            message.send(this_message)

        @listen_to('^won ([@a-zA-z0-9]*) ([@a-zA-z0-9]*)',re.IGNORECASE)
        @listen_to('^win ([@a-zA-z0-9]*) ([@a-zA-z0-9]*)',re.IGNORECASE)
        def won(message,opponentname,gamename):
            #setup
            sender = "@" + message.channel._client.users[message.body['user']][u'name']
            opponentname = opponentname if opponentname.find('@') != -1 else '@' + opponentname

            #body
            Game.objects.create(winner=sender,loser=opponentname,gamename=gamename,created_on=datetime.now(),modified_on=datetime.now())

            #send response
            message.send("#win recorded")

        @listen_to('^lost ([@a-zA-z0-9]*) ([@a-zA-z0-9]*)',re.IGNORECASE)
        @listen_to('^loss ([@a-zA-z0-9]*) ([@a-zA-z0-9]*)',re.IGNORECASE)
        def loss(message,opponentname,gamename):
            sender = "@" + message.channel._client.users[message.body['user']][u'name']
            opponentname = opponentname if opponentname.find('@') != -1 else '@' + opponentname

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

        @listen_to('^challenge ([@a-zA-z0-9]*)$',re.IGNORECASE)
        @listen_to('^accept ([@a-zA-z0-9]*)$',re.IGNORECASE)
        @listen_to('^win ([@a-zA-z0-9]*)$',re.IGNORECASE)
        @listen_to('^won ([@a-zA-z0-9]*)$',re.IGNORECASE)
        @listen_to('^lost ([@a-zA-z0-9]*)$',re.IGNORECASE)
        @listen_to('^loss ([@a-zA-z0-9]*)$',re.IGNORECASE)
        def error_history_3(message,next_arg):
            message.reply('Please specify both a gametype and an opponent handle.')

        def main():
            bot = Bot()
            bot.run()

        main()
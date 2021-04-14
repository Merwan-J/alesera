from telegram.ext import *
from telegram import *
# import requests
from telethon import TelegramClient, events

import re
import json
import time
import logging
import mongoengine
import datetime
import emoji
import configparser
import os

from db.users import Seeker
from db.jobs import Post
from db.job_types import JobType

from keyboards import *
# config = configparser.ConfigParser()
# config.read('config.ini')

# db_url = config['db']['db_url']
# api_id = config.getint('telegram_api', 'api_id')
# api_hash = config['telegram_api']['api_hash']
# TOKEN = config['bot_api']['token']

PORT = int(os.environ.get('PORT', 5000))

db_url = 'mongodb+srv://merwan:n8Bu9xq4AJResU4m@alesera.5idrx.mongodb.net/alesera?retryWrites=true&w=majority'
db = 'alesera'
mongoengine.connect(alias='user-db-alias',db=db, host=db_url)
mongoengine.connect(alias='jobtype-db-alias',db=db, host=db_url)
mongoengine.connect(alias='post-db-alias',db=db, host=db_url)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

api_id = 3883924
api_hash = '00c46303da8d943ccf5c88f7172efee9'


client = TelegramClient('anon', api_id, api_hash)
print(client)




def admin(update,context):
    bot=context.bot
    user_id = update.effective_user.id

    if user_id != 323726825:
        bot.send_message(
            chat_id = user_id,
            text= emoji.emojize('ACCESS DENIED :anger_symbol:', use_aliases=True)
        )
    else:
        bot.send_message(
            chat_id = user_id,
            text= "Welcome Admin!"
        )


def start(updates, context):
    bot = context.bot
    try:
        user = Seeker.objects.get(user_id=update.effective_user.id)
        username = " " + str(user.username) if user.username else ""
        keyboard = [InlineKeyboardButton("Show Me",callback_data="show me")]
        open_jobs=[]
        for obj_id in user.jobs_not_seen:
            job = Job(id=obj_id)
            if job.job_status.lower() == 'open':
                open_jobs.append(obj_id)
    
        bot.send_photo(
            chat_id = updates.effective_user.id,
            photo = 'AgACAgQAAxkBAAIEzGBXWNc11AgVXU9UYaCbFlvNvTSDAAKNtjEbu9LBUmUEi5oVvqnd7wL4KF0AAwEAAwIAA20AA3bjBAABHgQ',
            caption=f"<b>Hey{username}!\nWelcome to Back to Ale Sera Bot!</b> \nYou have got {str(len(open_jobs))} Jobs under {user.job_type}\nCheck them out!",
            reply_markup=InlineKeyboardMarkup([keyboard]),
            parse_mode=ParseMode.HTML
                       )
    except:
        register_keyboard = [InlineKeyboardButton("Register",callback_data="register")]
        reply_markup = InlineKeyboardMarkup([register_keyboard])
        bot.send_photo(
            chat_id = updates.effective_user.id,
            photo = 'AgACAgQAAxkBAAIEzGBXWNc11AgVXU9UYaCbFlvNvTSDAAKNtjEbu9LBUmUEi5oVvqnd7wL4KF0AAwEAAwIAA20AA3bjBAABHgQ',
            caption="<b>Welcome to Ale Sera Bot!</b> \nClick on the Register button to get notified everytime a new job of your need is available.",
            reply_markup=reply_markup ,
            parse_mode=ParseMode.HTML
        )


def regex_fun(text):
    # get me everything that is not a new line(since I saw no multi line title job type company and closed tag) so yea
    status = '.+closed.+'
    title = 'Job Title: (.+)'
    company = 'Company: (.+)'
    job_type = 'Job Type: (.+)'
    description = 'Description: ([\W\w\s]+)\n\n#'
    pattern_list = [status,title,company,job_type,description]
    match_list = []
    return_list = []
    for i in pattern_list:
        match_list.append(re.findall(i,text))
    for i in range(len(match_list)):
        try:
            return_list.append(match_list[i][0])
        except IndexError:
            return_list.append(match_list[i])
    return {'status':return_list[0] if return_list[0] else 'Open', 'title':return_list[1],
            'company':return_list[2], 'type':return_list[3], 'description':return_list[4]}


def get_job_type(title):
    """ this function takes job title as its parameter. Then gets all jobtypes from db and again gets those certain
    keys and checks if the are in job title """
    the_job_type = ""
    jobtypes = JobType.objects.all()
    
    for jobtype in jobtypes:
        for key in jobtype.keys:
            if key in title.lower():
                the_job_type = jobtype.name.lower()
    if the_job_type:
        return the_job_type
    else:
        return 'others'

def check_for_users(title):
    jobtype = get_job_type(title)
    users_qs = Seeker.objects.filter(job_type=jobtype)
    user_id_list = []
    if users_qs:
        for user in users_qs:
            user_id_list.append(user.user_id)
    return user_id_list


def close_job(job_dic,demanders,msg_id,from_chat_id):
    try:
        job = Post.objects.get(status='Open',job_title=job_dic['title'],
                               company=job_dic['company'],
                               description=job_dic['description'])
        job.status = 'Closed'
        job.save()
    except:
        register_job(job_dic,demanders,msg_id,from_chat_id,'closed')


def notify_users(update, context,job,filtered_users):
    bot = context.bot
    keyboard = [[InlineKeyboardButton("Show Me!", callback_data='show me')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    for id in filtered_users:
        user = Seeker.objects.get(user_id=id)
        user.jobs_not_seen.append(job.id)
        last_msg = bot.send_message(chat_id=id,
                                    text=f"You have got {str(len(user.jobs_not_seen))} Jobs under {user.job_type}\nCheck them out!",
                                    reply_markup=reply_markup)
        if user.last_message_id:
            if int(user.last_message_id)+2 == last_msg.message_id:
                bot.deleteMessage(chat_id=id,message_id=user.last_message_id)
        user.last_message_id = last_msg.message_id
        user.save()


def register_job(job_dict, demanders,msg_id,from_chat_id,status='open'):
    try:
        job = Post.objects.get(
              job_title=job_dict['title'],job_type=job_dict['type'],
              description=job_dict['description'],company=job_dict['company'] if job_dict['company'] else "",
              category=get_job_type(job_dict['title']),job_status=status)
    except:
        job_type = get_job_type(job_dict['title'])
        job = Post(message_id=msg_id,
              job_title=job_dict['title'],job_type=job_dict['type'],
              description=job_dict['description'],company=job_dict['company'] if job_dict['company'] else "",
              demanding_users = demanders, from_chat_id=from_chat_id,category=job_type,job_status=status)
        job.save()
    return job


# this is the function that handles the job update and do all the neccesary stuff
def fwd_msg_handler(update, context):
    bot = context.bot
    user_id = update.effective_user.id
    msg_id = update.message.message_id
    from_chat_id = update.message.chat_id
    chat_id = update.effective_chat.id

    if user_id != 931262932:
        bot.send_message(
            chat_id = user_id,
            text= "Unrecognised Command!!! \nNeed Help? click here -> /help"
        )
    # the message is a forwarded message from the channel
    # so call the regex function and then check the database for users
    else:
    #"https://t.me/freelance_ethio/{update.message.message_id}"
        print("recieved the job")
        rgx_dict = regex_fun(update.message.text)
        if rgx_dict['status'].lower() == 'open':
            filtered_users = check_for_users(rgx_dict['title'])
            job = register_job(rgx_dict,len(filtered_users),msg_id,from_chat_id)
            if filtered_users:
                notify_users(update,context,job,filtered_users)
        elif rgx_dict['status'].lower() == 'closed':
            close_job(rgx_dict,len(filtered_users),msg_id,from_chat_id)


def register_user(user_id, username, job_type):
    user = Seeker(user_id=user_id, username=str(username),job_type=job_type.lower())
    user.save()
    jobs = Post.objects.filter(category=job_type,job_status='open')
    if jobs:
        for job in jobs:
            job.demanding_users += 1
            job.save()


def showme(update,context, user_id):
    # this is where the most fucked up code starts
    # so I decided to do 2 loops and some shitty code as well good luck
    # for some reason when I loop over jobs not seen it gets out of index where in reality it is not
    bot = context.bot
    user = Seeker.objects.get(user_id=user_id)
    jobs_not_seen = user.jobs_not_seen

    for obj_id in jobs_not_seen:
        job = Post.objects.get(id=obj_id)
        msg = bot.forward_message(chat_id=user_id,
                    from_chat_id=job.from_chat_id,
                    message_id=job.message_id)
        user.jobs_seen.append(job.id)
        user.jobs_not_seen.remove(job.id)
        user.save()
    jobs_not_seen = user.jobs_not_seen

    if jobs_not_seen:
        job = Post.objects.get(id=obj_id)
        for obj_id in jobs_not_seen:
            msg = bot.forward_message(chat_id=user_id,
                    from_chat_id=job.from_chat_id,
                    message_id=job.message_id)
            user.jobs_seen.append(job.id)
            user.save()


    

    reply_markup = InlineKeyboardMarkup(menu_keyboard)
    bot.send_message(chat_id=user_id,
                    text="You're all Caught Up!",
                    reply_markup=reply_markup
                    )
    user.jobs_not_seen = []
    user.save()


def get_jobs_by_status(update, context, user_id,status):
    print("inside get_jobs by status")
    print(status)
    bot = context.bot
    query = update.callback_query
    user = Seeker.objects.get(user_id=user_id)
    print(user.job_type)
    jobs = Post.objects.filter(category=user.job_type.lower(),job_status=status)
    print(jobs)

    reply_markup = InlineKeyboardMarkup(menu_keyboard)
    if jobs:
        for job in jobs:
            msg = bot.forward_message(chat_id=user_id,
                        from_chat_id=job.from_chat_id,
                        message_id=job.message_id)
        bot.send_message(chat_id=user_id,text="You're All Caught Up!",reply_markup=reply_markup)


    elif not jobs and status=='open':
        query.edit_message_text(text='No Jobs Available for now!',reply_markup=reply_markup)

    else:
        query.edit_message_text(text='All Jobs are Open, No closed Jobs!',reply_markup=reply_markup)

def other_jobs(update, context, user_id, job_type):
    bot = context.bot
    query = update.callback_query
    jobs = Post.objects.filter(category=job_type,job_status='open')
    if jobs:
        for job in jobs:
            bot.forward_message(chat_id=user_id,
                    from_chat_id=job.from_chat_id,
                    message_id=job.message_id)
        reply_markup = InlineKeyboardMarkup(menu_keyboard)
        bot.send_message(chat_id=user_id,
                    text="You're all Caught Up!",
                    reply_markup=reply_markup
                    )
    else:
        reply_markup = InlineKeyboardMarkup(menu_keyboard)
        query.edit_message_text(
                    text="No jobs available for now",
                    reply_markup=reply_markup
                    )

def get_user_profile(update, context, user_id):
    bot = context.bot
    query = update.callback_query
    user = Seeker.objects.get(user_id=user_id)
    username = user.username
    date_registered = user.date_registered
    job_type = user.job_type   

    text = f"""
    Username: @{username}
UserID: {user_id}
Date Registered: {date_registered}
Job Type: {job_type}
    """
    keyboard = [
                    [InlineKeyboardButton("Change Job Type",callback_data="update profile"),
                    InlineKeyboardButton("Back",callback_data="back")
                    ],
                    [InlineKeyboardButton("Main Menu",callback_data="main menu")],
                ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text = text,
        reply_markup = reply_markup
    )

def get_bot_status(update,context,user_id):
    bot = context.bot
    query = update.callback_query
    total_users = Seeker.objects.count()
    job_type = Seeker.objects.get(user_id=user_id).job_type
    jobs = Post.objects.filter(category=job_type.lower())
    total_jobs = Post.objects.count()
    if jobs:
        job_seekers = jobs[0].demanding_users
    else:
        job_seekers = 1
    
    text = f"""
    Total Job Seekers: {total_users}

Total Available Jobs: {total_jobs}

Total {job_type} Job Seekers: {job_seekers}

Total Available {job_type} Jobs: {jobs.count()}



More Analytics Features Will be Added Soon
"""
    reply_markup = InlineKeyboardMarkup(after_menu_keyboard)
    query.edit_message_text(text=text,reply_markup=reply_markup)


def about(update,context):
    bot = context.bot
    query = update.callback_query
    user_id = update.effective_user.id

    text = """
    This bot is created to ease the the tiring process of job searching.

All Jobs the Bot sends are from a telegram channel @freelance_ethio.

Bot is created by @MerwanJ
    """

    reply_markup = InlineKeyboardMarkup(after_menu_keyboard)
    query.edit_message_text(text=text,reply_markup=reply_markup)



def update_profile(update,context):
    bot = context.bot
    query = update.callback_query
    reply_markup = InlineKeyboardMarkup(job_keyboard)
    query.edit_message_text(text="Please Select One:",reply_markup=reply_markup)


def button(update, context) -> None:
    bot = context.bot
    user_id = update.effective_user.id
    username = update.effective_user.username
    query = update.callback_query
    query.answer(text=f"you selected option {query.data}")
    if query.data == 'register':
        reply_markup = InlineKeyboardMarkup(job_keyboard)
        context.bot.send_message(update.effective_user.id,'Please Select One:', reply_markup=reply_markup)


    elif query.data == 'show me':
        showme(update,context,user_id)

    elif query.data == 'open jobs':
        print("inside of open jobs")
        get_jobs_by_status(update,context,user_id,'open')
    
    elif query.data == 'closed jobs':
        get_jobs_by_status(update,context,user_id,'close')

    elif query.data == 'other jobs':
        reply_markup = InlineKeyboardMarkup(other_job_keyboard)
        query.edit_message_text(
                    text="Please Select One",
                    reply_markup=reply_markup
                    )
    elif query.data.startswith('other'):
        job_type = 'other (.+)'
        job_type = re.findall(job_type,query.data)[0].lower()
        other_jobs(update,context,user_id,job_type)
        
    elif query.data == 'main menu':
        reply_markup = InlineKeyboardMarkup(after_menu_keyboard)
        query.edit_message_text(
                    text="Main Menu",
                    reply_markup=reply_markup
                    )
    elif query.data == 'back':
        reply_markup = InlineKeyboardMarkup(menu_keyboard)
        query.edit_message_text(
                    text="Options",
                    reply_markup=reply_markup
                    )

    elif query.data == 'profile':
        get_user_profile(update,context,user_id)
    elif query.data == 'update profile':
        update_profile(update,context)
    elif query.data == 'about':
        about(update,context)
    elif query.data == 'bot status':
        get_bot_status(update,context,user_id)
    else:
        print("inside the field choice #######################")
        job_type = query.data
        print(job_type,"#########################")
        
        reply_markup = InlineKeyboardMarkup(menu_keyboard)
        query.edit_message_text(text=f"You have selected {job_type} You will be Notified when there is a new job available",
                                parse_mode=ParseMode.MARKDOWN,reply_markup=reply_markup
                                )
        try:
            user = Seeker.objects.get(user_id=user_id)
            user.job_type = job_type
            user.save()
        except:
            register_user(user_id,username,job_type)
            
        print("after the editing ########################")
        
    print("at the end of the button function s")

def main():
    TOKEN = "1633317216:AAH6Hv95bENbVQlWAmVzx5IqtLj1v2j_HyU"
    bot = Bot(TOKEN)
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('admin', admin))
    dp.add_handler(MessageHandler(Filters.forwarded,fwd_msg_handler,run_async=True))
    dp.add_handler(CallbackQueryHandler(button,run_async=True))

#     @client.on(events.NewMessage(from_users=(-1001404646371)))
#     async def my_event_handler(event):
#         msg = event.message
#         bot_id = 1633317216
#         channel_username = 'chillhabesha'
#         await client.forward_messages(bot_id,msg)

   
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://alesera.herokuapp.com/' + TOKEN)
#     client.start()
#     print("####################################### client started")
    
#     client.run_until_disconnected()
#     print("####################################### client run until disconected")
    
    updater.idle()
    print("####################################### updater idle")





if __name__ == '__main__':
    main()

from telegram.ext import *
from telegram import *


job_keyboard = [
        [
            InlineKeyboardButton("Software developer", callback_data='software developer'),
            InlineKeyboardButton("Social media manager", callback_data='Social media manage'),
        ],
        [InlineKeyboardButton("Accountant", callback_data='Accountant'),
         InlineKeyboardButton("Archtiet", callback_data='Archtiet'),
         InlineKeyboardButton("Translator", callback_data='Translator'),
        ],
        
        [
        
        InlineKeyboardButton("Graphic Designer", callback_data='Graphic Designer'),
        InlineKeyboardButton("Sales", callback_data='Sales'),


        ],

        [InlineKeyboardButton("Teacher", callback_data='Teacher'),
         InlineKeyboardButton("Doctor", callback_data='Doctor'),
         InlineKeyboardButton("Nurse", callback_data='Nurse'),
        ],

        [
         InlineKeyboardButton("Assistant", callback_data='Assistant'),
         InlineKeyboardButton("Tutor", callback_data='Tutor'),
         InlineKeyboardButton("Others", callback_data='Others'),
        ],
        ]


other_job_keyboard = [
        [
            InlineKeyboardButton("Software developer", callback_data='other software developer'),
            InlineKeyboardButton("Social media manager", callback_data='other Social media manage'),
        ],
        [InlineKeyboardButton("Accountant", callback_data='other Accountant'),
         InlineKeyboardButton("Archtiet", callback_data='other Archtiet'),
         InlineKeyboardButton("Translator", callback_data='other Translator'),
        ],
        
        [
        
        InlineKeyboardButton("Graphic Designer", callback_data='other Graphic Designer'),
        InlineKeyboardButton("Sales", callback_data='other Sales'),


        ],

        [InlineKeyboardButton("Teacher", callback_data='other Teacher'),
         InlineKeyboardButton("Doctor", callback_data='other Doctor'),
         InlineKeyboardButton("Nurse", callback_data='other Nurse'),
        ],

        [
         InlineKeyboardButton("Assistant", callback_data='other Assistant'),
         InlineKeyboardButton("Tutor", callback_data='other Tutor'),
         InlineKeyboardButton("Others", callback_data='other Others'),
        ],
        ]
 



menu_keyboard = [
                    [InlineKeyboardButton("Available Jobs",callback_data="open jobs"),
                    InlineKeyboardButton("Closed Jobs",callback_data="closed jobs")
                    ],
                    [InlineKeyboardButton("Main Menu",callback_data="main menu")],
                ]

after_menu_keyboard = [
                    [InlineKeyboardButton("Other Available Jobs",callback_data="other jobs")
                    ],
                    [InlineKeyboardButton(" 🧑‍💻👩‍💻  My Profile   ",callback_data="profile"),
                    InlineKeyboardButton("  Analysis  ",callback_data="bot status")],
                    [InlineKeyboardButton("About",callback_data="about"),
                    InlineKeyboardButton("Back",callback_data="back")],
                ]



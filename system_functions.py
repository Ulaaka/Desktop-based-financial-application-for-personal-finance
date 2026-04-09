import random, os
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from database_connection import database

class system_functions:

    """
    Manages the functions for authentication the user
    """

    def __init__(self):
        connection = database()
        self.db = connection.db
        self.cursor = connection.cursor

    # Generates random digits for user authentication for 2FA
    def generate_random_digits(self, digits_size):
        digits_string = ''
        for i in range(digits_size):
            number = random.randint(0, 9)
            digits_string+=str(number)

        return digits_string

    # https://sendlayer.com/blog/how-to-send-email-with-django/
    # Sends the random digits the users email
    def send_reset_digits(self, digits_size, username=None, userID=None):
        try:
            email_query = "SELECT email_address FROM users WHERE username = %s"
            self.cursor.execute(email_query, (username, ))
            user_email = self.cursor.fetchone()[0]

            number = self.generate_random_digits(digits_size)
            subject = "Reset Password"
            html_message = render_to_string('registration/reset_form.html', {
                'user_email': user_email,
                'site_name': 'Finance App',
                'number': number
            })

            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email='batzayabtrdn@gmail.com',
                to=[user_email]
            )
            email.content_subtype = 'html'
            email.send()
            print("random digits is successfully sent")
            print(number)
            return number
        except:
            return None

class manage_seconds_qt():
    def __init__(self, label, timer, duration, expire_func=None):
        self.duration = duration
        self.timer = timer
        self.label = label
        self.expire_func = expire_func

    def begin_timer(self):
        self.remaining = self.duration
        self.timer.timeout.connect(self.time_out)
        self.timer.start(1000)

    def time_out(self):
        self.remaining -= 1
        if self.remaining == 0:
            self.remaining = self.duration
            if self.expire_func:
                self.expire_func()
        self.update_label()

    def update_label(self):
        time = self.convert_secs(self.remaining)
        self.label.setText(time)

    def convert_secs(self, seconds):
        return f'{seconds // 60:02}:{seconds % 60:02}'
class ui_support_functions:
    color_dic = {
        "login_page": {
            "title_color" :"#32CD32",
            "background_color":"#000000",
            "login_button_color":{
                "normal":"#32CD32",
                "focus":"#00FF7F"
            },
            "sign_up_button_color":{
                "normal":"#1877F2",
                "focus":"#18d5f2"
            }
        },
        "sign_up_page":{
            "title_color":"#1877F2",
            "background_color":"#000000",
            "submit_button_color":{
                "normal":"#1877F2",
                "focus":"#18d5F2"
            }
        },
        "validation_page":{
            "title_color":"#1877F2",
            "background_color":"#000000",
            "submit_button_color":{
                "normal":"#1877F2",
                "focus":"#18d5F2"
            }
        },
        'reset_password':{
            "title_color":"#1877F2",
            "background_color":"#000000",
            "submit_button_color":{
                "normal":"#1877F2",
                "focus":"#18d5F2"
            }
        }}

    # if underline_button, button_color = "transparent"
    def handle_button_style(if_handle, button_color, hover_color, underline_flag=None):
            handle_button_additional = """
                border-radius: 25px;
                padding: 15px;
            """

            if underline_flag:
                underline_button_additional = """
                    text-decoration: underline;
                    font-size: 15px;
                """
            else:
                underline_button_additional = """
                    font-size: 15px;
                """

            if if_handle:
                add_text = handle_button_additional
                add_color = "background-color"
            else:
                add_text = underline_button_additional
                add_color = "color"

            line = f'''
                QPushButton {{
                    background-color: {button_color};
                    color: white;
                    border: none;
                    {add_text}
                }}
                QPushButton:hover {{
                    {add_color}: {hover_color};
                }}
            '''
            return line
    


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

    def convert_secs(seconds):
        return f'{seconds // 60:02}:{seconds % 60:02}'
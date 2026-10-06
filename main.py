import os
import re
import json
import urllib.request
import urllib.error

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform

from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup


# =========================================================
# WINDOW
# =========================================================

Window.minimum_width = dp(320)
Window.minimum_height = dp(520)

if platform == "android":
    Window.fullscreen = "auto"


# =========================================================
# COLORS
# =========================================================

BLUE = (0.04, 0.30, 0.65, 1)
DARK_BLUE = (0.02, 0.12, 0.25, 1)

WHITE = (1, 1, 1, 1)
BLACK = (0.05, 0.05, 0.05, 1)

LIGHT_BG = (0.94, 0.96, 1, 1)
LIGHT_BLUE = (0.70, 0.85, 1, 1)

GREEN = (0.10, 0.65, 0.25, 1)
RED = (0.80, 0.15, 0.15, 1)
ORANGE = (0.95, 0.55, 0.05, 1)
GRAY = (0.45, 0.45, 0.45, 1)


# =========================================================
# UI HELPERS
# =========================================================

def make_button(text, height=56, color=BLUE):
    return Button(
        text=text,
        size_hint_y=None,
        height=dp(height),
        font_size=sp(16),
        background_normal="",
        background_color=color,
        color=WHITE
    )


def make_input(hint="", password=False):
    return TextInput(
        hint_text=hint,
        password=password,
        multiline=False,
        size_hint_y=None,
        height=dp(52),
        font_size=sp(16),
        padding=[dp(12), dp(12)],
        background_normal="",
        background_color=WHITE,
        foreground_color=BLACK
    )


def make_label(text="", size=17, bold=False, color=WHITE):
    label = Label(
        text=text,
        font_size=sp(size),
        bold=bold,
        color=color,
        size_hint_y=None,
        height=dp(42),
        halign="left",
        valign="middle"
    )

    label.bind(
        width=lambda obj, value:
        setattr(
            obj,
            "text_size",
            (value - dp(10), None)
        )
    )

    return label


def show_message(title, message):

    content = BoxLayout(
        orientation="vertical",
        padding=dp(16),
        spacing=dp(12)
    )

    label = Label(
        text=message,
        font_size=sp(16),
        color=BLACK,
        halign="center",
        valign="middle"
    )

    label.bind(
        size=lambda obj, value:
        setattr(
            obj,
            "text_size",
            (value[0] - dp(20), None)
        )
    )

    close_btn = make_button("OK", 50)

    content.add_widget(label)
    content.add_widget(close_btn)

    popup = Popup(
        title=title,
        content=content,
        size_hint=(0.90, 0.45),
        auto_dismiss=False
    )

    close_btn.bind(on_release=popup.dismiss)

    popup.open()


def add_back_button(layout, screen_name="home"):

    back_btn = make_button(
        "⬅ BACK",
        54,
        DARK_BLUE
    )

    layout.add_widget(back_btn)

    back_btn.bind(
        on_release=lambda x:
        setattr(
            App.get_running_app().sm,
            "current",
            screen_name
        )
    )

    return back_btn


# =========================================================
# BACKEND API
# =========================================================

class BackendAPI:

    # Apna actual backend URL baad me yahan lagana.
    BASE_URL = "https://YOUR-BACKEND-DOMAIN.com/api"

    @staticmethod
    def request(endpoint, data=None, method="POST"):

        url = BackendAPI.BASE_URL + endpoint

        payload = None

        if data is not None:
            payload = json.dumps(data).encode("utf-8")

        request = urllib.request.Request(
            url,
            data=payload,
            method=method,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )

        try:

            with urllib.request.urlopen(
                request,
                timeout=15
            ) as response:

                raw = response.read().decode("utf-8")

                try:
                    return json.loads(raw)

                except json.JSONDecodeError:
                    return {
                        "success": True,
                        "message": raw
                    }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def submit_loan(application):

        return BackendAPI.request(
            "/loan/apply",
            application,
            "POST"
        )

    @staticmethod
    def get_loan_status(application_id):

        return BackendAPI.request(
            "/loan/status/" + str(application_id),
            None,
            "GET"
        )


# =========================================================
# BASE SCREEN
# =========================================================

class BaseScreen(Screen):

    def build_scroll(self):

        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(4)
        )

        layout = BoxLayout(
            orientation="vertical",
            padding=[dp(16), dp(16)],
            spacing=dp(10),
            size_hint_y=None
        )

        layout.bind(
            minimum_height=layout.setter("height")
        )

        scroll.add_widget(layout)

        self.add_widget(scroll)

        return layout


# =========================================================
# LOADING SCREEN
# =========================================================

class LoadingScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(30),
            spacing=dp(20)
        )

        layout.add_widget(
            Label(
                text="PAYAL LOAN",
                font_size=sp(34),
                bold=True,
                color=BLUE
            )
        )

        layout.add_widget(
            Label(
                text="Smart Loan & EMI",
                font_size=sp(20),
                color=GRAY
            )
        )

        self.add_widget(layout)

        Clock.schedule_once(
            self.open_password,
            1.2
        )

    def open_password(self, dt):

        App.get_running_app().sm.current = "password"


# =========================================================
# PASSWORD SCREEN
# =========================================================

class PasswordScreen(BaseScreen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        layout = self.build_scroll()

        layout.add_widget(
            make_label(
                "🔐 PAYAL LOAN",
                28,
                True,
                BLUE
            )
        )

        layout.add_widget(
            make_label(
                "Enter Password",
                20,
                True,
                BLACK
            )
        )

        self.password_input = make_input(
            "Password",
            True
        )

        layout.add_widget(
            self.password_input
        )

        login_btn = make_button(
            "LOGIN",
            56,
            BLUE
        )

        layout.add_widget(
            login_btn
        )

        login_btn.bind(
            on_release=self.login
        )

        forgot_btn = make_button(
            "Forgot Password?",
            50,
            GRAY
        )

        layout.add_widget(
            forgot_btn
        )

        forgot_btn.bind(
            on_release=self.forgot_password
        )

    def login(self, instance):

        app = App.get_running_app()

        saved_password = app.store.get(
            "security"
        ).get(
            "password",
            "1234"
        )

        if self.password_input.text == saved_password:

            self.password_input.text = ""

            app.sm.current = "home"

        else:

            show_message(
                "Wrong Password",
                "Password galat hai."
            )

    def forgot_password(self, instance):

        show_message(
            "Password",
            "Default password: 1234\n\n"
            "Aap Settings me jaakar password change kar sakte hain."
        )


# =========================================================
# HOME SCREEN
# =========================================================

class HomeScreen(BaseScreen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        layout = self.build_scroll()

        layout.add_widget(
            make_label(
                "PAYAL LOAN",
                30,
                True,
                BLUE
            )
        )

        layout.add_widget(
            make_label(
                "Smart Loan & EMI",
                18,
                False,
                GRAY
            )
        )

        layout.add_widget(
            make_label(
                "Welcome 👋",
                20,
                True,
                BLACK
            )
        )

        buttons = [
            ("💰 Loan Calculator", "loan"),
            ("📝 Apply / Take Loan", "apply"),
            ("📊 Credit Score", "credit"),
            ("✅ Eligibility Test", "eligibility"),
            ("📄 Loan Status", "status"),
            ("👤 Profile", "profile"),
            ("⚙ Settings", "settings"),
            ("🔐 Change Password", "change_password"),
            ("❓ Help / About", "help")
        ]

        for text, screen_name in buttons:

            btn = make_button(
                text,
                58,
                BLUE
            )

            layout.add_widget(btn)

            btn.bind(
                on_release=lambda x,
                name=screen_name:
                setattr(
                    App.get_running_app().sm,
                    "current",
                    name
                )
            )


# =========================================================
# LOAN CALCULATOR
# =========================================================

class LoanScreen(BaseScreen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        layout = self.build_scroll()

        layout.add_widget(
            make_label(
                "💰 LOAN CALCULATOR",
                26,
                True,
                BLUE
            )
        )

        # IMPORTANT:
        # self.name use nahi karna.
        # Screen me name already built-in property hai.
        self.name_input = make_input(
            "Full Name"
        )

        self.mobile_input = make_input(
            "Mobile Number"
        )

        self.amount_input = make_input(
            "Loan Amount (₹)"
        )

        self.interest_input = make_input(
            "Annual Interest (%)"
        )

        self.months_input = make_input(
            "Loan Period (Months)"
        )

        layout.add_widget(
            self.name_input
        )

        layout.add_widget(
            self.mobile_input
        )

        layout.add_widget(
            self.amount_input
        )

        layout.add_widget(
            self.interest_input
        )

        layout.add_widget(
            self.months_input
        )

        calculate_btn = make_button(
            "CALCULATE EMI",
            58,
            BLUE
        )

        layout.add_widget(
            calculate_btn
        )

        calculate_btn.bind(
            on_release=self.calculate_emi
        )

        self.result_label = make_label(
            "",
            18,
            True,
            BLACK
        )

        layout.add_widget(
            self.result_label
        )

        apply_btn = make_button(
            "📝 APPLY / TAKE LOAN",
            58,
            GREEN
        )

        layout.add_widget(
            apply_btn
        )

        apply_btn.bind(
            on_release=self.open_apply
        )

        add_back_button(
            layout,
            "home"
        )

    def calculate_emi(self, instance):

        try:

            amount = float(
                self.amount_input.text
            )

            interest = float(
                self.interest_input.text
            )

            months = int(
                self.months_input.text
            )

            if amount < 1000:

                show_message(
                    "Invalid Amount",
                    "Minimum loan amount ₹1000 hai."
                )

                return

            if months <= 0:

                show_message(
                    "Invalid Period",
                    "Loan period months me 1 se zyada hona chahiye."
                )

                return

            monthly_rate = (
                interest / 12 / 100
            )

            if monthly_rate == 0:

                emi = amount / months

            else:

                emi = (
                    amount
                    * monthly_rate
                    * (1 + monthly_rate) ** months
                    / (
                        (1 + monthly_rate) ** months
                        - 1
                    )
                )

            total_payment = emi * months

            total_interest = (
                total_payment - amount
            )

            self.calculated_data = {

                "amount": round(
                    amount,
                    2
                ),

                "interest": interest,

                "months": months,

                "emi": round(
                    emi,
                    2
                ),

                "total_payment": round(
                    total_payment,
                    2
                ),

                "total_interest": round(
                    total_interest,
                    2
                )
            }

            self.result_label.text = (
                "Loan Amount: ₹"
                + f"{amount:,.2f}"
                + "\n\n"
                "Monthly EMI: ₹"
                + f"{emi:,.2f}"
                + "\n\n"
                "Total Interest: ₹"
                + f"{total_interest:,.2f}"
                + "\n\n"
                "Total Payment: ₹"
                + f"{total_payment:,.2f}"
            )

        except ValueError:

            show_message(
                "Invalid Input",
                "Amount, interest aur months sahi enter karein."
            )

    def open_apply(self, instance):

        if not hasattr(
            self,
            "calculated_data"
        ):

            show_message(
                "Calculate First",
                "Pehle EMI calculate karein."
            )

            return

        apply_screen = App.get_running_app().sm.get_screen(
            "apply"
        )

        apply_screen.set_loan_data(
            self.name_input.text,
            self.mobile_input.text,
            self.calculated_data
        )

        App.get_running_app().sm.current = "apply"


# =========================================================
# APPLY LOAN SCREEN
# =========================================================

class ApplyLoanScreen(BaseScreen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        layout = self.build_scroll()

        layout.add_widget(
            make_label(
                "📝 APPLY / TAKE LOAN",
                26,
                True,
                BLUE
            )
        )

        self.name_input = make_input(
            "Full Name"
        )

        self.mobile_input = make_input(
            "Mobile Number"
        )

        self.pan_input = make_input(
            "PAN Card Number"
        )

        self.amount_input = make_input(
            "Loan Amount (₹)"
        )

        self.emi_label = make_label(
            "EMI: ₹0",
            18,
            True,
            BLACK
        )

        layout.add_widget(
            self.name_input
        )

        layout.add_widget(
            self.mobile_input
        )

        layout.add_widget(
            self.pan_input
        )

        layout.add_widget(
            self.amount_input
        )

        layout.add_widget(
            self.emi_label
        )

        submit_btn = make_button(
            "SUBMIT LOAN APPLICATION",
            60,
            GREEN
        )

        layout.add_widget(
            submit_btn
        )

        submit_btn.bind(
            on_release=self.submit_application
        )

        add_back_button(
            layout,
            "loan"
        )

    def set_loan_data(
        self,
        name,
        mobile,
        loan_data
    ):

        self.name_input.text = name
        self.mobile_input.text = mobile

        self.loan_data = loan_data

        self.amount_input.text = str(
            loan_data["amount"]
        )

        self.emi_label.text = (
            "Monthly EMI: ₹"
            + f"{loan_data['emi']:,.2f}"
            + "\n"
            "Period: "
            + str(loan_data["months"])
            + " Months"
        )

    def submit_application(self, instance):

        name = self.name_input.text.strip()

        mobile = self.mobile_input.text.strip()

        pan = self.pan_input.text.strip().upper()

        amount_text = self.amount_input.text.strip()

        if not name:

            show_message(
                "Required",
                "Full name enter karein."
            )

            return

        if not re.fullmatch(
            r"[0-9]{10}",
            mobile
        ):

            show_message(
                "Invalid Mobile",
                "10 digit mobile number enter karein."
            )

            return

        if not re.fullmatch(
            r"^[A-Z]{5}[0-9]{4}[A-Z]$",
            pan
        ):

            show_message(
                "Invalid PAN",
                "PAN format example: ABCDE1234F"
            )

            return

        try:

            amount = float(
                amount_text
            )

        except ValueError:

            show_message(
                "Invalid Amount",
                "Loan amount sahi enter karein."
            )

            return

        if amount < 1000:

            show_message(
                "Invalid Amount",
                "Minimum loan amount ₹1000 hai."
            )

            return

        if not hasattr(
            self,
            "loan_data"
        ):

            show_message(
                "Loan Data",
                "Pehle Loan Calculator se loan calculate karein."
            )

            return

        app = App.get_running_app()

        application_id = (
            "PL"
            + str(
                int(
                    Clock.get_time()
                    * 1000
                )
            )[-8:]
        )

        application = {

            "application_id":
                application_id,

            "name":
                name,

            "mobile":
                mobile,

            "pan":
                pan,

            "amount":
                amount,

            "interest":
                self.loan_data["interest"],

            "months":
                self.loan_data["months"],

            "emi":
                self.loan_data["emi"],

            "total_payment":
                self.loan_data["total_payment"],

            "total_interest":
                self.loan_data["total_interest"],

            "status":
                "APPLICATION_SUBMITTED"
        }

        # Local storage
        app.store.put(
            "loan",
            **application
        )

        # Profile save
        app.store.put(
            "profile",
            name=name,
            mobile=mobile
        )

        # Backend request
        result = BackendAPI.submit_loan(
            application
        )

        if result.get("success"):

            status_message = (
                "Loan application successfully "
                "backend par submit ho gayi.\n\n"
                "Application ID: "
                + application_id
            )

        else:

            status_message = (
                "Application local device par save ho gayi.\n\n"
                "Application ID: "
                + application_id
                + "\n\n"
                "Backend connect nahi hua, "
                "isliye real loan approve/disburse nahi hua."
            )

        show_message(
            "Loan Application",
            status_message
        )

        app.sm.current = "status"


# =========================================================
# CREDIT SCORE SCREEN
# =========================================================

class CreditScoreScreen(BaseScreen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        layout = self.build_scroll()

        layout.add_widget(
            make_label(
                "📊 CREDIT SCORE",
                26,
                True,
                BLUE
            )
        )

        score = App.get_running_app().store.get(
            "settings"
        ).get(
            "demo_credit_score",
            750
        )

        layout.add_widget(
            make_label(
                "Current Demo Score",
                20,
                True,
                BLACK
            )
        )

        layout.add_widget(
            make_label(
                str(score),
                55,
                True,
                BLUE
            )
        )

        layout.add_widget(
            make_label(
                "⚠ This is a demo score.\n\n"
                "Real credit score ke liye authorised "
                "credit bureau integration required hai.",
                17,
                False,
                GRAY
            )
        )

        add_back_button(
            layout,
            "home"
        )


# =========================================================
# ELIGIBILITY SCREEN
# =========================================================

class EligibilityScreen(BaseScreen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        layout = self.build_scroll()

        layout.add_widget(
            make_label(
                "✅ ELIGIBILITY TEST",
                26,
                True,
                BLUE
            )
        )

        self.age_input = make_input(
            "Age"
        )

        self.income_input = make_input(
            "Monthly Income (₹)"
        )

        self.existing_emi_input = make_input(
            "Existing EMI (₹)"
        )

        self.required_loan_input = make_input(
            "Required Loan (₹)"
        )

        layout.add_widget(
            self.age_input
        )

        layout.add_widget(
            self.income_input
        )

        layout.add_widget(
            self.existing_emi_input
        )

        layout.add_widget(
            self.required_loan_input
        )

        check_btn = make_button(
            "CHECK ELIGIBILITY",
            58,
            BLUE
        )

        layout.add_widget(
            check_btn
        )

        check_btn.bind(
            on_release=self.check
        )

        self.result = make_label(
            "",
            18,
            True,
            BLACK
        )

        layout.add_widget(
            self.result
        )

        add_back_button(
            layout,
            "home"
        )

    def check(self, instance):

        try:

            age = int(
                self.age_input.text
            )

            income = float(
                self.income_input.text
            )

            existing_emi = float(
                self.existing_emi_input.text
            )

            required_loan = float(
                self.required_loan_input.text
            )

            if age < 18:

                self.result.text = (
                    "❌ Age 18 se kam hai."
                )

                return

            if income <= 0:

                self.result.text = (
                    "❌ Income valid nahi hai."
                )

                return

            if required_loan < 1000:

                self.result.text = (
                    "❌ Minimum loan amount ₹1000 hai."
                )

                return

            remaining_income = (
                income - existing_emi
            )

            if remaining_income <= 0:

                self.result.text = (
                    "❌ Existing EMI income ke "
                    "comparison me bahut zyada hai."
                )

            else:

                self.result.text = (
                    "ℹ Basic affordability check passed.\n\n"
                    "Final loan eligibility authorised "
                    "lender hi decide karega."
                )

        except ValueError:

            show_message(
                "Invalid Input",
                "Sabhi details sahi enter karein."
            )


# =========================================================
# LOAN STATUS SCREEN
# =========================================================

class LoanStatusScreen(BaseScreen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.layout = self.build_scroll()

        self.refresh()

    def on_pre_enter(self):

        self.refresh()

    def refresh(self):

        if not hasattr(
            self,
            "layout"
        ):
            return

        self.layout.clear_widgets()

        self.layout.add_widget(
            make_label(
                "📄 LOAN STATUS",
                26,
                True,
                BLUE
            )
        )

        app = App.get_running_app()

        if not app.store.exists("loan"):

            self.layout.add_widget(
                make_label(
                    "No loan application found.",
                    18,
                    False,
                    BLACK
                )
            )

        else:

            loan = app.store.get(
                "loan"
            )

            pan = loan.get(
                "pan",
                ""
            )

            masked_pan = "******"

            if len(pan) >= 4:
                masked_pan = (
                    "*****"
                    + pan[-4:]
                )

            details = (
                "Application ID: "
                + str(
                    loan.get(
                        "application_id",
                        "-"
                    )
                )
                + "\n\n"
                "Name: "
                + str(
                    loan.get(
                        "name",
                        "-"
                    )
                )
                + "\n\n"
                "Mobile: "
                + str(
                    loan.get(
                        "mobile",
                        "-"
                    )
                )
                + "\n\n"
                "PAN: "
                + masked_pan
                + "\n\n"
                "Loan Amount: ₹"
                + f"{float(loan.get('amount', 0)):,.2f}"
                + "\n\n"
                "Monthly EMI: ₹"
                + f"{float(loan.get('emi', 0)):,.2f}"
                + "\n\n"
                "Interest: "
                + str(
                    loan.get(
                        "interest",
                        0
                    )
                )
                + "%"
                + "\n\n"
                "Loan Period: "
                + str(
                    loan.get(
                        "months",
                        0
                    )
                )
                + " Months"
                + "\n\n"
                "Status: "
                + str(
                    loan.get(
                        "status",
                        "-"
                    )
                )
            )

            self.layout.add_widget(
                make_label(
                    details,
                    17,
                    False,
                    BLACK
                )
            )

        add_back_button(
            self.layout,
            "home"
        )


# =========================================================
# PROFILE SCREEN
# =========================================================

class ProfileScreen(BaseScreen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        layout = self.build_scroll()

        layout.add_widget(
            make_label(
                "👤 PROFILE",
                26,
                True,
                BLUE
            )
        )

        self.name_input = make_input(
            "Full Name"
        )

        self.mobile_input = make_input(
            "Mobile Number"
        )

        layout.add_widget(
            self.name_input
        )

        layout.add_widget(
            self.mobile_input
        )

        save_btn = make_button(
            "SAVE PROFILE",
            56,
            GREEN
        )

        layout.add_widget(
            save_btn
        )

        save_btn.bind(
            on_release=self.save_profile
        )

        add_back_button(
            layout,
            "home"
        )

        self.load_profile()

    def on_pre_enter(self):

        self.load_profile()

    def load_profile(self):

        app = App.get_running_app()

        if app.store.exists(
            "profile"
        ):

            profile = app.store.get(
                "profile"
            )

            self.name_input.text = profile.get(
                "name",
                ""
            )

            self.mobile_input.text = profile.get(
                "mobile",
                ""
            )

    def save_profile(self, instance):

        name = self.name_input.text.strip()

        mobile = self.mobile_input.text.strip()

        if not name:

            show_message(
                "Profile",
                "Name enter karein."
            )

            return

        App.get_running_app().store.put(
            "profile",
            name=name,
            mobile=mobile
        )

        show_message(
            "Profile",
            "Profile save ho gaya."
        )


# =========================================================
# SETTINGS SCREEN
# =========================================================

class SettingsScreen(BaseScreen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        layout = self.build_scroll()

        layout.add_widget(
            make_label(
                "⚙ SETTINGS",
                26,
                True,
                BLUE
            )
        )

        layout.add_widget(
            make_label(
                "Theme",
                20,
                True,
                BLACK
            )
        )

        blue_btn = make_button(
            "🔵 Blue Theme",
            54,
            BLUE
        )

        light_btn = make_button(
            "☀ Light Theme",
            54,
            LIGHT_BLUE
        )

        dark_btn = make_button(
            "🌙 Dark Theme",
            54,
            DARK_BLUE
        )

        layout.add_widget(
            blue_btn
        )

        layout.add_widget(
            light_btn
        )

        layout.add_widget(
            dark_btn
        )

        blue_btn.bind(
            on_release=lambda x:
            App.get_running_app().set_theme(
                "Blue"
            )
        )

        light_btn.bind(
            on_release=lambda x:
            App.get_running_app().set_theme(
                "Light"
            )
        )

        dark_btn.bind(
            on_release=lambda x:
            App.get_running_app().set_theme(
                "Dark"
            )
        )

        layout.add_widget(
            make_label(
                "Language",
                20,
                True,
                BLACK
            )
        )

        english_btn = make_button(
            "English",
            54,
            BLUE
        )

        hindi_btn = make_button(
            "हिंदी",
            54,
            GREEN
        )

        layout.add_widget(
            english_btn
        )

        layout.add_widget(
            hindi_btn
        )

        english_btn.bind(
            on_release=lambda x:
            App.get_running_app().set_language(
                "English"
            )
        )

        hindi_btn.bind(
            on_release=lambda x:
            App.get_running_app().set_language(
                "Hindi"
            )
        )

        layout.add_widget(
            make_label(
                "Privacy & Data",
                20,
                True,
                BLACK
            )
        )

        layout.add_widget(
            make_label(
                "App data local storage me save hota hai. "
                "Real lending ke liye secure backend, "
                "proper consent, KYC, privacy controls "
                "aur authorised lender integration required hai.",
                16,
                False,
                GRAY
            )
        )

        add_back_button(
            layout,
            "home"
        )


# =========================================================
# CHANGE PASSWORD
# =========================================================

class ChangePasswordScreen(BaseScreen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        layout = self.build_scroll()

        layout.add_widget(
            make_label(
                "🔐 CHANGE PASSWORD",
                26,
                True,
                BLUE
            )
        )

        self.old_password = make_input(
            "Old Password",
            True
        )

        self.new_password = make_input(
            "New Password",
            True
        )

        self.confirm_password = make_input(
            "Confirm New Password",
            True
        )

        layout.add_widget(
            self.old_password
        )

        layout.add_widget(
            self.new_password
        )

        layout.add_widget(
            self.confirm_password
        )

        save_btn = make_button(
            "CHANGE PASSWORD",
            58,
            GREEN
        )

        layout.add_widget(
            save_btn
        )

        save_btn.bind(
            on_release=self.change_password
        )

        add_back_button(
            layout,
            "home"
        )

    def change_password(self, instance):

        app = App.get_running_app()

        old = self.old_password.text

        new = self.new_password.text

        confirm = self.confirm_password.text

        current_password = app.store.get(
            "security"
        ).get(
            "password",
            "1234"
        )

        if old != current_password:

            show_message(
                "Password",
                "Old password galat hai."
            )

            return

        if len(new) < 4:

            show_message(
                "Password",
                "New password minimum 4 characters ka hona chahiye."
            )

            return

        if new != confirm:

            show_message(
                "Password",
                "New password aur confirm password same nahi hain."
            )

            return

        app.store.put(
            "security",
            password=new
        )

        self.old_password.text = ""
        self.new_password.text = ""
        self.confirm_password.text = ""

        show_message(
            "Success",
            "Password successfully change ho gaya."
        )


# =========================================================
# HELP SCREEN
# =========================================================

class HelpScreen(BaseScreen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        layout = self.build_scroll()

        layout.add_widget(
            make_label(
                "❓ HELP / ABOUT",
                26,
                True,
                BLUE
            )
        )

        help_text = (
            "PAYAL LOAN\n\n"
            "Features:\n"
            "• Loan EMI Calculator\n"
            "• Loan Application\n"
            "• PAN Validation\n"
            "• Loan Status\n"
            "• Credit Score Screen\n"
            "• Eligibility Test\n"
            "• Profile\n"
            "• Hindi / English\n"
            "• Blue / Light / Dark Theme\n"
            "• Password Protection\n\n"
            "IMPORTANT:\n"
            "Current app local/demo functionality provide "
            "karta hai. Real loan approval, KYC, credit "
            "bureau verification aur money disbursement "
            "ke liye authorised lender aur secure backend "
            "integration required hai."
        )

        layout.add_widget(
            make_label(
                help_text,
                17,
                False,
                BLACK
            )
        )

        add_back_button(
            layout,
            "home"
        )


# =========================================================
# MAIN APP
# =========================================================

class LoanApp(App):

    def build(self):

        self.title = "Payal Loan"

        self.store = JsonStore(
            os.path.join(
                self.user_data_dir,
                "payal_loan_data.json"
            )
        )

        # Default settings
        if not self.store.exists(
            "security"
        ):

            self.store.put(
                "security",
                password="1234"
            )

        if not self.store.exists(
            "settings"
        ):

            self.store.put(
                "settings",
                theme="Blue",
                language="English",
                demo_credit_score=750
            )

        self.sm = ScreenManager(
            transition=FadeTransition(
                duration=0.15
            )
        )

        # Add screens
        self.sm.add_widget(
            LoadingScreen(
                name="loading"
            )
        )

        self.sm.add_widget(
            PasswordScreen(
                name="password"
            )
        )

        self.sm.add_widget(
            HomeScreen(
                name="home"
            )
        )

        self.sm.add_widget(
            LoanScreen(
                name="loan"
            )
        )

        self.sm.add_widget(
            ApplyLoanScreen(
                name="apply"
            )
        )

        self.sm.add_widget(
            CreditScoreScreen(
                name="credit"
            )
        )

        self.sm.add_widget(
            EligibilityScreen(
                name="eligibility"
            )
        )

        self.sm.add_widget(
            LoanStatusScreen(
                name="status"
            )
        )

        self.sm.add_widget(
            ProfileScreen(
                name="profile"
            )
        )

        self.sm.add_widget(
            SettingsScreen(
                name="settings"
            )
        )

        self.sm.add_widget(
            ChangePasswordScreen(
                name="change_password"
            )
        )

        self.sm.add_widget(
            HelpScreen(
                name="help"
            )
        )

        self.sm.current = "loading"

        self.apply_saved_theme()

        return self.sm

    # =====================================================
    # THEME
    # =====================================================

    def apply_saved_theme(self):

        settings = self.store.get(
            "settings"
        )

        theme = settings.get(
            "theme",
            "Blue"
        )

        self.set_theme(
            theme,
            show_popup=False
        )

    def set_theme(
        self,
        theme,
        show_popup=True
    ):

        settings = self.store.get(
            "settings"
        )

        language = settings.get(
            "language",
            "English"
        )

        credit_score = settings.get(
            "demo_credit_score",
            750
        )

        self.store.put(
            "settings",
            theme=theme,
            language=language,
            demo_credit_score=credit_score
        )

        if theme == "Dark":

            Window.clearcolor = DARK_BLUE

        elif theme == "Light":

            Window.clearcolor = LIGHT_BG

        else:

            Window.clearcolor = WHITE

        if show_popup:

            show_message(
                "Theme",
                theme + " theme applied."
            )

    # =====================================================
    # LANGUAGE
    # =====================================================

    def set_language(self, language):

        settings = self.store.get(
            "settings"
        )

        theme = settings.get(
            "theme",
            "Blue"
        )

        credit_score = settings.get(
            "demo_credit_score",
            750
        )

        self.store.put(
            "settings",
            theme=theme,
            language=language,
            demo_credit_score=credit_score
        )

        show_message(
            "Language",
            language
            + " selected.\n\n"
            "Language changes complete karne ke liye "
            "app restart karein."
        )


# =========================================================
# RUN APP
# =========================================================

if __name__ == "__main__":
    LoanApp().run()

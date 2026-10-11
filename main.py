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
    # High-contrast input fields: visible on white backgrounds and easy to tap.
    field = TextInput(
        hint_text=hint,
        password=password,
        multiline=False,
        size_hint=(1, None),
        height=dp(54),
        font_size=sp(16),
        padding=[dp(12), dp(14)],
        background_normal="",
        background_active="",
        background_color=LIGHT_BG,
        foreground_color=BLACK,
        hint_text_color=(0.35, 0.39, 0.45, 1),
        cursor_color=BLUE,
        selection_color=LIGHT_BLUE,
        write_tab=False,
    )
    return field


def make_label(text="", size=17, bold=False, color=WHITE):
    """A wrapping label whose height follows its rendered text."""
    label = Label(
        text=str(text),
        font_size=sp(size),
        bold=bold,
        color=color,
        size_hint=(1, None),
        height=dp(max(42, size * 1.7)),
        halign="left",
        valign="top",
        padding=(dp(6), dp(7)),
    )

    def refresh_layout(*_):
        # Set text_size before asking Kivy to measure the wrapped text.
        available_width = max(dp(100), label.width - dp(20))
        label.text_size = (available_width, None)
        label.texture_update()
        label.height = max(dp(size * 1.7), label.texture_size[1] + dp(18))

    label.bind(width=refresh_layout, text=refresh_layout, font_size=refresh_layout)
    Clock.schedule_once(refresh_layout, 0)
    Clock.schedule_once(refresh_layout, 0.1)
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
            spacing=dp(14),
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
                text="Payal I Love You",
                font_size=sp(30),
                bold=True,
                color=BLUE
            )
        )

        layout.add_widget(
            Label(
                text="PAYAL LOAN  |  Smart Loan & EMI",
                font_size=sp(18),
                color=GRAY
            )
        )

        self.add_widget(layout)

        Clock.schedule_once(
            self.open_home,
            1.8
        )

    def open_home(self, dt):

        App.get_running_app().sm.current = "home"


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
                "Welcome to Payal Loan",
                20,
                True,
                BLACK
            )
        )
        layout.add_widget(
            make_label(
                "Aapki Zaroorat, Hamara Saath",
                16,
                False,
                GRAY
            )
        )
        layout.add_widget(
            make_label(
                "Minimum Loan Amount: Rs. 1,000",
                17,
                True,
                BLUE
            )
        )
        layout.add_widget(
            make_label(
                "Apply for a loan, calculate EMI, and track your application from one place.",
                16,
                False,
                BLACK
            )
        )

        buttons = [
            ("LOAN CALCULATOR", "loan"),
            ("APPLY / TAKE LOAN", "apply"),
            ("CREDIT SCORE", "credit"),
            ("ELIGIBILITY TEST", "eligibility"),
            ("LOAN STATUS", "status"),
            ("MY PROFILE", "profile"),
            ("SETTINGS", "settings"),
            ("CHANGE PASSWORD", "change_password"),
            ("HELP / ABOUT", "help"),
            ("ADMIN PANEL", "admin"),
            ("BANK DETAILS", "bank_details"),
            ("LOGOUT", "loading")
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
                "LOAN CALCULATOR",
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

        self.interest_label = make_label(
            "Admin-set annual interest: loading...",
            17, True, BLACK
        )
        layout.add_widget(self.interest_label)
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
            "APPLY / TAKE LOAN",
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
        self.refresh_admin_interest()

    def on_pre_enter(self):
        self.refresh_admin_interest()

    def refresh_admin_interest(self):
        app = App.get_running_app()
        rate = app.store.get("settings").get("interest_rate", 12.0)
        self.admin_interest_rate = float(rate)
        self.interest_label.text = f"Admin-set annual interest: {self.admin_interest_rate:.2f}%"

    def calculate_emi(self, instance):

        try:

            amount = float(
                self.amount_input.text
            )

            interest = float(self.admin_interest_rate)

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
                "APPLY / TAKE LOAN",
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
        self.bank_holder_input = make_input("Bank Account Holder Name")
        self.account_input = make_input("Bank Account Number")
        self.ifsc_input = make_input("IFSC Code")

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
        layout.add_widget(self.bank_holder_input)
        layout.add_widget(self.account_input)
        layout.add_widget(self.ifsc_input)

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

        bank_holder = self.bank_holder_input.text.strip()
        account_number = self.account_input.text.strip()
        ifsc = self.ifsc_input.text.strip().upper()
        if not bank_holder or not account_number or not re.fullmatch(r"[A-Z]{4}0[A-Z0-9]{6}", ifsc):
            show_message("Bank Details", "Bank holder name, account number aur valid IFSC enter karein.")
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
            "bank_holder": bank_holder,
            "account_number": account_number,
            "ifsc": ifsc,
            "payment_status": "NOT_PAID",

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
                "CREDIT SCORE",
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
                "Bank Account: " + str(loan.get("account_number", "-"))
                + "\nIFSC: " + str(loan.get("ifsc", "-"))
                + "\nPayment Status: " + str(loan.get("payment_status", "NOT_PAID"))
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
                "ABOUT PAYAL LOAN",
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
# ADMIN PANEL
# =========================================================
class AdminScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = self.build_scroll()
        self.build_ui()

    def build_ui(self):
        self.layout.clear_widgets()
        self.layout.add_widget(make_label("ADMIN PANEL", 26, True, BLUE))
        self.admin_password_input = make_input("Admin password", True)
        self.layout.add_widget(self.admin_password_input)
        login_btn = make_button("ADMIN LOGIN", 54, BLUE)
        self.layout.add_widget(login_btn)
        login_btn.bind(on_release=self.admin_login)
        add_back_button(self.layout, "home")

    def admin_login(self, instance):
        app = App.get_running_app()
        settings = app.store.get("settings")
        expected = settings.get("admin_password", "2468")
        if self.admin_password_input.text != expected:
            show_message("Admin Login", "Admin password galat hai.")
            return
        self.show_admin_controls()

    def show_admin_controls(self):
        self.layout.clear_widgets()
        app = App.get_running_app()
        settings = app.store.get("settings")
        self.layout.add_widget(make_label("ADMIN SETTINGS", 25, True, BLUE))
        self.rate_input = make_input("Annual interest rate (%)")
        self.rate_input.text = str(settings.get("interest_rate", 12.0))
        self.new_admin_password = make_input("New admin password (optional)", True)
        self.layout.add_widget(make_label("Interest rate used by all customer EMI calculations", 16, False, BLACK))
        self.layout.add_widget(self.rate_input)
        self.layout.add_widget(self.new_admin_password)
        save = make_button("SAVE ADMIN SETTINGS", 56, GREEN)
        self.layout.add_widget(save)
        save.bind(on_release=self.save_admin_settings)
        self.layout.add_widget(make_label("Loan application review", 20, True, BLUE))
        if app.store.exists("loan"):
            loan = app.store.get("loan")
            summary = f"ID: {loan.get('application_id','-')}\nName: {loan.get('name','-')}\nAmount: ₹{float(loan.get('amount',0)):,.2f}\nBank holder: {loan.get('bank_holder','-')}\nAccount: {loan.get('account_number','-')}\nIFSC: {loan.get('ifsc','-')}\nStatus: {loan.get('status','-')}\nPayment: {loan.get('payment_status','NOT_PAID')}"
            if loan.get("transfer_utr"):
                summary += f"\nTransferred: ₹{float(loan.get('transfer_amount', 0)):,.2f}\nUTR: {loan.get('transfer_utr')}\nTransfer date: {loan.get('transfer_date', '-')}"
            # Give the full application details enough vertical space. The old
            # fixed-height label clipped multi-line text and let buttons overlap it.
            details = Label(
                text=summary,
                font_size=sp(16),
                color=BLACK,
                size_hint=(1, None),
                height=dp(190),
                halign="left",
                valign="top",
                padding=(dp(10), dp(10)),
            )
            details.bind(
                width=lambda obj, value: setattr(
                    obj, "text_size", (max(0, value - dp(20)), None)
                )
            )
            details.bind(
                texture_size=lambda obj, value: setattr(
                    obj, "height", max(dp(190), value[1] + dp(24))
                )
            )
            self.layout.add_widget(details)
            approve = make_button("APPROVE APPLICATION", 52, GREEN)
            reject = make_button("REJECT APPLICATION", 52, RED)
            self.layout.add_widget(approve)
            self.layout.add_widget(reject)
            approve.bind(on_release=lambda *_: self.update_loan(status="APPROVED"))
            reject.bind(on_release=lambda *_: self.update_loan(status="REJECTED"))

            # Manual money-distribution record: transfer is made separately
            # using the Admin's bank app; this section only records that transfer.
            self.layout.add_widget(make_label("MANUAL MONEY DISTRIBUTION", 20, True, BLUE))
            self.layout.add_widget(make_label(
                "Bank app se transfer karne ke baad hi neeche details bharein.",
                15, False, BLACK
            ))
            self.transfer_amount_input = make_input("Transferred amount (₹)")
            self.transfer_amount_input.text = str(float(loan.get("amount", 0)))
            self.transfer_utr_input = make_input("UTR / Transaction ID")
            self.transfer_date_input = make_input("Transfer date (YYYY-MM-DD)")
            from datetime import date
            self.transfer_date_input.text = date.today().isoformat()
            self.layout.add_widget(make_label("Transfer amount", 15, True, BLACK))
            self.layout.add_widget(self.transfer_amount_input)
            self.layout.add_widget(make_label("UTR / Transaction ID", 15, True, BLACK))
            self.layout.add_widget(self.transfer_utr_input)
            self.layout.add_widget(make_label("Transfer date", 15, True, BLACK))
            self.layout.add_widget(self.transfer_date_input)
            paid = make_button("SAVE TRANSFER RECORD / MARK PAID", 52, BLUE)
            self.layout.add_widget(paid)
            paid.bind(on_release=self.record_manual_transfer)
        else:
            self.layout.add_widget(make_label("No loan application submitted yet.", 16, False, BLACK))
        self.layout.add_widget(make_label("Admin UPI ID: 9693387758@slc (for receiving payments only)", 16, True, BLUE))
        add_back_button(self.layout, "home")

    def save_admin_settings(self, instance):
        app = App.get_running_app()
        try:
            rate = float(self.rate_input.text.strip())
            if not 0 <= rate <= 100:
                raise ValueError
        except ValueError:
            show_message("Interest Rate", "Rate 0 se 100 ke beech enter karein.")
            return
        old = app.store.get("settings")
        data = dict(old)
        data["interest_rate"] = rate
        if self.new_admin_password.text:
            if len(self.new_admin_password.text) < 4:
                show_message("Admin Password", "Password kam se kam 4 characters ka ho.")
                return
            data["admin_password"] = self.new_admin_password.text
        app.store.put("settings", **data)
        show_message("Saved", "Admin settings save ho gayi.")
        self.show_admin_controls()

    def update_loan(self, **changes):
        app = App.get_running_app()
        if not app.store.exists("loan"):
            show_message("Loan", "Application nahi mili.")
            return
        loan = dict(app.store.get("loan"))
        loan.update(changes)
        app.store.put("loan", **loan)
        show_message("Loan Updated", "Application record update ho gaya.")
        self.show_admin_controls()

    def record_manual_transfer(self, instance):
        app = App.get_running_app()
        if not app.store.exists("loan"):
            show_message("Transfer", "Loan application nahi mili.")
            return
        loan = dict(app.store.get("loan"))
        if loan.get("status") != "APPROVED":
            show_message("Transfer", "Pehle application approve karein.")
            return
        try:
            amount = float(self.transfer_amount_input.text.strip())
            if amount <= 0:
                raise ValueError
        except (ValueError, AttributeError):
            show_message("Transfer", "Sahi transferred amount enter karein.")
            return
        utr = self.transfer_utr_input.text.strip()
        transfer_date = self.transfer_date_input.text.strip()
        if not utr:
            show_message("Transfer", "UTR / Transaction ID zaroor bharein.")
            return
        try:
            from datetime import date
            date.fromisoformat(transfer_date)
        except ValueError:
            show_message("Transfer Date", "Date YYYY-MM-DD format mein bharein.")
            return
        loan.update({
            "payment_status": "PAID",
            "transfer_amount": round(amount, 2),
            "transfer_utr": utr,
            "transfer_date": transfer_date,
            "payment_method": "MANUAL_BANK_TRANSFER"
        })
        app.store.put("loan", **loan)
        show_message("Transfer Saved", "Manual transfer record save ho gaya. Bank transfer apne bank app mein alag se karna hota hai.")
        self.show_admin_controls()


# =========================================================
# BANK DETAILS SCREEN
# =========================================================
class BankDetailsScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = self.build_scroll()
        layout.add_widget(make_label("BANK DETAILS", 26, True, BLUE))
        layout.add_widget(make_label("Customer bank details are collected with the loan application and shown only in the Admin Panel on this device.", 17, False, BLACK))
        layout.add_widget(make_label("Admin UPI ID: 9693387758@slc", 20, True, BLUE))
        layout.add_widget(make_label("UPI ID is for receiving money. To disburse a loan, manually transfer from your bank app to the customer's verified account and then mark the record Paid in Admin Panel.", 16, False, BLACK))
        add_back_button(layout, "home")


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
                demo_credit_score=750,
                interest_rate=12.0,
                admin_password="2468"
            )
        else:
            saved_settings = self.store.get("settings")
            settings_data = dict(saved_settings)
            settings_data.setdefault("interest_rate", 12.0)
            settings_data.setdefault("admin_password", "2468")
            self.store.put("settings", **settings_data)

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
        self.sm.add_widget(AdminScreen(name="admin"))
        self.sm.add_widget(BankDetailsScreen(name="bank_details"))

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

        saved = dict(settings)
        saved["theme"] = theme
        saved["language"] = language
        saved["demo_credit_score"] = credit_score
        saved.setdefault("interest_rate", 12.0)
        saved.setdefault("admin_password", "2468")
        self.store.put("settings", **saved)

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

        saved = dict(settings)
        saved["theme"] = theme
        saved["language"] = language
        saved["demo_credit_score"] = credit_score
        saved.setdefault("interest_rate", 12.0)
        saved.setdefault("admin_password", "2468")
        self.store.put("settings", **saved)

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

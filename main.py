import os
import re

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.storage.jsonstore import JsonStore

from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup


# =========================================================
# BUTTON
# =========================================================

def make_button(text, height=55):
    return Button(
        text=text,
        size_hint_y=None,
        height=height,
        font_size=17
    )


# =========================================================
# LOADING
# =========================================================

class LoadingScreen(Screen):

    def on_enter(self):
        Clock.schedule_once(self.go_password, 1.2)

    def go_password(self, dt):
        self.manager.current = "password"


# =========================================================
# PASSWORD
# =========================================================

class PasswordScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_screen()

    def build_screen(self):

        self.clear_widgets()

        main = BoxLayout(
            orientation="vertical",
            padding=30,
            spacing=18
        )

        title = Label(
            text="PAYAL LOAN",
            font_size=32,
            bold=True,
            size_hint_y=None,
            height=80
        )

        subtitle = Label(
            text="Secure Loan Application",
            font_size=18,
            size_hint_y=None,
            height=45
        )

        self.password_input = TextInput(
            hint_text="Enter Password",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=55,
            font_size=18
        )

        login_btn = make_button("🔐 Login")
        login_btn.bind(on_release=self.login)

        forgot_btn = make_button("Forgot Password", 45)
        forgot_btn.bind(on_release=self.forgot_password)

        main.add_widget(title)
        main.add_widget(subtitle)
        main.add_widget(self.password_input)
        main.add_widget(login_btn)
        main.add_widget(forgot_btn)

        self.add_widget(main)

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
            self.manager.current = "home"

        else:

            self.show_popup(
                "Wrong Password",
                "Password is incorrect."
            )

    def forgot_password(self, instance):

        self.show_popup(
            "Forgot Password",
            "Default password is 1234.\n\n"
            "If you changed the password and forgot it, "
            "reset the application data."
        )

    def show_popup(self, title, message):

        content = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=15
        )

        label = Label(
            text=message,
            halign="center"
        )

        button = make_button("OK", 50)

        content.add_widget(label)
        content.add_widget(button)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.85, 0.4)
        )

        button.bind(on_release=popup.dismiss)

        popup.open()


# =========================================================
# HOME
# =========================================================

class HomeScreen(Screen):

    def on_pre_enter(self):
        self.build_screen()

    def build_screen(self):

        self.clear_widgets()

        app = App.get_running_app()

        main = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=10
        )

        title = Label(
            text="PAYAL LOAN",
            font_size=30,
            bold=True,
            size_hint_y=None,
            height=65
        )

        welcome = Label(
            text=(
                "Welcome to Payal Loan"
                if app.language == "English"
                else "Payal Loan में आपका स्वागत है"
            ),
            font_size=18,
            size_hint_y=None,
            height=45
        )

        main.add_widget(title)
        main.add_widget(welcome)

        if app.language == "Hindi":

            buttons = [
                ("💰 लोन / EMI कैलकुलेटर", "loan"),
                ("📝 लोन लें / Apply Loan", "apply"),
                ("💳 Credit Score", "credit"),
                ("✅ Eligibility Test", "eligibility"),
                ("📊 लोन स्टेटस", "status"),
                ("👤 प्रोफाइल", "profile"),
                ("⚙️ सेटिंग्स", "settings"),
                ("🔑 पासवर्ड बदलें", "change_password"),
                ("❓ मदद / About", "help")
            ]

        else:

            buttons = [
                ("💰 Loan / EMI Calculator", "loan"),
                ("📝 Apply / Take Loan", "apply"),
                ("💳 Credit Score", "credit"),
                ("✅ Loan Eligibility Test", "eligibility"),
                ("📊 Loan Status", "status"),
                ("👤 Profile", "profile"),
                ("⚙️ Settings", "settings"),
                ("🔑 Change Password", "change_password"),
                ("❓ Help / About", "help")
            ]

        for text, screen_name in buttons:

            btn = make_button(text)

            btn.bind(
                on_release=lambda instance,
                name=screen_name:
                self.go_to(name)
            )

            main.add_widget(btn)

        self.add_widget(main)

    def go_to(self, screen_name):
        self.manager.current = screen_name


# =========================================================
# LOAN EMI CALCULATOR
# =========================================================

class LoanScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.emi = 0
        self.total_payment = 0
        self.total_interest = 0

        self.build_screen()

    def build_screen(self):

        self.clear_widgets()

        app = App.get_running_app()

        if app.language == "Hindi":

            title = "लोन EMI कैलकुलेटर"
            name_hint = "पूरा नाम"
            mobile_hint = "मोबाइल नंबर"
            amount_hint = "लोन राशि (₹)"
            interest_hint = "वार्षिक ब्याज (%)"
            period_hint = "लोन अवधि (महीने)"

            calculate_text = "🧮 EMI Calculate करें"
            summary_text = "📋 Summary"
            apply_text = "📝 Loan के लिए Apply करें"
            back_text = "⬅ वापस"

        else:

            title = "Loan EMI Calculator"
            name_hint = "Full Name"
            mobile_hint = "Mobile Number"
            amount_hint = "Loan Amount (₹)"
            interest_hint = "Annual Interest (%)"
            period_hint = "Loan Period (Months)"

            calculate_text = "🧮 Calculate EMI"
            summary_text = "📋 Summary"
            apply_text = "📝 Apply for Loan"
            back_text = "⬅ Back"

        scroll = ScrollView()

        main = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=12,
            size_hint_y=None
        )

        main.bind(
            minimum_height=main.setter("height")
        )

        title_label = Label(
            text=title,
            font_size=28,
            bold=True,
            size_hint_y=None,
            height=65
        )

        self.name_input = TextInput(
            hint_text=name_hint,
            multiline=False,
            size_hint_y=None,
            height=55
        )

        self.mobile_input = TextInput(
            hint_text=mobile_hint,
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=55
        )

        self.amount_input = TextInput(
            hint_text=amount_hint,
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=55
        )

        self.rate_input = TextInput(
            hint_text=interest_hint,
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=55
        )

        self.period_input = TextInput(
            hint_text=period_hint,
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=55
        )

        calculate_btn = make_button(calculate_text)
        calculate_btn.bind(
            on_release=self.calculate_emi
        )

        self.result_label = Label(
            text="Monthly EMI: ₹0.00",
            font_size=22,
            bold=True,
            size_hint_y=None,
            height=60
        )

        summary_btn = make_button(summary_text)
        summary_btn.bind(
            on_release=self.show_summary
        )

        apply_btn = make_button(apply_text)
        apply_btn.bind(
            on_release=self.prepare_apply
        )

        back_btn = make_button(back_text, 50)
        back_btn.bind(
            on_release=lambda x:
            setattr(
                self.manager,
                "current",
                "home"
            )
        )

        main.add_widget(title_label)
        main.add_widget(self.name_input)
        main.add_widget(self.mobile_input)
        main.add_widget(self.amount_input)
        main.add_widget(self.rate_input)
        main.add_widget(self.period_input)
        main.add_widget(calculate_btn)
        main.add_widget(self.result_label)
        main.add_widget(summary_btn)
        main.add_widget(apply_btn)
        main.add_widget(back_btn)

        scroll.add_widget(main)

        self.add_widget(scroll)

    def calculate_emi(self, instance):

        try:

            principal = float(
                self.amount_input.text
            )

            annual_rate = float(
                self.rate_input.text
            )

            months = int(
                self.period_input.text
            )

            if principal < 1000:

                self.show_popup(
                    "Invalid Amount",
                    "Minimum loan amount is ₹1000."
                )
                return

            if annual_rate < 0:

                self.show_popup(
                    "Invalid Interest",
                    "Interest cannot be negative."
                )
                return

            if months <= 0:

                self.show_popup(
                    "Invalid Period",
                    "Loan period must be at least 1 month."
                )
                return

            monthly_rate = (
                annual_rate / 12 / 100
            )

            if monthly_rate == 0:

                emi = principal / months

            else:

                emi = (
                    principal
                    * monthly_rate
                    * (1 + monthly_rate) ** months
                    /
                    (
                        (1 + monthly_rate) ** months
                        - 1
                    )
                )

            self.emi = emi

            self.total_payment = (
                emi * months
            )

            self.total_interest = (
                self.total_payment - principal
            )

            self.result_label.text = (
                f"Monthly EMI: ₹{emi:,.2f}"
            )

        except ValueError:

            self.show_popup(
                "Error",
                "Please enter valid loan details."
            )

    def show_summary(self, instance):

        if self.emi <= 0:

            self.show_popup(
                "Calculate EMI",
                "Please calculate EMI first."
            )
            return

        summary = (
            f"Loan Amount: ₹"
            f"{float(self.amount_input.text):,.2f}\n\n"

            f"Interest: "
            f"{self.rate_input.text}%\n\n"

            f"Period: "
            f"{self.period_input.text} Months\n\n"

            f"Monthly EMI: ₹"
            f"{self.emi:,.2f}\n\n"

            f"Total Payment: ₹"
            f"{self.total_payment:,.2f}\n\n"

            f"Total Interest: ₹"
            f"{self.total_interest:,.2f}"
        )

        self.show_popup(
            "Loan Summary",
            summary
        )

    def prepare_apply(self, instance):

        if self.emi <= 0:

            self.show_popup(
                "Calculate EMI",
                "Please calculate EMI before applying."
            )
            return

        apply_screen = self.manager.get_screen(
            "apply"
        )

        apply_screen.name_input.text = (
            self.name_input.text
        )

        apply_screen.mobile_input.text = (
            self.mobile_input.text
        )

        apply_screen.amount_input.text = (
            self.amount_input.text
        )

        apply_screen.emi = self.emi

        apply_screen.interest = (
            self.rate_input.text
        )

        apply_screen.period = (
            self.period_input.text
        )

        self.manager.current = "apply"

    def show_popup(self, title, message):

        content = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=15
        )

        label = Label(
            text=message,
            halign="center"
        )

        button = make_button("OK", 50)

        content.add_widget(label)
        content.add_widget(button)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.88, 0.55)
        )

        button.bind(
            on_release=popup.dismiss
        )

        popup.open()


# =========================================================
# APPLY LOAN
# =========================================================

class ApplyLoanScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.emi = 0
        self.interest = ""
        self.period = ""

        self.build_screen()

    def build_screen(self):

        self.clear_widgets()

        scroll = ScrollView()

        main = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=12,
            size_hint_y=None
        )

        main.bind(
            minimum_height=main.setter("height")
        )

        title = Label(
            text="Apply / Take Loan",
            font_size=28,
            bold=True,
            size_hint_y=None,
            height=65
        )

        self.name_input = TextInput(
            hint_text="Full Name",
            multiline=False,
            size_hint_y=None,
            height=55
        )

        self.mobile_input = TextInput(
            hint_text="Mobile Number",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=55
        )

        self.pan_input = TextInput(
            hint_text="PAN Card Number",
            multiline=False,
            size_hint_y=None,
            height=55
        )

        self.amount_input = TextInput(
            hint_text="Loan Amount (₹)",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=55
        )

        self.emi_label = Label(
            text="Monthly EMI: ₹0.00",
            font_size=20,
            bold=True,
            size_hint_y=None,
            height=55
        )

        submit_btn = make_button(
            "✅ Submit Loan Application",
            60
        )

        submit_btn.bind(
            on_release=self.submit_application
        )

        back_btn = make_button(
            "⬅ Back",
            50
        )

        back_btn.bind(
            on_release=lambda x:
            setattr(
                self.manager,
                "current",
                "home"
            )
        )

        main.add_widget(title)
        main.add_widget(self.name_input)
        main.add_widget(self.mobile_input)
        main.add_widget(self.pan_input)
        main.add_widget(self.amount_input)
        main.add_widget(self.emi_label)
        main.add_widget(submit_btn)
        main.add_widget(back_btn)

        scroll.add_widget(main)

        self.add_widget(scroll)

    def on_pre_enter(self):

        self.emi_label.text = (
            f"Monthly EMI: ₹{self.emi:,.2f}"
        )

    def submit_application(self, instance):

        app = App.get_running_app()

        name = self.name_input.text.strip()
        mobile = self.mobile_input.text.strip()
        pan = self.pan_input.text.strip().upper()

        try:
            amount = float(
                self.amount_input.text
            )
        except ValueError:

            self.show_popup(
                "Invalid Amount",
                "Please enter a valid loan amount."
            )
            return

        if not name:

            self.show_popup(
                "Missing Name",
                "Please enter your full name."
            )
            return

        if not re.fullmatch(
            r"[0-9]{10}",
            mobile
        ):

            self.show_popup(
                "Invalid Mobile",
                "Enter a valid 10 digit mobile number."
            )
            return

        if not re.fullmatch(
            r"[A-Z]{5}[0-9]{4}[A-Z]",
            pan
        ):

            self.show_popup(
                "Invalid PAN",
                "PAN format should be ABCDE1234F."
            )
            return

        if amount < 1000:

            self.show_popup(
                "Invalid Amount",
                "Minimum loan amount is ₹1000."
            )
            return

        if self.emi <= 0:

            self.show_popup(
                "EMI Missing",
                "Please calculate EMI first."
            )
            return

        # Credit score from saved/demo score
        credit_score = app.get_credit_score()

        loan_data = {
            "name": name,
            "mobile": mobile,
            "pan": pan,
            "amount": amount,
            "emi": self.emi,
            "interest": self.interest,
            "period": self.period,
            "credit_score": credit_score,
            "status": "Pending"
        }

        app.store.put(
            "loan_application",
            **loan_data
        )

        self.show_popup(
            "Application Submitted",
            f"Loan application submitted.\n\n"
            f"Credit Score: {credit_score}\n"
            f"Status: Pending"
        )

        self.manager.current = "status"

    def show_popup(self, title, message):

        content = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=15
        )

        label = Label(
            text=message,
            halign="center"
        )

        button = make_button("OK", 50)

        content.add_widget(label)
        content.add_widget(button)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.88, 0.5)
        )

        button.bind(
            on_release=popup.dismiss
        )

        popup.open()


# =========================================================
# CREDIT SCORE
# =========================================================

class CreditScoreScreen(Screen):

    def on_pre_enter(self):

        self.build_screen()

    def build_screen(self):

        self.clear_widgets()

        app = App.get_running_app()

        score = app.get_credit_score()

        if score >= 750:

            rating = "Excellent"
            message = (
                "Your credit score is excellent."
            )

        elif score >= 700:

            rating = "Good"
            message = (
                "Your credit score is good."
            )

        elif score >= 650:

            rating = "Average"
            message = (
                "Your credit score is average."
            )

        else:

            rating = "Low"
            message = (
                "Your credit score is low."
            )

        main = BoxLayout(
            orientation="vertical",
            padding=25,
            spacing=15
        )

        title = Label(
            text="💳 Credit Score",
            font_size=30,
            bold=True,
            size_hint_y=None,
            height=65
        )

        score_label = Label(
            text=str(score),
            font_size=55,
            bold=True,
            size_hint_y=None,
            height=100
        )

        rating_label = Label(
            text=rating,
            font_size=25,
            bold=True,
            size_hint_y=None,
            height=50
        )

        message_label = Label(
            text=message,
            font_size=18
        )

        info = Label(
            text=(
                "750+ = Excellent\n"
                "700-749 = Good\n"
                "650-699 = Average\n"
                "Below 650 = Low\n\n"
                "This is a demo score and is not "
                "a real CIBIL score."
            ),
            font_size=16
        )

        back_btn = make_button(
            "⬅ Back",
            50
        )

        back_btn.bind(
            on_release=lambda x:
            setattr(
                self.manager,
                "current",
                "home"
            )
        )

        main.add_widget(title)
        main.add_widget(score_label)
        main.add_widget(rating_label)
        main.add_widget(message_label)
        main.add_widget(info)
        main.add_widget(back_btn)

        self.add_widget(main)


# =========================================================
# ELIGIBILITY TEST
# =========================================================

class EligibilityScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_screen()

    def build_screen(self):

        self.clear_widgets()

        scroll = ScrollView()

        main = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=12,
            size_hint_y=None
        )

        main.bind(
            minimum_height=main.setter("height")
        )

        title = Label(
            text="✅ Loan Eligibility Test",
            font_size=28,
            bold=True,
            size_hint_y=None,
            height=65
        )

        self.age_input = TextInput(
            hint_text="Age",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=55
        )

        self.income_input = TextInput(
            hint_text="Monthly Income (₹)",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=55
        )

        self.existing_emi_input = TextInput(
            hint_text="Existing Monthly EMI (₹)",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=55
        )

        self.loan_amount_input = TextInput(
            hint_text="Required Loan Amount (₹)",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=55
        )

        self.credit_input = TextInput(
            hint_text="Credit Score",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=55
        )

        test_btn = make_button(
            "🔍 Check Eligibility",
            60
        )

        test_btn.bind(
            on_release=self.check_eligibility
        )

        self.result_label = Label(
            text="",
            font_size=19,
            bold=True,
            size_hint_y=None,
            height=130
        )

        back_btn = make_button(
            "⬅ Back",
            50
        )

        back_btn.bind(
            on_release=lambda x:
            setattr(
                self.manager,
                "current",
                "home"
            )
        )

        main.add_widget(title)
        main.add_widget(self.age_input)
        main.add_widget(self.income_input)
        main.add_widget(self.existing_emi_input)
        main.add_widget(self.loan_amount_input)
        main.add_widget(self.credit_input)
        main.add_widget(test_btn)
        main.add_widget(self.result_label)
        main.add_widget(back_btn)

        scroll.add_widget(main)

        self.add_widget(scroll)

    def check_eligibility(self, instance):

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

            loan_amount = float(
                self.loan_amount_input.text
            )

            credit_score = int(
                self.credit_input.text
            )

        except ValueError:

            self.show_popup(
                "Error",
                "Please enter all details correctly."
            )
            return

        if age < 18:

            self.result_label.text = (
                "🔴 NOT ELIGIBLE\n\n"
                "Age must be 18 or above."
            )
            return

        if income <= 0:

            self.result_label.text = (
                "🔴 NOT ELIGIBLE\n\n"
                "Monthly income is required."
            )
            return

        if loan_amount < 1000:

            self.result_label.text = (
                "🔴 NOT ELIGIBLE\n\n"
                "Minimum loan amount is ₹1000."
            )
            return

        if credit_score >= 750:

            score_points = 2

        elif credit_score >= 700:

            score_points = 1

        else:

            score_points = 0

        # Simple demo income test
        remaining_income = (
            income - existing_emi
        )

        loan_limit = (
            remaining_income * 10
        )

        if loan_amount <= loan_limit:

            income_ok = True

        else:

            income_ok = False

        if (
            score_points == 2
            and income_ok
        ):

            self.result_label.text = (
                "🟢 ELIGIBLE\n\n"
                "Your basic eligibility looks good."
            )

        elif (
            score_points >= 1
            and income_ok
        ):

            self.result_label.text = (
                "🟡 MAY BE ELIGIBLE\n\n"
                "You may be eligible, subject to "
                "further verification."
            )

        else:

            self.result_label.text = (
                "🔴 NOT ELIGIBLE\n\n"
                "Income or credit score does not "
                "meet this demo's criteria."
            )

    def show_popup(self, title, message):

        content = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=15
        )

        label = Label(
            text=message
        )

        button = make_button(
            "OK",
            50
        )

        content.add_widget(label)
        content.add_widget(button)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.85, 0.4)
        )

        button.bind(
            on_release=popup.dismiss
        )

        popup.open()


# =========================================================
# LOAN STATUS
# =========================================================

class LoanStatusScreen(Screen):

    def on_pre_enter(self):

        self.build_screen()

    def build_screen(self):

        self.clear_widgets()

        app = App.get_running_app()

        main = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        title = Label(
            text="📊 Loan Status",
            font_size=28,
            bold=True,
            size_hint_y=None,
            height=65
        )

        if app.store.exists(
            "loan_application"
        ):

            data = app.store.get(
                "loan_application"
            )

            pan = data.get(
                "pan",
                ""
            )

            if len(pan) >= 6:

                masked_pan = (
                    pan[:2]
                    + "******"
                    + pan[-2:]
                )

            else:

                masked_pan = "********"

            details = (
                f"Name: {data.get('name', '')}\n\n"
                f"Mobile: {data.get('mobile', '')}\n\n"
                f"PAN: {masked_pan}\n\n"
                f"Credit Score: "
                f"{data.get('credit_score', 0)}\n\n"
                f"Loan Amount: ₹"
                f"{data.get('amount', 0):,.2f}\n\n"
                f"Monthly EMI: ₹"
                f"{data.get('emi', 0):,.2f}\n\n"
                f"Interest: "
                f"{data.get('interest', '')}%\n\n"
                f"Loan Period: "
                f"{data.get('period', '')} Months\n\n"
                f"Status: "
                f"{data.get('status', 'Pending')}"
            )

        else:

            details = (
                "No loan application found.\n\n"
                "Please apply for a loan first."
            )

        details_label = Label(
            text=details,
            font_size=17,
            halign="left"
        )

        back_btn = make_button(
            "⬅ Back",
            50
        )

        back_btn.bind(
            on_release=lambda x:
            setattr(
                self.manager,
                "current",
                "home"
            )
        )

        main.add_widget(title)
        main.add_widget(details_label)
        main.add_widget(back_btn)

        self.add_widget(main)


# =========================================================
# PROFILE
# =========================================================

class ProfileScreen(Screen):

    def on_pre_enter(self):

        self.build_screen()

    def build_screen(self):

        self.clear_widgets()

        app = App.get_running_app()

        main = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        title = Label(
            text="👤 Profile",
            font_size=28,
            bold=True,
            size_hint_y=None,
            height=65
        )

        profile = {}

        if app.store.exists("profile"):

            profile = app.store.get(
                "profile"
            )

        self.name_input = TextInput(
            text=profile.get(
                "name",
                ""
            ),
            hint_text="Your Name",
            multiline=False,
            size_hint_y=None,
            height=55
        )

        self.mobile_input = TextInput(
            text=profile.get(
                "mobile",
                ""
            ),
            hint_text="Mobile Number",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=55
        )

        save_btn = make_button(
            "💾 Save Profile"
        )

        save_btn.bind(
            on_release=self.save_profile
        )

        back_btn = make_button(
            "⬅ Back",
            50
        )

        back_btn.bind(
            on_release=lambda x:
            setattr(
                self.manager,
                "current",
                "home"
            )
        )

        main.add_widget(title)
        main.add_widget(self.name_input)
        main.add_widget(self.mobile_input)
        main.add_widget(save_btn)
        main.add_widget(back_btn)

        self.add_widget(main)

    def save_profile(self, instance):

        app = App.get_running_app()

        app.store.put(
            "profile",
            name=self.name_input.text,
            mobile=self.mobile_input.text
        )

        self.show_popup(
            "Saved",
            "Profile saved successfully."
        )

    def show_popup(self, title, message):

        content = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=15
        )

        label = Label(text=message)

        button = make_button("OK", 50)

        content.add_widget(label)
        content.add_widget(button)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.35)
        )

        button.bind(
            on_release=popup.dismiss
        )

        popup.open()


# =========================================================
# SETTINGS
# =========================================================

class SettingsScreen(Screen):

    def on_pre_enter(self):

        self.build_screen()

    def build_screen(self):

        self.clear_widgets()

        main = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        title = Label(
            text="⚙️ Settings",
            font_size=28,
            bold=True,
            size_hint_y=None,
            height=65
        )

        theme_btn = make_button(
            "🎨 Change Theme"
        )

        theme_btn.bind(
            on_release=self.change_theme
        )

        language_btn = make_button(
            "🌐 Change Language"
        )

        language_btn.bind(
            on_release=self.change_language
        )

        privacy_btn = make_button(
            "🔒 Privacy"
        )

        privacy_btn.bind(
            on_release=self.show_privacy
        )

        back_btn = make_button(
            "⬅ Back",
            50
        )

        back_btn.bind(
            on_release=lambda x:
            setattr(
                self.manager,
                "current",
                "home"
            )
        )

        main.add_widget(title)
        main.add_widget(theme_btn)
        main.add_widget(language_btn)
        main.add_widget(privacy_btn)
        main.add_widget(back_btn)

        self.add_widget(main)

    # -----------------------------------------------------
    # THEME
    # -----------------------------------------------------

    def change_theme(self, instance):

        content = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        dark_btn = make_button(
            "🌙 Dark Theme"
        )

        light_btn = make_button(
            "☀ Light Theme"
        )

        blue_btn = make_button(
            "🔵 Blue Theme"
        )

        content.add_widget(dark_btn)
        content.add_widget(light_btn)
        content.add_widget(blue_btn)

        popup = Popup(
            title="Select Theme",
            content=content,
            size_hint=(0.8, 0.5)
        )

        dark_btn.bind(
            on_release=lambda x:
            self.set_theme(
                "Dark",
                popup
            )
        )

        light_btn.bind(
            on_release=lambda x:
            self.set_theme(
                "Light",
                popup
            )
        )

        blue_btn.bind(
            on_release=lambda x:
            self.set_theme(
                "Blue",
                popup
            )
        )

        popup.open()

    def set_theme(self, theme, popup):

        app = App.get_running_app()

        app.theme = theme

        app.store.put(
            "settings",
            language=app.language,
            theme=theme
        )

        app.apply_theme()

        popup.dismiss()

        app.refresh_all_screens()

    # -----------------------------------------------------
    # LANGUAGE
    # -----------------------------------------------------

    def change_language(self, instance):

        content = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        english_btn = make_button(
            "🇬🇧 English"
        )

        hindi_btn = make_button(
            "🇮🇳 Hindi"
        )

        content.add_widget(
            english_btn
        )

        content.add_widget(
            hindi_btn
        )

        popup = Popup(
            title="Select Language",
            content=content,
            size_hint=(0.8, 0.4)
        )

        english_btn.bind(
            on_release=lambda x:
            self.set_language(
                "English",
                popup
            )
        )

        hindi_btn.bind(
            on_release=lambda x:
            self.set_language(
                "Hindi",
                popup
            )
        )

        popup.open()

    def set_language(self, language, popup):

        app = App.get_running_app()

        app.language = language

        app.store.put(
            "settings",
            language=language,
            theme=app.theme
        )

        popup.dismiss()

        app.refresh_all_screens()

    def show_privacy(self, instance):

        self.show_popup(
            "Privacy",
            "This is a demo/local loan application.\n\n"
            "Loan information is stored locally "
            "on this device."
        )

    def show_popup(self, title, message):

        content = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=15
        )

        label = Label(
            text=message,
            halign="center"
        )

        button = make_button(
            "OK",
            50
        )

        content.add_widget(label)
        content.add_widget(button)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.88, 0.55)
        )

        button.bind(
            on_release=popup.dismiss
        )

        popup.open()


# =========================================================
# CHANGE PASSWORD
# =========================================================

class ChangePasswordScreen(Screen):

    def on_pre_enter(self):

        self.build_screen()

    def build_screen(self):

        self.clear_widgets()

        main = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        title = Label(
            text="🔑 Change Password",
            font_size=28,
            bold=True,
            size_hint_y=None,
            height=65
        )

        old_password = TextInput(
            hint_text="Current Password",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=55
        )

        new_password = TextInput(
            hint_text="New Password",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=55
        )

        confirm_password = TextInput(
            hint_text="Confirm New Password",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=55
        )

        save_btn = make_button(
            "🔐 Change Password"
        )

        save_btn.bind(
            on_release=lambda x:
            self.change_password(
                old_password,
                new_password,
                confirm_password
            )
        )

        back_btn = make_button(
            "⬅ Back",
            50
        )

        back_btn.bind(
            on_release=lambda x:
            setattr(
                self.manager,
                "current",
                "home"
            )
        )

        main.add_widget(title)
        main.add_widget(old_password)
        main.add_widget(new_password)
        main.add_widget(confirm_password)
        main.add_widget(save_btn)
        main.add_widget(back_btn)

        self.add_widget(main)

    def change_password(
        self,
        old_password,
        new_password,
        confirm_password
    ):

        app = App.get_running_app()

        saved_password = app.store.get(
            "security"
        ).get(
            "password",
            "1234"
        )

        if old_password.text != saved_password:

            self.show_popup(
                "Error",
                "Current password is incorrect."
            )
            return

        if len(new_password.text) < 4:

            self.show_popup(
                "Error",
                "New password must contain at least 4 characters."
            )
            return

        if new_password.text != confirm_password.text:

            self.show_popup(
                "Error",
                "Passwords do not match."
            )
            return

        app.store.put(
            "security",
            password=new_password.text
        )

        self.show_popup(
            "Success",
            "Password changed successfully."
        )

    def show_popup(self, title, message):

        content = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=15
        )

        label = Label(text=message)

        button = make_button(
            "OK",
            50
        )

        content.add_widget(label)
        content.add_widget(button)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4)
        )

        button.bind(
            on_release=popup.dismiss
        )

        popup.open()


# =========================================================
# HELP
# =========================================================

class HelpScreen(Screen):

    def on_pre_enter(self):

        self.build_screen()

    def build_screen(self):

        self.clear_widgets()

        main = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        title = Label(
            text="❓ Payal Loan",
            font_size=30,
            bold=True,
            size_hint_y=None,
            height=65
        )

        info = Label(
            text=(
                "Payal Loan is a demo loan application.\n\n"
                "Features:\n"
                "• Loan EMI Calculator\n"
                "• Loan Application\n"
                "• Credit Score\n"
                "• Eligibility Test\n"
                "• Loan Status\n"
                "• Hindi / English\n"
                "• Dark / Light / Blue Theme\n"
                "• Password Protection\n\n"
                "This application is not connected "
                "to a real bank or lender."
            ),
            font_size=17,
            halign="left"
        )

        back_btn = make_button(
            "⬅ Back",
            50
        )

        back_btn.bind(
            on_release=lambda x:
            setattr(
                self.manager,
                "current",
                "home"
            )
        )

        main.add_widget(title)
        main.add_widget(info)
        main.add_widget(back_btn)

        self.add_widget(main)


# =========================================================
# MAIN APP
# =========================================================

class LoanApp(App):

    def build(self):

        self.title = "Payal Loan"

        data_file = os.path.join(
            self.user_data_dir,
            "payal_loan_data.json"
        )

        self.store = JsonStore(
            data_file
        )

        # -------------------------------------------------
        # SETTINGS
        # -------------------------------------------------

        if self.store.exists("settings"):

            settings = self.store.get(
                "settings"
            )

            self.language = settings.get(
                "language",
                "English"
            )

            self.theme = settings.get(
                "theme",
                "Blue"
            )

        else:

            self.language = "English"
            self.theme = "Blue"

            self.store.put(
                "settings",
                language=self.language,
                theme=self.theme
            )

        # -------------------------------------------------
        # PASSWORD
        # -------------------------------------------------

        if not self.store.exists(
            "security"
        ):

            self.store.put(
                "security",
                password="1234"
            )

        # -------------------------------------------------
        # CREDIT SCORE
        # -------------------------------------------------

        if not self.store.exists(
            "credit_score"
        ):

            self.store.put(
                "credit_score",
                score=750
            )

        # -------------------------------------------------
        # SCREEN MANAGER
        # -------------------------------------------------

        self.sm = ScreenManager(
            transition=FadeTransition(
                duration=0.2
            )
        )

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

        self.apply_theme()

        return self.sm

    # -----------------------------------------------------
    # CREDIT SCORE
    # -----------------------------------------------------

    def get_credit_score(self):

        if self.store.exists(
            "credit_score"
        ):

            return self.store.get(
                "credit_score"
            ).get(
                "score",
                750
            )

        return 750

    # -----------------------------------------------------
    # THEME
    # -----------------------------------------------------

    def apply_theme(self):

        if self.theme == "Dark":

            Window.clearcolor = (
                0.08,
                0.08,
                0.08,
                1
            )

        elif self.theme == "Light":

            Window.clearcolor = (
                0.95,
                0.95,
                0.95,
                1
            )

        elif self.theme == "Blue":

            Window.clearcolor = (
                0.04,
                0.16,
                0.32,
                1
            )

    # -----------------------------------------------------
    # REFRESH
    # -----------------------------------------------------

    def refresh_all_screens(self):

        current = self.sm.current

        for screen in self.sm.screens:

            if hasattr(
                screen,
                "build_screen"
            ):

                try:
                    screen.build_screen()
                except Exception:
                    pass

        self.sm.current = current


# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    LoanApp().run()

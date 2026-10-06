from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView


class LoanApp(App):

    def build(self):
        # =========================
        # LOADING SCREEN
        # =========================
        self.loading = BoxLayout(
            orientation="vertical",
            padding=40,
            spacing=20
        )

        self.loading.add_widget(
            Label(
                text="PAYAL LOAN",
                font_size=40,
                bold=True
            )
        )

        self.loading.add_widget(
            Label(
                text="Loading...",
                font_size=25
            )
        )

        Clock.schedule_once(self.show_home, 2)

        return self.loading

    # =========================
    # HOME SCREEN
    # =========================
    def show_home(self, dt):

        main = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=12
        )

        title = Label(
            text="PAYAL LOAN",
            font_size=32,
            bold=True,
            size_hint_y=None,
            height=60
        )
        main.add_widget(title)

        scroll = ScrollView()

        form = GridLayout(
            cols=1,
            spacing=10,
            padding=10,
            size_hint_y=None
        )

        form.bind(minimum_height=form.setter("height"))

        # =========================
        # CUSTOMER NAME
        # =========================
        form.add_widget(
            Label(
                text="Customer Name",
                font_size=20,
                size_hint_y=None,
                height=40
            )
        )
        self.customer_name = TextInput(
           hint_text="Enter customer name",
            multiline=False,
             size_hint_y=None,
             height=50
)
        form.add_widget(self.customer_name)

        # =========================
        # MOBILE NUMBER
        # =========================
        form.add_widget(
            Label(
                text="Mobile Number",
                font_size=20,
                size_hint_y=None,
                height=40
            )
        )

        self.mobile = TextInput(
            hint_text="Enter mobile number",
            input_filter="int",
            multiline=False,
            size_hint_y=None,
            height=50
        )
        form.add_widget(self.mobile)

        # =========================
        # LOAN AMOUNT
        # =========================
        form.add_widget(
            Label(
                text="Loan Amount (₹)",
                font_size=20,
                size_hint_y=None,
                height=40
            )
        )

        self.amount = TextInput(
            hint_text="Example: 300000",
            input_filter="float",
            multiline=False,
            size_hint_y=None,
            height=50
        )
        form.add_widget(self.amount)

        # =========================
        # INTEREST RATE
        # =========================
        form.add_widget(
            Label(
                text="Interest Rate (%)",
                font_size=20,
                size_hint_y=None,
                height=40
            )
        )

        self.rate = TextInput(
            hint_text="Example: 10",
            input_filter="float",
            multiline=False,
            size_hint_y=None,
            height=50
        )
        form.add_widget(self.rate)

        # =========================
        # LOAN PERIOD
        # =========================
        form.add_widget(
            Label(
                text="Loan Period (Years)",
                font_size=20,
                size_hint_y=None,
                height=40
            )
        )

        self.years = TextInput(
            hint_text="Example: 5",
            input_filter="float",
            multiline=False,
            size_hint_y=None,
            height=50
        )
        form.add_widget(self.years)

        # =========================
        # CALCULATE BUTTON
        # =========================
        calculate_button = Button(
            text="CALCULATE EMI",
            font_size=22,
            size_hint_y=None,
            height=60
        )

        calculate_button.bind(
            on_press=self.calculate_emi
        )

        form.add_widget(calculate_button)

        # =========================
        # RESET BUTTON
        # =========================
        reset_button = Button(
            text="RESET",
            font_size=20,
            size_hint_y=None,
            height=55
        )

        reset_button.bind(
            on_press=self.reset_form
        )

        form.add_widget(reset_button)

        # =========================
        # RESULT
        # =========================
        self.result = Label(
            text="Monthly EMI: ₹0",
            font_size=25,
            bold=True,
            size_hint_y=None,
            height=60
        )

        form.add_widget(self.result)

        # =========================
        # SUMMARY BUTTON
        # =========================
        summary_button = Button(
            text="VIEW LOAN SUMMARY",
            font_size=20,
            size_hint_y=None,
            height=55
        )

        summary_button.bind(
            on_press=self.show_summary
        )

        form.add_widget(summary_button)

        # =========================
        # HELP BUTTON
        # =========================
        help_button = Button(
            text="HELP / ABOUT",
            font_size=20,
            size_hint_y=None,
            height=55
        )

        help_button.bind(
            on_press=self.show_help
        )

        form.add_widget(help_button)

        scroll.add_widget(form)

        main.add_widget(scroll)

        self.root.clear_widgets()
        self.root.add_widget(main)

    # =========================
    # EMI CALCULATION
    # =========================
    def calculate_emi(self, instance):

        try:

            if not self.customer_name.text.strip():
                self.result.text = "Please enter customer name"
                return

            if len(self.mobile.text) != 10:
                self.result.text = "Please enter valid mobile number"
                return

            principal = float(self.amount.text)
            rate = float(self.rate.text)
            years = float(self.years.text)

            if principal <= 0:
                self.result.text = "Enter valid loan amount"
                return

            if rate < 0:
                self.result.text = "Enter valid interest rate"
                return

            if years <= 0:
                self.result.text = "Enter valid loan period"
                return

            monthly_rate = rate / 12 / 100
            months = years * 12

            if monthly_rate == 0:

                emi = principal / months

            else:

                emi = (
                    principal
                    * monthly_rate
                    * (1 + monthly_rate) ** months
                    / (
                        (1 + monthly_rate) ** months - 1
                    )
                )

            total_payment = emi * months
            total_interest = total_payment - principal

            self.emi_value = emi
            self.total_payment = total_payment
            self.total_interest = total_interest

            self.result.text = (
                f"Monthly EMI: ₹{emi:,.2f}"
            )

        except ValueError:

            self.result.text = (
                "Please enter valid numbers"
            )

    # =========================
    # LOAN SUMMARY
    # =========================
    def show_summary(self, instance):

        try:

            emi = self.emi_value

            summary = (
                f"Customer Name: {self.customer_name.text}\n\n"
                f"Mobile: {self.mobile.text}\n\n"
                f"Loan Amount: ₹{float(self.amount.text):,.2f}\n\n"
                f"Interest Rate: {self.rate.text}%\n\n"
                f"Loan Period: {self.years.text} Years\n\n"
                f"Monthly EMI: ₹{emi:,.2f}\n\n"
                f"Total Interest: "
                f"₹{self.total_interest:,.2f}\n\n"
                f"Total Payment: "
                f"₹{self.total_payment:,.2f}"
            )

            content = BoxLayout(
                orientation="vertical",
                padding=20,
                spacing=15
            )

            content.add_widget(
                Label(
                    text=summary,
                    font_size=18
                )
            )

            close_button = Button(
                text="CLOSE",
                size_hint_y=None,
                height=50
            )

            content.add_widget(close_button)

            popup = Popup(
                title="Loan Summary",
                content=content,
                size_hint=(0.9, 0.8)
            )

            close_button.bind(
                on_press=popup.dismiss
            )

            popup.open()

        except AttributeError:

            self.result.text = (
                "Please calculate EMI first"
            )

    # =========================
    # RESET
    # =========================
    def reset_form(self, instance):

        self.customer_name.text = ""
        self.mobile.text = ""
        self.amount.text = ""
        self.rate.text = ""
        self.years.text = ""

        self.result.text = "Monthly EMI: ₹0"

        if hasattr(self, "emi_value"):
            del self.emi_value

    # =========================
    # HELP / ABOUT
    # =========================
    def show_help(self, instance):

        message = (
            "PAYAL LOAN\n\n"
            "EMI Calculator Demo\n\n"
            "Enter customer details, "
            "loan amount, interest rate "
            "and loan period to calculate "
            "an estimated monthly EMI.\n\n"
            "This app is for demonstration "
            "and calculation purposes."
        )

        content = BoxLayout(
            orientation="vertical",
            padding=20,
            spacing=15
        )

        content.add_widget(
            Label(
                text=message,
                font_size=18
            )
        )

        close_button = Button(
            text="CLOSE",
            size_hint_y=None,
            height=50
        )

        content.add_widget(close_button)

        popup = Popup(
            title="Help / About",
            content=content,
            size_hint=(0.9, 0.7)
        )

        close_button.bind(
            on_press=popup.dismiss
        )

        popup.open()


LoanApp().run()

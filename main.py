from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


class LoanApp(App):

    def build(self):
        layout = BoxLayout(
            orientation="vertical",
            padding=30,
            spacing=15
        )

        title = Label(
            text="PAYAL LOAN",
            font_size=30,
            bold=True
        )
        layout.add_widget(title)

        layout.add_widget(Label(text="Loan Amount (₹)"))
        self.amount = TextInput(
            hint_text="Example: 300000",
            input_filter="float",
            multiline=False
        )
        layout.add_widget(self.amount)

        layout.add_widget(Label(text="Interest Rate (%)"))
        self.rate = TextInput(
            hint_text="Example: 10",
            input_filter="float",
            multiline=False
        )
        layout.add_widget(self.rate)

        layout.add_widget(Label(text="Loan Period (Years)"))
        self.years = TextInput(
            hint_text="Example: 5",
            input_filter="float",
            multiline=False
        )
        layout.add_widget(self.years)

        button = Button(
            text="CALCULATE EMI",
            font_size=60
        )
        button.bind(on_press=self.calculate_emi)
        layout.add_widget(button)

        self.result = Label(
            text="Monthly EMI: ₹0",
            font_size=60
        )
        layout.add_widget(self.result)

        return layout

    def calculate_emi(self, instance):
        try:
            principal = float(self.amount.text)
            rate = float(self.rate.text)
            years = float(self.years.text)

            monthly_rate = rate / 12 / 100
            months = years * 12

            if monthly_rate == 0:
                emi = principal / months
            else:
                emi = (
                    principal
                    * monthly_rate
                    * (1 + monthly_rate) ** months
                    / ((1 + monthly_rate) ** months - 1)
                )

            self.result.text = f"Monthly EMI: ₹{emi:.2f}"

        except:
            self.result.text = "Please enter valid numbers"


LoanApp().run()

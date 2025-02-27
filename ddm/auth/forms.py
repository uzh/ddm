from django import forms


class TokenCreationForm(forms.Form):
    expiration_days = forms.IntegerField(
        initial=30,
        min_value=1,
        max_value=90,
        required=True
    )
    action = forms.CharField(
        max_length=20,
        initial='create',
        widget=forms.HiddenInput()
    )

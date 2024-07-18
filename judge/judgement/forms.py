from django import forms


class CodeForm(forms.Form):
    code = forms.CharField(label="",
                           required=True,
                            widget=forms.Textarea(
                                attrs={'placeholder': 'Enter your code'}
                            ))

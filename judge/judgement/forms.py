from django import forms


class CodeForm(forms.Form):
    code = forms.CharField(label="",
                            widget=forms.Textarea(
                                attrs={'placeholder': 'Enter your code'}
                            ))

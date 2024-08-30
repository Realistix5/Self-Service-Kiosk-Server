# forms.py

from django import forms


class FeedbackForm(forms.Form):
    feedback_text = forms.CharField(widget=forms.Textarea, label='Feedback', required=True)
    feedback_sender = forms.CharField(label='Absender (optional)', required=False)

from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=Review.RATING_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
    )

    class Meta:
        model = Review
        fields = ('rating', 'comment')

from django.forms import ModelForm, Textarea
from .models import Listing, Comment

class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'category', 'price', 'image_link', 'image_alt_text', 'description']
        widgets = {
            'description': Textarea(attrs={'cols': 80, 'rows': 10}),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': Textarea(attrs={'cols': 70, 'rows': 5}),
        }
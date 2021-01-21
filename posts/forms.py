from django import forms
from .models import Post, Group, Comment


class PostForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)
    group = forms.ModelChoiceField(Group.objects.all(), required=False)

    class Meta:
        model = Post
        fields = ['text', 'group', 'image']


class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Comment
        fields = ['text']

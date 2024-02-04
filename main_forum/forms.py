from .models import Question, Tag, Answer
from django import forms
from ckeditor.widgets import CKEditorWidget
from django_quill.forms import QuillFormField
from taggit.forms import TagField


class QuestionForm(forms.ModelForm):
    """
    Form for asking a question. The user can enter a subject line and the main body of the question. They can also tag the question with up to 5 tags. If the user is updating a question, the form needs to be pre-populated with the existing data.
    """
    subject = forms.CharField(
        max_length=100, 
        required=True, 
        label='Enter your question heading here',  # Update the label here
        help_text='Enter a subject line for your question.'
    )
    content = QuillFormField()
    tags = forms.CharField(required=False)

    class Meta:
        """
        the Meta class is used to specify the model to which the form is associated and the fields from the model you want the form to include.
        """
        model = Question  # Specifies the model in models.py associated with this form
        fields = ['subject', 'content', 'tags']

    def clean_subject(self):
        print('cleaning subject')
        subject = self.cleaned_data.get('subject')
        if self.instance.pk:  # if this form is updating an existing instance
            print('checking if question with same subject exists')
            if Question.objects.filter(subject=subject).exclude(pk=self.instance.pk).exists(): # Check if a question with the same subject exists, excluding the current question
                print('question with same subject exists')
                print('raising error')
                raise forms.ValidationError('A question with this subject already exists.')
        else: # if this form is creating a new instance
            if Question.objects.filter(subject=subject).exists():
                raise forms.ValidationError('A question with this subject already exists.')
        return subject
  

    def clean_tags(self):
        print('cleaning tags')
        tags = self.cleaned_data.get('tags', '')
        print('saving cleaned tags', tags)
        return tags

    def save(self, *args, **kwargs):
        print('saving question')
        instance = super(QuestionForm, self).save(commit=False)
        # Do not commit yet, need to save m2m relations (tags) after the instance is saved
        instance.save()
        # Handling tags here
        tags = self.cleaned_data.get('tags', '')
        tag_names = tags.split()  # Split the string into a list of tag names
        instance.tags.set(tag_names, clear=True) # Set the tags for the instance
        print('instance.tags.all:', instance.tags.all())
        return instance

class AnswerForm(forms.ModelForm) :
    body = QuillFormField()

    class Meta: # Meta class is used to specify the model to which the form is associated
        model = Answer
        fields = ['body']

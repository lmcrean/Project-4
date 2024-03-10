from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from ..models import Question, Answer, UserProfile, ReputationPoints
import re

class BaseVotingView(LoginRequiredMixin, View):
    """
    Base view for upvoting and downvoting questions and answers. This view is inherited by the specific views for each type of vote from QuestionUpvote, QuestionDownvote, AnswerUpvote, and AnswerDownvote.

        def post(self, request, *args, **kwargs) is the Method for handling the POST request, and is called when a user clicks the upvote or downvote button on a question or answer. 
            1. If the user has already voted in the opposite direction, a message is displayed to remove the existing vote before voting in the opposite direction.  opposite_vote_type is used to determine the opposite vote type for the object. 
            2. If the user has already voted in the same direction, the vote is removed. 
            3. If the user has not voted, the vote is added. The method then calls the get_redirect_url method to redirect the user to the appropriate page.
        
        def get_redirect_url(self, obj) is the Method for getting the redirect URL based on the type of object. This method is overridden in the specific views for each type of vote to redirect the user to the appropriate page after voting.

        def get(self, request, *args, **kwargs) is the Method for handling GET requests. This method returns an HttpResponseNotAllowed response to prevent users from voting by directly accessing the URL.
    """
    model = None
    vote_type = None

    def post(self, request, *args, **kwargs):
        """
        This method is called when a user clicks the upvote or downvote button on a question or answer.

        1. if the user is the author of the question or answer, a message is displayed to inform the user that they cannot vote on their own post. obj.author is used to determine the author of the object.
        2. If the user has already voted in the opposite direction, a message is displayed to remove the existing vote before voting in the opposite direction.  opposite_vote_type is used to determine the opposite vote type for the object.
        3. If the user has already voted in the same direction, the vote is removed instead of added. This is important to prevent users from voting multiple times in the same direction.
        4. If the user has not voted, the vote is added. 
        
        The method then calls the get_redirect_url method to redirect the user to the appropriate page.
        """
        identifier = kwargs.get('pk') or kwargs.get('slug')
        obj = get_object_or_404(self.model, slug=identifier) if 'slug' in kwargs else get_object_or_404(self.model, pk=identifier)
        user_profile = UserProfile.objects.get(user=obj.author)
        vote_attr = getattr(obj, self.vote_type) # this is being tested, vote attr can be upvotes or downvotes
        opposite_vote_attr = getattr(obj, 'downvotes' if self.vote_type == 'upvotes' else 'upvotes')
        vote_already_exists = vote_attr.filter(id=request.user.id).exists()
        action = 'remove' if vote_already_exists else 'add'
        origin_page = request.META.get('HTTP_REFERER', '/')  # Capture the referring page

        if obj.author == request.user:
            messages.error(request, "You cannot vote on your own post.")
            return self.get_redirect_url(obj)

        if opposite_vote_attr.filter(id=request.user.id).exists():
            messages.error(request, "Please remove your existing vote before voting in the opposite direction.")
            return self.get_redirect_url(obj)

        if vote_already_exists:
            vote_attr.remove(request.user)
            messages.success(request, "Your vote has been removed.")
        else:
            vote_attr.add(request.user) # add the vote if it does not exist
            messages.success(request, "Your vote has been added.")

        return self.get_redirect_url(obj, origin_page=origin_page)


    def get_redirect_url(self, obj, origin_page='/'):
        """
        This method is overridden in the specific views for each type of vote to redirect the user to the appropriate page after voting.
        """
        tag_regex = r'/tags/([\w-]+)/'
        if origin_page:  # Only proceed if origin_page is not an empty string
            match = re.search(tag_regex, origin_page)
            if match:
                # If origin_page matches the filtered tag list pattern, redirect back to that filtered list
                tag_name = match.group(1)
                return HttpResponseRedirect(reverse('filtered_questions', args=[tag_name]))
        elif origin_page == 'questions_list':
            return HttpResponseRedirect(reverse('questions'))
        elif isinstance(obj, Question):
            return HttpResponseRedirect(reverse('question_detail', args=[obj.slug]))
        elif isinstance(obj, Answer):
            return HttpResponseRedirect(reverse('question_detail', kwargs={'slug': obj.question.slug}))
        else:
            return HttpResponseRedirect('/')


    def get(self, request, *args, **kwargs): 
        """only allow POST requests. This is to prevent users from voting by directly accessing the URL"""
        return HttpResponseNotAllowed(['POST'])

class QuestionUpvote(BaseVotingView):
    """ view for upvoting questions using the BaseVotingView class"""
    model = Question
    vote_type = 'upvotes'

class QuestionDownvote(BaseVotingView):
    """ view for downvoting questions using the BaseVotingView class"""
    model = Question
    vote_type = 'downvotes'

class AnswerUpvote(BaseVotingView):
    """ view for upvoting answers using the BaseVotingView class"""
    model = Answer
    vote_type = 'upvotes'

    def get_redirect_url(self, obj, origin_page=None): 
        return redirect('question_detail', slug=obj.question.slug)

class AnswerDownvote(BaseVotingView):
    """ view for downvoting answers using the BaseVotingView class """
    model = Answer
    vote_type = 'downvotes'

    def get_redirect_url(self, obj, origin_page=None):
        return redirect('question_detail', slug=obj.question.slug)

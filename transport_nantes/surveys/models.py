from django.db import models

# Cf. https://docs.djangoproject.com/en/3.0/ref/models/fields/

class Survey(models.Model):
    """Represent a survey.

    This does not represent the questions (SurveyQuestions) or
    anyone's responses.

    """
    # A human-presentable name of the survey
    name = models.CharField(max_length=200)
    # More information about the survey.  For humans.
    description = models.TextField()

class SurveyQuestion(models.Model):
    """Represent a set of questions (a survey).

    This does not represent anyone's responses.

    """
    survey_id = models.ForeignKey(Survey, on_delete=models.CASCADE)
    # Question numbers are strings because we might have "3a" and
    # "3b", for example.
    question_number = models.CharField(max_length=10)
    # For a given survey, the questions will be sorted in ascending
    # order by sort_index.  This primarily avoids having to use "09"
    # as soon as question "10" is added.
    sort_index = models.IntegerField()
    question_title = models.CharField(max_length=200)
    question_text = models.TextField()

class SurveyResponder(models.Model):
    """Represent someone or something that might respond to a survey.

    We use this for tracking people and parties who might respond to
    the survey.  This is not fully normalised because people and lists
    join together and split apart.

    """
    # People are generally authorised only to respond for one
    # party/list and for one survey.  If they wish to respond to
    # another survey, they'll need to be revalidated (and to have a
    # new entry in this table)..
    survey_id = models.ForeignKey(Survey, on_delete=models.CASCADE)

    # In a self-service context, we'll use validated to indicate that
    # we've confirmed that the person is authorised to reply for the
    # list.
    validated = models.BooleanField()
    # Our surveys typically involve political entities.
    commune = models.CharField(max_length=100)
    liste = models.CharField(max_length=100)
    # The list head is a person.  We use this name to personalise information.
    tete_de_liste = models.CharField(max_length=100)

    # The email_liste is the official email for the list or party, if
    # we know it.  The email_person is the specific email of the
    # person who is responding, if we know it.  When we provide
    # self-service, the intent is that email_person is the mail that
    # will be asked to verify that a contribution or change is
    # legimiate (i.e., used for login/authentication).
    email_liste = models.CharField(max_length=100)
    email_person = models.CharField(max_length=100)

    url = models.URLField(max_length=200)
    # The twitter fields are the part after the "@".
    twitter_liste = models.CharField(max_length=100)
    twitter_candidat = models.CharField(max_length=100)
    # The facebook username, after the "/" in the page URL.
    facebook = models.CharField(max_length=100)

class SurveyResponse(models.Model):
    """Represent candidate/party responses to survey questions.
    """
    survey_id = models.ForeignKey(Survey, on_delete=models.CASCADE)
    survey_question_id = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE)
    survey_responder_id = models.ForeignKey(SurveyResponder, on_delete=models.CASCADE)

    survey_question_response = models.TextField()

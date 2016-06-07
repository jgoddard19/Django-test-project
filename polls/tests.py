import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import Question

def create_question(question_text, days):
	"""
	Creates a question with the given 'question_text'
	"""
	time = timezone.now() + datetime.timedelta(days=days)
	return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionViewTests(TestCase):
	def test_index_view_w_no_questions(self):
		"""
		If no questions exist, display appropriate message
		"""
		response = self.client.get(reverse('polls:index'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(response.context['latest_question_list'], [])

	def test_index_view_w_past_question(self):
		"""
		Questions w/ a pub_date in the past should 
		be displayed on the index page
		"""
		create_question(question_text="Past question.", days=-30)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(
			response.context['latest_question_list'],
			['<Question: Past question.>']
		)

	def test_index_view_w_future_question(self):
		"""
		Questions w/ a pub_date in the future should not
		be displayed on the index page
		"""
		create_question(question_text="Future question.", days=30)
		response = self.client.get(reverse('polls:index'))
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(response.context['latest_question_list'], [])

	def test_index_view_w_future_question_and_past_question(self):
		"""
		Even if both past and future questions exist, only past questions
        should be displayed
    	"""
		create_question(question_text="Past question.", days=-30)
		create_question(question_text="Future question.", days=30)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(
        	response.context['latest_question_list'],
        	['<Question: Past question.>']
    	)

	def test_index_view_w_two_past_questions(self):
		"""
		The questions index page may display multiple questions
		"""
		create_question(question_text="Past question 1.", days=-30)
		create_question(question_text="Past question 2.", days=-5)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(
			response.context['latest_question_list'],
			['<Question: Past question 2.>', '<Question: Past question 1.>']
			)

class QuestionMethodTests(TestCase):
	def test_was_published_recently_w_future_question(self):
		"""
		was_published_recently() should return False for future pub_date entries
		"""
		time = timezone.now() + datetime.timedelta(days=30)
		future_question = Question(pub_date=time)
		self.assertEqual(future_question.was_published_recently(), False)
	def test_was_published_recently_w_old_question(self):
		"""
		was_published_recently() should return False for questions w/
		pub_date older than one day
		"""
		time = timezone.now() - datetime.timedelta(days=30)
		old_question = Question(pub_date=time)
		self.assertEqual(old_question.was_published_recently(), False)
	def test_was_published_recently_w_recent_question(self):
		"""
		was_published_recently() should return True for questions w/
		pub_date w/in the last day
		"""
		time = timezone.now() - datetime.timedelta(hours=1)
		recent_question = Question(pub_date=time)
		self.assertEqual(recent_question.was_published_recently(), True)

class QuestionIndexDetailTests(TestCase):
	def test_detail_view_w_future_question(self):
		"""
		The detail view of a question w/ a pub_date in the future
		should return a 404
		"""
		future_question = create_question(question_text='Future question.', days=5)
		url = reverse('polls:detail', args=(future_question.id,))
		response = self.client.get(url)
		self.assertEqual(response.status_code, 404)

	def test_detail_view_w_past_question(self):
		"""
		The detail view of a question w/ a pub_date in the past
		should display the question text
		"""
		past_question = create_question(question_text='Past question.', days=-5)
		url = reverse('polls:detail', args=(past_question.id,))
		response = self.client.get(url)
		self.assertContains(response, past_question.question_text)

		


from django.test import TestCase, Client
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .models import Subject,Course, UserInfo, ShoppingCart, Comments, FriendList, FriendRequest, Review
from .forms import NewReview
from django.contrib.auth import get_user_model
from django.test import Client
from django.contrib.auth.models import User
import unittest, requests

def create_subject(subject, name):
    """
    Global function to allow the creation of subject objects
    """
    return Subject.objects.create(subject=subject, name=name)


class GoogleLoginTests(TestCase):

    def test_login_page(self):
        """Check that the login page successfully loads"""
        response1 = self.client.get('/')
        self.assertContains(response1, "Google Sign-In")
        response2 = self.client.get(reverse('google_login'))
        self.assertEqual(response2.status_code, 200)

    def test_that_login_works(self):
        """Check that the login page successfully loads and that the user can successfully login"""
        response1 = self.client.get('/')
        self.assertContains(response1, "Google Sign-In")
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client = Client()
        self.client.login(username=user.username, password='pass')
        self.assertTrue(user.is_authenticated)
        response2 = self.client.get('/')
        self.assertContains(response2, "Welcome, You are logged in as")

    def test_that_logout_works(self):
        """Check that the user is able to successfully logout"""
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client = Client()
        self.client.login(username=user.username, password='pass')
        self.assertTrue(user.is_authenticated)
        self.client.logout()
        response2 = self.client.get(reverse('NewLousList:logout'))
        response3 = self.client.get('/')
        self.assertContains(response3, "Google Sign-In")
        self.assertEqual(response3.status_code, 200)


class HomePageTests(TestCase):

    def test_home_page_without_login(self):
        """
        Home page, which contains a list of all subjects will redirect if not logged in
        """
        response = self.client.get(reverse('NewLousList:index'))
        #redirect since not logged int
        self.assertEqual(response.status_code, 302)


    def test_home_page_with_login(self):
        """
        Home page, which contains a list of all subjects, successfully laads after login
        """
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')
        response = self.client.get(reverse('NewLousList:index'))
        self.assertEqual(response.status_code, 200)

    def test_subject_model(self):
        """
        Test to ensure the subject model works
        """
        subjects = [{"subject": "XX1"}, {"subject": "XX2"}, {"subject": "XX3"}]
        subject_and_names = {"XX1": "TEST1", "XX2": "TEST2", "XX3": "TEST3"}

        for sub in subjects:
            Subject.objects.get_or_create(subject=sub['subject'],name=subject_and_names[sub['subject']])
        self.assertTrue(Subject.objects.filter(subject__exact="XX1").exists())
        self.assertTrue(Subject.objects.filter(subject__exact="XX2").exists())
        self.assertTrue(Subject.objects.filter(subject__exact="XX3").exists())
        Subject.objects.get(subject='XX1').delete()
        Subject.objects.get(subject='XX2').delete()
        Subject.objects.get(subject='XX3').delete()

    def test_subject_list_display(self):
        """
        The home page displays all the subjects in the database
        """
        sub1 = create_subject('XXX', 'Test Subject 1')
        sub2 = create_subject('ZZZ', 'Test Subject 2')
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')
        url = reverse('NewLousList:index')
        response = self.client.get(url)
        # self.assertContains(response, sub1.name)
        # self.assertContains(response, sub2.name)
        self.assertContains(response, 'Subject Departments')
        self.assertContains(response, 'ACCT - Accounting')
        self.assertContains(response, 'BIOL - Biology')
        self.assertContains(response, 'CS - Computer Science')
        self.assertContains(response, 'EURS')
        # Subject.objects.get(subject='XXX').delete()
        # Subject.objects.get(subject='ZZZ').delete()


    def test_subject_redirect(self):
        """
        When a subject is selected, the site is redirected to a page that displays all
        the courses for that subject
        """
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')
        ACCT_subject = Subject.objects.create(subject='ACCT')
        response = self.client.get(reverse('NewLousList:courses_by_subject', args=('ACCT',)))
        self.assertEqual(response.status_code, 200)
        Subject.objects.get(subject='ACCT').delete()


    def test_logout_url_on_homePage(self):
        """
        When logout button is selected, the user is logged out and the site is redirected to the login page
        """
        user = User.objects.create_user(username='testUser', password='pass',email='test@gmail.com')
        self.client.login(username=user.username, password='pass')
        response = self.client.get(reverse('NewLousList:index'))
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        response2 = self.client.get(reverse('NewLousList:logout'))
        response3 = self.client.get('/')
        self.assertContains(response3, "Google Sign-In")
        self.assertEqual(response3.status_code, 200)

class homePageSubjectSearchTests(TestCase):
    def test_specific_search(self):
        """
        Search for a valid subject with only one result expected
        """
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')

        response = self.client.get("/NewLousList/?search=computer+science")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CS - Computer Science')
        self.assertFalse('ACCT' in response)

    def test_broad_search(self):
        """
        Search for a valid subject with multiple results expected
        """
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')

        response = self.client.get("/NewLousList/?search=no")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ASTR - Astronomy')
        self.assertContains(response, 'ECON - Economics')
        self.assertContains(response, 'IT - Informational Technology')
        self.assertFalse('on' in response)

    def test_no_results_search(self):
        """
        Search for a invalid subject with no expected search results
        """
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')

        response = self.client.get("/NewLousList/?search=maraki")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Subjects to display.')



class courseBySubjectTests(TestCase):

    def test_courses_by_subject_valid(self):
        """
        Check that courses for a specific subject appear when selected
        """
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')

        ACCT_subject = Subject.objects.create(subject='ACCT')
        response = self.client.get(reverse('NewLousList:courses_by_subject', args=('ACCT',)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Introductory Accounting I')

        CS_subject = Subject.objects.create(subject='CS')
        response = self.client.get(reverse('NewLousList:courses_by_subject', args=('CS',)))
        self.assertEqual(response.status_code, 200)

        Subject.objects.get(subject='ACCT').delete()
        Subject.objects.get(subject='CS').delete()



    def test_template_used(self):
        """
        Check that the proper template is used to display courses for a specific subject
        """
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')

        ACCT_subject = Subject.objects.create(subject='ACCT')
        response = self.client.get(reverse('NewLousList:courses_by_subject', args=('ACCT',)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'NewLousList/courses_by_subject.html')

        CS_subject = Subject.objects.create(subject='CS')
        response = self.client.get(reverse('NewLousList:courses_by_subject', args=('CS',)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'NewLousList/courses_by_subject.html')

        Subject.objects.get(subject='ACCT').delete()
        Subject.objects.get(subject='CS').delete()


class singleCourseViewTests(TestCase):

    def test_single_course_subject(self):
        """Check that there is an individual course site for a course that exists"""
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')
        ACCT_subject = Subject.objects.create(subject='ACCT')
        response = self.client.get("/NewLousList/subject/ACCT/20762/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ACCT 2010')

        Subject.objects.get(subject='ACCT').delete()

    def test_template_used(self):
        """
        Check that the proper template is used to display info for an individual course
        """
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')
        AMST_subject = Subject.objects.create(subject='AMST')
        response = self.client.get("/NewLousList/subject/AMST/12585/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AMST 2001')
        self.assertContains(response, 'Introduction to American Studies')
        self.assertTemplateUsed(response, 'NewLousList/single_course.html')



class courseSearchPageTests(TestCase):
    def test_class_search_page(self):
        """
        Check that course search page is working
        """
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')


        CS_subject = Subject.objects.create(subject='CS')

        test_course1 = Course.objects.create(
            instructor_name="Alexis Osipovs",
            instructor_email="test@gmail.com",
            course_number="55555",
            semester_code="11111",
            course_section="101",
            subject='CS',
            catalog_number='1010',
            description='Intro to Testing',
            units='3',
            component='LEC',
            class_capacity='50',
            wait_list='2',
            wait_cap='10',
            enrollment_total='50',
            enrollment_available='0',
            topic='topic',
            meetings={}
        )

        test_course2 = Course.objects.create(
            instructor_name="Maraki Fanuil",
            instructor_email="test@gmail.com",
            course_number="12345",
            semester_code="11111",
            course_section="100",
            subject='CS',
            catalog_number='2020',
            description='Advanced Software Development',
            units='3',
            component='LEC',
            class_capacity='50',
            wait_list='2',
            wait_cap='10',
            enrollment_total='50',
            enrollment_available='0',
            topic='topic',
            meetings=[{'days': 'MoWe',
                       "start_time": "17.00.00.000000-05:00",
                       "end_time": "18.15.00.000000-05:00",
                       "facility_description": "Olsson Hall 009"}]
        )

        #self.assertEqual(response.status_code, 200)
        response = self.client.get('/NewLousList/search/CS/?title=Advanced&instructor=maraki&catalog_number=2020&units=3&component=&submit=Search')
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'Maraki Fanuil')
        self.assertContains(response, 'CS 2020')
        self.assertContains(response, 'Open seats: 0/50')
        self.assertContains(response, 'Olsson Hall 009')
        self.assertContains(response, 'Add to Shopping Cart')

        with self.assertRaises(AssertionError):
            self.assertContains(response, 'Alexis Osipovs')
            self.assertContains(response, 'CS 1010')

    def test_class_search_page_with_no_results(self):
        """
        Check that no search results are displayed if there is no match query
        """
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')


        CS_subject = Subject.objects.create(subject='CS')

        test_course1 = Course.objects.create(
            instructor_name="Alexis Osipovs",
            instructor_email="test@gmail.com",
            course_number="55555",
            semester_code="11111",
            course_section="101",
            subject='CS',
            catalog_number='1010',
            description='Intro to Testing',
            units='3',
            component='LEC',
            class_capacity='50',
            wait_list='2',
            wait_cap='10',
            enrollment_total='50',
            enrollment_available='0',
            topic='topic',
            meetings={}
        )

        response = self.client.get('/NewLousList/search/CS/?title=Advanced&instructor=maraki&catalog_number=2020&units=3&component=&submit=Search')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No search results for this query')



class ShoppingCartTests(TestCase):

    def test_shopping_cart_url(self):
        """
        Check that the Shopping Cart Url is working
        """
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')

        response = self.client.get(reverse('NewLousList:view_cart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Shopping Cart')

    def test_add_course_to_shopping_cart(self):
        """
        Check that a course can be added to the Shopping Cart
        """
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')

        AMST_subject = Subject.objects.create(subject='AMST')
        test_course = Course.objects.create(
            instructor_name="Testing Teacher",
            instructor_email="test@gmail.com",
            course_number="12345",
            semester_code="11111",
            course_section="100",
            subject='AMST',
            catalog_number='1010',
            description='Intro to Testing',
            units='3',
            component='LEC',
            class_capacity='50',
            wait_list='2',
            wait_cap='10',
            enrollment_total='50',
            enrollment_available='0',
            topic='topic',
            meetings={}
        )


        response = self.client.get('/NewLousList/cart/1/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Class added to schedule')
        self.assertContains(response, 'AMST 1010')
        self.assertContains(response, 'Testing Teacher')
        self.assertContains(response, 'Remove from Cart')
        self.assertContains(response, 'Create Schedule')

        cart = ShoppingCart.objects.get(user=user)
        class_list = cart.class_list.all()[:1].get()
        self.assertEqual(class_list, test_course)

    def test_add_same_course_to_shopping_cart(self):
        """
        Check that the same course cannot be added to the Shopping Cart
        """
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')

        AMST_subject = Subject.objects.create(subject='AMST')
        test_course = Course.objects.create(
            instructor_name="Testing Teacher",
            instructor_email="test@gmail.com",
            course_number="12345",
            semester_code="11111",
            course_section="100",
            subject='AMST',
            catalog_number='1010',
            description='Intro to Testing',
            units='3',
            component='LEC',
            class_capacity='50',
            wait_list='2',
            wait_cap='10',
            enrollment_total='50',
            enrollment_available='0',
            topic='topic',
            meetings=[{ 'days': 'MoWe',
                "start_time": "17.00.00.000000-05:00",
                "end_time": "18.15.00.000000-05:00",
                "facility_description": "Olsson Hall 009"}]
        )

        response = self.client.get('/NewLousList/cart/1/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Class added to schedule')
        self.assertContains(response, 'AMST 1010')
        self.assertContains(response, 'Testing Teacher')
        self.assertContains(response, 'Remove from Cart')
        self.assertContains(response, 'Create Schedule')

        response = self.client.get('/NewLousList/cart/1/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cannot add two sections of the same class')

        cart = ShoppingCart.objects.get(user=user)
        class_list = cart.class_list.all()[:1].get()
        self.assertEqual(class_list, test_course)

    def test_add_courses_with_conflicting_time(self):
        """
        Check that the courses with overlapping times cannot be added to the Shopping Cart
        """
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')

        AMST_subject = Subject.objects.create(subject='AMST')
        test_course1 = Course.objects.create(
            instructor_name="Testing Teacher 1",
            instructor_email="test@gmail.com",
            course_number="12345",
            semester_code="11111",
            course_section="100",
            subject='AMST',
            catalog_number='1010',
            description='Intro to Testing',
            units='3',
            component='LEC',
            class_capacity='50',
            wait_list='2',
            wait_cap='10',
            enrollment_total='50',
            enrollment_available='0',
            topic='topic',
            meetings=[{ 'days': 'MoWe',
                "start_time": "17.00.00.000000-05:00",
                "end_time": "18.15.00.000000-05:00",
                "facility_description": "Olsson Hall 009"}]
        )

        CS_subject = Subject.objects.create(subject='CS')
        test_course2 = Course.objects.create(
            instructor_name="Testing Teacher 2",
            instructor_email="test@gmail.com",
            course_number="22222",
            semester_code="11111",
            course_section="101",
            subject='CS',
            catalog_number='1111',
            description='Intro to Testing',
            units='3',
            component='LEC',
            class_capacity='50',
            wait_list='2',
            wait_cap='10',
            enrollment_total='50',
            enrollment_available='0',
            topic='topic',
            meetings=[{'days': 'MoWe',
                       "start_time": "17.00.00.000000-05:00",
                       "end_time": "18.15.00.000000-05:00",
                       "facility_description": "Olsson Hall 009"}]
        )

        response = self.client.get('/NewLousList/cart/1/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Class added to schedule')
        self.assertContains(response, 'AMST 1010')
        self.assertContains(response, 'Testing Teacher')
        self.assertContains(response, 'Remove from Cart')
        self.assertContains(response, 'Create Schedule')

        response = self.client.get('/NewLousList/cart/2/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The class you added has a time conflict')

        cart = ShoppingCart.objects.get(user=user)
        class_list = cart.class_list.all()[:1].get()
        self.assertEqual(class_list, test_course1)

    def test_add_multiple_courses_with_no_conflicting_time(self):
        """
        Check that muliple courses with no overlapping times can be added to the Shopping Cart
        """
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')

        AMST_subject = Subject.objects.create(subject='AMST')
        test_course1 = Course.objects.create(
            instructor_name="Testing Teacher 1",
            instructor_email="test@gmail.com",
            course_number="12345",
            semester_code="11111",
            course_section="100",
            subject='AMST',
            catalog_number='1010',
            description='Intro to Testing',
            units='3',
            component='LEC',
            class_capacity='50',
            wait_list='2',
            wait_cap='10',
            enrollment_total='50',
            enrollment_available='0',
            topic='topic',
            meetings=[{ 'days': 'MoWe',
                "start_time": "17.00.00.000000-05:00",
                "end_time": "18.15.00.000000-05:00",
                "facility_description": "Olsson Hall 009"}]
        )

        CS_subject = Subject.objects.create(subject='CS')
        test_course2 = Course.objects.create(
            instructor_name="Testing Teacher 2",
            instructor_email="test@gmail.com",
            course_number="22222",
            semester_code="11111",
            course_section="101",
            subject='CS',
            catalog_number='1111',
            description='Intro to Testing',
            units='3',
            component='LEC',
            class_capacity='50',
            wait_list='2',
            wait_cap='10',
            enrollment_total='50',
            enrollment_available='0',
            topic='topic',
            meetings=[{
                "days": "Th",
                "start_time": "09.30.00.000000-05:00",
                "end_time": "10.45.00.000000-05:00",
                "facility_description": "Olsson Hall 018"
            }]
        )

        response = self.client.get('/NewLousList/cart/1/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Class added to schedule')
        self.assertContains(response, 'AMST 1010')
        self.assertContains(response, 'Testing Teacher 1')
        self.assertContains(response, 'Remove from Cart')
        self.assertContains(response, 'Create Schedule')

        response = self.client.get('/NewLousList/cart/2/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Class added to schedule')
        self.assertContains(response, 'CS 1111')
        self.assertContains(response, 'Testing Teacher 2')
        self.assertContains(response, 'AMST 1010')
        self.assertContains(response, 'Testing Teacher 1')
        self.assertContains(response, 'Remove from Cart')
        self.assertContains(response, 'Create Schedule')

        cart = ShoppingCart.objects.get(user=user)
        class_list = cart.class_list.all()
        self.assertEqual(class_list.count(), 2)

    def test_delete_course_to_shopping_cart(self):
        """
        Check that a course can be added to the Shopping Cart
        """
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')

        AMST_subject = Subject.objects.create(subject='AMST')
        test_course = Course.objects.create(
            instructor_name="Testing Teacher",
            instructor_email="test@gmail.com",
            course_number="12345",
            semester_code="11111",
            course_section="100",
            subject='AMST',
            catalog_number='1010',
            description='Intro to Testing',
            units='3',
            component='LEC',
            class_capacity='50',
            wait_list='2',
            wait_cap='10',
            enrollment_total='50',
            enrollment_available='0',
            topic='topic',
            meetings={}
        )

        response = self.client.get('/NewLousList/cart/1/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Class added to schedule')
        self.assertContains(response, 'AMST 1010')
        self.assertContains(response, 'Testing Teacher')
        self.assertContains(response, 'Remove from Cart')
        self.assertContains(response, 'Create Schedule')

        cart = ShoppingCart.objects.get(user=user)
        class_list = cart.class_list.all()[:1].get()
        self.assertEqual(class_list, test_course)

        response = self.client.get('/NewLousList/cart/remove/1/')
        with self.assertRaises(AssertionError):
            self.assertContains(response, 'AMST 1010')
            self.assertContains(response, 'Testing Teacher')
            self.assertContains(response, 'Remove from Cart')
            self.assertContains(response, 'Create Schedule')

        cart = ShoppingCart.objects.get(user=user)
        class_list = cart.class_list.all()
        self.assertEqual(class_list.count(), 0)

class ScheduleTests(TestCase):

    def test_schedule_url(self):
        """
        Check that the Schedule Url is working
        """
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')

        response = self.client.get('/NewLousList/schedule/')
        self.assertEqual(response.status_code, 200)

    def test_create_schedule_url(self):
        """
        Check that the courses in the cart also appear in the schedule when the user creates a schedule
        """
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')


        AMST_subject = Subject.objects.create(subject='AMST')
        test_course2 = Course.objects.create(
            instructor_name="Testing Teacher 1",
            instructor_email="test@gmail.com",
            course_number="12345",
            semester_code="11111",
            course_section="100",
            subject='AMST',
            catalog_number='1010',
            description='Intro to Testing',
            units='3',
            component='LEC',
            class_capacity='50',
            wait_list='2',
            wait_cap='10',
            enrollment_total='50',
            enrollment_available='0',
            topic='topic',
            meetings=[{'days': 'MoWe',
                       "start_time": "17.00.00.000000-05:00",
                       "end_time": "18.15.00.000000-05:00",
                       "facility_description": "Olsson Hall 009"}]
        )

        response = self.client.get('/NewLousList/cart/1/')
        self.assertEqual(response.status_code, 200)

        CS_subject = Subject.objects.create(subject='CS')
        test_course2 = Course.objects.create(
            instructor_name="Testing Teacher 2",
            instructor_email="test@gmail.com",
            course_number="22222",
            semester_code="11111",
            course_section="101",
            subject='CS',
            catalog_number='1111',
            description='Intro to cs',
            units='3',
            component='LEC',
            class_capacity='50',
            wait_list='2',
            wait_cap='10',
            enrollment_total='50',
            enrollment_available='0',
            topic='topic',
            meetings=[{
                "days": "Th",
                "start_time": "09.30.00.000000-05:00",
                "end_time": "10.45.00.000000-05:00",
                "facility_description": "Olsson Hall 018"
            }]
        )

        response = self.client.get('/NewLousList/cart/2/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/NewLousList/schedule/')
        self.assertContains(response, 'Monday')
        self.assertContains(response, 'Tuesday')
        self.assertContains(response, 'Wednesday')
        self.assertContains(response, 'Thursday')
        self.assertContains(response, 'Friday')
        self.assertContains(response, 'AMST 1010')
        self.assertContains(response, 'Intro to Testing')

        self.assertContains(response, 'CS 1111')
        self.assertContains(response, 'Intro to cs')

class ProfileTests(TestCase):
    def test_profile_page(self):
        """
        Check that the Profile Url and page is working
        """
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')
        response = self.client.get('/NewLousList/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user.username)
        self.assertContains(response, "View Your Schedule")



class FriendTests(TestCase):
    def test_friend_search_url(self):
        """
        Check that the Friend Search Url is working
        """
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')

        response = self.client.get(reverse('NewLousList:friend_search'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add Friends')

    def test_friend_requests_url(self):
        """
        Check that the Friend requests Url is working
        """
        user = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user.username, password='pass')

        response = self.client.get(reverse('NewLousList:requests'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You have no requests.')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You have no pending requests.')

    def test_friend_search_bar_works(self):
        """
        Check that the Friend Search bar is working
        """
        user1 = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user1.username, password='pass')
        self.client.logout()

        user2 = User.objects.create_user(username='testUser2', password='pass', email='test@gmail.com')
        self.client.login(username=user2.username, password='pass')

        response = self.client.post('/NewLousList/friendsearch/', {"username": user1.username})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user1.username)
        self.assertContains(response, 'Send Friend Request')

    def test_send_and_accept_friend_request(self):
        """
        Check that sending and accepting a friend request works and is pending
        """
        #login as user1 to save user info on site then logout
        user1 = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user1.username, password='pass')
        self.client.logout()

        #login as user2
        user2 = User.objects.create_user(username='testUser2', password='pass', email='test@gmail.com')
        self.client.login(username=user2.username, password='pass')

        #send friend request to user 1 and verify that it was sent
        response = self.client.post('/NewLousList/friendsearch/', {"recipient": user1.username})
        response = self.client.post('/NewLousList/friendsearch/', {"submit": "Send Friend Request"})
        response = self.client.get('/NewLousList/friendrequests/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user1.username)
        self.assertContains(response, "Cancel Request")

        self.client.logout()

        #log back in as user1 to accept request
        self.client.login(username=user1.username, password='pass')

        response = self.client.get('/NewLousList/friendrequests/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user2.username)
        self.assertContains(response, "Accept")
        self.assertContains(response, "Decline")

        friend_request = FriendRequest.objects.filter(receiver=user1)
        response = self.client.post('/NewLousList/friendrequests/', {"friend_accept": friend_request})
        self.assertContains(response, "You have no requests.")
        friend = FriendList.objects.get(user=user1).friends.all()[:1].get()
        self.assertEqual(friend, user2 )

    def test_cancel_friend_request(self):
        """
        Check that friend requests are able to be cancelled before they are accepted by the other user
        """

        # login as user1 to save user info on site then logout
        user1 = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user1.username, password='pass')
        self.client.logout()

        # login as user2
        user2 = User.objects.create_user(username='testUser2', password='pass', email='test@gmail.com')
        self.client.login(username=user2.username, password='pass')

        # send friend request to user 1, verify that it was sent
        response = self.client.post('/NewLousList/friendsearch/', {"recipient": user1.username})
        response = self.client.post('/NewLousList/friendsearch/', {"submit": "Send Friend Request"})
        response = self.client.get('/NewLousList/friendrequests/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user1.username)
        self.assertContains(response, "Cancel Request")

        #cancel request
        pending_request = FriendRequest.objects.filter(receiver=user1).get(sender=user2).cancel()
        self.assertEqual(pending_request, None)

    def test_decline_friend_request(self):
        """
        Check that friend requests are able to be declined by receiver
        """

        # login as user1 to save user info on site then logout
        user1 = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user1.username, password='pass')
        self.client.logout()

        # login as user2
        user2 = User.objects.create_user(username='testUser2', password='pass', email='test@gmail.com')
        self.client.login(username=user2.username, password='pass')

        # send friend request to user 1, verify that it was sent
        response = self.client.post('/NewLousList/friendsearch/', {"recipient": user1.username})
        response = self.client.post('/NewLousList/friendsearch/', {"submit": "Send Friend Request"})
        response = self.client.get('/NewLousList/friendrequests/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user1.username)
        self.assertContains(response, "Cancel Request")

        self.client.logout()

        # login as user1 again to decline request
        self.client.login(username=user1.username, password='pass')

        #decline request
        pending_request = FriendRequest.objects.filter(receiver=user1).get(sender=user2).decline()
        self.assertEqual(pending_request, None)


    def test_remove_friend(self):
        """
        Check that a friend can be removed
        """
        #login as user1 to save user info on site then logout
        user1 = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user1.username, password='pass')
        self.client.logout()

        #login as user2
        user2 = User.objects.create_user(username='testUser2', password='pass', email='test@gmail.com')
        self.client.login(username=user2.username, password='pass')

        #send friend request to user 1 and verify that it was sent
        response = self.client.post('/NewLousList/friendsearch/', {"recipient": user1.username})
        response = self.client.post('/NewLousList/friendsearch/', {"submit": "Send Friend Request"})
        response = self.client.get('/NewLousList/friendrequests/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user1.username)
        self.assertContains(response, "Cancel Request")

        self.client.logout()

        #log back in as user1 to accept request
        self.client.login(username=user1.username, password='pass')

        response = self.client.get('/NewLousList/friendrequests/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user2.username)
        self.assertContains(response, "Accept")
        self.assertContains(response, "Decline")

        friend_request = FriendRequest.objects.filter(receiver=user1)
        response = self.client.post('/NewLousList/friendrequests/', {"friend_accept": friend_request})
        self.assertContains(response, "You have no requests.")

        #remove friend
        response = self.client.get('/NewLousList/friends/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user2.username)
        friend = FriendList.objects.get(user=user1).unfriend(user2)
        friend = FriendList.objects.get(user=user1).friends.all()
        self.assertEqual(friend.count(), 0)

    def test_view_friend_profile(self):
        """
        Check that a friends profile can be viewed
        """
        #login as user1 to save user info on site then logout
        user1 = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user1.username, password='pass')
        self.client.logout()

        #login as user2
        user2 = User.objects.create_user(username='testUser2', password='pass', email='test@gmail.com')
        self.client.login(username=user2.username, password='pass')

        #send friend request to user 1 and verify that it was sent
        response = self.client.post('/NewLousList/friendsearch/', {"recipient": user1.username})
        response = self.client.post('/NewLousList/friendsearch/', {"submit": "Send Friend Request"})
        response = self.client.get('/NewLousList/friendrequests/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user1.username)
        self.assertContains(response, "Cancel Request")

        self.client.logout()

        #log back in as user1 to accept request
        self.client.login(username=user1.username, password='pass')
        friend_request = FriendRequest.objects.filter(receiver=user1)
        response = self.client.post('/NewLousList/friendrequests/', {"friend_accept": friend_request})

        #view friend profile
        response = self.client.get('/NewLousList/profile/testUser2')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user1.username)
        self.assertContains(response, "View Schedule")

        #view friend schedule
        response = self.client.get('/NewLousList/schedule/testUser2/')
        self.assertEqual(response.status_code, 200)

    def test_comment_on_friend_schedule(self):
        """
        Check that a comment can be made and deleted from a friend's schedule
        """
        # login as user1 to save user info on site then logout
        user1 = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user1.username, password='pass')
        self.client.logout()

        # login as user2
        user2 = User.objects.create_user(username='testUser2', password='pass', email='test@gmail.com')
        self.client.login(username=user2.username, password='pass')

        # send friend request to user 1 and verify that it was sent
        response = self.client.post('/NewLousList/friendsearch/', {"recipient": user1.username})
        response = self.client.post('/NewLousList/friendsearch/', {"submit": "Send Friend Request"})
        response = self.client.get('/NewLousList/friendrequests/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user1.username)
        self.assertContains(response, "Cancel Request")

        self.client.logout()

        # log back in as user1 to accept request
        self.client.login(username=user1.username, password='pass')
        friend_request = FriendRequest.objects.filter(receiver=user1)
        response = self.client.post('/NewLousList/friendrequests/', {"friend_accept": friend_request})

        # view friend schedule
        response = self.client.get('/NewLousList/schedule/testUser2/')
        self.assertEqual(response.status_code, 200)

        #create comment
        comment = Comments.objects.create(sender=user1, receiver=user2, message="Nice Schedule")
        response = self.client.post('/NewLousList/schedule/testUser2/' , {"friend_accept": comment})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nice Schedule")

        #delete comment
        response = self.client.post('/NewLousList/schedule/testUser2/', {"comment_delete": comment.id})
        self.assertEqual(response.status_code, 200)
        comments_list = Comments.objects.all()
        self.assertEqual(comments_list.count(), 0)
        with self.assertRaises(AssertionError):
            self.assertContains(response, "Nice Schedule")


class CourseReviewTests(TestCase):

    def test_course_reviews(self):
        """
        Check that a review can be made on a course
        """
        user1 = User.objects.create_user(username='testUser', password='pass', email='test@gmail.com')
        self.client.login(username=user1.username, password='pass')

        FREN_subject = Subject.objects.create(subject='FREN')
        response = self.client.get('/NewLousList/review')
        self.assertEqual(response.status_code, 200)

        #post review
        review = Review.objects.create(subject='FREN', course_number='1010', review_text="Great Course!")
        form = NewReview()
        response = self.client.post('/NewLousList/review', {"submit": form})
        self.assertEqual(response.status_code, 200)

        #check if review is there
        response = self.client.get('/NewLousList/subject/FREN/11935/')
        self.assertContains(response, "Great Course!")

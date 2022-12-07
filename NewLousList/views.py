from django.http import HttpResponse
from django.shortcuts import get_object_or_404,render
import requests
from .models import Subject, Course, FriendList, FriendRequest, ShoppingCart, UserInfo, Comments, Review
from django.db.models import Q
from django.contrib.auth.models import User
from .names import get_names
from datetime import time, datetime
from django.contrib.auth.decorators import login_required
from .forms import NewReview, ContactForm
from django.views import generic
from .names import get_names, college_arts_sci, edu_hum_dev_school, engr_school, other_schools

SHOPPING_CART = set()


# Create your views here.
@login_required
def courses_by_subject(request, subject_name):

    #retrieve the subject based on its id
    #subject = get_object_or_404(Subject, pk=subject_id)


    subject = get_object_or_404(Subject, subject=subject_name)
    #subject = Subject.objects.get(subject=subject_name)

    #pull data from api for the specific subject
    response = requests.get('http://luthers-list.herokuapp.com/api/dept/' + subject.subject + '?format=json')

    #convert reponse data into json
    courses = response.json()

    course_titles = {}
    course_gpa = {}

    course_id = {}

    i = 1
    # for each subject, create a python object using model
    for course in courses:

        # add course titles to a dictionary to help organize classes that have the same title
        if course['description'] not in course_titles:
            course_titles[course['description']] = []
            course_gpa[course['description']] = 0

         # create course objects for each subject

        meetings = course['meetings']

        # Standardize course meeting times
        # First check if the list isn't empty
        if len(meetings) > 0:
            for meeting in meetings:
                # Then check if start and end times have actual values to them
                if (meeting['start_time'] != '') and meeting['end_time'] != '':
                    # Convert hours to GMT-5 standard time format
                    start_hour = meeting['start_time'][0:2]
                    start_hour = int(start_hour)
                    start_minute = meeting['start_time'][3:5]
                    start_minute = int(start_minute)
                    end_hour = meeting['end_time'][0:2]
                    end_hour = int(end_hour)
                    end_minute = meeting['end_time'][3:5]
                    end_minute = int(end_minute)

                    start_time = time(start_hour, start_minute)
                    meeting['start_time'] = start_time.strftime('%I:%M %p')
                    end_time = time(end_hour, end_minute)
                    meeting['end_time'] = end_time.strftime('%I:%M %p')
            course['meetings'] = meetings

        Course.objects.get_or_create(
            instructor_name=course['instructor']['name'],
            instructor_email=course['instructor']['email'],
            course_number=course['course_number'],
            semester_code=course['semester_code'],
            course_section=course['course_section'],
            subject=course['subject'],
            catalog_number=course['catalog_number'],
            description=course['description'],
            units=course['units'],
            component=course['component'],
            class_capacity=course['class_capacity'],
            wait_list=course['wait_list'],
            wait_cap=course['wait_cap'],
            enrollment_total=course['enrollment_total'],
            enrollment_available=course['enrollment_available'],
            topic=course['topic'],
            meetings=course['meetings']
        )

    # organize courses by their class name in a dictonary; key: course name, value: list of courses that share the course name
    for course in courses:
        c = Course.objects.get(course_number=course['course_number'])
        c_id = c.id
        course_with_id = {c_id:course}
        course_titles[course['description']].append(course_with_id)

    #display courses for that subject
    return render(request, 'NewLousList/courses_by_subject.html', {'subject': subject,  'course_titles': course_titles, 'subject_id': subject_name})

def single_course(request, subject_name, course_id):
    #subject = get_object_or_404(Subject, pk=subject_id)
    subject = get_object_or_404(Subject, subject=subject_name)
    response = requests.get('http://luthers-list.herokuapp.com/api/dept/' + subject.subject + '?format=json')
    courses = response.json()
    single_course = 0
    for course in courses:
        if course['course_number'] == course_id:
            single_course = course

    meetings = single_course['meetings']

    # Standardize course meeting times
    # First check if the list isn't empty
    if len(meetings) > 0:
        for meeting in meetings:
            # Then check if start and end times have actual values to them
            if (meeting['start_time'] != '') and meeting['end_time'] != '':
                # Convert hours to GMT-5 standard time format
                start_hour = meeting['start_time'][0:2]
                start_hour = int(start_hour)
                start_minute = meeting['start_time'][3:5]
                start_minute = int(start_minute)
                end_hour = meeting['end_time'][0:2]
                end_hour = int(end_hour)
                end_minute = meeting['end_time'][3:5]
                end_minute = int(end_minute)

                start_time = time(start_hour, start_minute)
                meeting['start_time'] = start_time.strftime('%I:%M %p')
                end_time = time(end_hour, end_minute)
                meeting['end_time'] = end_time.strftime('%I:%M %p')
        single_course['meetings'] = meetings

    html = 'https://vagrades.com/api/uva/course/'
    new_html = html + subject_name + str(single_course['catalog_number'])
    response = requests.get(new_html)
    gpa = 0
    letter = "GPA NOT FOUND"
    if response:
        class_info = response.json()
        gpa = class_info["course"]["avg"]
        if gpa:
            gpa  = round(gpa,2)
             
            if gpa > 3.7:
                letter = "A"
            elif gpa > 3.3:
                letter = "A-"
            elif gpa > 3.0:
                letter = "B+"
            elif gpa > 2.7:
                letter = "B"
            elif gpa > 2.3:
                letter = "B-"
            elif gpa > 2.0:
                letter = "C+"
            elif gpa > 1.7:
                letter = "C"
            elif gpa > 1.3:
                letter = "C-"
            elif gpa > 1.0:
                letter = "D+"
            elif gpa > 0.7:
                letter = "D"
            elif gpa > 0.3:
                letter = "D-"
            else:
                letter = "F"
    gpa = str(gpa) + " (" + letter + ")" 
    class_reviews = []
    for r in Review.objects.all():
        print(r.review_text)
        if r.subject == subject_name and r.course_number == single_course['catalog_number']:
            class_reviews.append(r)
    return render(request, 'NewLousList/single_course.html', {'course_id' : course_id, 'subject_id' : subject_name, 'single_course' : single_course, 'gpa': gpa, 'all_reviews' : class_reviews})

@login_required
def index(request):
    
    # pull data on subjects from api
    response = requests.get('http://luthers-list.herokuapp.com/api/deptlist?format=json')

    # convert reponse data into json
    subjects = response.json()

    #dictionary for actual subject names, so we dont have to use mnemonics

    engr_list = []
    college_list = []
    edu_list = []
    other_list = []

    #for each subject, create a python object using model
    for sub in subjects:
        Subject.objects.get_or_create(subject=sub['subject'],name=get_names[sub['subject']])


    #list of all the subjects
    allSubjects = Subject.objects.all()

    # Sort Subjects into schools
    for sub in college_arts_sci.keys():
        # print(sub)
        # temp_subs = Subject.objects.filter(Q(subject__icontains=sub))
        try:
            college_list.append(get_object_or_404(Subject, subject=sub))
        except:
            college_list.append(Subject.objects.filter(Q(subject__icontains=sub))[1])  
        # college_list.append(Subject.objects.filter(Q(subject__icontains=sub))[0])

    for sub in engr_school.keys():
        try:
            engr_list.append(get_object_or_404(Subject, subject=sub))
        except:
            engr_list.append(Subject.objects.filter(Q(subject__icontains=sub))[1]) 

    for sub in edu_hum_dev_school.keys():
        try:
            edu_list.append(get_object_or_404(Subject, subject=sub))
        except:
            edu_list.append(Subject.objects.filter(Q(subject__icontains=sub))[1]) 

    for sub in other_schools.keys():
        try:
            other_list.append(get_object_or_404(Subject, subject=sub))
        except:
            other_list.append(Subject.objects.filter(Q(subject__icontains=sub))[1]) 

    filteredSubjects = []

    context = {
        'subjects': allSubjects,
        'filtered': filteredSubjects,
        'engr_list': engr_list,
        'college_list': college_list,
        'edu_list': edu_list,
        'other_list': other_list
    }

    # Search feature for departments
    if 'search' in request.GET:
        q = request.GET['search']
        filteredSubjects = Subject.objects.filter(Q(name__icontains=q) | Q(subject__icontains=q))

        context = {
            'filtered': filteredSubjects
        }

        return render(request, "NewLousList/index.html", context)

    return render(request, "NewLousList/index.html", context)


@login_required
def search_courses(request, subject_name):

    subject = get_object_or_404(Subject, subject=subject_name)


    if request.method == 'GET':
        title = request.GET.get('title')
        prof = request.GET.get('instructor')
        catalog_num = request.GET.get('catalog_number')
        units = request.GET.get('units')
        component = request.GET.get('component')
        # start_time = request.GET.get('start_time')
        # end_time = request.GET.get('end_time')
        # day = request.GET.get('day')
        # location = request.GET.get('location ')


        submitbutton = request.GET.get('submit')


        results = Course.objects.filter(subject = subject.subject)
        if prof:
            results = results.filter(Q(instructor_name__icontains=prof))

        if title:
            results = results.filter(Q(description__icontains=title))

        if catalog_num:
            results = results.filter(Q(catalog_number__icontains=catalog_num))

        if units:
            results = results.filter(Q(units__icontains=units))

        if component:
            results = results.filter(Q(component__icontains=component))

        # if day:
        #     for item in meetings:
        #         results = results.filter(Q(meetings__days__icontains=day))

        # if start_time:
        #     results = results.filter(Q(meetings__start_time__icontains=start_time))


        context = {'results': results,
                    'submitbutton': submitbutton,
                   'subject': subject,
                   'subject_name': subject.subject}

        return render(request, 'NewLousList/search_courses.html', context)


    else:
        return render(request, 'NewLousList/search_courses.html', {'subject': subject})

@login_required
def friend_search(request):
    if request.method=='POST':
        recipient = request.POST.get("recipient", "")
        curr_user = User.objects.get(username=request.user)
        if recipient and not FriendRequest.objects.filter(receiver = User.objects.get(username=recipient)).filter(sender=curr_user) and (not FriendList.objects.filter(user = curr_user) or not FriendList.objects.get(user = curr_user).is_mutual_friend(User.objects.get(username=recipient))):
            new_request = FriendRequest.objects.create(receiver = User.objects.get(username=recipient), sender = User.objects.get(username=request.user), is_active = True)
        request_username = request.POST.get("username", "")
        no_search = False
        if request_username:
            results = User.objects.all().filter(Q(username__icontains=request_username)).exclude(username=request.user)
        else:
            results = User.objects.none()
            no_search = True
        return render(request, 'NewLousList/friend_search.html',
            {"request_type":request.method, "results":results, "no_search":no_search})
    else:
        return render(request, 'NewLousList/friend_search.html',
            {"request_type":request.method})

@login_required
def view_requests(request):
    curr_user = User.objects.get(username=request.user)
    if(request.method == 'POST'):
        is_accept = request.POST.get("friend_accept", "")
        is_decline = request.POST.get("friend_decline", "")
        if is_accept:
            curr_sender = User.objects.get(username = request.POST.get("friend_accept", ""))
            completed_request, created = FriendRequest.objects.filter(sender = curr_sender).filter(receiver = curr_user).get_or_create(is_active = True)
            if not FriendList.objects.filter(user = curr_user):
                FriendList.objects.create(user = curr_user)
            if not FriendList.objects.filter(user = curr_sender):
                FriendList.objects.create(user = curr_sender)
            completed_request.accept()
        elif is_decline:
            curr_sender = User.objects.get(username = request.POST.get("friend_decline", ""))
            FriendRequest.objects.filter(sender = curr_sender).get(receiver = curr_user).decline()
        else:
            curr_cancel = User.objects.get(username = request.POST.get("friend_cancel", ""))
            FriendRequest.objects.filter(sender = curr_user).get(receiver = curr_cancel).cancel()

    friend_requests = FriendRequest.objects.filter(receiver = curr_user)
    pending_requests = FriendRequest.objects.filter(sender = curr_user)
    return render(request, 'NewLousList/view_requests.html',
        {"request_type":request.method, "friend_requests":friend_requests, "pending":pending_requests})

@login_required
def view_friends(request):
    curr_user = User.objects.get(username=request.user)
    if(request.method == 'POST'):
        curr_remove = User.objects.get(username = request.POST.get("friend_remove", ""))
        FriendList.objects.get(user = curr_user).unfriend(curr_remove)
    friend_list, created = FriendList.objects.get_or_create(user = curr_user)
    friend_list = friend_list.friends.all()
    return render(request, 'NewLousList/friends.html',
        {"request_type":request.method, "friend_list":friend_list})

@login_required
def view_profile(request, owner = None):
    curr_user = User.objects.get(username=request.user)
    if owner:
        owner_user = User.objects.get(username = owner)
    else:
        owner_user = curr_user
    owner_profile, created = UserInfo.objects.get_or_create(user = owner_user)
    user_list, created = FriendList.objects.get_or_create(user = curr_user)
    owner_list, created = FriendList.objects.get_or_create(user = owner_user)
    mutuals = user_list.friends.all() & owner_list.friends.all()
    return render(request, 'NewLousList/profile.html',
        {"request_type":request.method, "user":curr_user, "profile":owner_profile, "owner":owner_user, "friend_list":mutuals})

@login_required
def edit_profile(request):
    curr_user = User.objects.get(username=request.user)
    profile = UserInfo.objects.get(user = curr_user)
    if request.method == 'POST':
        post = request.POST
        profile.first_name = post['first_name']
        profile.last_name = post['last_name']
        profile.grad_year = post['grad_year']
        profile.major = post['major']
        profile.save()
        return render(request, 'NewLousList/profile.html',
        {"request_type":request.method, "user":curr_user, "owner":curr_user, "profile":profile})
    curr_time = datetime.now().year
    return render(request, 'NewLousList/edit_profile.html',
        {"request_type":request.method, "profile":profile, "year":curr_time,})

@login_required
def cart_view(request):
    curr_user = User.objects.get(username=request.user)
    cart,created = ShoppingCart.objects.get_or_create(user = curr_user)
    class_list = cart.class_list.all()
    return render(request, 'NewLousList/shopping_cart.html', {'cart': class_list})

@login_required
def cart_add(request, course_id):
    curr_user = User.objects.get(username=request.user)
    cart,created = ShoppingCart.objects.get_or_create(user = curr_user)
    course = get_object_or_404(Course, pk=course_id)
    class_repeat, class_overlap = cart.add_class(course)
    class_list = cart.class_list.all()

    if request.method == 'GET':
        course_from_button = request.GET.get('add_cart_button')

        return render(request, 'NewLousList/shopping_cart.html', {'cart': class_list, 'course': course, 'course_from_button': course_from_button, 'class_overlap': class_overlap, 'class_repeat': class_repeat})

    return render(request, 'NewLousList/shopping_cart.html', {'cart': class_list, 'course': course, 'class_overlap': class_overlap, 'class_repeat': class_repeat})

@login_required
def cart_delete(request, course_id):
    curr_user = User.objects.get(username=request.user)
    cart,created = ShoppingCart.objects.get_or_create(user = curr_user)
    course = get_object_or_404(Course, pk=course_id)
    cart.remove_class(course)
    class_list = cart.class_list.all()

    if request.method == 'GET':
        rm_course_from_button = request.GET.get('remove_cart_button')
        return render(request, 'NewLousList/shopping_cart.html', {'cart': class_list, 'rm_course_from_button': rm_course_from_button})


    return render(request, 'NewLousList/shopping_cart.html', {'cart': class_list})

@login_required
def create_schedule(request, owner = None):
    def by_hour(ele):
        # start_hour = ele['start_time'][0:2]
        # start_hour = int(start_hour)
        # start_minute = ele['start_time'][3:5]
        # start_minute = int(start_minute)

        return ele.meetings[0]['start_time']

    curr_user = User.objects.get(username=request.user)
    if owner:
        owner_user = User.objects.get(username=owner)
    else:
        owner_user = curr_user
    not_friended = False
    user_flist, created = FriendList.objects.get_or_create(user = curr_user)
    if owner_user != curr_user and not owner_user in user_flist.friends.all():
        owner = request.user
        owner_user = curr_user
        not_friended = True
    message = request.POST.get("message","")
    if message:
        Comments.objects.create(message = message, sender = curr_user, receiver = owner_user)
    deleted_id = request.POST.get("comment_delete","")
    if deleted_id:
        Comments.objects.get(id = deleted_id).delete()
    cart,created = ShoppingCart.objects.get_or_create(user = owner_user)
    class_list = cart.class_list.all()
    # lists to order times
    ordered_list = []
    ordered_list_AM = []
    ordered_list_PM = []
    # sets to order days
    Mo_set = set()
    Tu_set = set()
    We_set = set()
    Th_set = set()
    Fr_set = set()
    other_set = set()

    #print(SHOPPING_CART)
    for course in class_list:
        if not course.valid():
            other_set.add(course)
            continue
        meetings_list = course.meetings
        # print(meetings_list)
        for meeting in meetings_list:
            # separate course into different lists based on AM or PM
            if 'AM' in meeting['start_time']:
                #print(meeting['start_time'])
                ordered_list_AM.append(course)
            else:
                ordered_list_PM.append(course)

            # key=meeting['start_time'])
            # sort lists
            ordered_list_AM = sorted(ordered_list_AM, key=by_hour)
            ordered_list_PM = sorted(ordered_list_PM, key=by_hour)
            #print(ordered_list_AM)
            #print(ordered_list_PM)
        # join lists together
        #print(ordered_list)
        for course in ordered_list_AM:
            ordered_list.append(course)
            #print(ordered_list)
        for course in ordered_list_PM:
            ordered_list.append(course)
            #print(ordered_list)
        #print(ordered_list)
    # add courses in ordered list to respective day
    for course in ordered_list:
        for meeting in course.meetings:
            if 'Mo' in meeting['days']:
                Mo_set.add(course)
            if 'Tu' in meeting['days']:
                Tu_set.add(course)
            if 'We' in meeting['days']:
                We_set.add(course)
            if 'Th' in meeting['days']:
                Th_set.add(course)
            if 'Fr' in meeting['days']:
                Fr_set.add(course)
        # remove course from cart
        # SHOPPING_CART.remove(course)

    # for course in Mo_set:
    # print(Mo_set, Tu_set, We_set, Th_set, Fr_set)

    # comments =  if owner else None


    comments = Comments.objects.filter(receiver = owner_user).order_by("-id")
    context = {
        # 'cart': SHOPPING_CART,
        'Mo_set': Mo_set,
        'Tu_set': Tu_set,
        'We_set': We_set,
        'Th_set': Th_set,
        'Fr_set': Fr_set,
        'other_set': other_set,
        'owner': owner_user,
        'comments' : comments,
        'user' : curr_user,
        'not_friended' : not_friended
    }
    return render(request, 'NewLousList/schedule.html', context)


def review(request):
    form = NewReview()
    if request.method == 'POST':
        form = NewReview(request.POST)
        if form.is_valid():
            form.save()
    context = {'form':form}
    return render(request, 'NewLousList/review.html', context)

@login_required
def review_confirm(request):
    form = NewReview()
    if request.method == 'POST':
        form = NewReview(request.POST)
        if form.is_valid():
            form.save()
    context = {'form':form}
    return render(request, 'NewLousList/review_confirm.html', context)

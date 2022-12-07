from django.db import models
from django.conf import settings
from datetime import datetime

# Create your models here.
class Subject(models.Model):
    subject = models.CharField(max_length=200)
    name = models.CharField(max_length=200, default=' ')
    def __str__(self):
        return self.name

# converts "HH:MM XM" to cooresponding time in minutes from 00:00 
def convert_time(time):
    val = 0
    val += int(time[3:5])
    val += 60 * (int(time[0:2])%12)
    if time[-2:] == 'PM':
        val += 12*60
    return val

class Course(models.Model):
    instructor_name = models.CharField(max_length=200)
    instructor_email = models.CharField(max_length=200)
    course_number = models.IntegerField(default=0)
    semester_code = models.IntegerField(default=0)
    course_section = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    catalog_number = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    units = models.CharField(max_length=200)
    component = models.CharField(max_length=200)
    class_capacity = models.IntegerField(default=0)
    wait_list = models.IntegerField(default=0)
    wait_cap = models.IntegerField(default=0)
    enrollment_total = models.IntegerField(default=0)
    enrollment_available = models.IntegerField(default=0)
    topic = models.CharField(max_length=200)
    meetings = models.JSONField(default = dict)

    def __str__(self):
        return self.description
    
    def repeat(self,other):
        if self.catalog_number==other.catalog_number:
            return True

    def overlap(self, other):
        if not self.valid() or not other.valid():
            return False
        for meeting1 in self.meetings:
            for meeting2 in other.meetings:
                days1 = meeting1['days']
                days2 = meeting2['days']
                start1 = convert_time(meeting1['start_time'])
                start2 = convert_time(meeting2['start_time'])
                end1 = convert_time(meeting1['end_time'])
                end2 = convert_time(meeting2['end_time'])
                for i in range(0,len(days1),2):
                    for j in range(0,len(days2),2):
                        if days1[i:i+2] == days2[j:j+2] and  max(start1,start2) <= min(end1,end2):
                            return True
        return False
    
    def valid(self):
        for meeting in self.meetings:
            if len(meeting['days'])<2:
                return False
            day = meeting['days'][:2]
            if day != 'Mo' and day != 'Tu' and day != 'We' and day != 'Th' and day != 'Fr':
                return False
        return True

class UserInfo(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = 'userinfo_user')
    grad_year = models.IntegerField(null = True,default = datetime.now().year)
    major = models.CharField(max_length=50, default=' ')
    first_name = models.CharField(max_length=50, default=' ')
    last_name = models.CharField(max_length=50, default=' ')
    def __str__(self):
        return self.user.username

class ShoppingCart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = 'shop_user')
    class_list = models.ManyToManyField(Course, blank=True, related_name = "class_list")
    def __str__(self):
        return f"class list for {self.user.username}"
    def add_class(self, course):
        is_overlap = False
        is_repeat = False
        for curr_class in self.class_list.all():
            if curr_class.repeat(course):
                is_repeat = True
                break
            if curr_class.overlap(course):
                is_overlap = True
                break
        if not is_repeat and not is_overlap:
            self.class_list.add(course)
        return is_repeat,is_overlap
    def remove_class(self, course):
        if course in self.class_list.all():
            self.class_list.remove(course)

class Comments(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,  related_name="com_sender")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="com_receiver")
    message = models.CharField(max_length=500)

    
# Friending models based on code from CodingWithMitch: 
# https://www.youtube.com/watch?v=hyJO4mkdwuM
class FriendList(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user')
    friends = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='friends')
    def __str__(self):
        return self.user.username
    def add_friend(self, account):
        if not account in self.friends.all():
            self.friends.add(account)
    def remove_friend(self,account):
        if account in self.friends.all():
            self.friends.remove(account)
    def unfriend(self, account):
        #account is the current friend that will be removed in this operation
        self.remove_friend(account)
        account_list = FriendList.objects.get(user=account)
        account_list.remove_friend(self.user)

    def is_mutual_friend(self,friend):
        if friend in self.friends.all():
            return True
        return False
    

class FriendRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,  related_name="sender")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="receiver")
    is_active = models.BooleanField(blank = True, null = False, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.sender.username
    def accept(self):
        receiver_list = FriendList.objects.get(user=self.receiver)
        sender_list = FriendList.objects.get(user=self.sender)
        receiver_list.add_friend(self.sender)
        sender_list.add_friend(self.receiver)
        self.delete()
    def decline(self):
        #receiver declines
        self.delete()
    def cancel(self):
        #sender cancels request
        self.delete()

class Review(models.Model):
    subject = models.CharField(max_length=10)
    course_number = models.CharField(max_length=10)
    review_text = models.CharField(max_length=1000)


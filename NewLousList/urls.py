from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'NewLousList'
urlpatterns = [
    path('', views.index, name="index"),
    path('subject/<str:subject_name>/', views.courses_by_subject, name='courses_by_subject'),
    path('subject/<str:subject_name>/<int:course_id>/', views.single_course, name='single_course'),
    path('logout', LogoutView.as_view(), name="logout"),
    path("search/<str:subject_name>/", views.search_courses, name="search"),
    path('friendsearch/', views.friend_search, name="friend_search"),
    path('friends/', views.view_friends, name="friends"),
    path('profile/', views.view_profile, name="profile"),
    path('editprofile/', views.edit_profile, name="edit_profile"),
    path('profile/<str:owner>', views.view_profile, name="profile"),
    path('friendrequests/', views.view_requests, name="requests"),
    path("search/", views.search_courses, name="search"),
    path('cart/', views.cart_view, name='view_cart'),
    path('cart/<int:course_id>/', views.cart_add, name='cart'),
    path('cart/remove/<int:course_id>/', views.cart_delete, name='remove_cart'),
    path('schedule/', views.create_schedule, name='schedule'),
    path('schedule/<str:owner>/', views.create_schedule, name='schedule'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    #path('comments/<str:owner>/', views.create_schedule, name='comments'),
    #path('comments/', views.create_schedule, name='schedule'),
    path('review', views.review, name="review"),
    path('review_confirm', views.review_confirm, name="review_confirm"),
]
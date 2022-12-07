from django.contrib import admin

from NewLousList.models import FriendRequest, FriendList, ShoppingCart, Comments, UserInfo

class FriendListAdmin(admin.ModelAdmin):
    list_filter = ['user']
    list_display = ['user']
    search_fields = ['user']

    class Meta:
        model = FriendList

admin.site.register(FriendList, FriendListAdmin)

class FriendRequestAdmin(admin.ModelAdmin):
    list_filter = ['sender', 'receiver']
    list_display = ['sender', 'receiver']
    search_fields = ['sender_username', 'sender_email', 'receiver_email', 'receiver_username']
    class Meta:
        model = FriendRequest

admin.site.register(FriendRequest, FriendRequestAdmin)


class CartAdmin(admin.ModelAdmin):
    list_filter = ['user']
    list_display = ['user']
    search_fields = ['user']
    class Meta:
        model = ShoppingCart

admin.site.register(ShoppingCart, CartAdmin)

class CommentsAdmin(admin.ModelAdmin):
    list_filter = ['sender', 'receiver', 'message']
    list_display = ['sender', 'receiver', 'message']
    class Meta:
        model = Comments

admin.site.register(Comments, CommentsAdmin)

class UserInfoAdmin(admin.ModelAdmin):
    list_filter = ['grad_year', 'major', 'first_name', 'last_name']
    list_filter = ['grad_year', 'major', 'first_name', 'last_name']
    class Meta:
        model = UserInfo

admin.site.register(UserInfo, UserInfoAdmin)
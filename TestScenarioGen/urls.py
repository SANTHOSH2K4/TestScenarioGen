from django.contrib import admin
from django.urls import path
from chat import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('get_started/', views.get_started, name='get_started'),
    path('login/', views.ulogin, name='login'),
    path('register/', views.register, name='register'),
    path('otp_verify/', views.otp_verify, name='otp_verify'),
    path('pass_reset_req/', views.pass_reset_req, name='pass_reset_req'),
    path('pass_reset_otp/', views.pass_reset_otp, name='pass_reset_otp'),
    path('pass_reset/', views.pass_reset, name='pass_reset'),
    path('home/', views.home, name='home'),
    path('add_chat/', views.add_chat, name='add_chat'),
    path('get_chats/<str:convo_id>/', views.get_chats, name='get_chats'),
    path('get_conversations/', views.get_conversations, name='get_conversations'),
    path('new_convo/', views.new_convo, name='new_convo'),
    path('logout/', views.logout_view, name='logout'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


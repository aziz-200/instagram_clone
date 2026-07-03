from django.urls import path
from .serializers import SignUpSerializer
from .views import (CreateUserView,
                    VerifyUserView,
                    GetNewVerificationCodeView,
                    ChangeInformationView,
                    ChangeUsePhotoView,
                    LoginView,
                    LoginRefreshView,
                    LogOutView)

urlpatterns = [
    path('signup/', CreateUserView.as_view(), name='signup'),
    path('login/refresh/', LoginRefreshView.as_view(), name='login'), # loginni refresh qilish
    path('logout/', LogOutView.as_view(), name='logout'),
    path('newverify/', GetNewVerificationCodeView.as_view(), name='newverify'),
    path('update-info/', ChangeInformationView.as_view(), name='update-info'),
    path('update-photo/', ChangeUsePhotoView.as_view(), name='update-photo'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify/', VerifyUserView.as_view(), name='verify'),
]
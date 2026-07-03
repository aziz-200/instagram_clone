import code

from django.contrib.auth.views import PasswordResetView
from django.urls import path
from .views import (CreateUserView,
                    VerifyUserView,
                    GetNewVerificationCodeView,
                    ChangeInformationView,
                    ChangeUsePhotoView,
                    LoginView,
                    LoginRefreshView,
                    LogOutView,
                    ForgotPasswordView,
                    ResetPasswordView)

urlpatterns = [
    path('signup/', CreateUserView.as_view(), name='signup'),
    path('login/refresh/', LoginRefreshView.as_view(), name='login'), # loginni refresh qilish
    path('logout/', LogOutView.as_view(), name='logout'),
    path('newverify/', GetNewVerificationCodeView.as_view(), name='new-verify'),
    path('update-info/', ChangeInformationView.as_view(), name='update-info'),
    path('update-photo/', ChangeUsePhotoView.as_view(), name='update-photo'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('verify/', VerifyUserView.as_view(), name='verify'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]
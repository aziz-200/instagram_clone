from django.urls import path
from .serializers import SignUpSerializer
from .views import (CreateUserView,
                    VerifyUserView,
                    GetNewVerificationCodeView,
                    ChangeInformationView,
                    ChangeUsePhotoView)

urlpatterns = [
    path('signup/', CreateUserView.as_view(), name='signup'),
    path('newverify/', GetNewVerificationCodeView.as_view(), name='newverify'),
    path('update-info/', ChangeInformationView.as_view(), name='update-info'),
    path('update-photo/', ChangeUsePhotoView.as_view(), name='update-photo'),
    path('verify/', VerifyUserView.as_view(), name='verify'),
]
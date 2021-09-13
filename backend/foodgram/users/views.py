from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Follow
from .serializers import (FollowGetSerializerTest, FollowSerializer,
                          ShowFollowersSerializer)

User = get_user_model()


class FollowView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, user_id):
        following = get_object_or_404(User, id=user_id)
        data = {'user': request.user.id, 'following': user_id}
        serializer = FollowSerializer(
            data=data,
            context={'request': request},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = FollowGetSerializerTest(following)
        return Response(
            response.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, user_id):
        user = request.user
        following = User.objects.get(id=user_id)
        follow = get_object_or_404(
            Follow,
            user=user,
            following=following
        )
        follow.delete()
        return Response(
            {'detail': 'Подписка отменена'},
            status=status.HTTP_204_NO_CONTENT
        )


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
def my_subscriptions(request):
    user = request.user
    following = user.followers.all()
    user_obj = []
    for follow_obj in following:
        user_obj.append(follow_obj.following)
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(user_obj, request)
    serializer = ShowFollowersSerializer(
        result_page, many=True, context={'current_user': request.user})
    return paginator.get_paginated_response(serializer.data)

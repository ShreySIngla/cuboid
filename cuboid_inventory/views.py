from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.contrib.auth import login, logout ,authenticate
from django.shortcuts import render, redirect
from .models import *
from .serializers import *
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.exceptions import APIException
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum
from django.utils import timezone

# Assuming A1, V1, L1, and L2 
A1 = 100
V1 = 1000
L1 = 100
L2 = 50


User = get_user_model()

@api_view(['POST'])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = User.objects.create_user(
            username=request.data.get('username'),
            email=request.data.get('email'),
            password=request.data.get('password')
        )

        user.is_staff = True
        user.save()
        return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_user(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Login the user
            login(request, user)
            return Response({'message': 'Login successful.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def logout_view(request):
    logout(request)
    return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def add_box(request):
    try:
        user = request.user
        print(user)
        length = request.data.get('length')
        breadth = request.data.get('breadth')
        height = request.data.get('height')

        if length is not None and breadth is not None and height is not None:
            # Calculate area and volume
            area = 2 * ((length * breadth) + (breadth * height) + (length * height))
            volume = length * breadth * height

            # Check average area
            all_boxes = Box.objects.all()
            total_area = all_boxes.aggregate(Sum('area'))['area__sum'] or 0
            total_volume = all_boxes.aggregate(Sum('volume'))['volume__sum'] or 0
            total_user_boxes = Box.objects.filter(created_by=user.id)
            total_user_area = total_user_boxes.aggregate(Sum('area'))['area__sum'] or 0

            if total_area / all_boxes.count() > A1:
                return Response({"detail": f"Average area exceeds {A1}"}, status=status.HTTP_400_BAD_REQUEST)

            if total_volume / all_boxes.count() > V1:
                return Response({"detail": f"Average volume exceeds {V1}"}, status=status.HTTP_400_BAD_REQUEST)

            if total_user_area + area > L2:
                return Response({"detail": f"User's total area exceeds {L2}"}, status=status.HTTP_400_BAD_REQUEST)

            # Check total boxes added in a week
            week_start_date = timezone.now() - timedelta(days=7)
            total_boxes_in_week = Box.objects.filter(created_at__gte=week_start_date).count()

            if total_boxes_in_week > L1:
                return Response({"detail": f"Total boxes added in a week exceeds {L1}"}, status=status.HTTP_400_BAD_REQUEST)

            box_data = {
                'length': length,
                'breadth': breadth,
                'height': height,
                'area': area,
                'volume': volume,
                'created_by': request.user.id,
            }

            serializer = BoxSerializer(data=box_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Missing required data in request."}, status=status.HTTP_400_BAD_REQUEST)
    except APIException as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def update_box(request):
    try:
        box = Box.objects.get(id=request.data.get('box_id'))
        length =  request.data.get('length')
        breadth = request.data.get('breadth')
        height = request.data.get('height')


        # Check if the logged-in user is staff or the creator of the box
        if request.user.is_staff :
            area = 2 * ((length * breadth) + (breadth * height) + (length * height))
            volume = length * breadth * height

            all_boxes = Box.objects.all()
            total_area = all_boxes.aggregate(Sum('area'))['area__sum'] or 0
            total_volume = all_boxes.aggregate(Sum('volume'))['volume__sum'] or 0
            total_user_boxes = Box.objects.filter(created_by=user.id)
            total_user_area = total_user_boxes.aggregate(Sum('area'))['area__sum'] or 0

            if total_area / all_boxes.count() > A1:
                return Response({"detail": f"Average area exceeds {A1}"}, status=status.HTTP_400_BAD_REQUEST)

            if total_volume / all_boxes.count() > V1:
                return Response({"detail": f"Average volume exceeds {V1}"}, status=status.HTTP_400_BAD_REQUEST)

            if total_user_area + area > L2:
                return Response({"detail": f"User's total area exceeds {L2}"}, status=status.HTTP_400_BAD_REQUEST)

            # Check total boxes added in a week
            week_start_date = timezone.now() - timedelta(days=7)
            total_boxes_in_week = Box.objects.filter(created_at__gte=week_start_date).count()

            if total_boxes_in_week > L1:
                return Response({"detail": f"Total boxes added in a week exceeds {L1}"}, status=status.HTTP_400_BAD_REQUEST)


            box.length = request.data.get('length')
            box.breadth = request.data.get('breadth')
            box.height = request.data.get('height')
            box.area = area 
            box.volume =  volume 
            box.updated_at = timezone.now()
            box.save()
            return Response({'message': 'Box updated successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'You do not have permission to update this box.'}, status=status.HTTP_403_FORBIDDEN)
    except Box.DoesNotExist:
        return Response({'message': 'Box not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_all_boxes(request):
    try:
        # Apply filters based on query parameters
        length_more_than = request.data.get('length_more_than')
        length_less_than = request.data.get('length_less_than')
        breadth_more_than = request.data.get('breadth_more_than')
        breadth_less_than = request.data.get('breadth_less_than')
        height_more_than = request.data.get('height_more_than')
        height_less_than = request.data.get('height_less_than')
        area_more_than = request.data.get('area_more_than')
        area_less_than = request.data.get('area_less_than')
        volume_more_than = request.data.get('volume_more_than')
        volume_less_than = request.data.get('volume_less_than')
        created_by_username = request.data.get('created_by_username')
        created_after = request.data.get('created_after')
        created_before = request.data.get('created_before')

        # Start with all boxes
        boxes = Box.objects.all()

        # Apply filters based on query parameters
        if length_more_than:
            boxes = boxes.filter(length__gt=length_more_than)
        if length_less_than:
            boxes = boxes.filter(length__lt=length_less_than)
        if breadth_more_than:
            boxes = boxes.filter(breadth__gt=breadth_more_than)
        if breadth_less_than:
            boxes = boxes.filter(breadth__lt=breadth_less_than)
        if height_more_than:
            boxes = boxes.filter(height__gt=height_more_than)
        if height_less_than:
            boxes = boxes.filter(height__lt=height_less_than)
        if area_more_than:
            boxes = boxes.filter(area__gt=area_more_than)
        if area_less_than:
            boxes = boxes.filter(area__lt=area_less_than)
        if volume_more_than:
            boxes = boxes.filter(volume__gt=volume_more_than)
        if volume_less_than:
            boxes = boxes.filter(volume__lt=volume_less_than)
        if created_by_username:
            boxes = boxes.filter(created_by__username=created_by_username)
        if created_after:
            boxes = boxes.filter(created_at__gte=created_after)
        if created_before:
            boxes = boxes.filter(created_at__lte=created_before)

        # Serialize the boxes based on user's permissions
        if request.user.is_staff:
            serializer = BoxSerializer(boxes, many=True)
            # serializer = BoxSerializer(boxes, many=True)
        else:
            serializer = NonStaffBoxSerializer(boxes, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_my_boxes(request):
    try:
        if request.user.is_staff:
            user = request.user

            length_more_than = request.data.get('length_more_than')
            length_less_than = request.data.get('length_less_than')
            breadth_more_than = request.data.get('breadth_more_than')
            breadth_less_than = request.data.get('breadth_less_than')
            height_more_than = request.data.get('height_more_than')
            height_less_than = request.data.get('height_less_than')
            area_more_than = request.data.get('area_more_than')
            area_less_than = request.data.get('area_less_than')
            volume_more_than = request.data.get('volume_more_than')
            volume_less_than = request.data.get('volume_less_than')

            boxes = Box.objects.filter(created_by=request.user)
            
            if length_more_than:
                boxes = boxes.filter(length__gt=length_more_than)
            if length_less_than:
                boxes = boxes.filter(length__lt=length_less_than)
            if breadth_more_than:
                boxes = boxes.filter(breadth__gt=breadth_more_than)
            if breadth_less_than:
                boxes = boxes.filter(breadth__lt=breadth_less_than)
            if height_more_than:
                boxes = boxes.filter(height__gt=height_more_than)
            if height_less_than:
                boxes = boxes.filter(height__lt=height_less_than)
            if area_more_than:
                boxes = boxes.filter(area__gt=area_more_than)
            if area_less_than:
                boxes = boxes.filter(area__lt=area_less_than)
            if volume_more_than:
                boxes = boxes.filter(volume__gt=volume_more_than)
            if volume_less_than:
                boxes = boxes.filter(volume__lt=volume_less_than)
            serializer = BoxSerializer(boxes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def delete_box(request):
    try:
        box = Box.objects.get(id=request.data.get('box_id'))
        if box.created_by == request.user:
            box.delete()
            return Response({'message': 'Box deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message': 'You do not have permission to delete this box.'}, status=status.HTTP_403_FORBIDDEN)
    except Box.DoesNotExist:
        return Response({'message': 'Box not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def add_box(request ):
#         try:
#             user = request.user
#             print(user)
#             length = request.data.get('length')
#             breadth = request.data.get('breadth')
#             height = request.data.get('height')

#             if length is not None and breadth is not None and height is not None:
#                 box_data = {
#                     'length': length,
#                     'breadth': breadth,
#                     'height': height,
#                     'created_by': request.user, 
#                      # Assuming you have a 'user' field in Box model
#                 }

#                 serializer = BoxSerializer(data=box_data)
#                 if serializer.is_valid():
#                     serializer.save()
#                     return Response(serializer.data, status=status.HTTP_201_CREATED)
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 return Response({"detail": "Missing required data in request."}, status=status.HTTP_400_BAD_REQUEST)
#         except:
#         # else:
#             return Response(
#                 {"detail": "You do not have permission to perform this action."},
#                 status=status.HTTP_403_FORBIDDEN
#             )


# @api_view(['GET'])
# def add_box(request):
#     try:
#         box = Box.objects.get()  # This query might need more specific filtering.
#         # Replace 'Box.objects.get()' with the appropriate query based on your model.

#         # Assuming you have a serializer for your Box model
#         serializer = BoxSerializer(box)  # Replace 'BoxSerializer' with your serializer.

#         return Response(serializer.data, status=status.HTTP_200_OK)
#     except Box.DoesNotExist:
#         return Response({'message': 'Box not found.'}, status=status.HTTP_404_NOT_FOUND)
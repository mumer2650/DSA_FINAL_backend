from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .serializers import LayoutRequestSerializer, LayoutResponseSerializer, HomeLayoutSerializer
from .services.homebuilder_service import HomeBuilderService
from .models import HomeLayout

class GenerateLayoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LayoutRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            home_layout = HomeBuilderService.generate_house_layout(
                user=request.user,
                request_data=serializer.validated_data
            )

            layout_with_adjacency = HomeBuilderService.get_layout_with_adjacency(
                layout_id=home_layout.id,
                user=request.user
            )

            response_serializer = LayoutResponseSerializer(layout_with_adjacency)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Failed to generate layout. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserLayoutsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            layouts = HomeBuilderService.get_user_layouts(request.user)

            processed_layouts = []
            for layout in layouts:
                layout_with_adjacency = HomeBuilderService.get_layout_with_adjacency(
                    layout_id=layout.id,
                    user=request.user
                )

                if layout_with_adjacency:
                    processed_layouts.append(layout_with_adjacency)
                else:
                    processed_layouts.append(layout)

            serializer = HomeLayoutSerializer(processed_layouts, many=True)
            return Response({'layouts': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': 'Failed to retrieve layouts.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LayoutDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, layout_id):
        try:
            layout = HomeBuilderService.get_layout_with_adjacency(
                layout_id=layout_id,
                user=request.user
            )

            if not layout:
                return Response(
                    {'error': 'Layout not found or access denied.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = LayoutResponseSerializer(layout)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': 'Failed to retrieve layout.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
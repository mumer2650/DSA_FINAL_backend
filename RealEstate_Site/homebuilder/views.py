from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .serializers import LayoutRequestSerializer, LayoutResponseSerializer, HomeLayoutSerializer
from .services.homebuilder_service import HomeBuilderService
from .models import HomeLayout


class GenerateLayoutView(APIView):
    """
    API endpoint for generating house layouts.
    POST /api/homebuilder/generate/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Generate a new house layout based on user specifications.
        """
        # Validate request data
        serializer = LayoutRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Generate layout using service
            home_layout = HomeBuilderService.generate_house_layout(
                user=request.user,
                request_data=serializer.validated_data
            )

            # Get layout with adjacency data
            layout_with_adjacency = HomeBuilderService.get_layout_with_adjacency(
                layout_id=home_layout.id,
                user=request.user
            )

            # Serialize response
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
    """
    API endpoint for retrieving user's house layouts.
    GET /api/homebuilder/my-layouts/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get all layouts for the authenticated user.
        """
        try:
            # Get user's layouts
            layouts = HomeBuilderService.get_user_layouts(request.user)

            # Process each layout to add adjacency data
            processed_layouts = []
            for layout in layouts:
                # Get layout with adjacency data
                layout_with_adjacency = HomeBuilderService.get_layout_with_adjacency(
                    layout_id=layout.id,
                    user=request.user
                )

                if layout_with_adjacency:
                    # Use the layout with adjacency data (rooms already have adjacent_rooms attached)
                    processed_layouts.append(layout_with_adjacency)
                else:
                    # Fallback to original layout if adjacency calculation fails
                    processed_layouts.append(layout)

            # Serialize layouts
            serializer = HomeLayoutSerializer(processed_layouts, many=True)
            return Response({'layouts': serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': 'Failed to retrieve layouts.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LayoutDetailView(APIView):
    """
    API endpoint for retrieving a specific layout.
    GET /api/homebuilder/layout/<layout_id>/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, layout_id):
        """
        Get a specific layout by ID for the authenticated user.
        """
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

            # Serialize layout
            serializer = LayoutResponseSerializer(layout)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': 'Failed to retrieve layout.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

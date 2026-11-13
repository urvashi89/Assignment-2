from pathlib import Path

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination

from .models import Document, QueryLog
from .serializers import DocumentSerializer, QueryLogSerializer

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}


class DocumentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    page_query_param = "page"
    max_page_size = 100


class DocumentListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # POST /documents
    def post(self, request):

        uploaded_file = request.FILES.get("file")

        data = {
            "title": request.data.get("title", ""),
            "content": request.data.get("content", ""),
        }

        if uploaded_file:
            data["file"] = uploaded_file
        # Case 1: User uploaded a file
        if uploaded_file:

            # Validate file extension
            extension = Path(uploaded_file.name).suffix.lower()

            if extension not in ALLOWED_EXTENSIONS:
                return Response(
                    {"error": "File type not allowed"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate file size
            if uploaded_file.size > MAX_FILE_SIZE:
                return Response(
                    {"error": "File size exceeds 5 MB"},
                    status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
                )

            # Use filename as title if title was not provided
            if not data.get("title"):
                data["title"] = Path(uploaded_file.name).stem

        # Case 2: User sent JSON with title and content
        else:
            if not data.get("title") or not data.get("content"):
                return Response(
                    {"error": "Please provide title and content, or upload a file"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = DocumentSerializer(data=data)

        if serializer.is_valid():
            document = serializer.save(owner=request.user)

            return Response(
                DocumentSerializer(document).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # GET /documents
    def get(self, request):

        documents = Document.objects.filter(
            owner=request.user
        ).order_by("-uploaded_at")

        paginator = DocumentPagination()

        page = paginator.paginate_queryset(
            documents,
            request
        )

        serializer = DocumentSerializer(
            page,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )

class DocumentDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        try:
            document = Document.objects.get(
                id=pk,
                owner=request.user
            )

        except Document.DoesNotExist:
            return Response(
                {"error": "Document not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = DocumentSerializer(document)

        return Response(serializer.data)

    def delete(self, request, pk):

        try:
            document = Document.objects.get(id=pk)

        except Document.DoesNotExist:
            return Response(
                {"error": "Document not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if document.owner != request.user:
            return Response(
                {"error": "You are not the owner"},
                status=status.HTTP_403_FORBIDDEN
            )

        document.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

class QueryCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = QueryLogSerializer(data=request.data)

        if serializer.is_valid():

            query = serializer.save(user=request.user)

            return Response(
                QueryLogSerializer(query).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class QueryHistoryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        queries = QueryLog.objects.filter(
            user=request.user
        ).order_by("-created_at")

        paginator = DocumentPagination()

        page = paginator.paginate_queryset(
            queries,
            request
        )

        serializer = QueryLogSerializer(
            page,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )

class QueryHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queries = QueryLog.objects.filter(
            user=request.user
        ).order_by("-created_at")

        paginator = DocumentPagination()
        page = paginator.paginate_queryset(queries, request)

        serializer = QueryLogSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)
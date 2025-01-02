from django.shortcuts import get_object_or_404
<<<<<<< HEAD
from .serializers import *

from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
=======
from .serializers import PengaduanSerializer, CommentSerializer, SinglePengaduanSerializer
from .models import Pengaduan, Like, Comment, Evidence
from jwt.lib import sso_authenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
>>>>>>> 7a995f2be53741eeef590757b3a180c9fa4da832

@sso_authenticated
@api_view(['GET'])
def get_my_pengaduan(request):
    if request.sso_user is None:
        return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
    pengaduan = Pengaduan.objects.filter(author=request.sso_user)
    serializer = PengaduanSerializer(pengaduan, many=True)
    return Response(serializer.data)

@sso_authenticated
@api_view(['GET'])
def get_my_liked_pengaduan(request):
    if request.sso_user is None:
        return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
    pengaduan = Pengaduan.objects.filter(likes__akun_sso=request.sso_user)
    serializer = PengaduanSerializer(pengaduan, many=True)
    return Response(serializer.data)

@sso_authenticated
@api_view(['GET'])
def get_my_commented_pengaduan(request):
    if request.sso_user is None:
        return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
    pengaduan = Pengaduan.objects.filter(comments__author=request.sso_user)
    serializer = PengaduanSerializer(pengaduan, many=True)
    return Response(serializer.data)

@sso_authenticated
@api_view(['GET'])
def get_my_comment(request):
    if request.sso_user is None:
        return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
    comments = Comment.objects.filter(author=request.sso_user)
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 24
    page_size_query_param = 'page_size'

class CRPengaduanAPIView(APIView):
    def get(self, request):
        status_query = request.query_params.get('status')
        issues = Pengaduan.objects.all()
        if status_query:
            issues = issues.filter(status=status_query)

        judul_query = request.query_params.get('judul')
        if judul_query:
            issues = issues.filter(judul__icontains=judul_query)

        kategori_query = request.query_params.get('kategori')
        if kategori_query:
            issues = issues.filter(kategori=kategori_query)

        date_gt_query = request.query_params.get('date_gt')
        if date_gt_query:
            issues = issues.filter(tanggal_post__gte=date_gt_query)

        date_lt_query = request.query_params.get('date_lt')
        if date_lt_query:
            issues = issues.filter(tanggal_post__lte=date_lt_query)
        
        paginator = StandardResultsSetPagination()
        paginated_issues = paginator.paginate_queryset(issues, request)
        serializer = PengaduanSerializer(paginated_issues, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @sso_authenticated
    def post(self, request):
        sso_user = request.sso_user
        if sso_user is None:
            return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
        
        request.data["author"] = sso_user.npm
        serializer = PengaduanSerializer(data=request.data)

        if serializer.is_valid():
            pengaduan = serializer.save(author=sso_user)
            evidences = request.data.get('evidence')
            if type(evidences) is not list:
                evidences = [evidences]
            for evidence in evidences:
                Evidence.objects.create(pengaduan=pengaduan, url=evidence)
            return Response(PengaduanSerializer(pengaduan).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RUDPengaduanAPIView(APIView):
    def get(self, request, id=None):
        pengaduan = get_object_or_404(Pengaduan, pk=id)
        return Response(SinglePengaduanSerializer(pengaduan).data)

    @sso_authenticated
    def put(self, request, id=None):
        sso_user = request.sso_user
        if sso_user is None:
            return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
        pengaduan = get_object_or_404(Pengaduan, pk=id)
        if pengaduan.author.npm != sso_user.npm:
            return Response({'error_message': 'Anda tidak memiliki akses untuk mengubah pengaduan ini'}, status=status.HTTP_403_FORBIDDEN)
        
        if pengaduan.status != Pengaduan.Status.UNRESOLVED:
            return Response({'error_message': 'Pengaduan ini sudah diajukan, tidak dapat diubah'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = PengaduanSerializer(pengaduan, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @sso_authenticated
    def delete(self, request, id=None):
        sso_user = request.sso_user
        if sso_user is None:
            return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
        
        pengaduan = get_object_or_404(Pengaduan, pk=id)
        if pengaduan.author.npm != sso_user.npm:
            return Response({'error_message': 'Anda tidak memiliki akses untuk menghapus pengaduan ini'}, status=status.HTTP_403_FORBIDDEN)
        
        if pengaduan.status != Pengaduan.Status.UNRESOLVED:
            return Response({'error_message': 'Pengaduan ini sudah diajukan, tidak dapat dihapus'}, status=status.HTTP_403_FORBIDDEN)
        
        pengaduan.delete()
        return Response({
            'message': 'Pengaduan berhasil dihapus'
        }, status=status.HTTP_200_OK)

class LikePengaduanAPIView(APIView):
    @sso_authenticated
    def post(self, request, id=None):
        sso_user = request.sso_user
        if sso_user is None:
            return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
        
        pengaduan = get_object_or_404(Pengaduan, pk=id)
        like = Like.objects.filter(akun_sso=sso_user, pengaduan=pengaduan)
        if like.exists():
            like.delete()
            return Response({'message': 'Unlike berhasil'}, status=status.HTTP_200_OK)
        
        Like.objects.create(akun_sso=sso_user, pengaduan=pengaduan)
        return Response({'message': 'Like berhasil'}, status=status.HTTP_201_CREATED)
    
<<<<<<< HEAD
    def like_pengaduan(self, request, pk=None):
        pengaduan = get_object_or_404(self.queryset, pk=pk)

        # Check if the like already exists to toggle like/unlike
        pengaduan_like = Like.objects.get(npm = request.sso_user.npm, pengaduan=pengaduan)
        if pengaduan_like.exists():
            pengaduan_like.delete()
            action = 'unliked'
        else:
            Like.objects.create(npm = request.sso_user.npm, pengaduan=pengaduan)
            action = 'liked'
=======
class CCommentAPIView(APIView):
    @sso_authenticated
    def post(self, request, id=None):
        sso_user = request.sso_user
        if sso_user is None:
            return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
        
        pengaduan = get_object_or_404(Pengaduan, pk=id)
 
        author = sso_user
        isi = request.data.get('isi')
        if isi:
            comment = Comment.objects.create(author=author, isi=isi, pengaduan=pengaduan)
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
>>>>>>> 7a995f2be53741eeef590757b3a180c9fa4da832
        
        return Response({'error_message': 'Isi komentar tidak boleh kosong'}, status=status.HTTP_400_BAD_REQUEST)

class UDCommentAPIView(APIView):
    @sso_authenticated
    def put(self, request, id=None):
        if request.sso_user is None:
            return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
        
        comment = get_object_or_404(Comment, pk=id)
        if comment.author != request.sso_user:
            return Response({'error_message': 'Anda tidak memiliki akses untuk mengubah komentar ini'}, status=status.HTTP_403_FORBIDDEN)
        
        isi = request.data.get('isi')
        if isi:
            comment.isi = isi
            comment.save()
            return Response(CommentSerializer(comment).data, status=status.HTTP_200_OK)
        
        return Response({'error_message': 'Isi komentar tidak boleh kosong'}, status=status.HTTP_400_BAD_REQUEST)
    
<<<<<<< HEAD
    def add_comment(self, request, pk=None) :
        pengaduan = get_object_or_404(self.queryset, pk=pk)
        isi = request.data.get('isi')

        if isi:
            comment = Comment(npm=request.sso_user.npm, isi=isi, pengaduan=pengaduan)
            comment.save()
            comment_serializer = CommentSerializer(comment)
            if request.anonymous:
                comment.anonymous = True
                comment_serializer.data.get("user") = None
            return Response(comment_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response({'error_message': 'Komentar tidak boleh kosong!'}, status=status.HTTP_400_BAD_REQUEST)
        
    def edit_comment(self, request, pk=None) :
        comment = get_object_or_404(Comment, pk=pk)

        # Anonymous comments cannot be edited
        if comment.npm == request.sso_user.npm and not comment.anonymous:
            isi = request.data.get('isi')
            if isi:
                comment.isi = isi
                comment.save()
                comment_serializer = CommentSerializer(comment)
                return Response(comment_serializer.data, status=status.HTTP_200_OK)
            
            return Response({'error_message': 'Komentar tidak boleh kosong'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    def delete_comment(self, request, pk=None) :
        comment = get_object_or_404(Comment, pk=pk)

        # All comments can be deleted (by the author)
        if comment.npm == request.sso_user.npm:
            comment.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
=======
    @sso_authenticated
    def delete(self, request, id=None):
        if request.sso_user is None:
            return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
        
        comment = get_object_or_404(Comment, pk=id)
        if comment.author != request.sso_user:
            return Response({'error_message': 'Anda tidak memiliki akses untuk menghapus komentar ini'}, status=status.HTTP_403_FORBIDDEN)
        
        comment.delete()
        return Response({
            'message': 'Komentar berhasil dihapus'
        },status=status.HTTP_200_OK)
>>>>>>> 7a995f2be53741eeef590757b3a180c9fa4da832

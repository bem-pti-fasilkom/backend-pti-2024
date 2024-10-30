from django.shortcuts import get_object_or_404
from .serializers import PengaduanSerializer, CommentSerializer, SinglePengaduanSerializer
from .models import Pengaduan, Like, Comment, Evidence
from jwt.lib import sso_authenticated
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
"""
- logic filter belom bisa
- request body update pengaduan belum ada
- isLiked oleh user terkait belum ada (tampilan user yg udah like pengaduan dan belum soalnya beda) ~~~
- kategori gaada di api docs (ini di card pengaduan gaada kategori jg? cc @wi )
"""

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

class PengaduanViewSet(viewsets.ModelViewSet):
    serializer_class = PengaduanSerializer
    queryset = Pengaduan.objects.all()

    @sso_authenticated
    def update(self, request, pk=None) :
        # User biasa : Judul, isi, lokasi (status = unresolved)
        # Admin : Status
        pengaduan = get_object_or_404(self.queryset, pk=pk)
        serializer = PengaduanSerializer(pengaduan)
        if pengaduan.Status.UNRESOLVED :
            judul = request.data['judul']
            isi = request.data['isi']
            lokasi = request.data['lokasi']

            pengaduan.judul = judul
            pengaduan.isi = isi
            pengaduan.lokasi = lokasi
            pengaduan.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({'error_message' : 'Anda bukan Admin atau status bukan UNRESOLVED'}, status=status.HTTP_403_FORBIDDEN)

    @sso_authenticated
    def destroy(self, request, pk=None) :
        # Requirement Delete Pengaduan: 
        # 1. Pengaduan harus milik user
        # 2. Status unresolved
        pengaduan = get_object_or_404(self.queryset, pk=pk)
        if pengaduan.user.id != request.data["user"]:
            raise PermissionDenied("User tidak memiliki akses untuk menghapus pengaduan")
        elif not pengaduan.Status.UNRESOLVED: 
            raise PermissionDenied("Status bukan unresolved")
        else:
            pengaduan.delete()
            return Response(status=status.HTTP_200_OK)
    
    @sso_authenticated
    @action(detail=False, methods=['get'], url_path='filter', url_name='filter')
    # Hanya dapat melihat pengaduan yang dimiliki jika sudah login
    def filter(self, request):
        user = request.user.id
        pengaduan = Pengaduan.objects.filter(user=user)
        serializer = PengaduanSerializer(pengaduan, many=True)
        return Response(serializer.data)
    
    @sso_authenticated
    def like(self, request, pk=None):
        pengaduan = get_object_or_404(self.queryset, pk=pk)
        
        # Check if the like already exists to toggle like/unlike
        # Temporary implementation for 'akun_sso' field until authentication is done
        pengaduan_like = Like.objects.get(akun_sso='akun_sso', pengaduan=pengaduan)
        if pengaduan_like.exists():
            pengaduan_like.delete()
            action = 'unliked'
        else:
            Like.objects.create(akun_sso='akun_sso', pengaduan=pengaduan)
            action = 'liked'
        
        likes_count = Like.objects.filter(pengaduan=pengaduan).count()
        
        return Response({'amount_of_likes': likes_count, 'action': action}, status=status.HTTP_200_OK)
    
    @sso_authenticated
    def add_comment(self, request, pk=None) :
        pengaduan = get_object_or_404(self.queryset, pk=pk)

        if not pengaduan.is_anonymous:
            author = request.user.username
            isi = request.data.get('isi')

            if isi:
                comment = Comment(author=author, isi=isi, pengaduan=pengaduan)
                comment.save()
                comment_serializer = CommentSerializer(comment)
                return Response(comment_serializer.data, status=status.HTTP_201_CREATED)
            
            return Response({'error_message': 'Komentar tidak boleh kosong!'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'error_message' : 'User tidak terdaftar'}, status=status.HTTP_403_FORBIDDEN)
    
    @sso_authenticated
    def edit_comment(self, request, pk=None) :
        comment = get_object_or_404(Comment, pk=pk)

        if not comment.pengaduan.is_anonymous and comment.author == request.user.username:
            isi = request.data.get('isi')
            if isi:
                comment.isi = isi
                comment.save()
                comment_serializer = CommentSerializer(comment)
                return Response(comment_serializer.data, status=status.HTTP_200_OK)
            
            return Response({'error_message': 'Komentar tidak boleh kosong'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'error_message' : 'User tidak terdaftar'}, status=status.HTTP_403_FORBIDDEN)
    
    @sso_authenticated
    def delete_comment(self, request, pk=None) :
        comment = get_object_or_404(Comment, pk=pk)

        if not comment.pengaduan.is_anonymous and comment.author == request.user.username:
            comment.delete()
            return Response(status=status.HTTP_200_OK)
        
        return Response({'error_message' : 'User tidak terdaftar'}, status=status.HTTP_403_FORBIDDEN)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'

class CRPengaduanAPIView(APIView):
    def get(self, request):
        issues = Pengaduan.objects.all()
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
        return Response(status=status.HTTP_200_OK)

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
    
class CCommentAPIView(APIView):
    @sso_authenticated
    def post(self, request, id=None):
        sso_user = request.sso_user
        if sso_user is None:
            return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
        
        pengaduan = get_object_or_404(Pengaduan, pk=id)
        if pengaduan.is_anonymous:
            return Response({'error_message': 'Pengaduan ini tidak dapat diberikan komentar'}, status=status.HTTP_403_FORBIDDEN)
        
        author = sso_user
        isi = request.data.get('isi')
        if isi:
            comment = Comment.objects.create(author=author, isi=isi, pengaduan=pengaduan)
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        
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
    
    @sso_authenticated
    def delete(self, request, id=None):
        if request.sso_user is None:
            return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
        
        comment = get_object_or_404(Comment, pk=id)
        if comment.author != request.sso_user:
            return Response({'error_message': 'Anda tidak memiliki akses untuk menghapus komentar ini'}, status=status.HTTP_403_FORBIDDEN)
        
        comment.delete()
        return Response(status=status.HTTP_200_OK)
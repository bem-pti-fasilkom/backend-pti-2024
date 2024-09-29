from django.shortcuts import get_object_or_404
from .serializers import PengaduanSerializer, CommentSerializer
from .models import Pengaduan, Like, Comment
from jwt.lib import sso_authenticated
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

class PengaduanViewSet(viewsets.ModelViewSet):
    serializer_class = PengaduanSerializer
    queryset = Pengaduan.objects.all()

    @sso_authenticated
    def retrieve(self, request, pk=None):
        pengaduan = get_object_or_404(self.queryset, pk=pk)
        serializer = PengaduanSerializer(pengaduan)
        print("Anonymous")

        if pengaduan.is_anonymous:
            print("Anonymous")
            serializer.data['author'] = 'Anonymous'

        return Response(serializer.data)
    
    def update(self, request, pk=None) :
        # User biasa : Judul, isi, lokasi (status = unresolved)
        # Admin : Status
        pengaduan = get_object_or_404(self.queryset, pk=pk)
        serializer = PengaduanSerializer(pengaduan)
        if pengaduan.user.is_superuser :
            status = request.data['status']
            pengaduan.status = status
            pengaduan.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif pengaduan.Status.UNRESOLVED :
            judul = request.data['judul']
            isi = request.data['isi']
            lokasi = request.data['lokasi']

            pengaduan.judul = judul
            pengaduan.isi = isi
            pengaduan.lokasi = lokasi
            pengaduan.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({'error_message' : 'Anda bukan Admin atau status bukan UNRESOLVED'}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None) :
        # Requirement Delete Pengaduan: 
        # 1. Pengaduan harus milik user
        # 2. Status unresolved
        pengaduan = get_object_or_404(self.queryset, pk=pk)
        if pengaduan.is_anonymous:
            raise PermissionDenied("Anonymous tidak dapat menghapus pengaduan")
        elif pengaduan.user.id != request.data["user"]:
            raise PermissionDenied("User tidak memiliki akses untuk menghapus pengaduan")
        elif not pengaduan.Status.UNRESOLVED: 
            raise PermissionDenied("Status bukan unresolved")
        else:
            pengaduan.delete()
            return Response(status=status.HTTP_200_OK)
        
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

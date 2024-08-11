from django.shortcuts import get_object_or_404
from .serializers import *

from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action

from jwt.lib import sso_authenticated

class PengaduanViewSet(viewsets.ModelViewSet):
    serializer_class = PengaduanSerializer
    queryset = Pengaduan.objects.all()

    def retrieve(self, request, pk=None):
        pengaduan = get_object_or_404(self.queryset, pk=pk)
        serializer = PengaduanSerializer(pengaduan)

        # If the user desires to stay anonymous, do not return user object
        if pengaduan.anonymous :
            pengaduan.user = None
            pengaduan.save()

        ## Used to format datetime into a more readable format
        # unformatted_date = pengaduan.__getattribute__("tanggal_post")
        # pengaduan.__setattr__("tanggal_post", unformatted_date.strftime("%Y-%m-%d, %X"))

        return Response(serializer.data)
    
    @sso_authenticated
    def update(self, request, pk=None) :
        # User biasa : Judul, isi, lokasi (status = unresolved)
        # Admin : Status
        pengaduan = get_object_or_404(self.queryset, pk=pk)
        serializer = PengaduanSerializer(pengaduan)
        user = request.sso_user

        if user.get("is_superuser") :
            status = request.data['status']
            status_obj = get_object_or_404(StatusPengaduan, pk=status)
            pengaduan.status = status_obj
            pengaduan.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif pengaduan.status.status == StatusPengaduan.Status.UNRESOLVED :
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
        try:
            pengaduan = get_object_or_404(self.queryset, pk=pk)
            user = request.sso_user

            if pengaduan.anonymous:
                raise Exception("Anonymous tidak dapat menghapus pengaduan")
            elif pengaduan.user.id != user.get("id"):
                raise Exception("User tidak memiliki akses untuk menghapus pengaduan")
            elif not pengaduan.status.status != StatusPengaduan.Status.UNRESOLVED: 
                raise Exception("Status bukan unresolved")
            else:
                pengaduan.delete()
                return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error_message' : f'{e}'}, status=status.HTTP_403_FORBIDDEN)
        
    @action(detail=False, methods=['get'], url_path='filter', url_name='filter')
    # Hanya dapat melihat pengaduan yang dimiliki jika sudah login
    def filter(self, request):
        user = request.user.id
        pengaduan = Pengaduan.objects.filter(user=user)
        serializer = PengaduanSerializer(pengaduan, many=True)
        return Response(serializer.data)
    
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
    
    def add_comment(self, request, pk=None) :
        pengaduan = get_object_or_404(self.queryset, pk=pk)

        if not pengaduan.anonymous:
            author = request.user.username
            isi = request.data.get('isi')

            if isi:
                comment = Comment(author=author, isi=isi, pengaduan=pengaduan)
                comment.save()
                comment_serializer = CommentSerializer(comment)
                return Response(comment_serializer.data, status=status.HTTP_201_CREATED)
            
            return Response({'error_message': 'Komentar tidak boleh kosong!'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'error_message' : 'User tidak terdaftar'}, status=status.HTTP_403_FORBIDDEN)
    
    def edit_comment(self, request, pk=None) :
        comment = get_object_or_404(Comment, pk=pk)

        if not comment.pengaduan.anonymous and comment.author == request.user.username:
            isi = request.data.get('isi')
            if isi:
                comment.isi = isi
                comment.save()
                comment_serializer = CommentSerializer(comment)
                return Response(comment_serializer.data, status=status.HTTP_200_OK)
            
            return Response({'error_message': 'Komentar tidak boleh kosong'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'error_message' : 'User tidak terdaftar'}, status=status.HTTP_403_FORBIDDEN)
    
    def delete_comment(self, request, pk=None) :
        comment = get_object_or_404(Comment, pk=pk)

        if not comment.pengaduan.anonymous and comment.author == request.user.username:
            comment.delete()
            return Response(status=status.HTTP_200_OK)
        
        return Response({'error_message' : 'User tidak terdaftar'}, status=status.HTTP_403_FORBIDDEN)

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
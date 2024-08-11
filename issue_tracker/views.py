from django.shortcuts import get_object_or_404
from .serializers import *

from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action


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
        try:
            pengaduan = get_object_or_404(self.queryset, pk=pk)
            if pengaduan.anonymous:
                raise Exception("Anonymous tidak dapat menghapus pengaduan")
            elif pengaduan.user.id != request.data["user"]:
                raise Exception("User tidak memiliki akses untuk menghapus pengaduan")
            elif not pengaduan.Status.UNRESOLVED: 
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
        
        likes_count = Like.objects.filter(pengaduan=pengaduan).count()
        
        return Response({'amount_of_likes': likes_count, 'action': action}, status=status.HTTP_200_OK)
    
    def add_comment(self, request, pk=None) :
        pengaduan = get_object_or_404(self.queryset, pk=pk)
        user = request.sso_user

        # TODO: change this
        if not pengaduan.anonymous:
            isi = request.data.get('isi')
            user = request.sso_user
            if isi:
                comment = Comment(npm=user.npm, isi=isi, pengaduan=pengaduan)
                comment.save()
                comment_serializer = CommentSerializer(comment)
                return Response(comment_serializer.data, status=status.HTTP_201_CREATED)
            
            return Response({'error_message': 'Komentar tidak boleh kosong!'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'error_message' : 'User tidak terdaftar'}, status=status.HTTP_403_FORBIDDEN)
    
    def edit_comment(self, request, pk=None) :
        comment = get_object_or_404(Comment, pk=pk)

        if comment.npm == request.sso_user.npm:
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

        if comment.npm == request.sso_user.npm:
            comment.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
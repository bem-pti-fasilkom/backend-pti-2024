from rest_framework import status
from rest_framework.test import APITestCase, APIClient, APIRequestFactory


from .models import SSOAccount, Pengaduan, Like, Comment
from .views import (
    get_my_pengaduan, 
    get_my_liked_pengaduan, 
    get_my_commented_pengaduan,
    get_my_comment,
    CRPengaduanAPIView,
    RUDPengaduanAPIView,
    LikePengaduanAPIView,
    CCommentAPIView,
    UDCommentAPIView
)

# Create your tests here.
class IssueTrackerTest(APITestCase):

    # Setup test data
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()

        # Test SSOAccount instance
        self.user = SSOAccount.objects.create(
            npm='2106123456',
            full_name='Test User',
            username='testuser',
            faculty='Fakultas Ilmu Komputer',
            short_faculty='Fasilkom',
            major='Ilmu Komputer',
            program='S1 Reguler'
        )
        
        self.user2 = SSOAccount.objects.create(
            npm='2106654321',
            full_name='Test User 2',
            username='testuser2',
            faculty='Fakultas Ilmu Komputer',
            short_faculty='Fasilkom',
            major='Sistem Informasi',
            program='S1 Reguler'
        )

        # Test data pengaduan
        self.pengaduan1 = Pengaduan.objects.create(
            judul='Pengaduan Test 1',
            isi='Isi pengaduan 1',
            lokasi='Lokasi 1',
            author=self.user,
            status=Pengaduan.Status.UNRESOLVED,
            kategori=Pengaduan.Kaget.AKADEMIS
        )
        
        self.pengaduan2 = Pengaduan.objects.create(
            judul='Pengaduan Test 2',
            isi='Isi pengaduan 2',
            lokasi='Lokasi 2',
            author=self.user,
            status=Pengaduan.Status.RESOLVED,
            kategori=Pengaduan.Kaget.FASILITAS
        )
        
        self.pengaduan3 = Pengaduan.objects.create(
            judul='Pengaduan Test 3',
            isi='Isi pengaduan 3',
            lokasi='Lokasi 3',
            author=self.user2,
            status=Pengaduan.Status.UNRESOLVED,
            kategori=Pengaduan.Kaget.LAINNYA
        )

        # Test data comment
        self.comment1 = Comment.objects.create(
            author=self.user,
            isi='Test comment 1',
            pengaduan=self.pengaduan1
        )

        self.comment2 = Comment.objects.create(
            author=self.user,
            isi='Test comment 2',
            pengaduan=self.pengaduan2
        )
        
        # Setup like
        Like.objects.create(akun_sso=self.user, pengaduan=self.pengaduan1)

    # Authenticator helper
    def _create_authenticated_request(self, method, path, user, data=None):
        if method == 'GET':
            request = self.factory.get(path)
        elif method == 'POST':
            request = self.factory.post(path, data, format='json')
        elif method == 'PUT':
            request = self.factory.put(path, data, format='json')
        elif method == 'DELETE':
            request = self.factory.delete(path)
        
        request.sso_user = {
            'npm': user.npm,
            'user': user.username,
            'nama': user.full_name,
            'jurusan': {
                'faculty': user.faculty,
                'shortFaculty': user.short_faculty,
                'major': user.major,
                'program': user.program
            }
        }
        
        return request
    
    def test_get_my_pengaduan(self):
        request = self._create_authenticated_request('GET', '/pengaduan/histories/', self.user)
        
        response = get_my_pengaduan(request)
        
        self.assertEqual(response.status_code, 200)

        pengaduan_ids = [p['id'] for p in response.data]
        self.assertIn(self.pengaduan1.id, pengaduan_ids)
        self.assertIn(self.pengaduan2.id, pengaduan_ids)

    def test_get_my_liked_pengaduan(self):
        request = self._create_authenticated_request('GET', '/pengaduan/liked/', self.user)
        
        response = get_my_liked_pengaduan(request)
        
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data[0]['id'], self.pengaduan1.id)

    def test_get_my_commented_pengaduan(self):
        request = self._create_authenticated_request('GET', '/pengaduan/commented/', self.user)
        
        response = get_my_commented_pengaduan(request)
        
        self.assertEqual(response.status_code, 200)

        pengaduan_ids = [p['id'] for p in response.data]

        self.assertIn(self.pengaduan1.id, pengaduan_ids)
        self.assertIn(self.pengaduan2.id, pengaduan_ids)

    def test_get_my_comment(self):
        request = self._create_authenticated_request('GET', '/comments/my/', self.user)
        
        response = get_my_comment(request)
        
        self.assertEqual(response.status_code, 200)

        comment_ids = [c['id'] for c in response.data]

        self.assertIn(self.comment1.id, comment_ids)
        self.assertIn(self.comment2.id, comment_ids)



    # CRPengaduanAPIView
    
    def test_get_all_pengaduan(self):
        view = CRPengaduanAPIView.as_view()
        request = self.factory.get('/pengaduan/')
        
        response = view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)

    def test_get_pengaduan_unresolved(self):
        view = CRPengaduanAPIView.as_view()
        request = self.factory.get('/pengaduan/?status=UNRESOLVED')
        
        response = view(request)
        
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data['results'][0]['status'], 'UNRESOLVED')

    def test_get_pengaduan_akademis(self):
        view = CRPengaduanAPIView.as_view()
        request = self.factory.get('/pengaduan/?kategori=AKADEMIS')
        
        response = view(request)
        
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data['results'][0]['kategori'], 'AKADEMIS')

    def test_get_pengaduan_search_judul(self):
        view = CRPengaduanAPIView.as_view()
        request = self.factory.get('/pengaduan/?judul=Test')
        
        response = view(request)
        
        self.assertEqual(response.status_code, 200)

    def test_post_pengadua(self):
        view = CRPengaduanAPIView.as_view()
        
        data = {
            'judul': 'Test Post Pengaduan',
            'isi': 'Isi Test Post Pengaduan',
            'lokasi': 'Lokasi Test Post Pengaduam',
            'kategori': 'AKADEMIS',
            'evidence': []
        }
        
        request = self._create_authenticated_request('POST', '/pengaduan/', self.user, data)
        
        response = view(request)
        
        self.assertEqual(response.status_code, 201)
        
        self.assertTrue(Pengaduan.objects.filter(judul='Test Post Pengaduan').exists())

    # RUDPengaduanAPIView
    
    def test_get_pengaduan_by_id(self):
        view = RUDPengaduanAPIView.as_view()
        request = self.factory.get(f'/pengaduan/{self.pengaduan1.id}/')
        
        response = view(request, id=self.pengaduan1.id)
        
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data['id'], self.pengaduan1.id)
        self.assertEqual(response.data['judul'], 'Pengaduan Test 1')

    def test_put_pengaduan(self):
        view = RUDPengaduanAPIView.as_view()
        
        data = {
            'judul': 'Updated Title',
            'isi': 'Updated content'
        }
        
        request = self._create_authenticated_request('PUT', f'/pengaduan/{self.pengaduan1.id}/', self.user, data)
        
        response = view(request, id=self.pengaduan1.id)
        
        self.assertEqual(response.status_code, 200)
        
        updated = Pengaduan.objects.get(id=self.pengaduan1.id)

        self.assertEqual(updated.judul, 'Updated Title')

    def test_delete_pengaduan(self):
        view = RUDPengaduanAPIView.as_view()
        
        request = self._create_authenticated_request('DELETE', f'/pengaduan/{self.pengaduan1.id}/', self.user)
        
        response = view(request, id=self.pengaduan1.id)
        
        self.assertEqual(response.status_code, 200)
        
        self.assertFalse(Pengaduan.objects.filter(id=self.pengaduan1.id).exists())

    # LikePengaduanAPIView
    
    def test_like_pengaduan(self):
        view = LikePengaduanAPIView.as_view()
        
        # User2 like pengaduan1
        request = self._create_authenticated_request('POST', f'/pengaduan/{self.pengaduan1.id}/like/', self.user2)
        
        response = view(request, id=self.pengaduan1.id)
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('Like berhasil', response.data['message'])
        
        self.assertTrue(Like.objects.filter(akun_sso=self.user2, pengaduan=self.pengaduan1).exists())

    def test_unlike_pengaduan(self):
        view = LikePengaduanAPIView.as_view()
        
        # User unlike pengaduan1
        request = self._create_authenticated_request('POST', f'/pengaduan/{self.pengaduan1.id}/like/', self.user)
        
        response = view(request, id=self.pengaduan1.id)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Unlike berhasil', response.data['message'])

        self.assertFalse(Like.objects.filter(akun_sso=self.user, pengaduan=self.pengaduan1).exists())

    # CCommentAPIView
    
    def test_create_comment(self):
        view = CCommentAPIView.as_view()
        
        data = {'isi': 'New comment'}
        
        request = self._create_authenticated_request('POST', f'/pengaduan/{self.pengaduan3.id}/comment/', self.user, data)
        
        response = view(request, id=self.pengaduan3.id)
        
        self.assertEqual(response.status_code, 201)

        self.assertTrue(Comment.objects.filter(pengaduan=self.pengaduan3, isi='New comment').exists())

    # UDCommentAPIView
    
    def test_update_comment(self):
        view = UDCommentAPIView.as_view()
        
        data = {'isi': 'Updated comment'}
        
        request = self._create_authenticated_request('PUT', f'/comments/{self.comment1.id}/', self.user, data)
        
        response = view(request, id=self.comment1.id)
        
        self.assertEqual(response.status_code, 200)

        updated = Comment.objects.get(id=self.comment1.id)
        self.assertEqual(updated.isi, 'Updated comment')

    def test_delete_comment(self):
        view = UDCommentAPIView.as_view()
        
        request = self._create_authenticated_request('DELETE', f'/comments/{self.comment1.id}/', self.user)
        
        response = view(request, id=self.comment1.id)
        
        self.assertEqual(response.status_code, 200)

        self.assertFalse(Comment.objects.filter(id=self.comment1.id).exists())
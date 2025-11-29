# best_staff/test_tests.py
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from unittest.mock import patch
from datetime import datetime, timedelta

from .models import BEMMember, Event, Birdept, Vote
from jwt.models import SSOAccount
from .views import (
    authenticate_staff,
    get_event,
    get_all_statistics,
    get_birdept_member,
    get_all_winners,
    get_birdept,
    VoteAPIView,
)

# Bypass sso authentication
@patch("best_staff.views.sso_authenticated", lambda f: f)
class BestStaffTest(APITestCase):

    # Setup test data
    def setUp(self):
        self.factory = APIRequestFactory()

        # Test data SSOAccount
        self.sso_user1 = SSOAccount.objects.create(
            npm='2106001001',
            full_name='Staff One',
            username='staff1',
            faculty='Fakultas Ilmu Komputer',
            short_faculty='Fasilkom',
            major='Ilmu Komputer',
            program='S1 Reguler'
        )

        self.sso_user2 = SSOAccount.objects.create(
            npm='2106001002',
            full_name='BPH Member',
            username='bph1',
            faculty='Fakultas Ilmu Komputer',
            short_faculty='Fasilkom',
            major='Ilmu Komputer',
            program='S1 Reguler'
        )

        self.sso_user3 = SSOAccount.objects.create(
            npm='2106001003',
            full_name='Coordinator',
            username='koor1',
            faculty='Fakultas Ilmu Komputer',
            short_faculty='Fasilkom',
            major='Ilmu Komputer',
            program='S1 Reguler'
        )

        # Test data Birdepts
        self.birdept1 = Birdept.objects.create(
            nama='Internal',
            displayed_name='Internal',
            deskripsi='Departemen Internal',
            galeri=[]
        )

        self.birdept2 = Birdept.objects.create(
            nama='External',
            displayed_name='External',
            deskripsi='Departemen External',
            galeri=[]
        )

        # Test data BEMMembers
        self.bem_user1 = BEMMember.objects.create(
            sso_account=self.sso_user1,
            role=BEMMember.Role.STAFF,
            img_url='https://testdata.com/img1.jpg'
        )
        self.bem_user1.birdept.add(self.birdept1)

        self.bem_user2 = BEMMember.objects.create(
            sso_account=self.sso_user2,
            role=BEMMember.Role.BPH,
            img_url='https://testdata.com/img2.jpg'
        )
        self.bem_user2.birdept.add(self.birdept1)

        self.bem_user3 = BEMMember.objects.create(
            sso_account=self.sso_user3,
            role=BEMMember.Role.KOOR,
            img_url='https://testdata.com/img3.jpg'
        )
        self.bem_user3.birdept.add(self.birdept1, self.birdept2)

        # Test data Events
        now = datetime.now()
        self.event1 = Event.objects.create(
            start=now,
            end=now + timedelta(hours=2)
        )

        # Test data Votes
        Vote.objects.create(
            voter=self.bem_user1,
            voted=self.bem_user2,
            birdept=self.birdept1,
            created_at=now
        )

        Vote.objects.create(
            voter=self.bem_user2,
            voted=self.bem_user1,
            birdept=self.birdept1,
            created_at=now
        )

    # Authenticator helper (simulate autentikasi SSO)
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

    def test_authenticate_staff(self):
        request = self._create_authenticated_request('GET', '/auth/staff/', self.sso_user1)
        response = authenticate_staff(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['sso_account']['npm'], str(self.sso_user1.npm))
        self.assertEqual(response.data['role'], 'STAFF')

    def test_get_event(self):
        request = self.factory.get('/events/')
        response = get_event(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_birdept_member(self):
        request = self._create_authenticated_request('GET', '/birdept/member/', self.sso_user1)
        response = get_birdept_member(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        
        member_npms = [member['sso_account']['npm'] for member in response.data]
        
        # bem_user2 dan bem_user3 ada di birdept1
        self.assertIn(self.sso_user2.npm, member_npms)  
        self.assertIn(self.sso_user3.npm, member_npms)
    
        # Exclude current user
        self.assertNotIn(self.sso_user1.npm, member_npms)
        
        # Verify count (2 members: bem_user2 and bem_user3)
        self.assertEqual(len(response.data), 2)
    
    def test_get_all_statistics_success(self):
        request = self.factory.get('/statistics/')
        response = get_all_statistics(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('birdepts', response.data)
        self.assertEqual(len(response.data['birdepts']), 2)
        self.assertEqual(response.data['birdepts'][0]['name'], 'Internal')

    def test_get_all_statistics_detailed(self):
        request = self.factory.get('/statistics/')
        response = get_all_statistics(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('birdepts', response.data)
        self.assertEqual(len(response.data['birdepts']), 2)
        
        # Cek birdept pertama
        self.assertEqual(response.data['birdepts'][0]['name'], 'Internal')
        self.assertIn('votes', response.data['birdepts'][0])
        self.assertIsInstance(response.data['birdepts'][0]['votes'], list)
        
        # Cek struktur vote
        if len(response.data['birdepts'][0]['votes']) > 0:
            vote_detail = response.data['birdepts'][0]['votes'][0]
            self.assertIn('name', vote_detail)
            self.assertIn('count', vote_detail)
            self.assertIsInstance(vote_detail['count'], int)
        
        # Verify semua BEM Member di birdept1 termasuk di response
        birdept1_members = BEMMember.objects.filter(birdept=self.birdept1)
        vote_names = [v['name'] for v in response.data['birdepts'][0]['votes']]

        for member in birdept1_members:
            self.assertIn(member.sso_account.full_name, vote_names)
    
    def test_get_birdept_success(self):
        request = self._create_authenticated_request('GET', '/birdept/', self.sso_user1)
        response = get_birdept(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 2)
        
        # Cek struktur birdept
        birdept_names = [b['nama'] for b in response.data]
        self.assertIn('Internal', birdept_names)
        self.assertIn('External', birdept_names)
        
        first_birdept = response.data[0]
        self.assertIn('nama', first_birdept)
        self.assertIn('displayed_name', first_birdept)
        self.assertIn('deskripsi', first_birdept)
        self.assertIn('galeri', first_birdept)
        self.assertEqual(first_birdept['nama'], 'Internal')
        self.assertEqual(first_birdept['deskripsi'], 'Departemen Internal')
    
    def test_get_all_winners_current_month(self):
        request = self._create_authenticated_request('GET', '/winners/', self.sso_user1)
        response = get_all_winners(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('filters', response.data)
        self.assertIn('count', response.data)
        
        # Cek filter kosong maka akan menggunakan datetime.now()
        self.assertIsNone(response.data['filters']['year'])
        self.assertIsNone(response.data['filters']['month'])
        
        # Cek struktur data
        if response.data['count'] > 0:
            result = response.data['results'][0]
            self.assertIn('birdept_id', result)
            self.assertIn('birdept', result)
            self.assertIn('total_votes', result)
            self.assertIn('top_votes', result)
            self.assertIn('tie', result)
            self.assertIn('winners', result)
            self.assertIsInstance(result['winners'], list)
            
            if len(result['winners']) > 0:
                winner = result['winners'][0]
                self.assertIn('npm', winner)
                self.assertIn('name', winner)
                self.assertIn('votes', winner)

    def test_get_all_winners_with_year_month(self):
        now = datetime.now()
        request = self._create_authenticated_request(
            'GET', 
            f'/winners/?year={now.year}&month={now.month}', 
            self.sso_user1
        )
        response = get_all_winners(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['filters']['year'], str(now.year))
        self.assertEqual(response.data['filters']['month'], str(now.month))
        self.assertIn('results', response.data)
        
        # Cek setup vote
        self.assertGreater(response.data['count'], 0)
        
        # Cek jika birdept 1 menang (dummy vote di birdept 1)
        birdept_names = [r['birdept'] for r in response.data['results']]
        self.assertIn('Internal', birdept_names)

    # VoteAPIView
    def test_vote_api_view_get_success(self):
        view = VoteAPIView.as_view()
        request = self._create_authenticated_request(
            'GET', 
            f'/vote/statistics/{self.birdept1.nama}/', 
            self.sso_user1
        )
        
        response = view(request, birdept=self.birdept1.nama)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_votes', response.data)
        self.assertEqual(response.data['total_votes'], 2)
        self.assertIn('votes', response.data)
        self.assertIn('details', response.data['votes'])
        
        # Cek struktur vote
        vote_details = response.data['votes']['details']
        self.assertIsInstance(vote_details, list)
        self.assertGreater(len(vote_details), 0)
        
        # Cek vote detail bisa / tidak
        for detail in vote_details:
            self.assertIn('name', detail)
            self.assertIn('count', detail)
            self.assertIsInstance(detail['count'], int)
        
        # Verify semua member birdept 1 included
        birdept1_members = BEMMember.objects.filter(birdept=self.birdept1)
        vote_names = [v['name'] for v in vote_details]

        for member in birdept1_members:
            self.assertIn(member.sso_account.full_name, vote_names)
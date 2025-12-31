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
    get_statistic,
    create_vote,
)

@patch("best_staff.views.sso_authenticated", lambda f: f)
class BestStaffTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        self.sso_user1 = SSOAccount.objects.create(
            npm='0000000001',
            full_name='Staff One',
            username='staff1',
            faculty='Fakultas Ilmu Komputer',
            short_faculty='Fasilkom',
            major='Ilmu Komputer',
            program='S1 Reguler'
        )

        self.sso_user2 = SSOAccount.objects.create(
            npm='0000000002',
            full_name='Staff Two',
            username='staff2',
            faculty='Fakultas Ilmu Komputer',
            short_faculty='Fasilkom',
            major='Ilmu Komputer',
            program='S1 Reguler'
        )

        self.sso_user3 = SSOAccount.objects.create(
            npm='0000000003',
            full_name='Staff Three',
            username='staff3',
            faculty='Fakultas Ilmu Komputer',
            short_faculty='Fasilkom',
            major='Ilmu Komputer',
            program='S1 Reguler',
        )

        self.sso_user4 = SSOAccount.objects.create(
            npm='0000000004',
            full_name='BPH Member',
            username='bph1',
            faculty='Fakultas Ilmu Komputer',
            short_faculty='Fasilkom',
            major='Ilmu Komputer',
            program='S1 Reguler'
        )

        self.sso_user5 = SSOAccount.objects.create(
            npm='0000000005',
            full_name='Coordinator',
            username='koor1',
            faculty='Fakultas Ilmu Komputer',
            short_faculty='Fasilkom',
            major='Ilmu Komputer',
            program='S1 Reguler'
        )

        self.birdept1 = Birdept.objects.create(
            nama='Birdept Satu',
            displayed_name='Birdept1',
            deskripsi='Departemen Satu BEM',
            galeri=[]
        )

        self.birdept2 = Birdept.objects.create(
            nama='Birdept Dua',
            displayed_name='Birdept2',
            deskripsi='Departemen Dua BEM',
            galeri=[]
        )

        self.bem_user1 = BEMMember.objects.create(
            sso_account=self.sso_user1,
            role=BEMMember.Role.STAFF,
            img_url='https://testdata.com/img1.jpg'
        )
        self.bem_user1.birdept.add(self.birdept1)

        self.bem_user2 = BEMMember.objects.create(
            sso_account=self.sso_user2,
            role=BEMMember.Role.STAFF,
            img_url='https://testdata.com/img2.jpg'
        )
        self.bem_user2.birdept.add(self.birdept1)

        self.bem_user3 = BEMMember.objects.create(
            sso_account=self.sso_user3,
            role=BEMMember.Role.STAFF,
            img_url='https://testdata.com/img3.jpg'
        )
        self.bem_user3.birdept.add(self.birdept2)

        self.bem_user4 = BEMMember.objects.create(
            sso_account=self.sso_user4,
            role=BEMMember.Role.BPH,
            img_url='https://testdata.com/img4.jpg'
        )
        self.bem_user4.birdept.add(self.birdept1)

        self.bem_user5 = BEMMember.objects.create(
            sso_account=self.sso_user5,
            role=BEMMember.Role.KOOR,
            img_url='https://testdata.com/img5.jpg'
        )
        self.bem_user5.birdept.add(self.birdept1)

        now = datetime.now()
        self.event1 = Event.objects.create(
            start=now,
            end=now + timedelta(hours=2)
        )

        Vote.objects.create(
            voter=self.bem_user1,
            voted=self.bem_user2,
            birdept=self.birdept1,
            created_at=now
        )

        Vote.objects.create(
            voter=self.bem_user4,
            voted=self.bem_user2,
            birdept=self.birdept1,
            created_at=now
        )

    def _create_authenticated_request(self, method, path, user, data=None):
        if method == 'GET':
            request = self.factory.get(path)
        elif method == 'POST':
            request = self.factory.post(path, data or {})
        elif method == 'PUT':
            request = self.factory.put(path, data or {})
        elif method == 'DELETE':
            request = self.factory.delete(path)
        
        request.sso_user = user
        
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

    def test_get_birdept_member_as_staff(self):
        request = self._create_authenticated_request('GET', '/birdept/member/', self.sso_user1)
        response = get_birdept_member(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['sso_account']['npm'], self.sso_user2.npm) # Exclude self
    
    def test_get_birdept_member_as_koor(self):
        request = self._create_authenticated_request('GET', '/birdept/member/', self.sso_user5)
        response = get_birdept_member(request)
        
        self.assertEqual(response.status_code, 200)
        member_npms = [member['sso_account']['npm'] for member in response.data]
        
        # KOOR should see all STAFF
        self.assertIn(self.sso_user1.npm, member_npms)
        self.assertIn(self.sso_user2.npm, member_npms)
        self.assertIn(self.sso_user3.npm, member_npms)
        
        # KOOR should not see themselves or BPH
        self.assertNotIn(self.sso_user4.npm, member_npms)
        self.assertNotIn(self.sso_user5.npm, member_npms)
    
    def test_get_all_statistics_success(self):
        request = self._create_authenticated_request('GET', '/statistics/', self.sso_user1)
        response = get_all_statistics(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('birdepts', response.data)
        self.assertEqual(len(response.data['birdepts']), 2)

    def test_get_all_statistics_detailed(self):
        request = self._create_authenticated_request('GET', '/statistics/', self.sso_user1)
        response = get_all_statistics(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('birdepts', response.data)
        
        internal_data = next(
            (b for b in response.data['birdepts'] if b['name'] == 'Birdept Satu'),
            None
        )
        self.assertIsNotNone(internal_data)
        self.assertIn('votes', internal_data)
        self.assertIsInstance(internal_data['votes'], list)
        
        if len(internal_data['votes']) > 0:
            vote = internal_data['votes'][0]
            self.assertIn('name', vote)
            self.assertIn('count', vote)
            self.assertIn('img_url', vote)

    def test_get_all_statistics_with_date_filter(self):
        past_date = datetime.now() - timedelta(days=60)
        Vote.objects.create(
            voter=self.bem_user5,
            voted=self.bem_user3,
            birdept=self.birdept2,
            created_at=past_date
        )
        
        # Test current month (should exclude past vote)
        now = datetime.now()
        request = self._create_authenticated_request(
            'GET',
            f'/statistics/?year={now.year}&month={now.month}',
            self.sso_user1
        )
        response = get_all_statistics(request)
        
        self.assertEqual(response.status_code, 200)
        
        external_now = next(
            (b for b in response.data['birdepts'] if b['name'] == 'Birdept Dua'),
            None
        )
        self.assertIsNotNone(external_now)
        staff5_now = next(
            (v for v in external_now['votes'] if v['name'] == 'Staff Three'),
            None
        )
        self.assertIsNotNone(staff5_now)
        self.assertEqual(staff5_now['count'], 0)
        
        request_past = self._create_authenticated_request(
            'GET',
            f'/statistics/?year={past_date.year}&month={past_date.month}',
            self.sso_user1
        )
        response_past = get_all_statistics(request_past)
        
        self.assertEqual(response_past.status_code, 200)
        
        external_data = next(
            (b for b in response_past.data['birdepts'] if b['name'] == 'Birdept Dua'),
            None
        )
        self.assertIsNotNone(external_data)
        
        staff3_votes = next(
            (v for v in external_data['votes'] if v['name'] == 'Staff Three'),
            None
        )
        self.assertIsNotNone(staff3_votes)
        self.assertEqual(staff3_votes['count'], 1)

    def test_get_birdept_success(self):
        request = self.factory.get('/birdept/')
        response = get_birdept(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
    
    def test_get_all_winners_current_month(self):
        request = self.factory.get('/winners/')
        response = get_all_winners(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('filters', response.data)

    def test_get_all_winners_with_year_month(self):
        now = datetime.now()
        request = self.factory.get(f'/winners/?year={now.year}&month={now.month}')
        response = get_all_winners(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['filters']['year'], str(now.year))
        self.assertEqual(response.data['filters']['month'], str(now.month))

    def test_get_statistic_success(self):
        request = self._create_authenticated_request(
            'GET', 
            f'/vote/statistics/{self.birdept1.nama}/', 
            self.sso_user1
        )
        
        response = get_statistic(request, birdept=self.birdept1.nama)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_votes', response.data)
        self.assertEqual(response.data['total_votes'], 2)
        self.assertIn('votes', response.data)
        self.assertIn('details', response.data['votes'])
        
        vote_details = response.data['votes']['details']
        self.assertIsInstance(vote_details, list)
        
        for detail in vote_details:
            self.assertIn('name', detail)
            self.assertIn('count', detail)
            self.assertIn('img_url', detail)

    def test_get_statistic_with_date_filter(self):
        past_date = datetime.now() - timedelta(days=60)
        Vote.objects.create(
            voter=self.bem_user5,
            voted=self.bem_user3,
            birdept=self.birdept2,
            created_at=past_date
        )
        
        request_past = self._create_authenticated_request(
            'GET',
            f'/vote/statistics/{self.birdept2.nama}/?year={past_date.year}&month={past_date.month}',
            self.sso_user3
        )
        
        response_past = get_statistic(request_past, birdept=self.birdept2.nama)
        
        self.assertEqual(response_past.status_code, 200)
        self.assertEqual(response_past.data['total_votes'], 1)

        now = datetime.now()
        request_now = self._create_authenticated_request(
            'GET',
            f'/vote/statistics/{self.birdept2.nama}/?year={now.year}&month={now.month}',
            self.sso_user3
        )
        
        response_now = get_statistic(request_now, birdept=self.birdept2.nama)
        
        self.assertEqual(response_now.status_code, 200)
        self.assertEqual(response_now.data['total_votes'], 0)  # Should be 0 in current month

    def test_create_vote_success(self):
        request = self._create_authenticated_request(
            'POST',
            f'/vote/{self.bem_user3.pk}/',
            self.sso_user5
        )
        
        response = create_vote(request, voted_npm=self.bem_user3.pk)
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Vote berhasil')
        self.assertIn('payload', response.data)
        self.assertEqual(response.data['payload']['voted_name'], 'Staff Three')
        self.assertEqual(response.data['payload']['birdept'], 'Birdept Dua')
        
    def test_create_vote_already_voted_staff(self):
        request = self._create_authenticated_request(
            'POST',
            f'/vote/{self.bem_user2.pk}/',
            self.sso_user1
        )
        
        response = create_vote(request, voted_npm=self.bem_user2.pk)

        self.assertEqual(response.status_code, 403)
        self.assertIn('error_message', response.data)
        self.assertEqual(response.data['error_message'], 'Anda hanya bisa vote satu kali')

    def test_create_vote_cannot_vote_non_staff(self):
        request = self._create_authenticated_request(
            'POST',
            f'/vote/{self.bem_user4.pk}/',
            self.sso_user3
        )
        
        response = create_vote(request, voted_npm=self.bem_user4.pk)
        
        self.assertEqual(response.status_code, 403)
        self.assertIn('error_message', response.data)
        self.assertEqual(response.data['error_message'], 'Vote hanya bisa diberikan kepada STAFF')

    def test_create_vote_koor_already_voted_in_birdept(self):
        Vote.objects.create(
            voter=self.bem_user5,
            voted=self.bem_user1,
            birdept=self.birdept1,
            created_at=datetime.now()
        )

        request = self._create_authenticated_request(
            'POST',
            f'/vote/{self.bem_user2.pk}/',
            self.sso_user5
        )
        
        response = create_vote(request, voted_npm=self.bem_user2.pk)
        
        self.assertEqual(response.status_code, 403)
        self.assertIn('error_message', response.data)
        self.assertEqual(response.data['error_message'], 'Anda sudah vote staff di birdept ini')

    def test_create_vote_cannot_vote_self(self):
        request = self._create_authenticated_request(
            'POST',
            f'/vote/{self.bem_user1.pk}/',
            self.sso_user1
        )
        
        response = create_vote(request, voted_npm=self.bem_user1.pk)
        
        self.assertEqual(response.status_code, 403)
        self.assertIn('error_message', response.data)
        self.assertEqual(response.data['error_message'], 'Tidak bisa vote diri sendiri')

    def test_create_vote_staff_different_birdept(self):
        Vote.objects.filter(voter=self.bem_user1).delete()
        
        request = self._create_authenticated_request(
            'POST',
            f'/vote/{self.bem_user3.pk}/',
            self.sso_user1
        )
        
        response = create_vote(request, voted_npm=self.bem_user3.pk)
        
        self.assertEqual(response.status_code, 403)
        self.assertIn('error_message', response.data)
        self.assertEqual(response.data['error_message'], 'Anda hanya bisa vote staff di birdept sendiri')
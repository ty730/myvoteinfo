import pytest
import re
from pprint import pprint
from myvoteinfo import MyVoteInfo

def test_init():
  assert MyVoteInfo()

def test_lookup_fail():
  kmvi = MyVoteInfo()
  r = kmvi.lookup(first_name='No', last_name='Such', dob='2000-01-01')
  assert r == False

def test_lookup_kansas():
  kmvi = MyVoteInfo()
  r = kmvi.lookup(first_name='Kris', last_name='Kobach', dob='1966-03-26')
  pprint(r.parsed())
  assert r.parsed()[0]['tree']['Political Party'] == 'Republican'

def test_lookup_arkansas():
  kmvi = MyVoteInfo(state='ar', url='https://www.voterview.ar-nova.org/voterview')
  r = kmvi.lookup(first_name='William', last_name='Hutchinson', dob='1950-12-03')
  pprint(r.parsed())
  assert r.parsed()[0]['tree']['Political Party'] == 'Republican'

def test_lookup_rockthevote():
  kmvi = MyVoteInfo(state='rockthevote', url='https://am-i-registered-to-vote.org/verify-registration.php')
  r = kmvi.lookup(first_name='Tyler', last_name='Wong', dob='2000-07-30', gender='male', street='14025 Bagley Ave N', city='Seattle', state='WA', zipcode='98133', email='tylerwong2000@gmail.com', groupids='89407')
  pprint(r)

def test_lookup_rockthevote_fail():
  kmvi = MyVoteInfo(state='rockthevote', url='https://am-i-registered-to-vote.org/verify-registration.php')
  r = kmvi.lookup(first_name='No', last_name='Such', dob='1910-01-01', gender='male', street='notaplace', city='nocity', state='AL', zipcode='12345', email='no@such.email', groupids='89407')
  pprint(r)

def test_lookup_rockthevote_status_dropped():
  kmvi = MyVoteInfo(state='rockthevote', url='https://am-i-registered-to-vote.org/verify-registration.php')
  r = kmvi.lookup(first_name='Dean', last_name='No Runner', dob='1974-09-21', gender='male', street='801 E 2ND AVE', city='Spokane', state='WA', zipcode='99202', email='dean@false.com', groupids='89407')
  pprint(r)
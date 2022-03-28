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
  kmvi = MyVoteInfo(url='https://www.voterview.ar-nova.org/voterview')
  r = kmvi.lookup(first_name='William', last_name='Hutchinson', dob='1950-12-03')
  pprint(r.parsed())
  assert r.parsed()[0]['tree']['Political Party'] == 'Republican'

def test_lookup_rockthevote():
  kmvi = MyVoteInfo(url='https://register.rockthevote.com/lookup')
  r = kmvi.lookup(first_name='tyler', last_name='wong', dob='2000-07-30', gender='decline', street='14025 bagley ave n', city='seattle', state='wa', zipcode='98133', email='person@email.com')
  pprint(r)

def test_lookup_rockthevote_1():
  kmvi = MyVoteInfo(url='https://register.rockthevote.com/lookup')
  r = kmvi.lookup(
    first_name='Tyler',
    last_name='Wong',
    dob='2000-07-30',
    gender='decline', 
    street='14025 Bagley Ave N', 
    city='Seattle', 
    state='WA', 
    zipcode='98133', 
    email='person@email.com')
  pprint(r)

def test_lookup_rockthevote_fail():
  kmvi = MyVoteInfo(url='https://register.rockthevote.com/lookup')
  r = kmvi.lookup(first_name='No', last_name='Such', dob='1910-01-01', gender='male', street='notaplace', city='nocity', state='AL', zipcode='12345', email='no@such.email', groupids='89407')
  pprint(r)

def test_lookup_rockthevote_status_dropped():
  kmvi = MyVoteInfo(url='https://register.rockthevote.com/lookup')
  r = kmvi.lookup(first_name='Dean', last_name='No Runner', dob='1974-09-21', gender='male', street='801 E 2ND AVE', city='Spokane', state='WA', zipcode='99202', email='dean@false.com', groupids='89407')
  pprint(r)

def test_lookup_rtv_cali():
  kmvi = MyVoteInfo(url='https://register.rockthevote.com/lookup')
  r = kmvi.lookup(first_name='Gavin', last_name='Newsom', dob='1967-10-10', gender='male', street='1526 H St', city='Sacramento', state='CA', zipcode='94203', email='gavin@false.com', groupids='89407')
  pprint(r)

import re
import dateutil.parser
import http.client as http_client
import logging
import requests
from bs4 import BeautifulSoup
from pprint import pprint

class MyVoteInfoResult(object):
  def __init__(self, registrants):
    self.registrants = registrants

  def parsed(self):
    return self.registrants

class MyVoteInfoResultParser(object):
  def __init__(self, registrant_name, registrant_address, registrant_details, ballot_soup=None, district_soup=None, elections_soup=None, polling_soup=None):
    self.registrant_name = registrant_name
    self.registrant_address = registrant_address
    self.registrant_details = registrant_details
    self.ballot_soup = ballot_soup
    self.district_soup = district_soup
    self.elections_soup = elections_soup
    self.polling_soup = polling_soup

  def norm_whitespace(self, val):
    return ' '.join(val.replace("\xa0", ' ').replace("\n", ' ').replace("\r", ' ').replace("\t", ' ').split())

  def parsed(self):
    registrant = {}
    from myvoteinfo.counties import MyVoteInfoCounties
    counties = MyVoteInfoCounties().names()

    for el in self.registrant_details:
      registrant['spans'] = el.find_all('span')
      registrant['labels'] = el.find_all('label', class_='control-label-important')
      registrant['data'] = el.find_all('label', class_='control-data-important')
      tree = {}
      for idx, label in enumerate(registrant['labels']):
        key = self.norm_whitespace(label.get_text())
        strings = registrant['data'][idx].stripped_strings
        val = '<br/>'.join(strings)
        tree[key] = self.norm_whitespace(val)
      registrant['tree'] = tree

    address_with_county = self.norm_whitespace(self.registrant_address[0].get_text())
    address_matches = re.fullmatch(r"(.+) - ([a-z\ ]+)", address_with_county, re.I)
    address = address_matches.group(1)
    county = address_matches.group(2)
    if county not in counties:
      county = ''

    registrant['tree']['Address'] = address
    registrant['tree']['County'] = county
    registrant['tree']['Name'] = self.norm_whitespace(self.registrant_name.get_text())

    if self.ballot_soup: # only if we have one Result
      registrant['sample_ballots'] = []
      for ballot_link in self.ballot_soup:
        href = ballot_link.get('href')
        text = ballot_link.get_text()
        registrant['sample_ballots'].append({'href':MyVoteInfo.base_url + '/' + href, 'text':text})

    if self.district_soup:
      registrant['districts'] = []
      for row in self.district_soup:
        if not row.find_all('td'):
          continue
        name = row.find_all('td')[0]
        dtype = row.find_all('td')[1]
        if not dtype:
          continue
        registrant['districts'].append({'name':name.get_text(), 'type':dtype.get_text()})

    if self.elections_soup:
      registrant['elections'] = []
      for row in self.elections_soup:
        if not row.find_all('td'):
          continue
        cells = row.find_all('td')
        date = self.norm_whitespace(cells[0].get_text())
        name = self.norm_whitespace(cells[1].get_text())
        etype = self.norm_whitespace(cells[2].get_text())
        how = self.norm_whitespace(cells[3].get_text())
        registrant['elections'].append({'date':date, 'name':name, 'type':etype, 'how':how})

    if self.polling_soup:
      registrant['polling'] = []
      for location in self.polling_soup.select('a'):
        registrant['polling'].append({'name': self.norm_whitespace(location.get_text()), 'href': location.get('href')})

    # for backwards compat, return list of one
    return [registrant]

# end result class

class MyVoteInfo(object):
  version = '0.1'
  base_url = u'https://myvoteinfo.voteks.org/voterview'
  registrant_search_url = base_url
  states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

  def __init__(self, **kwargs):
    self.state = 'ks'
    if 'state' in kwargs:
      self.state = kwargs['state']
    self.url = self.__class__.registrant_search_url
    if 'url' in kwargs:
      self.url = kwargs['url']
    #print(self.url)
    self.debug = 'debug' in kwargs
    self.form_url = self.url + '/registrant/search'

  def get_auth_token(self, body):
    startstr = b'<input name="__RequestVerificationToken" type="hidden" value="'
    tag_len = len(startstr)
    start_ind = body.find(startstr) + tag_len
    end_ind = body.find(b'"', start_ind)
    auth_token = body[start_ind:end_ind]
    return auth_token

  def get_search_key(self, body):
    key_string = b'var key = "'
    start_key_idx = body.find(key_string) + len(key_string)
    end_key_idx = body.find(b'"', start_key_idx)
    search_key = body[start_key_idx:end_key_idx]
    return search_key.decode(encoding='UTF-8')

  def lookup(self, *, first_name, last_name, dob, **kwargs):
    if self.debug:
      http_client.HTTPConnection.debuglevel = 1
      logging.basicConfig()
      logging.getLogger().setLevel(logging.DEBUG)
      requests_log = logging.getLogger("requests.packages.urllib3")
      requests_log.setLevel(logging.DEBUG)
      requests_log.propagate = True
    else:
      http_client.HTTPConnection.debuglevel = False

    date = dateutil.parser.parse(dob)

    session = requests.Session()
    form_page = session.get(self.url) # cache session cookie
    form_page_text = form_page.content
    #pprint(form_page_text)

    if self.state.upper() != 'KS' and self.state.upper() != 'AR':
      gender = ''
      street = ''
      city = ''
      state = ''
      zipcode = ''
      email = ''
      if 'gender' in kwargs and 'street' in kwargs and 'city' in kwargs and 'state' in kwargs and 'zipcode' in kwargs and 'email' in kwargs:
        gender = kwargs['gender']
        street = kwargs['street']
        city = kwargs['city']
        state = kwargs['state']
        zipcode = kwargs['zipcode']
        email = kwargs['email']
      else:
        return False
      payload = {
        'cons_first_name': first_name,
        'cons_last_name': last_name,
        'cons_gender': gender,
        'cons_street1': street,
        'cons_city': city,
        'cons_state': state,
        'cons_zip_code': zipcode,
        'cons_email': email,
        'birth_date_month': date.strftime('%m'),
        'birth_date_day': date.strftime('%d'),
        'birth_date_year': date.strftime('%Y')
      }
      resp = session.post(self.form_url, data=payload)
      #print(resp.content)
      registrant_page = BeautifulSoup(resp.content, 'html.parser')
      #print(registrant_page.prettify())
      if registrant_page.select('#catalist-mperson'):
        registrant = {}
        registrant['name'] = registrant_page.select('#catalist-name')[0].get_text()[:-1]
        registrant['address'] = registrant_page.select('#catalist-regaddrline')[0].get_text()
        cityStateZip = registrant_page.select('#catalist-regaddrcity')[0].get_text()
        registrant['city'] = cityStateZip[:-10]
        registrant['state'] = cityStateZip[-8:-6]
        registrant['zipcode'] = cityStateZip[-5:]
        registrant['dob'] = registrant_page.select('#catalist-dob')[0].get_text()[-10:]
        registrant['status'] = registrant_page.select('#catalist-voterstatus')[0].get_text()[14:]
        return [registrant]
      else:
        return False
        
    else:
      auth_token = self.get_auth_token(form_page_text)
      #pprint(auth_token)

      payload = {
        'FirstName': first_name,
        'LastName': last_name,
        'DateOfBirth': date.strftime('%m/%d/%Y'),
        'DateOfBirth_[month]': date.strftime('%m'),
        'DateOfBirth_[day]': date.strftime('%d'),
        'DateOfBirth_[year]': date.strftime('%Y'),
        '__RequestVerificationToken':auth_token
      }
      resp = session.post(self.form_url, data=payload)

      #print(resp.content)

      # if there are multiple/ambiguous results, look for signal string
      if b'ShowBusyIndicator' in resp.content:
        search_ids = re.findall(r'data-search-result-id="(\w+)"', str(resp.content))
        registrants = []
        for search_id in search_ids:
          registrant = self.fetch_registrant(session, search_id).parsed()
          registrants.append(registrant[0])

        return MyVoteInfoResult(registrants)

      else:
        # search result key
        search_key = self.get_search_key(resp.content)
        if search_key == "\r":
          return False

        #print("search_key:%s" %(search_key))

        return MyVoteInfoResult([self.fetch_registrant(session, search_key)])

  def fetch_registrant(self, session, search_key):
    # registrant
    registrant_url = self.url + u'/registrant/searchresult/' + search_key
    registrant_page = BeautifulSoup(session.get(registrant_url).content, 'html.parser')
    #print(registrant_page.prettify())

    if registrant_page.select('h1'):
      elections = registrant_page.find('select', {'id':'cmboElection'})
      election_key = elections.find_all('option', selected=True)[0].get('value')
      #print('election_key={}'.format(election_key))
      precinct_key = registrant_page.find('input', {'id':'PrecinctPartKey'}).get('value')
      #print('precinct_key={}'.format(precinct_key))
      polling_url = self.url + u'/votingplace/getpollingplaceorvotecenters?KeyPrecinctPart={}&ElectionKey={}'.format(precinct_key, election_key)
      polling_response = session.post(polling_url).content

      return MyVoteInfoResultParser(
        registrant_page.find('h1'),
        registrant_page.select('#labelResidenceAddress'),
        registrant_page.select('#reg-detail-header-row'),
        registrant_page.select('.divSampleBallots'),
        registrant_page.select('container body-content accordion'),
        registrant_page.select('#tableVotingHistory tbody tr'),
        BeautifulSoup(polling_response, 'html.parser')
      )
    # TODO check browser response code for 5xx
    else:
      return False


import requests
from Reader import reader
import random
import json
import uuid

class Arist:
    def __init__(self, name='', id='', albums=[],tracks=[]):
        self.name = name
        self.id = id
        self.albums = albums
        self.tracks = tracks


class Albums:
    def __init__(self, name='', id='', artist='',tracks=[]):
        self.name = name
        self.id = id
        self.artist = artist
        self.tracks = tracks


def rand_track(obj):
    random.choice(obj.tracks)


def get_list_of_random_tracks_uri(list_of_artists):
    return [rand_track(artist)['uri'] for artist in list_of_artists]


def get_dict_item(dict, key):
    return dict.setdefault(key, {})


def download_needed_data(token):
    #TODO Remove
    search_url = 'https://api.spotify.com/v1/search'
    artists_names_list = reader.get_list_from_file('tmp_data/artists.txt')
    artist_list = []
    for artist in artists_names_list:
        artist_name = artist.replace(' ','%20')
        artist_query = '{}?q={}&type=artist&limit=1'.format(search_url,artist_name)
        response = requests.get(artist_query, headers={"Content-Type":"application/json",
                               "Authorization": "Bearer {}".format(token)})
        artist_resp  = get_dict_item(get_dict_item(response.json(),'artists'),'items')[0]
        albums_query = 'https://api.spotify.com/v1/artists/{}/albums?include_groups=album,single,compilation'.format(get_dict_item(artist_resp,'id'))
        albums_response = requests.get(albums_query, headers={"Authorization": "Bearer {}".format(token)})
        tmp_albums_list = []
        for item in get_dict_item(albums_response.json(),'items'):
            tracks_query = 'https://api.spotify.com/v1/albums/{}/tracks?limit=50'.format(item['id'])
            tracks_response = requests.get(tracks_query, headers={"Authorization": "Bearer {}".format(token)})
            album_tracks = [{'uri': t['uri'], 'name': t['name']} for t in tracks_response.json()['items']]
            album = Albums(item['name'], item['id'], get_dict_item(artist_resp,'name'), album_tracks)
            tmp_albums_list.append(album)
        artist_obj =  Arist(get_dict_item(artist_resp,'name'), get_dict_item(artist_resp,'id'), tmp_albums_list, [track for alb in tmp_albums_list for track in alb.tracks])
        artist_list.append(artist_obj)
    return artist_list


def get_arist_data(token, api_url, artist_name):
    artist_name = artist_name.replace(' ','%20')
    query = '{}search/?q={}&type=artist&limit=1'.format(api_url,artist_name)
    response = requests.get(query, headers={"Content-Type":"application/json",
                           "Authorization": "Bearer {}".format(token)})
    try:
        artist_json  = get_dict_item(get_dict_item(response.json(),'artists'),'items')[0]
    except IndexError:
        import pdb;pdb.set_trace()
    return artist_json


def get_album_data(token, api_url, artist_json):
    albums_query = '{}/artists/{}/albums?include_groups=album,single,compilation'.format(api_url, get_dict_item(artist_json,'id'))
    albums_response = requests.get(albums_query, headers={"Authorization": "Bearer {}".format(token)})
    return albums_response.json()


def get_albums_tracks(token, api_url, album_json):
    tracks_query = '{}/albums/{}/tracks?limit=50'.format(api_url, album_json['id'])
    tracks_response = requests.get(tracks_query, headers={"Authorization": "Bearer {}".format(token)})
    return tracks_response.json()


def create_empty_playlist(token, user_id, playlist_name):
    query = 'https://api.spotify.com/v1/users/{}/playlists'.format(user_id)
    request_body = json.dumps({
          "name": playlist_name,
          "description": "Karuta_generated_playlist",
          "public": False
        })
    playlist_response = requests.post(url = query, data = request_body,
                                      headers={"Content-Type":"application/json",
                                      "Authorization": "Bearer {}".format(token)}
                                      )
    return  playlist_response.json()


def add_tracks_to_playlist(token, playlist_id, tracks_list):
    query = 'https://api.spotify.com/v1/playlists/{}/tracks'.format(playlist_id)
    tracks_query = "?uris={}".format(','.join(tracks_list))
    query = query + tracks_query
    playlist_response = requests.post(url = query,
                                      headers={"Content-Type":"application/json",
                                      "Authorization": "Bearer {}".format(token)}
                                      )
    return playlist_response




#TODO It (not)works! Refactor in progress
token = ""                                                       # token will expire frequently so it need to be changed
user_id = ""                                                     # insert your spotify username here
api_url = 'https://api.spotify.com/v1/'
artists_names_list = reader.get_list_from_file('tmp_data/artists.txt')
random_name = uuid.uuid4().hex
print('Your new playlist is named:', random_name)
#artist_list = download_needed_data(token)
artist_list = []
for artist in artists_names_list:
    artist_json = get_arist_data(token,api_url,artist)
    albums_json = get_album_data(token,api_url,artist_json)
    albums_list = []
    for album in get_dict_item(albums_json,'items'):
        tracks__json = get_albums_tracks(token,artist_list,album)
        album_tracks = [{'uri': t['uri'], 'name': t['name']} for t in tracks__json['items']]
        album = Albums(album['name'], album['id'], get_dict_item(artist_json,'name'), album_tracks)
        albums_list.append(album)
    artist_obj =  Arist(get_dict_item(artist_json,'name'), get_dict_item(artist_json,'id'), albums_list, [track for alb in albums_list for track in alb.tracks])
    artist_list.append(artist_obj)
list_of_songs = get_list_of_random_tracks_uri(artist_list)
playlist_json = create_empty_playlist(token, user_id,random_name)
final_response = add_tracks_to_playlist(token, playlist_json['id'], list_of_songs)



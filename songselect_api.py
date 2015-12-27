import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

import songselect


package = 'SongselectApi'

class GetSongDataRequest(messages.Message):
    user = messages.StringField(1, required=True)
    password = messages.StringField(2, required=True)
    songIds = messages.StringField(3, repeated=True)


class SongSection(messages.Message):
    name = messages.StringField(1, required=True)
    lines = messages.StringField(2, repeated=True)


class Song(messages.Message):
    id = messages.StringField(1, required=True)
    title = messages.StringField(2, required=True)
    copyrightLines = messages.StringField(3, repeated=True)
    sections = messages.MessageField(SongSection, 4, repeated=True)


class GetSongDataResponse(messages.Message):
    # The song ordering shall be the same as that in the request.
    songs = messages.MessageField(Song, 1, repeated=True)


@endpoints.api(name='songselectApi',version='v1')
class SongselectApi(remote.Service):
    @endpoints.method(GetSongDataRequest, GetSongDataResponse,
                      path='getSongData', http_method='POST')
    def GetSongData(self, request):
        conn = songselect.Connection()
        try:
            conn.Login(request.user, request.password)
        except ValueError as e:
            raise endpoints.UnauthorizedException(e.message)

        songs = []
        for song_id in request.songIds:
            info = conn.GetSong(song_id)
            songs.append(Song(
                id=song_id,
                title=info['title'],
                copyrightLines=info['copyrightLines'],
                sections=[SongSection(name=s[0], lines=s[1])
                          for s in info['sections']]))
        return GetSongDataResponse(songs=songs)

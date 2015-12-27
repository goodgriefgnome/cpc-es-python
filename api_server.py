import endpoints

import songselect_api


APPLICATION = endpoints.api_server([
    songselect_api.SongselectApi
])

from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect
from django.views import View
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

class GoogleCalendarInitView(View):
    def get(self, request):
        flow = Flow.from_client_secrets_file(
            'calendar_integration/client_secret.json',
            scopes=['https://www.googleapis.com/auth/calendar.events.readonly'],
            redirect_uri='http://localhost:8000/rest/v1/calendar/redirect/'
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        request.session['state'] = state
        return redirect(authorization_url)

class GoogleCalendarRedirectView(View):
    def get(self, request):
        state = request.session.pop('state', None)
        if state is None:
            return redirect('/')

        flow = Flow.from_client_secrets_file(
            'calendar_integration/client_secret.json',
            scopes=['https://www.googleapis.com/auth/calendar.events.readonly'],
            redirect_uri='http://localhost:8000/rest/v1/calendar/redirect/',
            state=state
        )
        flow.fetch_token(authorization_response=request.get_full_path())

        credentials = flow.credentials
        request.session['credentials'] = credentials_to_dict(credentials)

        service = build('calendar', 'v3', credentials=credentials)
        events_result = service.events().list(calendarId='primary', maxResults=10, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        return JsonResponse({'events': events})

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
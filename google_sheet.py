import os
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class GoogleAPIClient:
    SECRET_PATH = 'credentials/client_secret.json'
    CREDS_PATH = 'credentials/cred.json'
    
    def __init__(self, serviceName: str, version: str, scopes: list) -> None:
        self.creds = None
        if os.path.exists(self.CREDS_PATH):
            self.creds = Credentials.from_authorized_user_file(self.CREDS_PATH, scopes)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.SECRET_PATH, scopes)
                self.creds = flow.run_local_server(port=0)
            with open(self.CREDS_PATH, 'w') as token:
                token.write(self.creds.to_json())

        self.googleAPIService = build(serviceName, version, credentials=self.creds)

class GoogleSheets(GoogleAPIClient):
    def __init__(self) -> None:
        super().__init__(
            'sheets',
            'v4',
            ['https://www.googleapis.com/auth/spreadsheets'],
        )
    
    def getWorksheet(self, spreadsheetId: str, range: str):
        unusecols = ['Question type', 'Question', 'Answer']
        request = self.googleAPIService.spreadsheets().values().get(
            spreadsheetId=spreadsheetId,
            range=range,
        )
        result = request.execute()['values']
        header = result[0]
        del result[0]
        result = pd.DataFrame(result, columns=header)
        return result.drop(unusecols, axis=1)
    
    def appendWorksheet(self, spreadsheetId: str, range: str, df: pd.DataFrame):
        self.googleAPIService.spreadsheets().values().append(
            spreadsheetId=spreadsheetId,
            range=range,
            valueInputOption='USER_ENTERED',
            body={
                'majorDimension': 'ROWS',
                'values': df.values.tolist()
            },
        ).execute()
        return 
    
    def clearWorksheet(self, spreadsheetId: str, range: str):
        self.googleAPIService.spreadsheets().values().clear(
            spreadsheetId=spreadsheetId,
            range=range,
        ).execute()
        return 
    
    def setWorksheet(self, spreadsheetId: str, range: str, df: pd.DataFrame):
        self.clearWorksheet(spreadsheetId, range)
        self.googleAPIService.spreadsheets().values().update(
            spreadsheetId=spreadsheetId,
            range=range,
            valueInputOption='USER_ENTERED',
            body={
                'majorDimension': 'ROWS',
                'values': df.T.reset_index().T.values.tolist()
            },
        ).execute()
        return 

if __name__ == '__main__':
    pass
from __future__ import print_function

import os.path
import secrets_

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class membership(object):
    """
    Helper class for managing the General Membership spreadsheet.
    """

    def __init__(self):

        #GDSC Club Data 23-24 Spreadsheet 
        self.SPREADSHEET_ID = secrets_.spreadsheet.getId()
        self.SPREADSHEET_RANGE = 'General Membership'
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets'] 

        self.refreshCredentials()

    def refreshCredentials(self):
        """
        Logs in the current user in or refreshes credentials if necessary.
        """

        creds = None

        # check for previous sign-in
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
            self.creds = creds

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:

                # first time sign-in
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
                self.creds = creds

            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

    def append_sheet(self, data):
        """
        Append data to the General Membership sheet using an array of arrays in 
        [[row1], [row2]] format.
        
        Row Headers: [[name, pronouns, cppEmail, altEmail, discord, status, degreeProgram, 
        gradYear, projects, attendanceCredit]]

        Note: Copies all the formatting from the row above.
        """

        try:
            service = build('sheets', 'v4', credentials=self.creds)

            value_input_option = 'RAW'
            value_render_option = 'UNFORMATTED_VALUE'
            insert_data_option = 'INSERT_ROWS'


            body = {'values': data}
            

            request = service.spreadsheets().values().append(spreadsheetId=self.SPREADSHEET_ID, 
                                                                range=self.SPREADSHEET_RANGE,
                                                                valueInputOption=value_input_option,
                                                                insertDataOption=insert_data_option,
                                                                responseValueRenderOption=value_render_option,
                                                                body=body)
            response = request.execute()
            print(response)

        except HttpError as error:
            print(f"An error occurred: {error}")
            return error
        
    def updateAttendance(self, eventCode, discord):
        """
        Updates the attendance cell under General Membership based off of a user's discord username.
        """
        # get range E2:E
        try:
            service = build('sheets', 'v4', credentials=self.creds)
            range_ = self.SPREADSHEET_RANGE + '!E2:E'
            value_render_option = 'FORMATTED_VALUE'

            request = service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_ID, 
                                                          range=range_,
                                                          valueRenderOption=value_render_option)
            
            response = request.execute()

            # find discord name, save what row it is in
            index = None
            print(response['values'])

            
            for i, value in enumerate(response['values']):
                if discord in value:
                    index = i

            if index is not None:
                rowNum = str(index + 2)

                # get current attendance
                value_input_option = 'RAW'
                current_range = self.SPREADSHEET_RANGE + "!K" + rowNum 
                current_request = service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_ID, 
                                                          range=current_range,
                                                          valueRenderOption=value_render_option)
                
                current_response = current_request.execute()

                # check for duplicates
                if 'values' not in current_response:
                    new_cell = eventCode
                else:
                    if eventCode not in current_response['values'][0][0]:
                        new_cell =  current_response['values'][0][0] + ", " + eventCode
                        print(new_cell)
                    else:
                        return "User already credited for this event"

                # append eventCode to cell

                update_body =  {
                    'values': [[new_cell]]
                }

                update_ = service.spreadsheets().values().update(spreadsheetId=self.SPREADSHEET_ID, 
                                                        range=current_range,
                                                        valueInputOption=value_input_option,
                                                        body=update_body)
                
                update_response = update_.execute()
                return update_response
         
            else:
                return "User not found"
        
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error
        
        


    


        




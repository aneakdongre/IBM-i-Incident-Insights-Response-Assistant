GMAIL OAUTH CREDENTIALS REQUIRED

This project uses Gmail API and Google OAuth 2.0.

The original developer's OAuth credentials are intentionally not included.

To enable the Gmail functionality:

1. Create your own Google Cloud project.
2. Enable the Gmail API.
3. Configure the OAuth consent screen.
4. Create an OAuth Desktop Client.
5. Download the OAuth client credentials JSON file.
6. Rename the downloaded file to:
   credentials.json

7. Place it in this credentials folder:
   credentials/credentials.json

After the first successful Gmail authorization, the application will automatically create:
   credentials/token.json

The token.json file is specific to the authenticated user and must remain private.
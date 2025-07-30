# BenchMusic
Group I project  
# Product Initialization - Backend and frontend will need to be on seperate terminals
## Backend
### Creating backend virtual python environment
1. Change to backend directory
2. Run the following command to create a python virtual environment: ```python -m venv venv```
### Starting the virtual python environment
- For Linux/MacOS Users (or Unix based Windows like GIT BASH): ```source venv/bin/activate```
- For Windows CMD: ```.\venv\Scripts\Activate.bat```
- For Windows PowerShell: ```.\venv\Scripts\Activate.ps1``` (if you recieve an error about not being able to run scripts run the following command: ```Set-ExecutionPolicy Unrestricted -Scope Process```)
### Installing Dependecies
- Once the environment is started, run the following command: ```pip install flask flask_cors spotipy google-auth-oauthlib google-auth google-api-python-client python-dotenv```
### Running the API
- After dependencies are installed, run the following command: ```python app.py```
### Closing the API
- To stop the API, simply use the following keybind: ```CTRL + C```
### Closing the Virtual Environment
- To close the venv, run the following command: ```deactivate```
## Frontend
### Installing Dependencies
1. Change to the client dirctory
2. Run the following command: ```npm install```
### Starting the frontend server with HTTPS capabilities
- remain in the client directory
- Run one of the following commands
  1. For Linux/MacOS Users (or Unix based Windows like GIT BASH): ```HTTPS=true npm start```
  2. For Windows CMD: ```set HTTPS=true&&npm start```
  3. For Windows PowerShell: ```($env:HTTPS = "true") -and (npm start)```
### Closing the frontend server
- To close the frontend server, simply use the following keybind: ```CTRL + C```
  


## Overview
- This Project uses the Gitflow branching model to manage its development and releases.
- It will be a web app that converts playlists between Spotify and YouTube and gives recommendations for those playlists.

### Branches
- Master Branch(main)- Represents the production-ready code. Only stable releases are merged into this branch.  
- Develop Branch-  Acts as the main integration branch for ongoing development. Feature branches are merged into this branch for testing and integration.
- Feature Branches- Created for each new feature or issue. These branches are based on the development branch and merged back into development upon completion.


## Software Used
- Python 3.12
- HTML 5
- CSS 3
- Flask

## Dependencies/APIs Used
- Spotify API
- OpenAI API
- YouTube Data API
- SQLite3 API
- GPT API

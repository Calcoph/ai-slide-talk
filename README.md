# Prerequisite:
* Google Account with a Google App-Password
* Client Secrets for a Google Service Account

## Setting Up an App Password in Google Account:
[Getting an Google App Password](https://support.google.com/accounts/answer/185833?hl=en)

## Getting a Client Secrets JSON for a Google Service Account
[Generate a clientsecrets-json](https://developers.google.com/workspace/guides/create-credentials#service-account)

# Setting up Project
To clone this repository:
```
git clone https://github.com/Calcoph/ai-slide-talk.git --recurse-submodules
```
Install mysql (ubuntu):
```
sudo apt install mysql-server
sudo systemctl start mysql.service
sudo mysql
```

Install mysql (windows):
```
winget install Oracle.MySQL
This will download an installer (MySQL Installer - Community), execute it and click "next" a lot
You will have to select a root password, remember it.
Then click "next" until mysql is installed
```

Configure mysql root password:
```
mysql> ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '<CHANGE PASSWORD HERE>';
mysql> exit
```
Mysql secure installation:
```
sudo mysql_secure_installation
```
Install dependencies:
```
sudo apt-get update
sudo apt-get install pkg-config
python3 -m venv ai-slide-talk-venv
source ai-slide-talk-venv/bin/activate
pip3 install -r requirements.txt
```
Start application:
```
streamlit run ai_slide_talk.py
```
Deactivate virtual environment:
```
deactivate
```

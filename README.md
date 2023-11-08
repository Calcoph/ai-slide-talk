To clone this repository:
```
git clone https://github.com/Calcoph/ai-slide-talk.git --recurse-submodules
```
Install mysql:
```
sudo apt install mysql-server
sudo systemctl start mysql.service
sudo mysql
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
pip3 install -r requirements.txt
```
Start application:
```
streamlit run ai_slide_talk.py
```

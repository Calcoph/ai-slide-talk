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

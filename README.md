# 哔哩哔哩视频解析  
## flask项目  
http://域名/?url=哔哩哔哩视频链接  解析视频直链  
示例网站 http://bili.tongxuewen.me  
## 项目部署
配置flask  
`pip install Flask requests   `

`cd /var/www/your_flask_app `

`pip install gunicorn  `

`gunicorn --workers 3 --bind 0.0.0.0:8000 app:app`  
安装反代  Nginx  

`sudo apt install nginx -y`

`sudo nano /etc/nginx/sites-available/your_flask_app
`  

在文件中添加以下内容，调整为您的实际情况：
````
server {
    listen 80;
    server_name your_server_domain_or_IP;
        location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
````
启动反代
````
sudo ln -s /etc/nginx/sites-available/your_flask_app /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
````
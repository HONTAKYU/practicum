# Setup 

### WAF
---

* Modsecurity v3, CRS with Nginx v1.13.x
	
   1. You must clone this to your home folder, or you need to modify `modsecurity_v3.sh` line 55~57 to your corresponding directories. `sudo git clone https://github.com/HONTAKYU/practicum.git`

   2. Go into the cloned folder with `cd practicum`

   3. Change `modsecurity_v3.sh` to executable file `chmod +x modsecurity_v3.sh`

   4. Install everything (we have Nginx, openWAF, CRS rules, Webgoat, docker, Juice-shop for now) `sudo ./modsecurity_v3.sh`

   Approach to get into juice-shop docker container: `sudo docker exec -it <container_id> sh`

   Nginx location:`/usr/local/nginx/`

### RASP
---

* Sqreen with Nginx v1.10.x

   1. get inside the docker container using `sudo docker exec -it <container-name> sh`

   2. run the command to install sqreen: `npm install --save sqreen`
   
   3. put the sqreen token in sqreen.json, this token is generated on the dashboard and is unique for every app that you want to monitor, so
    - first add a new app on the sqreen dashboard
	- a token will be generated, save this token using the command `echo '{ "token": "mysecrettoken" }' > sqreen.json` where mysecrettoken is the unique token of each app registered on sqreen
   
   4. edit server.js `vi server.js` and add the line at the top of the script `const sqreen=require('sqreen')`
   
   5. exit the container and restart the container `sudo docker restart <container-name>`
   
   Note: to see all running and stopped docker images use the command `sudo docker ps --all`

   Nginx location:`/etc/nginx/`

---

* Contrast Security with Nginx v1.10.x

   1. Clone our project to your home folder `sudo git clone https://github.com/HONTAKYU/practicum.git`

   2. Go into the cloned folder with `cd practicum`

   3. Install Nginx, docker and juice-shop with `sudo ./RASP.sh`

   4. Download `contrast.json` and `node-contrast-x.x.x.tgz` from Contrast security website.

   5. Transfer two files to the instance:
	`scp -i contrast_security.pem contrast.json ubuntu@54.183.15.129:~/`
	`scp -i contrast_security.pem node_contrast-* ubuntu@54.183.15.129:~/`

   6. Copy two files to docker container 
	`sudo docker cp contrast.json <container-name>:/juice-shop/`
	`sudo docker cp node_contrast-* <container-name>:/juice-shop/`

   7. get inside the docker container using `sudo docker exec -it <container-name> sh`

   8. In the container, install contrast agent with `npm install node-contrast-*`

   9. Modify line 129 of `package.json` to `"start": "./node_modules/node_contrast/cli.js server.js && node app",`

   10. restart Docker container `sudo docker restart <container-name>` 

   You should be able to see contrast agent is running on Contrast security website.

   Nginx location:`/etc/nginx/`

# Instance Location

|WAF/RASP		|Location 	 	|Port	|
|---------------|:-------------:|------:|
|Modsecurity 	|54.183.15.129	|80		|
|Sqreen			|54.218.116.227	|3000	|
|AWS WAF        |34.215.46.242  |80     |
|Contrast Security|54.85.15.24  |80     |
|F5				|TODO			|TODO	|

# Note

I temporarily put everything into my Github repo, if we have a public account, I would like to move everything to there.

Almost all reasons why this is complicate and we can't use `apt-get` to simple install everything are version issues. `juice-shop` requires `node.js` > 6.X. Forgot which version of `nginx` required by modsecurity, but far more high than the one in ubuntu repo. Also, modsecurity requires to install with nginx together.

One thing needs to be noticed is, we can't use docker as well for now, because installing Nginx with Modsecurity from source file requires to add `nginx.serivce` to `/lib/systemd/system/` and reload the daemon, this can't be done in docker as `/bin/bash` is PID 1, not `/sbin/init`. As far as I know, we have to use VM to run everything to fix this problem.

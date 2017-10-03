# Setup 

### WAF

* Modsecurity v3, CRS with Nginx v1.13.x
---
	
   1. You must clone this to your home folder, or you need to modify `modsecurity_v3.sh` line 55~57 to your corresponding directories.

   `sudo git clone https://github.com/HONTAKYU/practicum.git`

   2. Go into the cloned folder with `cd practicum`

   3. Change `modsecurity_v3.sh` to executable file `chmod +x modsecurity_v3.sh`

   4. Install everything (we have Nginx, openWAF, CRS rules, Webgoat, docker, Juice-shop for now) `sudo ./modsecurity_v3.sh`

   5. Approach to get into juice-shop docker container: `sudo docker exec -it 7a38390c602a sh`

   Source file location:`/usr/local/nginx/`

### RASP

* Sqreen with Nginx v1.10.x
---

   1. Approach to get into juice-shop docker container: `sudo docker exec -it 654ab472f7af sh`

   2. TODO

   Source file location:`/etc/nginx/`

# Instance Location

|WAF/RASP		|Location 	 	|Port	|
|---------------|:-------------:|------:|
|Modsecurity 	|54.183.15.129	|80		|
|Sqreen			|54.218.116.227	|3000	|

# Note

I temporarily put everything into my Github repo, if we have a public account, I would like to move everything to there.

Almost all reasons why this is complicate and we can't use `apt-get` to simple install everything are version issues. `juice-shop` requires `node.js` > 6.X. Forgot which version of `nginx` required by modsecurity, but far more high than the one in ubuntu repo. Also, modsecurity requires to install with nginx together.

One thing needs to be noticed is, we can't use docker as well for now, because installing Nginx with Modsecurity from source file requires to add `nginx.serivce` to `/lib/systemd/system/` and reload the daemon, this can't be done in docker as `/bin/bash` is PID 1, not `/sbin/init`. As far as I know, we have to use VM to run everything to fix this problem.

## Setup, required Ubuntu 16.x

1. You must clone this to your home folder, or you need to modify `install.sh` line 35~37 to your corresponding directories.

`sudo git clone https://github.com/HONTAKYU/practicum.git`

2. Go into the cloned folder with `cd practicum`

3. Change `install.sh` to executable file `chmod +x install.sh`

4. Install everything (we have Nginx, openWAF, CRS rules, Webgoat, Juice-shop for now) `sudo ./install.sh`

I didn't delete installation files, they are located in `~/practicum/` (if you didn't change the location)

## Note

I temporarily put everything into my Github repo, if we have a public account, I would like to move everything to there.

Almost all reasons why this is complicate and we can't use `apt-get` to simple install everything are version issues.
`juice-shop` requires `node.js` > 6.X

Forgot which version of `nginx` required by modsecurity, but far more high than the one in ubuntu repo. Also, modsecurity requires to install with nginx together.

One thing needs to be noticed is, we can't use docker as well for now, because installing Nginx with Modsecurity from source file requires to add `nginx.serivce` to `/lib/systemd/system/` and reload the daemon, this can't be done in docker as `/bin/bash` is PID 1, not `/sbin/init`. As far as I know, we have to use VM to run everything to fix this problem.

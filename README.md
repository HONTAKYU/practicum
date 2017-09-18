##Setup, required Ubuntu 16.x

First you must clone this to your home folder, or you need to modify `install.sh` line 35~37 to your corresponding directories.

`sudo git clone https://github.com/HONTAKYU/practicum.git`

Go into the cloned folder with `cd practicum`

Change `install.sh` to executable file `chmod +x install.sh`

Install everything (we have Nginx, openWAF, CRS rules, Webgoat, Juice-shop for now) `sudo ./install.sh`

I didn't delete installation files, they are located in `~/practicum/` (if you didn't change the location)

##Note
I temporarily put everything into my Github repo, if we have a public account, I would like to move everything to there.

Almost all reasons why this is complicate and we can't use `apt-get` to simple install everything are version issues.
`juice-shop` requires `node.js` > 6.X
Forgot which version of `nginx` required by modsecurity, but far more high than the one in ubuntu repo. Also, modsecurity requires to install with nginx together.

## Welcome!
First of all, thanks for your contribution. This guide works well on linux with docker installed, if you use in another 
way, feel free to contribute.

### System requirements
* Python 3.5+
* pip
* [Docker](https://docs.docker.com/get-docker/)
* Docker compose: `$ sudo pip install docker-compose`
* Some vnc client: in this guide we use [Remmina](https://remmina.org/)

### Prepare environment
* run `docker-compose up firefox`, then a instance of selenium in your 
[localhost:4444](http://localhost:4444/wd/hub/static/resource/hub.html) will be available
* open your vnc client in localhost:5900, it will ask for a password that is `secret`

### Run project
* create some virtual env
* install dependencies: `$ pip install -r requirements/development.txt`
* create selenium variable: `$ export SELENIUM=http://localhost:4444/wd/hub`
* create a number variable: `$ export MY_PHONE=55...`
* run `$ ipython` and load a example `%load sample/message_with_thumb.py`
* check your vnc client 
* run another example `%load sample/remote.py` 

### Commit standardization
Please, use our tool `utils/commit.sh` to make commits more standardized
* To apply [black](https://github.com/psf/black) style: `black .`
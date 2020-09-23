## New to WebWhatsapp-Wrapper?
This is a comprehensive guide to get you up and running with this project.

## Installation for Linux OS


**Requirements**
* Docker
* Python
* Sudo privilege 

### Creating a network

```
docker network create selenium
```

**Run a selenium standalone container**
```
docker run -d -p 4444:4444 -p 5900:5900 --name firefox --network selenium -v /dev/shm:/dev/shm selenium/standalone-firefox-debug:3.14.0-curium
```

### 1. Cloning WebWhatsapp-Wrapper repo

You'll need to have a local copy of the project in your machine.

```
$ git clone https://github.com/mukulhase/WebWhatsapp-Wrapper.git
$ cd WebWhatsapp-Wrapper
```


### 2. Creating an environment with dependencies

Before installing any project, it's a good practice to create an isolated environment. This should contain the required dependencies. A very easy way to create virtual environment is using virtualenv.

* install virtualenv: `$ pip install virtualenv`
* create virtual environment for WebWhatsapp-Wrapper: `$ virtualenv WhatsappwebapiEnv`
* activate the environment: `$ source WhatsappwebapiEnv/bin/activate`


### 3. Install the project dependencies

If you're using virtual environment as described in step 2, make sure the environment is activated.

```
$ pip install -r  /requirements/base.txt
```


### 4. Install the project from it's setup file

```
$ pip install ./
```


### 5. Running the examples

Using the [remote.py](/sample/remote.py) from the sample directory. You'll have to modify the following.

1. __Path to Selenium__.
    Before getting the environment variable, setup the path to selenium.


    ```
    os.environ['SELENIUM'] = "http://localhost:4444/wd/hub"
    ```

2. You can create your instance of WhatsAPIDriver, 
    ```
    driver = WhatsAPIDriver(
                profile=self.profiledir, client="remote",
                command_executor=os.environ["SELENIUM"],
                loadstyles=True
            )
    self.profiledir = os.path.join(".", "firefox_cache") # this is a directory
    ```

3. __Capture the qr code__, before waiting for login

    ```
    driver.get_qr("the_qr_code_image.png")

    driver.wait_for_login()
    ```

    The captured qr code image would be in the same directory as WebWhatsapp-Wrapper

    ```
    .
    ├── WebWhatsapp-Wrapper
    ├── the_qr_code_image.png
    ```

    Open the image and scan it using whatsapp mobile device.

    *Viola!!!*
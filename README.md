# chrawme

Pictures browser / viewer implemented as a local Django app:
- Compatible with **raw image** formats
- Can be used with **chromecast** (unique feature for Raw images)
- Integration with [**Hubic**](https://hubic.com): browse your remote files too!

## Setup

Setup steps for Linux, although it will be very similar on a Mac machine.

Preferably use `virtualenv`. Simply run
```
# If not installed yet
sudo apt-get install virtualenv

# In the project directory
virtualenv ENV
. ENV/bin/activate
pip install -r requirements.txt
```

## Run the App

On a Linux machine, run
```
. ENV/bin/activate
python manage.py runserver
```
and open the url `http://localhost:8000/browser/` in your navigator.

Alternatively, if Google Chrome is installed (not Chromium), simply execute `. run` from the project directory (simple `bash` script to do the above).

## Hubic integration

You will need to populate your API crendential file to allow the app to connect to your Hubic account.
Follow the steps described in the [Hubic API doc](https://api.hubic.com/) to get a `client_id`, `secret` and OAuth `refresh_token`.

## Screenshots

### Gallery
Example taken from one of my Github projects, here's what the picture gallery looks like:
![gallery](https://github.com/tcassou/chrawme/blob/master/screenshots/gallery.png)

### Viewer
![viewer](https://github.com/tcassou/chrawme/blob/master/screenshots/viewer.png)

# SmartAncestry

## goto web app root

cd ~/Prog/SmartAncestry/smartancestry

## Installation

### pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py

### Creating a virtual environment
python3 -m pip install --user virtualenv
python3 -m venv vsmartancentry


source bin/activate

brew install node

sudo pip3 install -r requirements.txt
https://www.princexml.com/doc/9.0/installing/#macosx
brew install cairo
brew install libjpeg
brew install graphviz
npm i request
npm i canvas

## run web server

cd ~/Prog/SmartAncestry/smartancestry/
source vsmartancentry/bin/activate
python3 manage.py runserver 7000

## data migration

cd ~/Prog/SmartAncestry/smartancestry/
source vsmartancentry/bin/activate

python3 manage.py makemigrations data
python3 manage.py sqlmigrate data 0007
python3 manage.py migrate
deactivate

## translations

### installation

brew install gettext
brew link gettext --force

### translations

cd ~/Prog/SmartAncestry/smartancestry/
source vsmartancentry/bin/activate
cd data
python3 ../manage.py makemessages -l de -e html,txt,py -e xml
translate with poedit
python3 ../manage.py compilemessages

## distributions

https://www.namenskarte.com/nachname/Name?

## pdf generator

prince --no-author-style -s http://127.0.0.1:7000/static/data/style_print.css http://127.0.0.1:7000/data/ancestry/1/Kliemank -o Kliemank.pdf

# todo

- add images to ancestry.js / dot script

# Links

- https://www.google.com/maps/d/u/0/viewer?ll=50.93992570930961%2C25.47879062957759&z=15&mid=1Sz-Sn4I1F-iqS2sNeeTPZ6-Jd8I
- https://wolhynien.de/images/Lueck1927_gr.jpg
- https://sites.rootsweb.com/~ukrgs/volhynia/#Marriages
- http://meta.genealogy.net/search/index
- https://www.sggee.org/research/PublicDatabases.html
- https://www.familysearch.org/tree/find
- http://ofb.genealogy.net/famreport.php?ofb=rusdorf&ID=I419&nachname=KR%C4HE&modus=&lang=se

- http://ged-inline.elasticbeanstalk.com/validate
- https://en.wikipedia.org/wiki/GEDCOM
- www.familysearch.org/developers/docs/guides/gedcom

- https://graphviz.org/doc/info/shapes.html#html

Icons made by <a href="https://www.flaticon.com/authors/freepik" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a>

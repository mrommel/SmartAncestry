# SmartAncestry

## goto web app root

cd ~/Prog/SmartAncestry/smartancestry

## Installation

brew install node
pip install -r requirements.txt
https://www.princexml.com/doc/9.0/installing/#macosx
brew install cairo
brew install libjpeg
brew install graphviz
npm i request

## run web server

python manage.py runserver 7000

## data migration

workon venv
python manage.py makemigrations data
python manage.py sqlmigrate data 0007
python manage.py migrate
deactivate

## translations

### installation

brew install gettext
brew link gettext --force

cd ~/Prog/SmartAncestry/smartancestry/data/
python ../manage.py makemessages -l de -e html,txt,py -e xml
python ../manage.py compilemessages

## node js scripts

cd ~/Prog/SmartAncestry/smartancestry/data/static/data/js

node bar.js 
==> Listening at http://localhost:4444

node colors.js 
==> prints colors (hsl / 12)

node tree.js
==> create ancestry trees

## misc

http://www.verwandt.de/karten/absolut/schossig.html

## jsdoc

cd ~/Prog/SmartAncestry/smartancestry/data/static/data/js
../../../../../../../node_modules/jsdoc/jsdoc -d ../doc ../ancestryTree.js 

## pdf generator

prince --no-author-style -s http://127.0.0.1:8000/static/data/style_print.css http://127.0.0.1:8000/data/ancestry/1/Kliemank -o Kliemank.pdf

# todo

- add images to ancestry.js / dot script

# Links

- https://www.google.com/maps/d/u/0/viewer?ll=50.93992570930961%2C25.47879062957759&z=15&mid=1Sz-Sn4I1F-iqS2sNeeTPZ6-Jd8I
- https://wolhynien.de/images/Lueck1927_gr.jpg
- https://sites.rootsweb.com/~ukrgs/volhynia/#Marriages
- http://meta.genealogy.net/search/index
- https://www.sggee.org/research/PublicDatabases.html
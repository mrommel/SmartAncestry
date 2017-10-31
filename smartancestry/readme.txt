
# goto web app root

cd ~/Prog/SmartAncestry/smartancestry

# run web server

python manage.py runserver

# data migration

workon venv
python manage.py makemigrations data
python manage.py sqlmigrate data 0007
python manage.py migrate
deactivate

# translations

cd ~/Prog/SmartAncestry/smartancestry/data/
python ../manage.py makemessages -l de -e html,txt -e xml
python ../manage.py compilemessages

# node js scripts

cd ~/Prog/SmartAncestry/smartancestry/data/static/data/js

node bar.js 
==> Listening at http://localhost:4444

node colors.js 
==> prints colors (hsl / 12)

node tree.js
==> create ancestry trees

# misc

http://www.verwandt.de/karten/absolut/schossig.html

# jsdoc

cd /Users/michael.rommel/Prog/SmartAncestry/smartancestry/data/static/data/js
../../../../../../../node_modules/jsdoc/jsdoc -d ../doc ../ancestryTree.js 

# pdf generator

prince --no-author-style -s http://127.0.0.1:8000/static/data/style_print.css http://127.0.0.1:8000/data/ancestry/1/Kliemank -o Kliemank.pdf
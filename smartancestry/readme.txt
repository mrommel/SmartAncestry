
# goto web app root

cd ~/Prog/SmartAncestry/smartancestry

# run web server

python manage.py runserver

# data migration

python manage.py makemigrations data
python manage.py sqlmigrate data 0007
python manage.py migrate

# translations

cd ~/Prog/SmartAncestry/smartancestry/data/
python ../manage.py makemessages -l de -e html,txt -e xml
python ../manage.py compilemessages

# node js scripts

cd /Users/mrommel/Prog/SmartAncestry/smartancestry/data/static/data/js

node bar.js 
==> Listening at http://localhost:4444

node colors.js 
==> prints colors (hsl / 12)

# misc

http://www.verwandt.de/karten/absolut/schossig.html


# pdf generator

prince --no-author-style -s http://127.0.0.1:8000/static/data/style_print.css http://127.0.0.1:8000/data/ancestry/1/Kliemank -o Kliemank.pdf
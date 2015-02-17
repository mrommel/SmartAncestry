
# goto web app root

cd /Users/mrommel/Prog/SmartAncestry/smartancestry

# run web server

python manage.py runserver

# data migration

python manage.py makemigrations data
python manage.py sqlmigrate data 0007
python manage.py migrate

# translations

cd /Users/mrommel/Prog/SmartAncestry/smartancestry/data/
python ../manage.py makemessages -l de -e html,txt -e xml
python ../manage.py compilemessages



http://www.verwandt.de/karten/absolut/schossig.html
# pip install django-ddm
# prev=$(pip show django-ddm | grep Version: | cut -d' ' -f2 )
minor=2
major=2.1
# let "minor++"
sed -i "s/__version__/$major.$minor/g" setup.cfg
sed -i "s/__version__/$major.$minor/g" ddm/__init__.py

pip install django-ddm
prev=$(pip show django-ddm | grep Version: | cut -d' ' -f2 )
minor=$(echo $prev | rev | cut -d"." -f1  | rev)
major=$(echo $prev | rev | cut -d"." -f2-  | rev)
let "minor++"
sed -i "s/__version__/$major.$minor/g" setup.cfg

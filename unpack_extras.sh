EXTRAS="$1"
REPOS="$2"

find $EXTRAS -name '*.zip' | \
while read file;
do
	DIR=$(echo "${file%.*}" | cut -d '_' -f 1)
	PID=$(echo "${file%.*}" | cut -d '_' -f 2)
	echo "Unzipping $file to $PID"
	mkdir -p $REPOS/$PID/$DIR
done

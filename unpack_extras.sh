EXTRAS="$1"
REPOS="$2"

rm repo.dirs.extra &>/dev/null

find $EXTRAS -name '*.zip' | \
while read file;
do
    basefile=$(basename $file)
    DIR=$(echo "${basefile%.*}" | cut -d '_' -f 1)
    PID=$(echo "${basefile%.*}" | cut -d '_' -f 2)
    mkdir -p $REPOS/$PID/$DIR
    ZIPDIR=$(realpath $REPOS/$PID/$DIR)
    if unzip "$file" -d "$ZIPDIR" </dev/null &>/dev/null
    then 
	echo "Unzipping files to $ZIPDIR" >&2
    else 
	unzip -f "$file" -d "$ZIPDIR" &>/dev/null
	echo "Freshened files in $ZIPDIR" >&2
    fi
    echo "$PID \"$ZIPDIR\"" >> repo.dirs.extra
done

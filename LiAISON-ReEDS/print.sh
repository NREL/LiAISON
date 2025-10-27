file='yaml'
while read line; do
echo '"'$line'",'
done <$file

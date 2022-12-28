foo = "10:10:58.719"
bar = "00:51:00.719"

# This works
if bar < foo:
    print("Correct!")
else:
    print("Incorrect!")

# This does not work!
print(foo - bar)

https://stackoverflow.com/questions/14295673/convert-string-into-datetime-time-object
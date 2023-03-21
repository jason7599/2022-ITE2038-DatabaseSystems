import random;
import csv;

MILLION = 1000000;

insertCount = 5000;
deleteCount = 5000-200;

insert = [i for i in range(1,insertCount+1)];
random.shuffle(insert);

delete = random.sample(insert, k=deleteCount);

with open("myInput.csv", "w", newline="") as file:

    writer = csv.writer(file);

    for i in insert:
        writer.writerow([i, i*2]);

with open("myDelete.csv", "w", newline="") as file:

    writer = csv.writer(file);

    for d in delete:
        writer.writerow([d]);

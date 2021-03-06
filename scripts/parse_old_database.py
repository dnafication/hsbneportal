import csv

with open('/home/jabelone/Downloads/access.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    kept_people = []
    kept_people_phone = []

    for row in csv_reader:
        if int(row[6]):
            active = "active"
        else:
            active = "inactive"

        if len(row[5]) == 10:
            kept_people_phone.append({"nickname": row[2], "first_name": row[1], "last_name": "", "mobile": "", "email": row[3], "rfid": row[5], "created": "2018-10-06 11:59:59", "active": active})
        else:
            kept_people.append({"nickname": row[2], "first_name": row[1], "last_name": "", "mobile": "", "email": row[3], "rfid": row[5], "created": "2018-10-06 11:59:59", "active": active})

    print("with card {}:".format(len(kept_people)))
    for person in kept_people:
        print(f"{person['nickname']},{person['first_name']},{person['last_name']},{person['mobile']},{person['email']},{person['rfid']},{person['created']},{person['active']}")

    print("\nwithout card {}:".format(len(kept_people_phone)))
    for person in kept_people_phone:
        print(
            f"{person['nickname']},{person['first_name']},{person['last_name']},{person['mobile']},{person['email']},{person['rfid']},{person['created']},{person['active']}")

    print("total: " + str(len(kept_people) + len(kept_people_phone)))
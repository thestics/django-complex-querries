Let we have a Django project.
With models:

```
Rental
 - name
```

```
Reservation
  - rental(FK)
  - checkin(date)
  - checkout(date)
```

Add the django view with the table of Reservations with "previous reservation ID".
A previous reservation is a reservation that is before by date the current one for the same rental.


Example:
```
Reservations for
Rental-1
(1, 2022-01-01, 2022-01-13)
(2, 2022-01-20, 2022-02-10)
(3, 2022-02-20, 2022-03-10)

Rental-2
(4, 2022-01-02, 2022-01-20)
(5, 2022-01-20, 2022-02-11)
```

Result table:
```
|Rental_name|ID|Checkin    |Checkout  |Previous reservation  ID|
|rental-1   |1 | 2022-01-01|2022-01-13| -                      |
|rental-1   |2 | 2022-01-20|2022-02-10| 1                      |
|rental-1   |3 | 2022-02-20|2022-03-10| 2                      |
|rental-2   |4 | 2022-01-02|2022-01-20| -                      |
|rental-2   |5 | 2022-01-20|2022-01-11| 4                      |
```
Also, add tests.
Create it into GitHub repo and provide a link to it.
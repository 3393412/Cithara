#  Cithara - Django Project Setup

##  Requirements

* Python 3.10+
* pip

---

##  1. Clone Project

```bash
git clone https://github.com/3393412/Cithara.git
cd <your-project-folder>
```

---

##  2. Create Virtual Environment

```bash
python -m venv venv
```

### Activate (Windows)

```bash
venv\Scripts\activate
```

### Activate (Mac/Linux)

```bash
source venv/bin/activate
```

---

##  3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

##  4. Setup Database

```bash
python manage.py makemigrations
python manage.py migrate
```

---

##  5. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

---

##  6. Run Server

```bash
python manage.py runserver
```

Open:

```
http://127.0.0.1:8000/
```

---

##  Admin Panel

```
http://127.0.0.1:8000/admin/
```

---

#  API Endpoints (Demo)

##  Songs API

Endpoint:

```
/api/songs/
```

รองรับ: `GET`, `POST`, `PUT`, `DELETE`

---

###  GET (ทั้งหมด / filter / รายตัว)

#### ทั้งหมด

```
GET /api/songs/
```

#### filter ด้วย username

```
GET /api/songs/?username=jo
```

#### ดึงตัวเดียว

```
GET /api/songs/?id=1
```

---

###  POST (สร้างเพลง + upload file)

```
POST /api/songs/
```

Body (form-data):

```
username: jo
title: test song
genre: pop
duration: 120
occasion: party
prompt: some prompt
story: some story
vocal: male
mood: happy
path: (file upload)
```

---

###  PUT (แก้ไข)

```
PUT /api/songs/
```

Body (JSON):

```json
{
  "id": 1,
  "title": "new title",
  "genre": "rock"
}
```

---

###  DELETE

```
DELETE /api/songs/
```

Body (JSON):

```json
{
  "id": 1
}
```

---

##  Share Link API

### Create

```
POST /share/
```

```json
{
  "song_id": 1,
  "token": "demo123"
}
```

### Get

```
GET /share/demo123/
```

### Delete

```
DELETE /share/delete/demo123/
```

---

##  Project Structure (Example)

```
Cithara/
│
├── song_api/
│   ├── models.py
│   ├── views.py   👈 songs_api อยู่ที่นี่
│
├── share/
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│
├── manage.py
└── requirements.txt
```

---

##  Notes

* เพิ่มใน `INSTALLED_APPS`:

```python
'song_api',
'share',
```

* register admin:

```python
admin.site.register(ShareLink)
```

---

##  Test Tools

* Postman
* curl




Getmethod
![คำอธิบายรูป](images/image.png)
![คำอธิบายรูป](images/Screenshot%202026-03-24%20232901.png)
Postmethod
![คำอธิบายรูป](images/Screenshot%202026-03-24%20232148.png)
![คำอธิบายรูป](images/Screenshot%202026-03-24%20232225.png)
![คำอธิบายรูป](images/Screenshot%202026-03-24%20232403.png)
Putmethod
![คำอธิบายรูป](images/Screenshot%202026-03-24%20232507.png)
![คำอธิบายรูป](images/Screenshot%202026-03-24%20232517.png)
DeleteMethod
![คำอธิบายรูป](images/Screenshot%202026-03-24%20232525.png)
![คำอธิบายรูป](images/Screenshot%202026-03-24%20232539.png)

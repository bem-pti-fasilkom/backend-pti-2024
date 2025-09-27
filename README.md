# Backend PTI

Berikut adalah dokumentasi untuk isi repository backend PTI beserta dengan API backend PTI.

## Struktur Repositori

| File/Folder      | Deskripsi                                                |
| ---------------- | -------------------------------------------------------- |
| backend_pti/     | Folder project dari aplikasi Django                      |
| best_staff/      | Folder app Best Staff (PSDM)                             |
| issue_tracker/   | Folder app Issue Tracker (Adkesma)                       |
| jwt/             | Folder app untuk management JWT based auth               |
| main_web/        | Folder app untuk Web Utama BEM Fasilkom                  |
| static/          | Folder berisi aset static untuk production release       |
| .gitignore       | Berisi file dan folder yang diabaikan oleh Git           |
| Dockerfile       | Dockerfile untuk mendefinisikan cara membangun container |
|                  | backend-pti                                              |
| README.md        | Dokumentasi mengenai repository dan aplikasi backend-pti |
| docker-compose   | Docker Compose manifest file untuk mendefinisikan        |
|                  | container eksternal, seperti DB dan server SSO           |
| init.sql         | File SQL yang membuat database staging, yang akan        |
|                  | dipanggil saat proses membangun container dengan         |
|                  | Docker Compose                                           |
| manage.py        | Entrypoint untuk memanggil command dengan                |
|                  | `python manage.py` pada aplikasi backend-pti             |
| requirements.txt | File dependency aplikasi backend-pti                     |

## Dokumentasi API

Berikut adalah dokumentasi untuk penggunaan REST API Backend PTI

<!--toc:start-->

- [1. Issue Tracker](#1-issue-tracker)
  - [Get All Pengaduan](#get-all-pengaduan)
  - [Get Pengaduan By ID](#get-pengaduan-by-id)
  - [Create Pengaduan](#create-pengaduan)
  - [Update Pengaduan](#update-pengaduan)
  - [Delete Pengaduan](#delete-pengaduan)
  - [Like/Unlike Pengaduan](#likeunlike-pengaduan)
  - [Add Comment](#add-comment)
  - [Update Comment](#update-comment)
  - [Hapus Komentar](#hapus-komentar)
  - [Lihat Pengaduan Pengguna](#lihat-pengaduan-pengguna)
  - [Lihat Semua Pengaduan yang di-like](#lihat-semua-pengaduan-yang-di-like)
  - [Lihat Seluruh Pengaduan yang di-comment](#lihat-seluruh-pengaduan-yang-di-comment)
  <!--toc:end-->

API dipanggil dengan format sebagai berikut:
`/{BASE_URL}/{PATHNAME}`

Autentikasi API menggunakan JWT Token dengan format Bearer Token.

```
headers:
  Authorization: "Bearer {JWT_TOKEN}"
```

Selanjutnya pada dokemntasi ini akan digunakan notasi `@sso_authenticated` pada suatu endpoint yang mengindikasikan bahwa Anda perlu menambahkan bearer token pada auth header pada saat melakukan request ke endpoint tersebut.

Untuk mengakses data pengguna, gunakan
`@sso_authenticated GET /auth/self`
Dengan response sebagai berikut

1. 200 OK

```typescript!=
export interface SSOUser {
    username:      string;
    npm:           string;
    full_name:     string;
    faculty:       string;
    short_faculty: string;
    major:         string;
}
```

3. 401 NOT AUTHENTICATED

```json=
{
  "error": "User not authenticated"
}
```

JWT Token didapatkan menggunakan SSO Server terpisah dengan format request berikut

`/{AUTH_API_BASE_URL}/login?redirect=${REDIRECT_URL}`
`REDIRECT_URL` adalah url yang dituju setelah proses login SSO telah selesai. Setelah selesai melakukan autentikasi, SSO server akan melakukan redirect ke `{REDIRECT_URL}?token={JWT_TOKEN}`

## 1. Issue Tracker

Secara umum issue tracker memiliki REST API endpoint berikut:

### Get All Pengaduan

```
GET /pengaduan?${QUERY_PARAM}=${VALUE}
```

Query Parameters:

- status: `"UNRESOLVED" | "RESOLVED" | "REPORTED"`
- judul: string

Dengan response:

- 200 OK

```typescript!=
export interface GetAllPengaduanResponse {
    count:    number;
    next:     string;
    previous: null;
    results:  Pengaduan[];
}

export interface Pengaduan {
    id:              number;
    is_anonymous:    boolean;
    judul:           string;
    isi:             string;
    lokasi:          string;
    tanggal_post:    Date;
    jumlah_like:     number;
    jumlah_komentar: number;
    status:          "UNRESOLVED" | "RESOLVED" | "REPORTED";
    author:          null;
    likes:           Like[];
    comments:        Comment[];
    evidence:        Evidence[];
}

export interface Comment {
    id:        number;
    author:    string;
    isi:       string;
    pengaduan: number;
}

export interface Evidence {
    id:        number;
    url:       string;
    pengaduan: number;
}

export interface Like {
    id:        number;
    akun_sso:  string;
    pengaduan: number;
}
```

### Get Pengaduan By ID

```
GET /pengaduan/<int:id>
```

Dengan response:

- 200 OK

```typescript=
export interface GetPengaduanResponse {
    id:              number;
    is_anonymous:    boolean;
    judul:           string;
    isi:             string;
    lokasi:          string;
    tanggal_post:    Date;
    jumlah_like:     number;
    jumlah_komentar: number;
    status:          "UNRESOLVED" | "RESOLVED" | "REPORTED";
    author:          null;
    likes:           Like[];
    comments:        Comment[];
    evidence:        Evidence[];
}

export interface Comment {
    id:        number;
    author:    string;
    isi:       string;
    pengaduan: number;
}

export interface Evidence {
    id:        number;
    url:       string;
    pengaduan: number;
}

export interface Like {
    id:        number;
    akun_sso:  string;
    pengaduan: number;
}
```

- 404 NOT FOUND

### Create Pengaduan

```
@sso_authenticated POST /pengaduan/
```

Dengan body:

```typescript!=
export interface CreatePengaduanDTO {
    is_anonymous: boolean;
    judul:        string;
    isi:          string;
    lokasi:       string;
    evidence:     string[];
}
```

Dengan response:

- 201 CREATED

```typescript!=
export interface CreatePengaduanResponse {
    id:              number;
    is_anonymous:    boolean;
    judul:           string;
    isi:             string;
    lokasi:          string;
    tanggal_post:    Date;
    jumlah_like:     number;
    jumlah_komentar: number;
    status:          string;
    author:          Author;
    likes:           any[];
    evidence:        Evidence[];
}

export interface Author {
    username:      string;
    npm:           string;
    full_name:     string;
    faculty:       string;
    short_faculty: string;
    major:         string;
    program:       string;
}

export interface Evidence {
    id:        number;
    url:       string;
    pengaduan: number;
}
```

- 401 UNAUTHORIZED

```json=
{
    "error_message": "Autentikasi Gagal"
}
```

### Update Pengaduan

```
@sso_authenticated PUT /pengaduan/<int:id>/
```

Dengan body:

```typescript!=
export interface UpdatePengaduanDTO {
    is_anonymous: boolean | null;
    judul:        string | null;
    isi:          string | null;
    lokasi:       string | null;
    evidence:     string[] | null;
}
```

Dengan response:

- 200 OK

```typescript!=
export interface UpdatePengaduanResponse {
    id:              number;
    is_anonymous:    boolean;
    judul:           string;
    isi:             string;
    lokasi:          string;
    tanggal_post:    Date;
    jumlah_like:     number;
    jumlah_komentar: number;
    status:          "UNRESOLVED" | "RESOLVED" | "REPORTED";
    author:          null;
    likes:           Like[];
    comments:        Comment[];
    evidence:        Evidence[];
}

export interface Comment {
    id:        number;
    author:    string;
    isi:       string;
    pengaduan: number;
}

export interface Evidence {
    id:        number;
    url:       string;
    pengaduan: number;
}

export interface Like {
    id:        number;
    akun_sso:  string;
    pengaduan: number;
}
```

Dengan response:

- 401 UNAUTHORIZED

```json=
{"error_message": "Autentikasi Gagal"}
```

- 403 FORBIDDEN

```json=
{"error_message": "Anda tidak memiliki akses untuk mengubah pengaduan ini"}
```

```json=
{"error_message": "Pengaduan ini sudah diajukan, tidak dapat diubah"}
```

- 404 NOT FOUND

### Delete Pengaduan

```
@sso_authenticated DELETE /pengaduan/<int:id>/
```

- 200 OK

```json=
{"message": "Pengaduan berhasil dihapus"}
```

- 401 UNAUTHORIZED

```json=
{"error_message": "Autentikasi Gagal"}
```

- 403 FORBIDDEN

```json=
{"error_message": "Anda tidak memiliki akses untuk menghapus pengaduan ini"}
```

```json=
{"error_message": "Pengaduan ini sudah diajukan, tidak dapat dihapus"}
```

### Like/Unlike Pengaduan

```
@sso_authenticated POST /pengaduan/<int:id>/like/
```

Dengan response:

- 200 OK

```json=
{"message": "Like berhasil"}
```

```json=
{"message": "Unlike berhasil"}
```

- 401 UNAUTHORIZED

```json=
{"error_message": "Autentikasi Gagal"}
```

### Add Comment

```
@sso_authenticated POST /pengaduan/<int:id>/comments/
```

Dengan body:

```typescript=
export interface CreateCommentDTO {
    isi: string;
}
```

Dengan response:

- 201 CREATED

```typescript=
export interface CreateCommentDTO {
    id:        number;
    author:    string;
    isi:       string;
    pengaduan: number; // id dari pengaduan
}
```

- 401 UNAUTHORIZED

```json=
{"error_message": "Autentikasi Gagal"}
```

### Update Comment

```
@sso_authenticated PUT /comments/<int:id>/
```

Dengan body:

```typescript=
export interface CreateCommentDTO {
    isi: string;
}
```

- 200 OK

```typescript=
export interface CreateCommentDTO {
    id:        number;
    author:    string;
    isi:       string;
    pengaduan: number; // id dari pengaduan
}
```

- 403 FORBIDDEN

```json=
{"error_message": "Anda tidak memiliki akses untuk mengubah komentar ini"}
```

- 401 UNAUTHORIZED

```json=
{"error_message": "Autentikasi Gagal"}
```

- 400 BAD REQUEST

```json=
{"error_message": "Isi komentar tidak boleh kosong"}
```

### Hapus Komentar

```
@sso_authenticated DELETE /comments/<int:id>
```

- 200 OK

```json=
{"message": "Komentar berhasil dihapus"}
```

- 401 UNAUTHORIZED

```json=
{"error_message": "Autentikasi Gagal"}
```

- 403 FORBIDDEN

```json=
{"error_message": "Anda tidak memiliki akses untuk menghapus komentar ini"}
```

### Lihat Pengaduan Pengguna

```
@sso_authenticated /pengaduan/histories/
```

Dengan response:

- 200 OK

```typescript=
export interface PengaduanPenggunaResponse {
    count:    number;
    next:     string;
    previous: null;
    results:  Pengaduan[];
}

export interface Pengaduan {
    id:              number;
    is_anonymous:    boolean;
    judul:           string;
    isi:             string;
    lokasi:          string;
    tanggal_post:    Date;
    jumlah_like:     number;
    jumlah_komentar: number;
    status:          "UNRESOLVED" | "RESOLVED" | "REPORTED";
    author:          null;
    likes:           Like[];
    comments:        Comment[];
    evidence:        Evidence[];
}

export interface Comment {
    id:        number;
    author:    string;
    isi:       string;
    pengaduan: number;
}

export interface Evidence {
    id:        number;
    url:       string;
    pengaduan: number;
}

export interface Like {
    id:        number;
    akun_sso:  string;
    pengaduan: number;
}
```

- 401 UNAUTHORIZED

```json=
{"error_message": "Autentikasi Gagal"}
```

### Lihat Semua Pengaduan yang di-like

```
@sso_authenticated /pengaduan/liked/
```

Dengan response:

- 200 OK

```typescript=
export interface LikedPengaduanResponse {
    count:    number;
    next:     string;
    previous: null;
    results:  Pengaduan[];
}

export interface Pengaduan {
    id:              number;
    is_anonymous:    boolean;
    judul:           string;
    isi:             string;
    lokasi:          string;
    tanggal_post:    Date;
    jumlah_like:     number;
    jumlah_komentar: number;
    status:          "UNRESOLVED" | "RESOLVED" | "REPORTED";
    author:          null;
    likes:           Like[];
    comments:        Comment[];
    evidence:        Evidence[];
}

export interface Comment {
    id:        number;
    author:    string;
    isi:       string;
    pengaduan: number;
}

export interface Evidence {
    id:        number;
    url:       string;
    pengaduan: number;
}

export interface Like {
    id:        number;
    akun_sso:  string;
    pengaduan: number;
}
```

- 401 UNAUTHORIZED

```json=
{"error_message": "Autentikasi Gagal"}
```

### Lihat Seluruh Pengaduan yang di-comment

```
@sso_authenticated /pengaduan/commented/
```

Dengan response:

- 200 OK

```typescript=
export interface CommentedPengaduanResponse {
    count:    number;
    next:     string;
    previous: null;
    results:  Pengaduan[];
}

export interface Pengaduan {
    id:              number;
    is_anonymous:    boolean;
    judul:           string;
    isi:             string;
    lokasi:          string;
    tanggal_post:    Date;
    jumlah_like:     number;
    jumlah_komentar: number;
    status:          "UNRESOLVED" | "RESOLVED" | "REPORTED";
    author:          null;
    likes:           Like[];
    comments:        Comment[];
    evidence:        Evidence[];
}

export interface Comment {
    id:        number;
    author:    string;
    isi:       string;
    pengaduan: number;
}

export interface Evidence {
    id:        number;
    url:       string;
    pengaduan: number;
}

export interface Like {
    id:        number;
    akun_sso:  string;
    pengaduan: number;
}
```

- 401 UNAUTHORIZED

```json=
{"error_message": "Autentikasi Gagal"}
```

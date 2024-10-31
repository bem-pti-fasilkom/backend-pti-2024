# API Documentation Backend PTI

Berikut adalah dokumentasi untuk penggunaan REST API Backend PTI 2024

## Format API

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

### a. Get All Pengaduan

```
GET /pengaduan
```

Dengan response:

- 200 OK

```typescript!=
export interface SeluruhPengaduan {
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
    author:          Author | null; // null if post is anonymous
    likes:           Like[];
    evidence:        string[];
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

export interface Like {
    id:        number;
    akun_sso:  string; // npm
    pengaduan: number; // id pengaduan
}
```

### b. Create Pengaduan

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

### c. Update Pengaduan

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

### d. Delete Pengaduan

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

### e. Like/Unlike Pengaduan

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

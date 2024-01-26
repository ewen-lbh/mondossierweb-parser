# mondossierweb

Get grades and detect changes in your grades, on schools using mon dossier web (mdw.(school domain))

## Installation

```bash
pip install mondossierweb
```

## Usage

```
Usage: mondossierweb [SAVE_AS] [URL] [GRADE_CODE] [USERNAME] [PASSWORD_COMMAND]
       mondossierweb --help

Environment variables:
    MDW_USE_CACHE: if set, the HTML will be cached to mdw.html and will be reused if it exists.
```

## Known `GRADE_CODE`s

| School   | Year | Department | `GRADE_CODE` |
| -------- | ---- | ---------- | ------------ |
| ENSEEIHT | 1A   | SN         | `N7I51`      |
| ENSEEIHT | 2A   | SN         | `N7I52`      |

# mondossierweb

Get grades and detect changes in your grades, on schools using mon dossier web (mdw.(school domain))

## Installation

```bash
pip install mondossierweb
```

## Usage

### Classique

```
Usage: mondossierweb [SAVE_AS] [URL] [GRADE_CODE] [USERNAME] [PASSWORD_COMMAND]
       mondossierweb --help

Environment variables:
    MDW_USE_CACHE: if set, the HTML will be cached to mdw.html and will be reused if it exists.
```

### Docker

First copy .env.exemple
```sh
cp .env.example .env
```

Then you can edit `.env`

```
SAVE_AS=grades.json
URL=https://mdw.inp-toulouse.fr
GRADE_CODE=N7I51
USERNAME= <Your username>
PASSWORD_COMMAND=echo '<Your password>'
MDW_USE_CACHE=1
PUSHBULLET_KEY=<Your pushbullet token>
PUSHBULLET_LINK=<The link of the notif (you can let this one empty)> 
```

## Known `GRADE_CODE`s

| School   | Year | Department | `GRADE_CODE` |
| -------- | ---- | ---------- | ------------ |
| ENSEEIHT | 1A   | 3EA        | `N7I41`      |
| ENSEEIHT | 2A   | 3EA        | `N7I42`      |
| ENSEEIHT | 3A   | 3EA        | `N7I43`      |
| ENSEEIHT | 1A   | SN         | `N7I51`      |
| ENSEEIHT | 2A   | SN         | `N7I52`      |


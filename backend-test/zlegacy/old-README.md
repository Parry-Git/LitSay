## 用户手册
https://fcnhy5uwfpqk.feishu.cn/wiki/YK6Qwu0h5imbF1kgXVocKI6cnfe?from=from_copylink

# interface-test

## Project setup
```
yarn install
```

### Compiles and hot-reloads for development
```
yarn serve
```

### Compiles and minifies for production
```
yarn build
```

### Lints and fixes files
```
yarn lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).



# backend-test

### Project setup
```
cd backend-test
conda create -n paperdb
conda activate paperdb
pip install -r requirements.txt
```

### Setup environment variables
```
touch .env
touch .flaskenv
```

**.env contains:**
```
# Flask
SECRET_KEY=
JWT_SECRET_KEY=

# OceanBase Connection
OB_HOST=
OB_PORT=
OB_USER=
OB_PASSWORD=
OB_DATABASE=
TEST_OB_DATABASE=

UPLOAD_FOLDER=
```

**.flask env contains:**
```
FLASK_APP=run.py
FLASK_ENV=development # or production
# FLASK_ENV can be 'development', 'production', 'testing'
# FLASK_DEBUG=1
```

### Flask init and run
```
flask init-db
flask run
```

### Test with examples in **app/utils/testcase.md**
╰─ curl --noproxy "127.0.0.1" http://127.0.0.1:5000/api/health
{"message":"Welcome to LitSay API!","status":"healthy"}

curl --noproxy "127.0.0.1" -X POST http://127.0.0.1:5000/api/auth/register -H "Content-Type: application/json" -d '{"username": "testuser", "password": "testpassword"}' -v

curl --noproxy "127.0.0.1" -X POST http://127.0.0.1:5000/api/auth/register -H "Content-Type: application/json" -d '{"username": "testuser", "password": "anotherpassword"}' -v

curl --noproxy "127.0.0.1" -X POST http://127.0.0.1:5000/api/auth/register -H "Content-Type: application/json" -d '{"password": "testpassword"}' -v

curl --noproxy "127.0.0.1" -X POST http://127.0.0.1:5000/api/auth/login -H "Content-Type: application/json" -d '{"username": "testuser", "password": "testpassword"}' -v

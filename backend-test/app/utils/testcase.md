### health check
curl --noproxy "127.0.0.1" http://127.0.0.1:5000/api/health
{"message":"Welcome to LitSay API!","status":"healthy"}

### rigister
curl --noproxy "127.0.0.1" -X POST -H "Content-Type: application/json" -d '{"username":"testuser1", "password":"password123"}' http://127.0.0.1:5000/api/auth/register

### login
curl --noproxy "127.0.0.1" -X POST -H "Content-Type: application/json" -d '{"username":"testuser1", "password":"password123"}' http://127.0.0.1:5000/api/auth/login

export YOUR_ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6InRlc3R1c2VyMSIsInJvbGUiOjAsImV4cCI6MTc0NzczNzkwM30.kSMtlKv5plp2u4KdnvUufRnBCMRmynPw5AiqTTwW4H8"

### Access a protected route
curl --noproxy "127.0.0.1" -H "Authorization: Bearer $YOUR_ACCESS_TOKEN" http://127.0.0.1:5000/api/auth/profile

### upload
curl --noproxy "127.0.0.1" -X POST \
     -H "Authorization: Bearer $YOUR_ACCESS_TOKEN" \
     -F "file=@/home/parry-wsl/study/database/upload_base/tests/mytest2.txt" \
     -F "title=My Test Paper2" \
     -F "directory_id=1" \
     -F "doi=10.1000/xyz123" \
     http://127.0.0.1:5000/api/papers/upload

### search
curl --noproxy "127.0.0.1" -H "Authorization: Bearer $YOUR_ACCESS_TOKEN" "http://127.0.0.1:5000/api/papers/search?q=Paper"

### list
curl --noproxy "127.0.0.1" -H "Authorization: Bearer $YOUR_ACCESS_TOKEN" http://127.0.0.1:5000/api/papers/

### get detials
curl --noproxy "127.0.0.1" -H "Authorization: Bearer $YOUR_ACCESS_TOKEN" http://127.0.0.1:5000/api/papers/1


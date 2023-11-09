# HIP02 Resolver

### Usage
HNS address lookup

`curl https://hip02.woodburn.au/<domain>`

### Examples

Getting HNS address for nathan.woodburn  
`curl https://hip02.woodburn.au/nathan.woodburn`  
Response: `hs1qjrtqpqk3xvzf5cxzss4wh2y9qyamksmv5sf5tt`

Getting HNS address for nathan.woodburn in JSON  
`curl https://hip02.woodburn.au/nathan.woodburn.json`  
Response: `{"address":"hs1qjrtqpqk3xvzf5cxzss4wh2y9qyamksmv5sf5tt","success":true}`

Getting BTC address for nathan.woodburn  
`curl https://hip02.woodburn.au/nathan.woodburn?token=btc`  
Response: `bc1qhs94zzcw64qnwq4hvk056rwxwvgrkd7tq7d4xw`  
`curl https://hip02.woodburn.au/nathan.woodburn.json?token=btc`  
Response: `{"address":"bc1qhs94zzcw64qnwq4hvk056rwxwvgrkd7tq7d4xw","success":true}`

### Docker Usage

`docker run -d -p 5000:5000 --name hip02 git.woodburn.au/nathanwoodburn/hip02-resolver:latest`
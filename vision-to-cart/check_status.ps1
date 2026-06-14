$out = "c:\Users\Admin\Documents\Hackthon_Project\vision-to-cart\status_out.txt"
"=== DOCKER PS ===" | Out-File $out
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>&1 | Out-File $out -Append
"" | Out-File $out -Append
"=== DOCKER COMPOSE PS ===" | Out-File $out -Append
docker compose -f "c:\Users\Admin\Documents\Hackthon_Project\vision-to-cart\docker-compose.yml" ps 2>&1 | Out-File $out -Append
"" | Out-File $out -Append
"=== DOCKER LOGS mcp-server (last 20) ===" | Out-File $out -Append
docker logs vision_cart_api --tail 20 2>&1 | Out-File $out -Append
"DONE" | Out-File $out -Append

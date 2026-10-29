import subprocess

print("==================================================")
print(" ABRIENDO TÚNEL PÚBLICO HACIA EL PUERTO 8000... ")
print("==================================================")
print(" Espera un segundo a que aparezca tu enlace '.lhr.life'\n")

# Comando directo sin bucles de lectura para evitar confusiones
subprocess.run([
    "ssh", 
    "-o", "StrictHostKeyChecking=no", 
    "-o", "User=nokey", 
    "-R", "80:localhost:8000", 
    "localhost.run"
])
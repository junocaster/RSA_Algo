import socket

def power(base, expo, m):
    res = 1
    base = base % m
    while expo > 0:
        if expo & 1:
            res = (res * base) % m
        base = (base * base) % m
        expo = expo // 2
    return res

def modInverse(e, phi):
    for d in range(2, phi):
        if (e * d) % phi == 1:
            return d
    return -1

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def generateKeys():
    p = 7919
    q = 1009
    
    n = p * q
    phi = (p - 1) * (q - 1)

    # Choose e, where 1 < e < phi(n) and gcd(e, phi(n)) == 1
    e = 0
    for i in range(2, 100):
        if gcd(i, phi) == 1:
            e = i
            break

    # Compute d such that e * d ≡ 1 (mod phi(n))
    d = modInverse(e, phi)

    return e, d, n

def encrypt(m, e, n):
    return power(m, e, n)

def decrypt(c, d, n):
    return power(c, d, n)

def main():
    # Generate RSA keys
    e, d, n = generateKeys()
    
    # Save public key to com.txt
    with open("com.txt", "w") as f:
        f.write(f"{e},{n}")
    
    print(f"Public key (e,n): ({e}, {n})")
    print(f"Private key (d,n): ({d}, {n})")
    print("Keys generated and public key saved to com.txt")
    
    # Set up server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('172.20.10.6', 5000)) 
    server.listen(1)
    print("Waiting for Bob to connect...")
    
    conn, addr = server.accept()
    print(f"Connected to Bob at {addr}")
    
    try:
        # Send public key to Bob
        conn.sendall(f"{e},{n}".encode())
        
        while True:
            # Receive encrypted message
            data = conn.recv(4096).decode()
            if not data:
                break
            
            # Parse the encrypted message
            encrypted_msg = [int(num) for num in data.split(',') if num]
            
            # Decrypt each number in the message
            decrypted_chars = [decrypt(c, d, n) for c in encrypted_msg]
            decrypted_msg = ''.join(chr(c) for c in decrypted_chars)
            print(f"Bob: {decrypted_msg}")
            
            # Get Alice's response
            response = input("Alice: ")
            if response.lower() == 'exit':
                conn.sendall("exit".encode())
                break
            
            # Encrypt each character in the response
            encrypted_response = [encrypt(ord(c), e, n) for c in response]
            # Convert to comma-separated string
            encrypted_str = ','.join(str(c) for c in encrypted_response)
            conn.sendall(encrypted_str.encode())
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
        server.close()
        print("Server closed")

if __name__ == "__main__":
    main()
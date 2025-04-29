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

def encrypt(m, e, n):
    return power(m, e, n)

def decrypt(c, d, n):
    return power(c, d, n)

def modInverse(e, phi):
    for d in range(2, phi):
        if (e * d) % phi == 1:
            return d
    return -1

def main():
    # Connect to Alice
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to Alice's server
        client.connect(('172.20.10.6', 5000))
        print("Connected to Alice's server")
        
        # Receive Alice's public key
        key_data = client.recv(1024).decode()
        e, n = map(int, key_data.split(','))
        print(f"Received Alice's public key: ({e}, {n})")
        
        # Alice's private key
        p = 7919
        q = 1009
        phi = (p - 1) * (q - 1)
        d = modInverse(e, phi)
        print(f"Calculated private key for decryption: d = {d}")
        
        while True:
            # Get message from Bob
            message = input("Bob: ")
            if message.lower() == 'exit':
                break
            
            # Encrypt each character in the message
            encrypted_msg = [encrypt(ord(c), e, n) for c in message]
            # Convert to comma-separated string
            encrypted_str = ','.join(str(c) for c in encrypted_msg)
            client.sendall(encrypted_str.encode())
            
            # Receive Alice's response
            response_data = client.recv(4096).decode()
            if not response_data:
                break
                
            # Check if server wants to exit
            if response_data == "exit":
                print("Alice has ended the conversation.")
                break
            
            # Parse the encrypted response
            encrypted_response = [int(num) for num in response_data.split(',') if num]
            
            # Decrypt each number in the response using the private key (d, n)
            try:
                decrypted_chars = []
                for c in encrypted_response:
                    # Decrypt the character
                    dec_value = decrypt(c, d, n)
                    
                    # Ensure it's in valid Unicode range
                    if 0 <= dec_value <= 0x10FFFF:
                        decrypted_chars.append(chr(dec_value))
                    else:
                        # If out of range, use a placeholder
                        decrypted_chars.append('?')
                
                decrypted_msg = ''.join(decrypted_chars)
                print(f"Alice: {decrypted_msg}")
            except Exception as ex:
                print(f"Decryption error: {ex}")
                print(f"Raw response: {response_data[:50]}...")
            
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client.close()
        print("Client closed")

if __name__ == "__main__":
    main()
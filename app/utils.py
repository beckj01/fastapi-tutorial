from passlib.context import CryptContext
# pip install passlib[argon2]


pwd_context = CryptContext(
    schemes=["argon2"],
    argon2__type="ID",           # Argon2id variant
    argon2__memory_cost=65536,   # 64 MiB
    argon2__rounds=3,            # 3 iterations
    argon2__parallelism=4       # 4 threads
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

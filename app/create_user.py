# create_user.py

from sqlalchemy.orm import Session
from app import models, database, auth

def create_user(username: str, password: str):
    db: Session = next(database.get_db())
    hashed_password = auth.get_password_hash(password)
    user = models.APIKey(username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"User {username} created successfully.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python create_user.py <username> <password>")
    else:
        create_user(sys.argv[1], sys.argv[2])

"""Demo user directory for MediAssist Health Network.

In production this would be backed by an identity provider or a users table.
For this assignment, five demo accounts (one per role) are hardcoded here with
bcrypt-hashed passwords.
"""
from dataclasses import dataclass

from app.core.security import hash_password


@dataclass(frozen=True)
class DemoUser:
    username: str
    password: str  # plaintext, only used to compute the hash below
    role: str
    display_name: str
    department: str


_RAW_USERS: list[DemoUser] = [
    DemoUser("dr.mehta", "Doctor@123", "doctor", "Dr. Mehta", "Clinical"),
    DemoUser("nurse.priya", "Nurse@123", "nurse", "Nurse Priya", "Clinical"),
    DemoUser("billing.ravi", "Billing@123", "billing_executive", "Ravi Kumar", "Billing & Insurance"),
    DemoUser("tech.anand", "Tech@123", "technician", "Anand Singh", "Medical Equipment"),
    DemoUser("admin.sys", "Admin@123", "admin", "System Admin", "Executive / IT"),
]

# username -> {hashed_password, role, display_name, department}
USERS: dict[str, dict] = {
    user.username: {
        "hashed_password": hash_password(user.password),
        "role": user.role,
        "display_name": user.display_name,
        "department": user.department,
    }
    for user in _RAW_USERS
}


def get_user(username: str) -> dict | None:
    return USERS.get(username)

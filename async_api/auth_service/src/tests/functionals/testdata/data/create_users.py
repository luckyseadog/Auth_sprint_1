from faker import Faker
import json
import uuid
import random

roles = [
    {
        'id': str(uuid.uuid4()),
        'title': 'admin',
        'description': 'admin role',
    },
    {
        'id': str(uuid.uuid4()),
        'title': 'user',
        'description': 'user role',
    },
    {
        'id': str(uuid.uuid4()),
        'title': 'guest',
        'description': 'guest role',
    },
    {
        'id': str(uuid.uuid4()),
        'title': 'subscriber',
        'description': 'subscriber role',
    },
]

def create_roles():
    with open('roles.json', 'w') as file:
        file.write(json.dumps(roles, indent=4))


def create_users():
    users = [
        {
            'id': str(uuid.uuid4()),
            'login': Faker().user_name(),
            'email': Faker().email(),
            'password': Faker().password(),
            'first_name': Faker().first_name(),
            'last_name': Faker().last_name(),
            'roles': random.choices(roles, k=random.randint(1, 2)),
            'history': [
                {
                    'id': str(uuid.uuid4()),
                    'occured_at': Faker().date_time().strftime('%Y-%m-%d %H:%M:%S'),
                    'action': random.choice(['login', 'logout']),
                    'fingerprint': Faker().user_agent(),
                } for _ in range(random.randint(0, 10))
            ],
        } for _ in range(100)
    ]
    return users


if __name__ == '__main__':
    with open('users.json', 'w') as file:
        file.write(json.dumps(create_roles(), indent=2))
        file.write(json.dumps(create_users(), indent=2))

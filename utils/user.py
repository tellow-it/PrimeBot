from typing import Dict


def format_user_data(user_data: Dict) -> str:
    role = ''
    if user_data["role"] == 'admin':
        role = "Администратор"
    elif user_data["role"] == 'user':
        role = "Пользователь"
    elif user_data["role"] == 'advanced_user':
        role = "Менеджер"
    return f"\nИмя:     {user_data['name']} \n" \
           f"\nФамилия: {user_data['surname']} \n" \
           f"\nРоль:    {role} \n" \
           f"\nТелефон: {user_data['telephone']} \n"

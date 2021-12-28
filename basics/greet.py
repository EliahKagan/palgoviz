"""Hello world example."""


def hello(name, lang='en'):
    """Greet the user."""
    if lang == 'en': 
        print(f'Hello, {name}!')  # fstring demonstration
    elif lang == 'es':
        print(f'¡Hola, {name}!')  # fstring demonstration en español
    else:
        raise ValueError(f'{lang} is an unrecognized language code')
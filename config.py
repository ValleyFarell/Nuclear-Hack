from environs import Env

def load_config(path: str | None):
    env: Env = Env()
    env.read_env(path=path)
    return env.str('TOKEN')

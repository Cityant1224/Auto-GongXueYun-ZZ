import json, os

# 配置文件本地路径
config_path = "user.json"
# 环境变量名称
env_var_name = "USERS"


def load_config():
    full_config_path = os.path.join(config_path)
    print(f"\n>>>>>>>>>> 打卡任务启动! <<<<<<<<<<\n")

    config_data = {}
    config_loaded = False

    if os.path.exists(full_config_path):
        try:
            with open(full_config_path, "r", encoding="utf-8") as file:
                config_data = json.load(file)
                config_loaded = True
                print(f"配置文件加载成功: {full_config_path}\n")
                # print("载入的配置文件信息: ", config_data)
        except Exception as e:
            print(f"配置文件加载失败: {full_config_path}\n")

    if not config_loaded:
        env_value = os.environ.get(env_var_name)
        if env_value:
            try:
                config_data = json.loads(env_value)
                config_loaded = True
                print(f"环境变量加载成功: {env_var_name}\n")
                # print("载入的环境变量配置信息: ", config_data)
            except Exception as e:
                print(f"环境变量加载失败: {env_var_name}\n")

    if not config_loaded:
        print("未找到配置信息, 使用默认空配置。\n")

    return config_data

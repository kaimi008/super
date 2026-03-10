[app]

# 应用的标题 (手机桌面上显示的名字)
title = 我的Python游戏

# 应用的包名 (必须是唯一的，通常用反向域名格式，如 com.你的名字.游戏名)
package.name = mypythongame

# 包名的域名部分 (上面两行组合起来就是 com.mypythongame.mypythongame)
package.domain = org.test

# 主程序文件名 (如果你的主文件叫 main.py，这里就填 main.py)
source.dir =Android-game.py
# 包含的文件扩展名
source.include_exts = py,png,jpg,kv,atlas,json

# 版本号
version = 0.1

# 作者名字
author = zhaomu

# 最低支持的 Android 版本 (建议 13 即 API 33，或者根据你的需求调整)
android.minapi = 21
android.sdk = 24
android.ndk = 25b

# 需要的权限 (例如访问网络、震动等，不需要可以留空或注释)
android.permissions = INTERNET,VIBRATE

# 应用方向 (portrait=竖屏, landscape=横屏)
orientation = portrait

# 是否开启全屏
android.fullscreen = True

[buildozer]

# 构建配置文件版本
profile = android

# 构建环境名称
build_dir = ./.buildozer

# 缓存目录
bin_dir = ./bin
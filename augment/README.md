# 弹球模拟器

这个项目模拟了五个不同颜色的球在多个嵌套、旋转的六边形中弹跳的视觉效果。每个六边形以不同的速度旋转，创造出引人入胜的视觉模式。除了最外层的六边形外，所有嵌套的六边形都有一个随机选择的缺失墙壁，允许球在内外六边形之间无缝通过。

## 特点

- 多个嵌套的旋转六边形
- 五个不同颜色的弹跳球
- 真实的物理效果：重力、摩擦力和角动量
- 球与旋转墙壁之间的精确碰撞检测
- 可调节的参数：重力强度、摩擦水平、旋转速度和六边形大小

## 安装与运行

我们提供了简单的脚本来自动设置环境并运行模拟器。所有的环境都将在当前文件夹内创建，确保完全隔离。

### Linux/macOS用户：

```bash
# 运行脚本
./run.sh
```

### Windows用户：

```
# 运行脚本
run.bat
```

### 手动安装和运行（如果脚本不起作用）：

1. 确保您已安装Python 3.6+
2. 创建虚拟环境：
   ```bash
   # 在当前文件夹创建虚拟环境
   python -m venv venv

   # Linux/macOS激活虚拟环境
   source venv/bin/activate

   # Windows激活虚拟环境
   venv\Scripts\activate
   ```
3. 安装依赖项：
   ```bash
   pip install -r requirements.txt
   ```
4. 运行模拟器：
   ```bash
   python bouncing_balls.py
   ```

## 自定义参数

您可以通过编辑`bouncing_balls.py`文件中的以下参数来自定义模拟：

- `GRAVITY`：重力强度
- `FRICTION`：摩擦系数
- `ELASTICITY`：弹性系数
- `BALL_RADIUS`：球的半径
- `NUM_BALLS`：球的数量
- `NUM_HEXAGONS`：六边形的数量

## 控制

- ESC键：退出模拟

# O3mini Simulation

该项目在独立的 O3mini 文件夹内实现了一个 Python 模拟程序，展示了多个嵌套旋转六边形内5个不同颜色小球的动态弹跳仿真。所有内容均在隔离的环境内运行，便于和其它项目代码进行对比。

## 环境配置

建议使用 Python 虚拟环境来隔离项目依赖。可以按照以下步骤进行设置：

1. **创建虚拟环境：**

   ```bash
   python3 -m venv venv
   ```

2. **激活虚拟环境：**

   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - Windows:
     ```bash
     venv\Scripts\activate
     ```

3. **安装依赖：**

   ```bash
   pip install -r requirements.txt
   ```

4. **运行脚本：**

   ```bash
   python simulation.py
   ```

## 调整参数

可以在 `simulation.py` 脚本中修改以下可调参数，根据需要调整重力、摩擦、旋转速度和六边形尺寸：

- `GRAVITY`
- `FRICTION`
- `HEX_ROT_SPEEDS`
- `HEX_BASE_SIZE`
- `HEX_SCALE`

Enjoy the simulation!
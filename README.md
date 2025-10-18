# 数字病理切片在线浏览系统

一个面向教学场景的数字病理切片在线浏览平台，支持 KFB 切片转换、深度缩放浏览与元数据管理，并提供 Docker Compose 一键部署能力。

## 功能特性

- ✅ **KFB 转换工具**：支持将 KFB/SVS 切片转换为金字塔 TIFF，并可选生成 DZI 数据集
- ✅ **在线浏览**：基于 OpenSeadragon 的深度缩放浏览，支持缩放、平移与导航
- ✅ **元数据管理**：PostgreSQL 存储切片元数据（标题、描述、扩展属性）
- ✅ **RESTful API**：Flask 后端提供切片列表、详情、DZI 参数与瓦片接口
- ✅ **Docker 化部署**：Compose 编排后端、前端、PostgreSQL 与 Nginx，一键启动

## 技术栈

| 模块     | 技术                                                   |
| -------- | ------------------------------------------------------ |
| 后端 API | Python, Flask, SQLAlchemy, OpenSlide, libvips/pyvips   |
| 前端 UI  | React, OpenSeadragon, Axios                            |
| 数据库   | PostgreSQL                                             |
| Web 服务 | Nginx（反向代理至前端与后端）                          |
| 容器化   | Docker, Docker Compose                                 |

## 仓库结构

```
.
├── backend/               # Flask 后端服务
│   ├── app.py             # 主应用与 REST API
│   ├── config.py          # 环境变量配置
│   ├── models.py          # SQLAlchemy 模型定义
│   ├── requirements.txt   # Python 依赖
│   └── slide_converter.py # KFB 转换工具脚本
├── frontend/              # React 前端应用
│   ├── Dockerfile
│   ├── package.json
│   ├── public/
│   └── src/
├── nginx/nginx.conf       # Nginx 反向代理配置
├── scripts/convert_kfb.sh # 批量/命令行转换脚本
├── docker-compose.yml     # 服务编排
├── init.sql               # PostgreSQL 初始化脚本
├── .env.example           # 环境变量示例
├── README.md              # 项目说明（本文档）
└── DEPLOYMENT.md          # 部署手册（详细步骤）
```

## 快速开始

### 1. 准备环境

- 已安装 Docker (>= 20.10) 与 Docker Compose (v2)
- 复制环境配置文件：

```bash
cp .env.example .env
```

如需修改数据库密码、切片目录等，请在 `.env` 中调整。

### 2. 启动服务

```bash
docker-compose up -d
```

- 前端访问地址：<http://服务器IP>
- REST API：<http://服务器IP>/api

首次启动会自动：
- 拉起 PostgreSQL 并执行 `init.sql` 创建表结构
- 构建并运行 Flask 后端（Gunicorn）
- 构建 React 前端并通过 Nginx 提供访问

### 3. 导入切片与元数据

1. 将 KFB/SVS 切片文件复制/挂载到 `slides_data` 卷，对应容器内 `/data/slides`
2. 使用脚本转换切片：

```bash
./scripts/convert_kfb.sh /路径/示例.kfb -o ./converted --dzi
```

3. 通过 API（或后续管理界面）追加元数据，例如：

```bash
curl -X POST http://服务器IP/api/slides \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "示例切片",
    "description": "肝组织 HE 染色",
    "file_path": "converted/示例.tif",
    "metadata": {"patient": "匿名", "magnification": "40x"}
  }'
```

完成后即可在前端列表中看到新切片并进行浏览。

## REST API 概览

| 方法 | 路径                                           | 说明                 |
| ---- | ---------------------------------------------- | -------------------- |
| GET  | `/api/slides`                                  | 获取切片列表         |
| GET  | `/api/slides/{id}`                             | 获取切片详情         |
| POST | `/api/slides`                                  | 新增切片元数据       |
| GET  | `/api/slides/{id}/dzi`                         | 获取 DZI 元数据参数  |
| GET  | `/api/slides/{id}/tiles/{level}/{col}/{row}`   | 获取指定瓦片（JPEG） |

- `level` 从 0 开始，数值越大表示分辨率越高
- `col`/`row` 表示瓦片列/行索引

## KFB 转换方案

1. **推荐**：内置脚本调用 **pyvips/libvips** 将 KFB/SVS 转为金字塔 TIFF
   - 自动为 DeepZoom 准备合适的瓦片结构
   - 可选生成标准 DeepZoom (`.dzi`) 数据集，适合离线加载
2. **备选**：如需使用专有 kfbReader/KFBIO 工具，可按供应商说明生成 TIFF，再上传至 `/data/slides`

转为金字塔 TIFF 后，前端可直接通过后端 API 进行动态瓦片访问，无需额外的静态瓦片部署。

## 服务器资源建议

| 场景   | 最低配置                     | 推荐配置                         |
| ------ | ---------------------------- | -------------------------------- |
| 教学/演示 | 2 核 CPU / 4 GB RAM / 50 GB 存储 | 4 核 CPU / 8-16 GB RAM / 200 GB SSD |

切片文件体积较大，请确保磁盘空间充足，并优先使用 SSD 以获得更好的随机读性能。

## 常见问题

- **OpenSlide/pyvips 未安装？** 请确认 Docker 镜像已正确构建，或在宿主机安装 `libopenslide`/`libvips` 库。
- **无法访问前端？** 检查 Nginx 容器日志 `docker-compose logs nginx`，确认端口 80 未被其他服务占用。
- **切片加载缓慢？** 可在 `.env` 中调整 `DEEPZOOM_TILE_SIZE`、`DEEPZOOM_OVERLAP`，或使用性能更好的服务器。

## 相关文档

- [DEPLOYMENT.md](./DEPLOYMENT.md)：详细部署、环境要求与运维指南
- [scripts/convert_kfb.sh](./scripts/convert_kfb.sh)：批量转换脚本
- [backend/slide_converter.py](./backend/slide_converter.py)：转换实现细节

如在部署或使用过程中遇到问题，欢迎通过 Issue 反馈或提交 PR 进行改进。

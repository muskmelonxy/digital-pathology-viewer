# 部署指南

本文档提供在云服务器环境中部署数字病理切片在线浏览系统的详细步骤。示例环境基于 Ubuntu 22.04，其它 Linux 发行版亦可参照执行。

## 一、环境准备

1. **安装 Docker 与 Docker Compose v2**

```bash
curl -fsSL https://get.docker.com | bash
sudo usermod -aG docker $USER
# 重新登录后
docker --version
docker compose version
```

2. **克隆仓库**

```bash
git clone https://your-domain/kfb-slide-viewer.git
cd kfb-slide-viewer
```

3. **配置环境变量**

```bash
cp .env.example .env
```

根据实际需求调整 `.env` 中的：

- 数据库用户名、密码（`POSTGRES_USER`/`POSTGRES_PASSWORD`）
- 切片存储路径 `SLIDE_STORAGE_PATH`（容器内默认 `/data/slides`）
- CORS 允许的来源 `ALLOWED_ORIGINS`（生产环境建议填写实际域名）
- React 构建时的 API 地址 `REACT_APP_API_BASE_URL`（默认 `/api`，使用同域反向代理）

## 二、目录与数据挂载

服务会创建以下 Docker 卷：

- `postgres_data`：持久化 PostgreSQL 数据
- `slides_data`：存放原始切片或转换后的 TIFF 文件

如需将本地已有切片挂载为卷，可编辑 `docker-compose.yml`，将宿主机目录映射到 `slides_data`。

```yaml
  backend:
    volumes:
      - /path/to/slides:/data/slides
```

> ⚠️ 切片数据体积较大，请确保存储空间充足，并优先使用 SSD。

## 三、启动服务

```bash
docker compose up -d --build
```

命令成功后，各服务状态可通过 `docker compose ps` 查看。

- 访问前端：`http://<服务器IP>`
- 验证后端：`curl http://<服务器IP>/api/health`
- 查看日志：`docker compose logs -f backend`

## 四、导入切片与元数据

1. **放置切片文件**：将 `.kfb` 或 `.tif` 文件复制到 `slides_data` 对应目录。

2. **转换 KFB（如需要）**：

```bash
./scripts/convert_kfb.sh /data/slides/source/sample.kfb -o /data/slides/converted --dzi
```

- 默认输出金字塔 TIFF（`sample.tif`）
- `--dzi` 选项会额外生成 DeepZoom 数据集（可用于离线浏览）

3. **写入元数据**：通过 REST API 注册切片路径与描述信息。

```bash
curl -X POST http://<服务器IP>/api/slides \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "肝组织 HE",
    "description": "40x 放大",
    "file_path": "converted/sample.tif",
    "metadata": {"teacher": "Dr. Zhang", "tags": ["肝", "教学"]}
  }'
```

成功后，前端列表会自动显示该切片。

## 五、运维与升级

### 1. 查看与管理容器

```bash
docker compose ps
# 查看某服务日志
docker compose logs -f nginx
# 重启后端
docker compose restart backend
```

### 2. 升级流程

```bash
git pull
# 如有依赖变更，重新构建镜像
docker compose up -d --build
```

### 3. 数据备份

- 数据库：`docker compose exec postgres pg_dump -U slides_user slides_db > backup.sql`
- 切片文件：直接备份宿主机映射或 Docker 卷内容

## 六、常见问题排查

| 问题 | 可能原因 | 解决方案 |
| ---- | -------- | -------- |
| 前端无法访问 | Nginx 未启动 / 端口被占用 | `docker compose logs nginx` 检查日志，确保 80 端口空闲 |
| API 返回 503 | OpenSlide/pyvips 未安装成功 | 重新构建后端镜像，确认安装步骤无报错 |
| 切片瓦片 404 | `file_path` 配置错误或文件不存在 | 核实 `slides` 表中的 `file_path` 与容器内实际路径 |
| 转换失败 | KFB 专有编码不受支持 | 使用厂商提供的 kfbReader/KFBIO 工具先导出 TIFF |

## 七、安全建议

- 生产环境中，请使用公网负载均衡或 Nginx 开启 HTTPS
- 为 API 添加认证/授权（如 JWT/Basic Auth）
- 限制上传来源，定期扫描切片文件存储目录

## 八、下线与清理

```bash
docker compose down
# 如需清理数据卷
docker compose down -v
```

此操作将删除容器与数据卷，请谨慎执行。

---

如需定制开发或二次集成，可参考后端（Flask）与前端（React）源码结构，根据业务需求扩展对应模块。

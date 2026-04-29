# FastAPI Items Demo

一个适合新手学习的 FastAPI 示例，使用**内存字典**保存数据（不接数据库）。

## 运行方式

```bash
pip install fastapi uvicorn pytest
uvicorn app:app --reload
```

## 接口说明

- `GET /health`：健康检查
- `GET /items`：获取所有 items
- `POST /items`：创建 item
- `GET /items/{item_id}`：获取单个 item
- `PUT /items/{item_id}`：更新指定 item
- `DELETE /items/{item_id}`：删除指定 item

> 当 `item_id` 不存在时：
> - `PUT /items/{item_id}` 返回 `404`
> - `DELETE /items/{item_id}` 返回 `404`
